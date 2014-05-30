import string
import time
import csv
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
def standardizeRescale(old_data_fn, new_data_fn):
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-2): #The last 2 columns, the url and the label, are skipped over.
		data=[float(x) for x in cols[i]]
		mn= min(data)
		diff= max(data)-mn
		cols[i]= [(float(elem)-mn)/diff for elem in cols[i]]
	cols[-1]= [float(x) for x in cols[-1]]
	listsToCSV(transpose(cols),new_data_fn)

def standardizeNorm(old_data_fn, new_data_fn):
	rows= csvToLists(old_data_fn)
	cols= transpose(rows)
	for i in range(len(cols)-2):
		data= [float(elem) for elem in cols[i]]
		norm= np.linalg.norm(data)
		cols[i]= [float(elem)/norm for elem in cols[i]]
	cols[-1]= [float(x) for x in cols[-1]]
	listsToCSV(transpose(cols),new_data_fn)

if __name__=="__main__":
	#transforming training data
	start=time.time()
	for name in ['all_stats', 'per_game', 'league_ranks']:
		fn= '/Users/nikhilnathwani/Desktop/BBall/Playoffs/training/raw/'+name
		standardizeNorm(fn,'/Users/nikhilnathwani/Desktop/BBall/Playoffs/training/norm/'+name+'_norm')
	print "Time taken:", time.time()-start