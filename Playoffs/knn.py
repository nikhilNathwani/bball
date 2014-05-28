import sys
import math
import numpy as np

class Team:
    def __init__(self,u,a,l,s):
        self.url= u
        self.attr= a
        self.label= l
        self.sim= s

#ignores last entry b/c that's assumed to be the label
def dist(a,b):
    arr_a= np.array(a.attr)
    arr_b= np.array(b.attr)
    return np.linalg.norm(arr_a-arr_b)

#type is train or test data
def csvToLists(csv, data_type):
    datafile = open(csv, 'r')
    data = []
    for row in datafile:
        stats= [elem for elem in row.strip().split(',')]
        if data_type=="train":
            data.append(Team(stats[-2], [float(elem) for elem in stats[:-2]], float(stats[-1]), sys.maxint))
        elif data_type=="test":
            data.append(Team(stats[-1], [float(elem) for elem in stats[:-1]], "", sys.maxint))
        else:
            raise Exception("data_type must be \"train\" or \"test\"!")
    return data

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
    return sorted(teams, key=lambda team: team.sim)

##IN THIS AND WEIGHTED CASE, NEED TO DEFINE SORT FOR ARRAY OF TEAMS
#no weighting, just majority vote
def kNN(k,trainSet,testPoint):
    kClosest= getNearestNeighbors(k, trainSet, testPoint)
    kClosest= teamSort(kClosest)
    mode= kClosest[0].label #guaranteed to exist (so no array bounds issue)
    modeFreq= 0
    currMode= kClosest[0].label
    currModeFreq= 0
    for neighbor in kClosest:
        if(neighbor.label == currMode):
            currModeFreq += 1
            if(currModeFreq > modeFreq):
                modeFreq= currModeFreq
                mode= currMode
        else:
            currMode= neighbor.label
            currModeFreq= 1
    return mode

#uses 1/similarity_score for weight, value of infinity if sim_score=0
def weightedKNN(k,trainSet,testPoint):
    kClosest= getNearestNeighbors(k, trainSet, testPoint)
    #majority vote, can be made more efficient
    kClosest= teamSort(kClosest)
    weighted_total= 0 #guaranteed to exist (so no array bounds issue)
    sum_of_weights= 0
    for neighbor in kClosest:
        weight= (1/neighbor.sim if neighbor.sim!=0 else sys.maxint/20)
        print neighbor.url, neighbor.label, neighbor.sim
        sum_of_weights += weight
        weighted_total += weight * neighbor.label
    return weighted_total/sum_of_weights

if __name__=="__main__":
    k= 10
    train= csvToLists("/Users/nikhilnathwani/Desktop/BBall/Playoffs/training/raw/all_stats", "train")
    test= csvToLists("/Users/nikhilnathwani/Desktop/BBall/Playoffs/test/raw/all_stats2014", "test")
    for team in test:
        print "\n-------------------------"
        print k, "Closest neighbors of:", team.url
        print weightedKNN(k, train, team)
        print "-------------------------\n"