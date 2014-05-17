import re
import string
import time
import csv
import urllib2
from bs4 import BeautifulSoup

#un-ignore wins_pyth and losses_pyth if lockout season stats are scaled properly
statsToIgnore= ["player","g", "mp", "arena_name", "attendance", "wins_pyth", "losses_pyth"]
currTeams= ['/teams/BRK/2014.html', '/teams/IND/2014.html', '/teams/MIA/2014.html', '/teams/WAS/2014.html',
            '/teams/SAS/2014.html', '/teams/LAC/2014.html', '/teams/OKC/2014.html', '/teams/POR/2014.html',
            '/teams/TOR/2014.html', '/teams/ATL/2014.html', '/teams/CHA/2014.html', '/teams/CHI/2014.html',
            '/teams/DAL/2014.html', '/teams/GSW/2014.html', '/teams/MEM/2014.html', '/teams/HOU/2014.html']

def grabSiteData(url):
    usock= urllib2.urlopen(url)
    data= usock.read()
    usock.close()
    return BeautifulSoup(data)

#returns dictionary of (playoff_team_url,num_wins_in_playoffs) pairs
def getPlayoffTeams(year):
    teams_wins= {}
    query_soup= grabSiteData("http://www.basketball-reference.com/playoffs/NBA_"+str(year)+".html")
    playoff_data= query_soup.find('div', {"id" : "all_playoffs"}).findAll('tr', {"class" : "mobile_text"})
    for row in playoff_data:
        tds= row.findAll("td")
        p_round= tds[0].text.encode("ascii","ignore")
        #if "First" not in p_round:
        record_index= p_round.find('(')
        wins= [int(p_round[record_index+1]), int(p_round[record_index+3])]
        matchup= [elem["href"].encode("ascii","ignore") for elem in tds[1].findAll("a")][:-1]
        for i,team in enumerate(matchup):
            teams_wins[team]= teams_wins.get(team,0) + wins[i]
    return teams_wins


def scrapeTeamStatsFromTable(id, query_soup, all_stats, per_game, lg_ranks):
    #get list of indices containing stats I care about
    div= query_soup.find('div', {"class" : "table_container", "id" : id})
    header= div.find("thead").findAll('tr')[-1]
    indices= []
    for i,elem in enumerate(header.findAll('th')): 
        if elem['data-stat'] not in statsToIgnore:
            indices += [i]

    #get stats located in desired indices
    stat_rows= div.findAll("tr")
    for row in stat_rows:
        statline= row.findAll('td')
        arraysToAddTo= []
        if len(statline) != 0: #statline is [] for table header rows
            #kind of janky
            if statline[0].text.encode("ascii","ignore")=="Lg Rank":
                arraysToAddTo += [lg_ranks,all_stats]
            if statline[0].text.encode("ascii","ignore") in ["Team/G", "Opponent/G"]: 
                arraysToAddTo += [per_game,all_stats]
            if statline[0].text.encode("ascii","ignore")=="Team" and id=="div_team_misc":
                arraysToAddTo += [per_game,all_stats]
            for j in indices:
                for arr in arraysToAddTo:
                    value= float(statline[j].text.encode("ascii","ignore").replace("%",""))
                    arr += [value]
    return (all_stats, per_game, lg_ranks)
    

#returns (all_stats, per_game, lg_ranks) tuple of arrays
def scrapeTeamStats(team_url):
    all_stats= []
    per_game= []
    lg_ranks= []
    soup= grabSiteData("http://www.basketball-reference.com"+team_url)

    #ids of tables I want to scrape from
    arr= (all_stats, per_game, lg_ranks)
    table_ids= ["div_team_stats", "div_team_misc"]
    for id in table_ids:
        (all_stats, per_game, lg_ranks)= scrapeTeamStatsFromTable(id, soup, all_stats, per_game, lg_ranks)
    
    return (all_stats, per_game, lg_ranks) 


#statType= 0 for all_stats, 1 for per_game, 2 for lg_ranks
def createTrainingSets(yearStart, yearEnd, folder, fn_all_stats, fn_per_game, fn_lg_ranks):
    #create CSVs and csv_writers
    asCSV= open(folder+fn_all_stats,'wb') #"as" for "all stats"
    pgCSV= open(folder+fn_per_game,'wb')  #"pg" for "per game"
    lrCSV= open(folder+fn_lg_ranks,'wb')  #"lr" for "league ranks"
    as_wr = csv.writer(asCSV)
    pg_wr = csv.writer(pgCSV)
    lr_wr = csv.writer(lrCSV)

    #populate CSVs
    for year in range(yearStart, yearEnd+1): 
        playoff_teams= getPlayoffTeams(year)
        for url,wins in playoff_teams.items():
            arrs= (all_stats,per_game,lg_ranks)= scrapeTeamStats(url)
            for arr in arrs:
                arr += [url, wins]
            as_wr.writerow(all_stats)
            pg_wr.writerow(per_game)
            lr_wr.writerow(lg_ranks)
        print "Done with year", year


def createTestSets(folder, fn_all_stats, fn_per_game, fn_lg_ranks):
    #create CSVs and csv_writers
    asCSV= open(folder+fn_all_stats,'wb')  #"as" for "all stats"
    pgCSV= open(folder+fn_per_game,'wb')   #"pg" for "per game"
    lrCSV= open(folder+fn_lg_ranks,'wb')   #"lr" for "league ranks"
    as_wr = csv.writer(asCSV)
    pg_wr = csv.writer(pgCSV)
    lr_wr = csv.writer(lrCSV)

    #populate CSVs
    for teamURL in currTeams:
        arrs= (all_stats,per_game,lg_ranks)= scrapeTeamStats(teamURL)
        for arr in arrs:
            arr += [teamURL] 
        as_wr.writerow(all_stats)
        pg_wr.writerow(per_game)
        lr_wr.writerow(lg_ranks)
    print "Done"

if __name__=="__main__":
    start= time.time()
    #createTrainingSets(1980,2013,'/Users/nikhilnathwani/Desktop/','all_stats','per_game','league_ranks')
    createTestSets('/Users/nikhilnathwani/Desktop/', 'all_stats2014', 'per_game2014', 'lg_ranks2014')
    #print getPlayoffTeams(2013)
    print "Time taken:", time.time()-start