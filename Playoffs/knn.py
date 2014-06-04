import sys
import math
import numpy as np
#import playoffs

class Team:
    def __init__(self,u,a,l,s):
        self.url= u
        self.attr= a
        self.true_label= l
        self.predicted_label= 0
        self.sim= s
        self.score= 0

class PlayoffTree:
    def __init__(self):
        self.standings= {"east":[], "west":[]}
        self.linear= []

def getWinningTeam(team1, team2):
    return team1 if team1.score>team2.score else team2

def simPlayoffs(pt):
    confs= {"east":0, "west":0} #value is winner of the conference
    for conf in confs:
        curr_round= [team for team in pt.standings[conf]]
        next_round= []
        while len(curr_round)+len(next_round)>1: 
            pt.linear += [(curr_round[0], curr_round[-1])]
            winner= getWinningTeam(curr_round[0], curr_round[-1])
            winner.predicted_label += 1
            next_round += [winner]
            curr_round= curr_round[1:-1]
            if len(curr_round)==0:
                curr_round= next_round
                next_round= []
        confs[conf]= curr_round[0] #last team in curr_round is conference winner
    pt.linear += [(confs["east"], confs["west"])]
    winner= getWinningTeam(confs["east"], confs["west"])
    winner.predicted_label += 1
    for conf in confs:
        for team in pt.standings[conf]:
            print team.url, "True:", team.true_label, "Predicted:", team.predicted_label
    rearrage= [0,3,1,2,7,10,8,9,4,5,11,12,6,13,14]
    pt.linear= [pt.linear[x] for x in rearrage]

#returns dict with "train" and "test" lists of data
def csvToTrainTest(csv, year):
    datafile = open(csv, 'r')
    train = []
    test= []
    for row in datafile:
        stats= [elem for elem in row.strip().split(',')]
        url= stats[-2]
        team= Team(url, [float(elem) for elem in stats[:-2]], float(stats[-1]), sys.maxint)
        team_yr= int(url[url.rfind('/')+1:url.rfind(".html")])
        if team_yr==year:
            test.append(team)
        if team_yr<year:
            train.append(team)
    return {"train":train, "test":test}

def dist(a,b):
    arr_a= np.array(a.attr)
    arr_b= np.array(b.attr)
    return np.linalg.norm(arr_a-arr_b)

#returns an array of the form:
#[[neighbor_1_label, similarity score], ..., [neighbor_k_label, similarity score]]
def getNearestNeighbors(k, trainSet, testPoint):
    if len(trainSet)==0 :
        raise Exception("Training set is empty!")
    kClosest= []
    distBound= -sys.maxint-1
    furthestIndex= 0
    for example in trainSet:
        example.sim= dist(example,testPoint)
        #if there aren't k neighbors yet, add one
        if(len(kClosest) < k):
            kClosest += [example]
            #print example.url, example.label, example.sim
            if(distBound < example.sim):
                distBound= example.sim
                furthestIndex= len(kClosest)-1
        #else only add if it is closer than the current furthest neighbor N,
        #and replace N with it
        else:
            if(example.sim < distBound):
                kClosest[furthestIndex]= example
                distBound= example.sim
                for j,neighbor in enumerate(kClosest):
                    if(neighbor.sim >= distBound):
                        distBound= neighbor.sim
                        furthestIndex= j
    return kClosest

def teamSort(teams):
    return sorted(teams, key=lambda team: team.true_label)

#no weighting, just majority vote
def kNN(k,trainSet,testPoint):
    kClosest= getNearestNeighbors(k, trainSet, testPoint)
    kClosest= teamSort(kClosest)
    mode= kClosest[0].true_label #guaranteed to exist (so no array bounds issue)
    modeFreq= 0
    currMode= kClosest[0].true_label
    currModeFreq= 0
    for neighbor in kClosest:
        print neighbor.url, neighbor.true_label, neighbor.sim
        if(neighbor.true_label == currMode):
            currModeFreq += 1
            if(currModeFreq > modeFreq):
                modeFreq= currModeFreq
                mode= currMode
        else:
            currMode= neighbor.true_label
            currModeFreq= 1
    testPoint.predicted_label= mode
    return mode

#uses 1/similarity_score for weight, value of infinity if sim_score=0
def weightedKNN(k,trainSet,testPoint):
    kClosest= getNearestNeighbors(k, trainSet, testPoint)
    #sorting for printing purposes
    kClosest= sorted(kClosest, key=lambda team: team.sim) 
    #majority vote, can be made more efficient
    weighted_total= 0 #guaranteed to exist (so no array bounds issue)
    sum_of_weights= 0
    for neighbor in kClosest:
        weight= (1/neighbor.sim if neighbor.sim!=0 else sys.maxint/20)
        print neighbor.url, neighbor.true_label, neighbor.sim
        sum_of_weights += weight
        weighted_total += weight * neighbor.true_label
    testPoint.score= weighted_total/sum_of_weights
    return weighted_total/sum_of_weights

def setPlayoffTree(year, teams):
    confs= ["east","west"]
    team_urls= {}
    pt= PlayoffTree()
    for team in teams:
        team_urls[team.url]= team
    for conf in confs:
        standings_file = open("standings/"+conf+"/"+str(year), 'r')
        teams= []
        for row in standings_file:
            teams += [str(row).strip()]
        pt.standings[conf]= [team_urls[t] for t in teams]
    return pt

if __name__=="__main__":
    if len(sys.argv)<=2:
        raise Exception("Must provide k value and test year!")
    k= int(sys.argv[1])
    year= int(sys.argv[2])
    data= csvToTrainTest("/Users/nikhilnathwani/Desktop/BBall/Playoffs/team_data/rescale/all_stats_rescale", year)
    [train,test]= [data["train"], data["test"]]
    print len(test), len(train)
    for team in test:
        print "\n-------------------------"
        print k, "Closest neighbors of:", team.url
        print weightedKNN(k, train, team)
        print "-------------------------\n"
    pt= setPlayoffTree(year, test)
    simPlayoffs(pt)
