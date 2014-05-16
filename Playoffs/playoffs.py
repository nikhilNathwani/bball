import re
import string
import time
import csv
import urllib2
from bs4 import BeautifulSoup

statsToIgnore= ["player","g", "mp", "arena_name", "attendance"]
currTeams= ['/teams/BRK/2014.html', '/teams/IND/2014.html', '/teams/MIA/2014.html', '/teams/WAS/2014.html',
            '/teams/SAS/2014.html', '/teams/LAC/2014.html', '/teams/OKC/2014.html', '/teams/POR/2014.html']

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


def scrapeTeamStatsFromTable(id, year, query_soup, all_stats, raw_vals, lg_ranks):
    #get list of indices containing stats I care about
    div= query_soup.find('div', {"class" : "table_container", "id" : id})
    header= div.find("thead").findAll('tr')[-1]
    indices= []
    for i,elem in enumerate(header.findAll('th')): 
        if elem['data-stat'] not in statsToIgnore:
            indices += [i]

    #get stats located in desired indices
    stat_rows= div.find("tbody").findAll("tr")
    for row in stat_rows:
        arraysToAddTo= [all_stats]
        statline= row.findAll('td')
        if statline[0].text.encode("ascii","ignore")=="Lg Rank":
            arraysToAddTo += [lg_ranks]
        else: 
            arraysToAddTo += [raw_vals]
        for j in indices:
            for arr in arraysToAddTo:
                value= float(statline[j].text.encode("ascii","ignore").replace("%",""))
                arr += [value]
    return (all_stats, raw_vals, lg_ranks)
    

#returns (all_stats, raw_vals, lg_ranks) tuple of arrays
def scrapeTeamStats(team_url):
    all_stats= []
    raw_vals= []
    lg_ranks= []
    soup= grabSiteData("http://www.basketball-reference.com"+team_url)

    #ids of tables I want to scrape from
    arr= (all_stats, raw_vals, lg_ranks)
    table_ids= ["div_team_stats", "div_team_misc"]
    for id in table_ids:
        (all_stats, raw_vals, lg_ranks)= scrapeTeamStatsFromTable("div_team_stats", soup, all_stats, raw_vals, lg_ranks)
    
    return (all_stats, raw_vals, lg_ranks) 


#statType= 0 for all_stats, 1 for raw_vals, 2 for lg_ranks
def createTrainingSets(yearStart, yearEnd, folder, fn_all_stats, fn_raw_stats, fn_lg_ranks):
    #create CSVs and csv_writers
    asCSV= open(folder+fn_all_stats,'wb')
    rsCSV= open(folder+fn_raw_stats,'wb')
    lrCSV= open(folder+fn_lg_ranks,'wb')
    as_wr = csv.writer(asCSV)
    rs_wr = csv.writer(rsCSV)
    lr_wr = csv.writer(lrCSV)

    #populate CSVs
    for year in range(yearStart, yearEnd+1): 
        playoff_teams= getPlayoffTeams(year)
        for url,wins in playoff_teams.items():
            arrs= (all_stats,raw_stats,lg_ranks)= scrapeTeamStats(url)
            for arr in arrs:
                arr += [url, wins]
            as_wr.writerow(all_stats)
            rs_wr.writerow(raw_stats)
            lr_wr.writerow(lg_ranks)
        print "Done with year", year


def createTestSets(year, folder, fn_all_stats, fn_raw_stats, fn_lg_ranks):
    #create CSVs and csv_writers
    asCSV= open(folder+fn_all_stats,'wb')  #"as" for "all stats"
    rsCSV= open(folder+fn_raw_stats,'wb')  #"rs" for "raw stats"
    lrCSV= open(folder+fn_lg_ranks,'wb')   #"lr" for "league ranks"
    as_wr = csv.writer(asCSV)
    rs_wr = csv.writer(rsCSV)
    lr_wr = csv.writer(lrCSV)

    #populate CSVs
    for teamURL in currTeams:
        data_to_append= [year] #to be appended to end of each attribute vectors
        arrs= (all_stats,raw_stats,lg_ranks)= scrapeTeamStats(teamURL,year)
        for arr in arrs:
            arr += data_to_append 
        as_wr.writerow(all_stats)
        rs_wr.writerow(raw_stats)
        lr_wr.writerow(lg_ranks)
    print "Done"

if __name__=="__main__":
    start= time.time()
    createTrainingSets(2011,2011,'/Users/nikhilnathwani/Desktop/','all_stats2011','raw_stats2011','league_ranks2011')
    #createTestSets(2014, '/Users/nikhilnathwani/Desktop/BBall/Playoffs/test/', 'all_stats2014', 'raw_stats2014', 'lg_ranks2014')
    #print getPlayoffTeams(2013)
    print "Time taken:", time.time()-start