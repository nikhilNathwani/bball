import re
import string
import math
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

attrs= {"train":[],"test":[],"other":[]}
targets= {"train":[],"test":[],"other":[]}
urls= {"train":[],"test":[],"other":[]}
indexDict= {} #keys are testPoint urls, values are indices

def yearFromURL(url):
    url= url
    return int(url[url.rfind('/')+1:url.rfind(".html")])

def teamName(url):
    return url[:url.rfind('/')][url[:url.rfind('/')].rfind('/')+1:]

def getWinPercentages():
    winPcts= [-1]*16
    for url,index in indexDict.iteritems():
        soup= grabSiteData("http://www.basketball-reference.com"+url)
        recordPar= [p for p in soup.findAll('p') if "Record:" in p.text]
        recordString= recordPar[0].text.encode("utf8","ignore")
        record= recordString[recordString.find(" ")+1:recordString.find(",")]
        wins,losses= [float(s) for s in record.split("-")]
        winPcts[index]= wins/(wins+losses)
    return winPcts

#scoreList provides the means for comparison. Can be targets, winPcts, etc.
#teamA and teamB are indices
def getWinningTeam(teamA, teamB, scoreList):
    return teamA if scoreList[teamA]>scoreList[teamB] else teamB

def baselinePlayoffs(year):
    return playoffEngine(getWinPercentages,year)

def kNNPlayoffs(knnScores,year):
    return playoffEngine(knnScores,year)

#scoreList used in getWinningTeam function
def playoffEngine(scoreList,year):
    confs= {"east":0, "west":0} #value is winner of the conference
    standings= {"east":[], "west":[]}
    wins= [0]*16
    num_series_correct= 0
    #set standings based on team.urls in standings file
    for conf in confs:
        standings_file = open("standings/"+conf+"/"+str(year), 'r')
        teams= []
        for row in standings_file:
            teams += [str(row).strip()]
        standings[conf]= teams

    #set matchups list (list of pairs corresp to predicted playoff matchups)
    matchups= []
    for conf in confs:
        curr= [indexDict[team] for team in standings[conf]] #current round
        next= [] #next round
        while len(curr)+len(next)>1: 
            #best and worst teams face off, winner moves on
            matchups += [(curr[0], curr[-1])]
            winner= getWinningTeam(curr[0], curr[-1], scoreList)
            wins[winner] += 1
            next += [getWinningTeam(curr[0],curr[-1],targets["test"])]
            if winner==next[-1]: 
                num_series_correct+=1
            #remove best and worst teams from current round
            curr= curr[1:-1]
            #if all teams have been removed from currend round, then next round begins
            if len(curr)==0:
                curr= next
                next= []
        confs[conf]= curr[0] #last team in curr is conference winner
    #add finals matchup to games list
    matchups += [(confs["east"], confs["west"])]
    champ= getWinningTeam(confs["east"], confs["west"], scoreList)
    wins[champ] += 1
    return (matchups,wins,num_series_correct)      

def errorRaw(predictedWins):
    p= np.array(predictedWins)
    true= np.array(targets["test"]) 
    diffs= [abs(true[i]-p[i]) for i in range(len(p))]
    return sum(diffs)

def errorEuclidean(predictedWins):
    p= np.array(predictedWins)
    true= np.array(targets["test"])
    return np.linalg.norm(true-p)