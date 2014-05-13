import re
import string
import time
import csv
import urllib2
from bs4 import BeautifulSoup

statsToIgnore= ["player","g", "mp", "arena_name", "attendance"]
statsToNotScale= ["fg_pct", "fg3_pct", "fg2_pct", "ft_pct", "pts_per_g"]
currTeams= ['/teams/BRK/2014.html', '/teams/IND/2014.html', '/teams/MIA/2014.html', '/teams/WAS/2014.html',
            '/teams/SAS/2014.html', '/teams/LAC/2014.html', '/teams/OKC/2014.html', '/teams/POR/2014.html']

def grabSiteData(url):
    usock= urllib2.urlopen(url)
    data= usock.read()
    usock.close()
    return BeautifulSoup(data)

#returns array of (playoff_team_url,year,num_wins_in_playoffs)
def getPlayoffTeams(year):
    teams_wins= {}
    query_soup= grabSiteData("http://www.basketball-reference.com/playoffs/NBA_"+str(year)+".html")
    playoff_data= query_soup.find('div', {"id" : "all_playoffs"}).findAll('tr', {"class" : "mobile_text"})
    for row in playoff_data:
        tds= row.findAll("td")
        p_round= tds[0].text.encode("ascii","ignore")
        if "First" not in p_round:
            record_index= p_round.find('(')
            wins= [int(p_round[record_index+1]), int(p_round[record_index+3])]
            matchup= [elem["href"].encode("ascii","ignore") for elem in tds[1].findAll("a")][:-1]
            for i,team in enumerate(matchup):
                teams_wins[team]= teams_wins.get(team, 0) + wins[i]
    teams_wins= [(k,year,teams_wins[k]) for k in teams_wins.keys()]
    return teams_wins


#returns (all_stats, only_raw_values, only_league_ranks) tuple of arrays
def scrapeTeamStats(team_url, year):
    all_stats= []
    only_raw_values= []
    only_league_ranks= []
    query_soup= grabSiteData("http://www.basketball-reference.com"+team_url)

    #get list of indices containing stats I care about
    team_and_opp_div= query_soup.find('div', {"class" : "table_container", "id" : "div_team_stats"})
    team_and_opp_header= team_and_opp_div.find("thead")
    indices= []
    not_scale_indices= []
    for i,elem in enumerate(team_and_opp_header.findAll('th')): 
        if elem['data-stat'] not in statsToIgnore:
            indices += [i]
        if elem['data-stat'] in statsToNotScale:
            not_scale_indices += [i]

    #get stats located in desired indices
    team_and_opp_stats= team_and_opp_div.find("tbody").findAll("tr")
    for row in team_and_opp_stats:
        arraysToAddTo= [all_stats]
        stats= row.findAll('td')
        isLgRank= False
        if stats[0].text.encode("ascii","ignore")=="Lg Rank":
            arraysToAddTo += [only_league_ranks]
            isLgRank= True
        else: 
            arraysToAddTo += [only_raw_values]
        for j in indices:
            for arr in arraysToAddTo:
                value= float(stats[j].text.encode("ascii","ignore"))
                scale= 1
                if j not in not_scale_indices: #meaning j needs scaling
                    if year==1999 and isLgRank==False: scale= float(82)/float(50)
                    if year==2012 and isLgRank==False: scale= float(82)/float(50)
                arr += [value * scale]


    #repeat above for team_misc stats
    team_misc_div= query_soup.find('div', {"class" : "table_container", "id" : "div_team_misc"})
    team_misc_header= team_misc_div.find("thead").findAll('tr')[-1] #first tr is an "over-header" to be ignored
    indices= []
    not_scale_indices= []
    for i,elem in enumerate(team_misc_header.findAll('th')): 
        if elem['data-stat'] not in statsToIgnore:
            indices += [i]
        if elem['data-stat'] in statsToNotScale:
            not_scale_indices += [i]

    team_misc_stats= team_misc_div.find("tbody").findAll("tr")
    for row in team_misc_stats:
        arraysToAddTo= [all_stats]
        stats= row.findAll('td')
        isLgRank= False
        if stats[0].text.encode("ascii","ignore")=="Lg Rank":
            arraysToAddTo += [only_league_ranks]
            isLgRank= True
        else: 
            arraysToAddTo += [only_raw_values]
        for j in indices:
            for arr in arraysToAddTo:
                value= float(stats[j].text.encode("ascii","ignore"))
                scale= 1
                if j not in not_scale_indices: #meaning j needs scaling
                    if year==1999 and isLgRank==False: scale= float(82)/float(50)
                    if year==2012 and isLgRank==False: scale= float(82)/float(66)
                arr += [value * scale]
    return (all_stats, only_raw_values, only_league_ranks) 

#statType= 0 for all_states, 1 for only_raw_values, 2 for only_league_ranks
def createTrainingSets(yearStart, yearEnd, folder, fn_all_stats, fn_raw_stats, fn_lg_ranks):
    #create CSVs and csv_writers
    asCSV= open(folder+fn_all_stats,'wb')
    rsCSV= open(folder+fn_raw_stats,'wb')
    lrCSV= open(folder+fn_lg_ranks,'wb')
    as_wr = csv.writer(asCSV)
    rs_wr = csv.writer(rsCSV)
    lr_wr = csv.writer(lrCSV)

    #populate CSVs
    for i in range(yearStart, yearEnd+1): 
        playoff_teams= getPlayoffTeams(i)
        for team in playoff_teams:
            url= team[0]
            year= team[1]
            wins= team[2]
            data_to_append= [year, wins]
            arrs= (all_stats,raw_stats,lg_ranks)= scrapeTeamStats(url,year)
            for arr in arrs:
                arr += data_to_append 
            as_wr.writerow(all_stats)
            rs_wr.writerow(raw_stats)
            lr_wr.writerow(lg_ranks)
        print "Done with year", i


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
    #createTrainingSets(2012,2012,'/Users/nikhilnathwani/Desktop/','all_stats2012','raw_stats2012','league_ranks2012')
    createTestSets(2014, '/Users/nikhilnathwani/Desktop/BBall/Playoffs/test/', 'all_stats2014', 'raw_stats2014', 'lg_ranks2014')
    print "Time taken:", time.time()-start