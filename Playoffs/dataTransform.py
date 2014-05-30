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
#isTrain is 1 if training, 0 if test. If dealing with training, then attribute mins and 
#ranges are saved to mins and diffs and written to file. If dealing with test, then 
#attribute mins and ranges are read from file and stored in mins and diffs
def standardizeRescale(old_data_fn, new_data_fn, file_base):
	mins= []
	diffs= []
	scale_fn= 'scales/rescale/'+file_base+'_scales'

	#if dealing with test data, read mins and diffs from file
	if not isTrain:
		[mins,diffs]= csvToLists(scale_fn)
		mins= [float(x) for x in mins]
		diffs= [float(x) for x in diffs]

	#get train/test data from file	
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-isTrain-1): #The url and the label columns (when present), are skipped over.
		#if dealing with training data, prepare to save min and diff data to file
		if isTrain:
			data=[float(x) for x in cols[i]]
			mins += [float(min(data))]
			diffs += [float(max(data))-float(min(data))]
		cols[i]= [(float(elem)-mins[i])/diffs[i] for elem in cols[i]]
	cols[-isTrain]= [float(x) for x in cols[-isTrain]] #convert label column entries to floats
	
	#save normalized data to new file
	listsToCSV(transpose(cols),new_data_fn)
	
	#if dealing with training data, save scaling info (mins and diffs) to file 
	if isTrain:
		listsToCSV([mins,diffs],scale_fn)


def standardizeNorm(old_data_fn, new_data_fn, file_base):
	norms=[]
	scale_fn= 'scales/norm/'+file_base+'_scales'

	#if dealing with test data, read norms from file
	if not isTrain:
		norms= csvToLists(scale_fn)[0]
		norms= [float(x) for x in norms]

	#get train/test data from file	
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-isTrain-1):
		#if dealing with training data, prepare to save min and diff data to file
		if isTrain:
			data= [float(elem) for elem in cols[i]]
			norms += [np.linalg.norm(data)]
		cols[i]= [float(elem)/norms[i] for elem in cols[i]]
	cols[-isTrain]= [float(x) for x in cols[-isTrain]] #convert label column entries to floats
	
	#save normalized data to new file
	listsToCSV(transpose(cols),new_data_fn)
	
	#if dealing with training data, save scaling info (mins and diffs) to file 
	if isTrain:
		listsToCSV([norms],'scales/norm/'+file_base+'_scales')


#input 1 if training, 0 if test
if __name__=="__main__":
	#for training data, last 2 entries shouldn't be normalized. fFr test data, last 1 entry 
	#shouldn't be normalized. Thus different offsets for each type of data!
	#isTrain allows me to sneakily cater my code to both train and test 
	global isTrain
	isTrain= int(sys.argv[1]) 
	data_type= "training" if int(sys.argv[1]) else "test"
	start=time.time()
	for name in ['all_stats', 'per_game', 'league_ranks']:
		#janky, the below 2 lines with filenames below need to be changes manually
		fn= data_type+'/raw/'+name+'2014'
		standardizeNorm(fn,data_type+'/norm/'+name+'2014_norm', name)
	print "Time taken:", time.time()-start