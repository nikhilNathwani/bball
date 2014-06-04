import sys
import math
import numpy as np
import time
import matplotlib.pyplot as plot
import playoffs

class Team:
    def __init__(self,u,a,l,s):
        self.url= u
        self.attr= a
        self.true_label= l
        self.predicted_label= 0
        self.sim= s
        self.score= 0
        self.winPct= -1

class PlayoffTree:
    def __init__(self):
        self.standings= {"east":[], "west":[]}
        self.games= [] #list of tuples of all playoff matchups, used in gui.py
        self.actuals= [] #actual game matchups
        self.trueWinner= ""

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
        #print neighbor.url, neighbor.true_label, neighbor.sim
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
        if team.true_label==4:
            pt.trueWinner= team.url
    for conf in confs:
        standings_file = open("standings/"+conf+"/"+str(year), 'r')
        teams= []
        for row in standings_file:
            teams += [str(row).strip()]
        pt.standings[conf]= [team_urls[t] for t in teams]
    #print "TRUE WINNER:", pt.trueWinner
    return pt

def predictWinningTeam(team1, team2, baseline):
    if baseline:
        return team1 if getWinPercentage(team1)>getWinPercentage(team2) else team2
    else:
        return team1 if team1.score>team2.score else team2

def getWinPercentage(team):
    if team.winPct>-1:
        return team.winPct
    else:
        soup= playoffs.grabSiteData("http://www.basketball-reference.com"+team.url)
        recordPar= [p for p in soup.findAll('p') if "Record:" in p.text]
        recordString= recordPar[0].text.encode("utf8","ignore")
        record= recordString[recordString.find(" ")+1:recordString.find(",")]
        wins,losses= [float(s) for s in record.split("-")]
        team.winPct= wins/(wins+losses)
        return team.winPct


def actualWinningTeam(team1, team2):
    return team1 if team1.true_label>team2.true_label else team2

def simPlayoffs(pt,baseline):
    confs= {"east":0, "west":0} #value is winner of the conference
    actual_confs= {"east":0, "west":0} #value is winner of the conference

    for conf in confs:
        curr_round= [team for team in pt.standings[conf]]
        actual_curr= [x for x in curr_round]
        next_round= []
        actual_next= []
        while len(curr_round)+len(next_round)>1: 
            pt.games += [(curr_round[0], curr_round[-1])]
            pt.actuals += [(actual_curr[0], actual_curr[-1])]
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

    pt.games += [(confs["east"], confs["west"])]
    pt.actuals += [(actual_confs["east"], actual_confs["west"])]

    winner= predictWinningTeam(confs["east"], confs["west"],True)
    winner.predicted_label += 1
    for conf in confs:
        for team in pt.standings[conf]:
            print team.url, "True:", team.true_label, "Predicted:", team.predicted_label
    rearrage= [0,3,1,2,7,10,8,9,4,5,11,12,6,13,14]
    pt.games= [pt.games[x] for x in rearrage]
    pt.actuals= [pt.actuals[x] for x in rearrage]

def numSeriesCorrect(teams):
    correct= 0
    for team in teams:
        correct += min(team.true_label,team.predicted_label)    
    return correct

def euclideanError(teams):
    trues= np.array([t.true_label for t in teams])
    predicts= np.array([t.predicted_label for t in teams])
    return np.linalg.norm(trues-predicts)

def reportKNNResults(k, year):
    data= csvToTrainTest("/Users/nikhilnathwani/Desktop/BBall/Playoffs/team_data/rescale/all_stats_rescale", year)
    [train,test]= [data["train"], data["test"]]
    for team in test:
        print "\n-------------------------"
        print k, "Closest neighbors of:", team.url
        print weightedKNN(k, train, team)
        print "-------------------------\n"

def reportPlayoffAccuracy(k, year): 
    scales= ["norm"]#, "norm", "raw"]
    data_types= ["league_ranks","all_stats","per_game"]
    results= {"league_ranks":[], "all_stats":[], "per_game":[]}
    x= range(15,16)
    for j in range(15, 16):
        for scale in scales:
            for dt in data_types:
                data= csvToTrainTest("team_data/"+scale+"/"+dt, year)
                [train,test]= [data["train"], data["test"]]
                for team in test:
                    weightedKNN(j, train, team)
                pt= setPlayoffTree(year, test)
                simPlayoffs(pt,False)
                results[dt] +=[euclideanError(test)]
                print "Scale:", scale, "Type:", dt, "Error:",str(euclideanError(test))
    plot.plot(x,results["league_ranks"],'r-', label="League Ranks")
    plot.plot(x,results["all_stats"],'b-', label="All Stats")
    plot.plot(x,results["per_game"],'g-', label="Per Game")
    #plot.axis( [0, 50, 0, 14])
    plot.xlabel( "k Value" )
    plot.ylabel( "Euclidean Error" )
    plot.show()


if __name__=="__main__":
    start= time.time()
    if len(sys.argv)<=2:
        raise Exception("Must provide k value and test year!")
    k= int(sys.argv[1])
    year= int(sys.argv[2])
    reportPlayoffAccuracy(k, year)
    #getWinPercentage("/teams/BOS/1984.html")
    print "Time taken:", time.time()-start
