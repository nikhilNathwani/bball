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
def kNNEngine(k,reg,weight="distance"):
    #create classifier
    clf= neighbors.KNeighborsRegressor(k,weight) if reg else neighbors.KNeighborsClassifier(k,weight)
    #print "knnEngine",attrs["train"], targets["train"]
    clf.fit(attrs["train"], targets["train"])

    predictions= []
    #run kNN for each test point
    for index,attr in enumerate(attrs["test"]):
        '''print "\nPredicting", urls["test"][index]'''
        x= clf.kneighbors(list(attr)) #returns array([distances list],[neighbor index list])
        [dists, neighs]= [x[0][0], x[1][0]]
        #print results
        '''print "         Neighbor        Wins   Similarity"
        for i in range(len(neighs)):
            if i<=8:
                print str(i+1)+". ", urls["train"][neighs[i]], targets["train"][neighs[i]], dists[i]
            else:
                print str(i+1)+".", urls["train"][neighs[i]], targets["train"][neighs[i]], dists[i]'''
        predictions.append(float(clf.predict(attr))) #save prediction to predictions dict
        '''print "Predicted series wins:", predictions[-1],"\n"'''
    return predictions

def kNN(k,weight="distance"):
    return kNNEngine(k,False,weight)

def regressionKNN(k,weight="distance"):
    return kNNEngine(k,True,weight)

def numSeriesCorrect(teams):
    correct= 0
    for team in teams:
        correct += min(team.true_label,team.predicted_label)    
    return correct

def euclideanError(teams):
    trues= np.array([t.true_label for t in teams])
    predicts= np.array([t.predicted_label for t in teams])
    return np.linalg.norm(trues-predicts)

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

def compareErrors(k,year):
    data={'per_game':[],'all_stats':[],'league_ranks':[]}
    scales= {'raw':[],'norm':[],'rescale':[]}
    for d in data:
        for scale in scales: 
            csvToTrainTest('team_data/'+scale+'/'+d,year)
            p=regressionKNN(k,"distance")
            w= kNNPlayoffs(p,year)
            print w, sum(w)
            e= errorEuclidean(w)
            data[d].append(e)
            scales[scale].append(e)
            print d, scale,'Error:', e
            #r=errorRaw(w)    
    for d in data:
        x= data[d]
        print d, "Average:",float(sum(x))/len(x)
    for scale in scales:
        x= scales[scale]
        print scale, "Average",float(sum(x))/len(x)

if __name__=='__main__':
    start= time.time()
    compareErrors(int(sys.argv[1]),int(sys.argv[2]))
    print "Time taken:", time.time()-start