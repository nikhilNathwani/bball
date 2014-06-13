import sys
import math
import numpy as np
import time
import matplotlib.pyplot as plot
from model import *
from dataProcess import *
from sklearn import neighbors

#weight is "uniform" or "distance", where distance weights 
#votes according to inverse euclidean distance
#data_type is all_stats, per_game, or league_ranks
def kNNEngine(k,reg,data_type,weight="distance"):
    #create classifier
    clf= neighbors.KNeighborsRegressor(k,weight) if reg else neighbors.KNeighborsClassifier(k,weight)
    #print "knnEngine",attrs["train"], targets["train"]
    clf.fit(attrs["train"], targets["train"])

    predictions= []
    #run kNN for each test point
    for index,attr in enumerate(attrs["test"]):
        #print "\n\n\n\nPredicting", urls["test"][index]
        x= clf.kneighbors(list(attr)) #returns array([distances list],[neighbor index list])
        [dists, neighs]= [x[0][0], x[1][0]]
        #print results
        '''print "         Neighbor        Wins   Similarity"
        for i in range(len(neighs)):
            if i<=8:
                print str(i+1)+". ", urls["train"][neighs[i]], targets["train"][neighs[i]], dists[i], xMostSimilarAttributes(5,index,neighs[i],data_type)
            else:
                print str(i+1)+".", urls["train"][neighs[i]], targets["train"][neighs[i]], dists[i], xMostSimilarAttributes(5,index,neighs[i],data_type)'''
        predictions.append(float(clf.predict(attr))) #save prediction to predictions dict
    return predictions

def kNN(k,data_type,weight="distance"):
    return kNNEngine(k,False,data_type,weight)

def regressionKNN(k,data_type,weight="distance"):
    return kNNEngine(k,True,data_type,weight)

#test is the test team and train is the train team
def xMostSimilarAttributes(x,test, train, data_type):
    te= attrs["test"][test]
    tr= attrs["train"][train]
    diffs= [(abs(te[i]-tr[i]),i) for i in range(len(te))]
    diffs.sort()
    return [(statDicts[data_type][ind],diff) for (diff,ind) in diffs[:x]]


def euclideanError(teams):
    trues= np.array([t.true_label for t in teams])
    predicts= np.array([t.predicted_label for t in teams])
    return np.linalg.norm(trues-predicts)

def reportPlayoffAccuracy(year):
    x= range(1,30) 
    results= []
    for k in x:
        for scale in scales:
            for dt in data_types:
                data= csvToTrainTest("team_data/"+scale+"/"+dt, year)
                [train,test]= [data["train"], data["test"]]
                for team in test:
                    weightedKNN(j, train, team)
                pt= PlayoffTree(year, test,False)
                results[dt] +=[euclideanError(test)]
                print "Scale:", scale, "Type:", dt, "Error:",str(euclideanError(test))
    plot.plot(x,results["league_ranks"],'r-', label="League Ranks")
    plot.plot(x,results["all_stats"],'b-', label="All Stats")
    plot.plot(x,results["per_game"],'g-', label="Per Game")
    #plot.axis( [0, 50, 0, 14])
    plot.xlabel( "k Value" )
    plot.ylabel( "Euclidean Error" )
    plot.show()

def compareErrors(year):
    data={'per_game':[],'all_stats':[],'league_ranks':[]}
    scale= 'rescale'
    pred= []
    kRange= range(1,50)
    d="all_stats"
    print "BASELINE"
    csvToTrainTest('team_data/'+scale+'/'+d,'team_data/winPcts',year)
    #p=regressionKNN(k,d,"distance")
    m,winList,numSeriesCorrect= baselinePlayoffs(year)
    base=[numSeriesCorrect]*len(kRange)
    for k in kRange:
        print "KNN"
        csvToTrainTest('team_data/'+scale+'/'+d,'team_data/winPcts',year)
        p=regressionKNN(k,d,"distance")
        m,winList,numSeriesCorrect= kNNPlayoffs(p,year)
        pred.append(numSeriesCorrect)
        #print winList, sum(winList)
        #data[d].append(numSeriesCorrect)
        #scales[scale].append(numSeriesCorrect)
        #print d, scale,'# series correct:', numSeriesCorrect
        #r=errorRaw(winList)    
    '''for d in data:
        x= data[d]
        print d, "Average:",float(sum(x))/len(x)
    for scale in scales:
        x= scales[scale]
        print scale, "Average",float(sum(x))/len(x)'''
    print "BASE:", base
    plot.plot(kRange,pred,'r-', label="Pred")
    plot.plot(kRange,base,'b-', label="Base")
    '''plot.plot(kRange,data["league_ranks"],'r-', label="League Ranks")
    plot.plot(kRange,data["all_stats"],'b-', label="All Stats")
    plot.plot(kRange,data["per_game"],'g-', label="Per Game")'''
    #plot.axis( [0, 50, 0, 14])
    plot.xlabel( "k Value" )
    plot.ylabel( "Num Series Correct" )
    plot.show()

if __name__=='__main__':
    start= time.time()
    compareErrors(int(sys.argv[1]))
    print "Time taken:", time.time()-start