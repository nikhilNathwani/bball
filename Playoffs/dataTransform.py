import string
import time
import csv
import sys
import numpy as np

#for training data, last 2 entries shouldn't be normalized
#for test data, last 1 entry shouldn't be normalized 
#offset allows me to sneakily reuse all my code for train and test 
#offset=1

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
def standardizeRescale(old_data_fn, new_data_fn, file_base):
	mins= []
	diffs= []
	scale_fn= 'scales/rescale/'+file_base+'_scales'
	if not (offset-1):
		[mins,diffs]= csvToLists(scale_fn)
		mins= [float(x) for x in mins]
		diffs= [float(x) for x in diffs]
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-offset): #The last 2 columns, the url and the label, are skipped over.
		if offset:
			data=[float(x) for x in cols[i]]
			mins += [float(min(data))]
			diffs += [float(max(data))-float(min(data))]
		cols[i]= [(float(elem)-mins[i])/diffs[i] for elem in cols[i]]
	cols[1-offset]= [float(x) for x in cols[1-offset]]
	listsToCSV(transpose(cols),new_data_fn)
	if (offset-1):
		listsToCSV([mins,diffs],scale_fn)


def standardizeNorm(old_data_fn, new_data_fn, file_base):
	norms=[]
	scale_fn= 'scales/norm/'+file_base+'_scales'
	if not (offset-1):
		norms= csvToLists(scale_fn)[0]
		norms= [float(x) for x in norms]
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-offset):
		if offset:
			data= [float(elem) for elem in cols[i]]
			norms += [np.linalg.norm(data)]
		cols[i]= [float(elem)/norms[i] for elem in cols[i]]
	cols[1-offset]= [float(x) for x in cols[1-offset]]
	listsToCSV(transpose(cols),new_data_fn)
	if (offset-1):
		listsToCSV([norms],'scales/norm/'+file_base+'_scales')

#input 1 if training, 0 if test
if __name__=="__main__":
	global offset
	#transforming training data
	offset= 1+int(sys.argv[1]) 
	data_type= "training" if int(sys.argv[1]) else "test"
	start=time.time()
	for name in ['all_stats', 'per_game', 'league_ranks']:
		fn= data_type+'/raw/'+name+'2014'
		standardizeNorm(fn,data_type+'/norm/'+name+'2014_norm', name)
	print "Time taken:", time.time()-start