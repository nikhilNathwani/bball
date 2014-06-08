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

    def dist(a,b):
        arr_a= np.array(a.attr)
        arr_b= np.array(b.attr)
        return np.linalg.norm(arr_a-arr_b)

class PlayoffTree:
    def __init__(self):
        self.standings= {"east":[], "west":[]}
        self.games= [] #list of tuples of all playoff matchups, used in gui.py
        self.actuals= [] #actual game matchups
        self.trueWinner= ""

    #year is from 1984-2014
    #teams is list of 16 playoff Team objects
    #baseline is boolean: True if baseline metric is to be used, False otherwise
    #(baseline metric is team winning percentage, otherwise knn score is used)
    def __init__(self, year, teams, baseline):
        self.games= []
        self.actuals= []
        confs= ["east","west"]
        team_urls= {}

        #set trueWinner var and hash teams based on team.url
        for team in teams:
            team_urls[team.url]= team
            if team.true_label==4:
                self.trueWinner= team.url

        #set standings based on team.urls in standings file
        for conf in confs:
            standings_file = open("standings/"+conf+"/"+str(year), 'r')
            teams= []
            for row in standings_file:
                teams += [str(row).strip()]
            self.standings[conf]= [team_urls[t] for t in teams]

        #set games and actuals lists
        self.simPlayoffs(baseline)

    def simPlayoffs(self,baseline):
        confs= {"east":0, "west":0} #value is winner of the conference
        actual_confs= {"east":0, "west":0} #value is winner of the conference

        for conf in confs:
            curr_round= [team for team in self.standings[conf]]
            actual_curr= [x for x in curr_round]
            next_round= []
            actual_next= []
            while len(curr_round)+len(next_round)>1: 
                self.games += [(curr_round[0], curr_round[-1])]
                self.actuals += [(actual_curr[0], actual_curr[-1])]
                winner= predictWinningTeam(curr_round[0], curr_round[-1],baseline)
                winner.predicted_label += 1

                next_round += [winner]
                actual_next += [actualWinningTeam(actual_curr[0], actual_curr[-1])]

                curr_round= curr_round[1:-1]
                actual_curr= actual_curr[1:-1]
                if len(curr_round)==0:
                    curr_round= next_round
                    actual_curr= actual_next

                    next_round= []
                    actual_next= []

            confs[conf]= curr_round[0] #last team in curr_round is conference winner
            actual_confs[conf]= actual_curr[0]

        self.games += [(confs["east"], confs["west"])]
        self.actuals += [(actual_confs["east"], actual_confs["west"])]

        winner= predictWinningTeam(confs["east"], confs["west"],True)
        winner.predicted_label += 1
        for conf in confs:
            for team in self.standings[conf]:
                print team.url, "True:", team.true_label, "Predicted:", team.predicted_label


if __name__=="__main__":
    start= time.time()
    #for year in range(1984,2014):
    #createTrainingSets(1984,2013,'/Users/nikhilnathwani/Desktop/','all_stats','per_game','league_ranks')
    #createTestSets('/Users/nikhilnathwani/Desktop/', 'all_stats2014', 'per_game2014', 'lg_ranks2014')
    #print getPlayoffTeams(2013)
    print "Time taken:", time.time()-start