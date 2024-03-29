import re
import string
import time
import csv
import urllib2
import sys
from bs4 import BeautifulSoup
import numpy as np

#fetches beautifulsoup-formatted data from given url
def grabSiteData(url):
    usock= urllib2.urlopen(url)
    data= usock.read()
    usock.close()
    return BeautifulSoup(data)

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
        self.year= self.yearFromURL()

    def yearFromURL(self):
        url= self.url
        return int(url[url.rfind('/')+1:url.rfind(".html")])

    def teamName(self):
        s= self.url
        return s[:s.rfind('/')][s[:s.rfind('/')].rfind('/')+1:]

    def dist(self,other):
        arr_self= np.array(self.attr)
        arr_other= np.array(other.attr)
        return np.linalg.norm(arr_self-arr_other)

    def getWinPercentage(self):
        if self.winPct>-1:
            return self.winPct
        else:
            soup= grabSiteData("http://www.basketball-reference.com"+self.url)
            recordPar= [p for p in soup.findAll('p') if "Record:" in p.text]
            recordString= recordPar[0].text.encode("utf8","ignore")
            record= recordString[recordString.find(" ")+1:recordString.find(",")]
            wins,losses= [float(s) for s in record.split("-")]
            self.winPct= wins/(wins+losses)
            return self.winPct

    #baseline is True if baseline metric is to be used, False otherwise
    def predictWinningTeam(self, other, baseline):
        if baseline:
            return self if self.getWinPercentage()>other.getWinPercentage() else other
        else:
            return self if self.score>other.score else other

    def actualWinningTeam(self, other):
        return self if self.true_label>other.true_label else other

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
        self.trueWinner= ""
        self.standings= {}

        team_urls= {}
        confs= ["east","west"]
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
        self.simPlayoffs()
        self.predictPlayoffs(baseline)

    def simPlayoffs(self):
        confs= {"east":0, "west":0} #value is winner of the conference
        #set actuals list (list of pairs corresp to actual playoff matchups)
        #methodology is similar to the way games list is created in predictPlayoffs
        for conf in confs:
            actual_curr= [team for team in self.standings[conf]]
            actual_next= []
            while len(actual_curr)+len(actual_next)>1: 
                self.actuals += [(actual_curr[0], actual_curr[-1])]
                actual_next += [actual_curr[0].actualWinningTeam(actual_curr[-1])]
                actual_curr= actual_curr[1:-1]
                if len(actual_curr)==0:
                    actual_curr= actual_next
                    actual_next= []
            confs[conf]= actual_curr[0] #last team in actual_curr is conference winner
        self.actuals += [(confs["east"], confs["west"])]

        #print playoff results, both actual and predicted
        for conf in confs:
            for team in self.standings[conf]:
                print team.url, "True:", team.true_label, "Predicted:", team.predicted_label

    def predictPlayoffs(self,baseline):
        confs= {"east":0, "west":0} #value is winner of the conference
        #set games list (list of pairs corresp to predicted playoff matchups)
        for conf in confs:
            curr_round= [team for team in self.standings[conf]]
            next_round= []
            while len(curr_round)+len(next_round)>1: 
                #best and worst teams face off
                self.games += [(curr_round[0], curr_round[-1])]
                winner= curr_round[0].predictWinningTeam(curr_round[-1],baseline)
                winner.predicted_label += 1
                #winner moves on to next round
                next_round += [winner] 
                #remove best and worst teams from current round
                curr_round= curr_round[1:-1]
                #if all teams have been removed from currend round, 
                #then next round commences
                if len(curr_round)==0:
                    curr_round= next_round
                    next_round= []
            #last team in curr_round is conference winner
            confs[conf]= curr_round[0] 
        #add finals matchup to games list
        self.games += [(confs["east"], confs["west"])]
        #simulate final round
        winner= confs["east"].predictWinningTeam(confs["west"],True)
        winner.predicted_label += 1        