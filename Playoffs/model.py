import re
import string
import time
import csv
import urllib2
import sys
from bs4 import BeautifulSoup

teamsByYear= {}

class Team:
    def __init__(self,u,a,l,s):
        self.url= u
        self.attr= a
        self.true_label= l
        self.predicted_label= 0
        self.sim= s
        self.score= 0
        self.winPct= -1
        self.year= 0

    def teamName(self, t):
        s= t.url
        return s[:s.rfind('/')][s[:s.rfind('/')].rfind('/')+1:]

class PlayoffTree:
    def __init__(self):
        self.standings= {"east":[], "west":[]}
        self.games= [] #list of tuples of all playoff matchups, used in gui.py
        self.actuals= [] #actual game matchups
        self.trueWinner= ""

#un-ignore wins_pyth and losses_pyth if lockout season stats are scaled properly
statsToIgnore= ["player","g", "mp", "arena_name", "attendance", "wins_pyth", "losses_pyth"]

#returns dictionary of (playoff_team_url,num_wins_in_playoffs) pairs
def getPlayoffTeams(year):
    teams_wins= {} #counts number of series each team won in a given playoff year
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
            #add 1 to "team" if that team won the series, 0 otherwise
            teams_wins[team]= teams_wins.get(team,0) + (wins[i] > wins[not i])
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


def getPlayoffStandings(year):
    query_soup= grabSiteData("http://www.basketball-reference.com/leagues/NBA_"+str(year)+".html")
    confs= {"east":[0]*8,"west":[0]*8}
    for conf in confs:
        standings_div= query_soup.find('div', {"id" : "div_"+conf[0].upper()+"_standings"})
        teams= standings_div.findAll('td', {"align" : "left"})
        for team in teams:
            url= str(team.find('a')['href'])
            rank= int(team.find('span').text[1:-1])
            if rank<9:
                confs[conf][rank-1]= [url]
        csv_file= open("standings/"+conf+"/"+str(year),'wb')
        wr= csv.writer(csv_file)
        for url in confs[conf]:
            print url
            wr.writerow(url)


if __name__=="__main__":
    start= time.time()
    #for year in range(1984,2014):
    #createTrainingSets(1984,2013,'/Users/nikhilnathwani/Desktop/','all_stats','per_game','league_ranks')
    #createTestSets('/Users/nikhilnathwani/Desktop/', 'all_stats2014', 'per_game2014', 'lg_ranks2014')
    #print getPlayoffTeams(2013)
    print "Time taken:", time.time()-start