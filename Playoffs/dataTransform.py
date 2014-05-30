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
def standardizeRescale(old_data_fn, new_data_fn):
	mins= []
	diffs= []
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-offset): #The last 2 columns, the url and the label, are skipped over.
		data=[float(x) for x in cols[i]]
		mins += [min(data)]
		diffs += [max(data)-min(data)]
		cols[i]= [(float(elem)-mins[-1])/diffs[-1] for elem in cols[i]]
	cols[1-offset]= [float(x) for x in cols[1-offset]]
	listsToCSV(transpose(cols),new_data_fn)
	if offset:
		fn= old_data_fn[old_data_fn.rfind('/')+1:]
		listsToCSV([mins,diffs],'scales/rescale/'+fn+'_scales')


def standardizeNorm(old_data_fn, new_data_fn):
	norms=[]
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-offset):
		data= [float(elem) for elem in cols[i]]
		norm= np.linalg.norm(data)
		norms += [norm]
		cols[i]= [float(elem)/norm for elem in cols[i]]
	cols[1-offset]= [float(x) for x in cols[1-offset]]
	listsToCSV(transpose(cols),new_data_fn)
	if offset:
		fn= old_data_fn[old_data_fn.rfind('/')+1:]
		listsToCSV([norms],'scales/norm/'+fn+'_scales')

#input 1 if training, 0 if test
if __name__=="__main__":
	global offset
	#transforming training data
	offset= 1+int(sys.argv[1]) 
	data_type= "training" if int(sys.argv[1]) else "test"
	start=time.time()
	for name in ['all_stats', 'per_game', 'league_ranks']:
		fn= '/Users/nikhilnathwani/Desktop/BBall/Playoffs/'+data_type+'/raw/'+name
		standardizeRescale(fn,'/Users/nikhilnathwani/Desktop/BBall/Playoffs/'+data_type+'/rescale/'+name+'_rescale')
	print "Time taken:", time.time()-start