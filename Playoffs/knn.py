import sys
import math

class Team:
    def __init__(self,u,a,l):
        self.url= u
        self.attr= a
        self.label= l
        
#ignores last entry b/c that's assumed to be the label
def dist(a,b):
    diffs= []
    for i in range(len(a)-1):
        diffs += [math.pow(a[i]-b[i],2)]
    return math.sqrt(sum(diffs))

def csvToLists(csv):
    datafile = open(csv, 'r')
    data = []
    for row in datafile:
        stats= [float(elem) for elem in row.strip().split(',')]
        print stats
        data.append(stats)
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
        label= example[-1]
        d= dist(example,testPoint)
        #if there aren't k neighbors yet, add one
        if(len(kClosest) < k):
            kClosest += [[label,d]]
            if(distBound < d):
                distBound= d
                furthestIndex= len(kClosest)-1
        #else only add if it is closer than the current furthest neighbor N,
        #and replace N with it
        else:
            if(d < distBound):
                kClosest[furthestIndex]= [label,d]
                distBound= d
                for j,neighbor in enumerate(kClosest):
                    if(neighbor[1] >= distBound):
                        distBound= neighbor[1]
                        furthestIndex= j
    return kClosest

#no weighting, just majority vote
def kNN(k,trainSet,testPoint):
    kClosest= getNearestNeighbors(k, trainSet, testPoint)
    kClosest.sort()
    mode= kClosest[0][0] #guaranteed to exist (so no array bounds issue)
    modeFreq= 0
    currMode= kClosest[0][0]
    currModeFreq= 0
    for neighbor in kClosest:
        if(neighbor[0] == currMode):
            currModeFreq += 1
            if(currModeFreq > modeFreq):
                modeFreq= currModeFreq
                mode= currMode
        else:
            currMode= neighbor[0]
            currModeFreq= 1
    return mode

#uses 1/similarity_score for weight, value of infinity if sim_score=0
def weightedKNN(k,trainSet,testPoint):
    kClosest= getNearestNeighbors(k, trainSet, testPoint)
    #majority vote, can be made more efficient
    kClosest.sort()
    mode= kClosest[0][0] #guaranteed to exist (so no array bounds issue)
    modeFreq= 0
    currMode= kClosest[0][0]
    currModeFreq= 0
    for neighbor in kClosest:
        if(neighbor[0] == currMode):
            currModeFreq += 1/neighbor[1] #when neighbor[1], currModeFreq= infinity
            if(currModeFreq > modeFreq):
                modeFreq= currModeFreq
                mode= currMode
        else:
            currMode= neighbor[0]
            currModeFreq= neighbor[1]
    return mode

if __name__=="__main__":
    print kNN(5,csvToLists("/Users/nikhilnathwani/Desktop/BBall/Playoffs/training_normalized/all_stats_normalized.csv"),csvToLists("/Users/nikhilnathwani/Desktop/BBall/Playoffs/test_normalized/all_stats2014_normalized.csv")[0])