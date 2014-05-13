import string
import time
import csv

all_stats_trainDataScales=[]
raw_stats_trainDataScales=[]
league_ranks_trainDataScales=[]

#normalize entries of arr so that they sum to X
def normalize(arr, X):
	return [(float(elem)*X)/float(sum(arr)) for elem in arr]

def scale(arr, c):
	return [float(elem)*float(c) for elem in arr]

def normalizeGivenScales(arr,scaleArray):
	return [scale(elem,scaleArray[i]) for i,elem in enumerate(arr)]

#normalize columns of CSV so that they sum to X
#-old_data_fn is the name of the CSV to be normalized
#-new_data_fn is the name of the CSV into which the normalized data should be placed. 
#   If equal to old_data_fn, then old_data_fn is overwritted
#-columnExceps is a list of column indices that shouldn't be normalized
#-scaleArray is either all_stats_trainDataScales, raw_stats_trainDataScales, 
#   or league_ranks_trainDataScales depending on which CSV we're dealing with
def normalizeColumnsToX(old_data_fn,new_data_fn,X,columnExceps, scaleArray):
	global all_stats_trainDataScales
	global raw_stats_trainDataScales
	global league_ranks_trainDataScales

	#parse data into 2D arrays and transpose
	rows= []
	with open(old_data_fn) as f:
		for line in f:
			arr= [[float(elem) for elem in line.split(',')]]
			rows += arr
	columnExceps= [excep if excep>=0 else excep+len(rows[0]) for excep in columnExceps]
	cols= [list(attr) for attr in zip(*rows)]
	
	#populate correct scale array
	if scaleArray is all_stats_trainDataScales:
		all_stats_trainDataScales= [float(X)/float(sum(col)) for col in cols]
	elif scaleArray is raw_stats_trainDataScales:
		raw_stats_trainDataScales= [float(X)/float(sum(col)) for col in cols]
	else:
		league_ranks_trainDataScales= [float(X)/float(sum(col)) for col in cols]
	
	#normalize columns, transpose back, and write to new CSV
	cols= [col if j in columnExceps else normalize(col,X) for j,col in enumerate(cols)]
	rows= [list(attr) for attr in zip(*cols)]
	normCSV= open(new_data_fn,'wb')
	norm_wr = csv.writer(normCSV)
	for row in rows:
		norm_wr.writerow(row)

def normalizeTestPoints(old_data_fn,new_data_fn,scaleArray):
	rows= []
	with open(old_data_fn) as f:
		for line in f:
			arr= [[float(elem) for elem in line.split(',')]]
			rows += arr
	cols= [list(attr) for attr in zip(*rows)]
	print scaleArray
	cols= normalizeGivenScales(cols, scaleArray)
	rows= [list(attr) for attr in zip(*cols)]
	normCSV= open(new_data_fn,'wb')
	norm_wr = csv.writer(normCSV)
	for row in rows:
		norm_wr.writerow(row)

if __name__=="__main__":
	#transforming training data
	oldFolder= "/Users/nikhilnathwani/Desktop/BBall/Playoffs/training/"
	normFolder= "/Users/nikhilnathwani/Desktop/BBall/Playoffs/training_normalized/"
	old_fns= {"all_stats":all_stats_trainDataScales, 
			  "raw_stats":raw_stats_trainDataScales, 
			  "league_ranks":league_ranks_trainDataScales}
	for fn in old_fns.keys():
		normalizeColumnsToX(oldFolder+fn,normFolder+fn+"_normalized",100,[-1], old_fns[fn])

	#transforming test data
	oldFolder= "/Users/nikhilnathwani/Desktop/BBall/Playoffs/test/"
	normFolder= "/Users/nikhilnathwani/Desktop/BBall/Playoffs/test_normalized/"
	old_fns= {"all_stats2014":all_stats_trainDataScales, 
		      "raw_stats2014":raw_stats_trainDataScales, 
		      "league_ranks2014":league_ranks_trainDataScales}
	for fn in old_fns:
		normalizeTestPoints(oldFolder+fn,normFolder+fn+"_normalized", old_fns[fn])