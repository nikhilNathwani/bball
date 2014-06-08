import string
import time
import csv
import sys
import numpy as np

def csvToLists(fn):
	rows= []
	with open(fn) as f:
		for line in f:
			arr= [line.split(',')]
			rows += arr 
	return rows 

def listsToCSV(lists,fn):
	csv_file= open(fn,'wb')
	csv_wr = csv.writer(csv_file)
	for row in lists:
		csv_wr.writerow(row)

def transpose(lst):
	return [list(attr) for attr in zip(*lst)]

#standardizes each attribute by "RESCALING": subtracting min and dividing by (max-min)
#-old_data_fn is the name of the CSV to be normalized
#-new_data_fn is the name of the CSV into which ,the normalized data should be placed. 
#   If equal to old_data_fn, then old_data_fn is overwritten
#-file_base is all_stats, per_game, or league_ranks
def standardizeRescale(scale,name):
	old_data_fn= 'team_data/raw/'+name
	new_data_fn= 'team_data/'+scale+'/'+name
	scale_fn= 'scales/'scale'/'+name+'_scales'
	mins, diffs= [[],[]]

	#get team data from file	
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-2): #The url and the label columns are skipped over.
		#prepare to save min and diff data to file
		data=[float(x) for x in cols[i]]
		mins += [float(min(data))]
		diffs += [float(max(data))-mins[i]]
		cols[i]= [(float(elem)-mins[i])/diffs[i] for elem in cols[i]]
	cols[-1]= [float(x) for x in cols[-1]] #convert label column entries to floats
	
	#save normalized data to new file
	listsToCSV(transpose(cols),new_data_fn)
	
	#save scaling info (mins and diffs) to file 
	listsToCSV([mins,diffs],scale_fn)


def standardizeNorm(scale,name):
	old_data_fn= 'team_data/raw/'+name
	new_data_fn= 'team_data/'+scale+'/'+name
	scale_fn= 'scales/'scale'/'+name+'_scales'
	norms=[]

	#get train/test data from file	
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-2):
		#prepare to save min and diff data to file
		data= [float(elem) for elem in cols[i]]
		norms += [np.linalg.norm(data)]
		cols[i]= [float(elem)/norms[i] for elem in cols[i]]
	cols[-1]= [float(x) for x in cols[-1]] #convert label column entries to floats
	
	#save normalized data to new file
	listsToCSV(transpose(cols),new_data_fn)
	
	#save scaling info (mins and diffs) to file 
	listsToCSV([norms],'scales/norm/'+file_base+'_scales')


if __name__=="__main__":
	start=time.time()
	for scale= ["rescale", "norm"]
		for name in ['all_stats', 'per_game', 'league_ranks']:
			if scale=="rescale":
				standardizeRescale(scale,name)
			else:
				standardizeNorm(scale,name)
	print "Time taken:", time.time()-start