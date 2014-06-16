from sklearn import linear_model
import sys
from dataProcess import *
from model import *

def lasso(attrs,targets, a):
	clf = linear_model.Lasso(alpha=a)
	clf.fit(attrs, targets)
	#print len(clf.coef_), len(allStatDict), clf.coef_
	'''for i,elem in enumerate(clf.coef_):
		if elem != 0:
			print elem, allStatDict[i]'''
	return clf


if __name__=="__main__":
	alphas=[0.0001,0.0005,0.001,0.005,0.01,0.05,0.1,0.5]
	nums= []
	diffs= []
	bestsAlphas= {}
	alphaAttrs= {}
	for a in alphas:
		for yr in range(int(sys.argv[1]),2014):
			csvToTrainTest('team_data/rescale/all_stats','team_data/winPcts',yr)
			m,winList,numSeriesCorrect= baselinePlayoffs(yr)
			base=numSeriesCorrect

			csvToTrainTest('team_data/rescale/all_stats','team_data/winPcts',yr)
			clf= lasso(attrs["train"],targets["train"],a)
			p= []
			pred= []
			for j in range(0,16): 
				#print urls["test"][j], targets["test"][j], clf.predict(attrs["test"][j])
				p.append(clf.predict(attrs["test"][j]))
			m,winList,numSeriesCorrect= playoffEngine(p,yr)
			#print numSeriesCorrect
			nums.append(numSeriesCorrect)
			diffs.append(numSeriesCorrect-base)
		print nums
		print diffs
		bestsAlphas[a]= sum(diffs)
		alphaAttrs[a]= []
		for i,elem in enumerate(clf.coef_):
			if elem != 0:
				alphaAttrs[a].append(allStatDict[i])
		nums= []
		diffs= []
	print bestsAlphas
	print alphaAttrs


