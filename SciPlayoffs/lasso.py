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

def getBestAttrs(data_type, scale,year):
	alphas=[0.0001,0.0005,0.001,0.005,0.01,0.05,0.1,0.5]

	if data_type=="all_stats":
		attrDict= allStatDict
	elif data_type=="per_game":
		attrDict= perGameDict
	else:
		attrDict= leagueRankDict

	diffs= {}
	alphaAttrs= {}
	alphaAttrNames= {}
	
	for a in alphas:
		alphaAttrs[a]= []
		alphaAttrNames[a]= []

		csvToTrainTest('team_data/'+scale+'/'+data_type,'team_data/winPcts',year)
		m,winList,numSeriesCorrect= baselinePlayoffs(year)
		base=numSeriesCorrect

		csvToTrainTest('team_data/'+scale+'/'+data_type,'team_data/winPcts',year)
		clf= lasso(attrs["train"],targets["train"],a)
		preds= []
		for attr in attrs["test"]: 
			#print urls["test"][j], targets["test"][j], clf.predict(attrs["test"][j])
			preds.append(clf.predict(attr))
		m,winList,numSeriesCorrect= playoffEngine(preds,year)

		for i,elem in enumerate(clf.coef_):
			if elem != 0:
				alphaAttrs[a].append(i)
				alphaAttrNames[a].append(attrDict[i])

		diffs[a]= numSeriesCorrect-base

	for a in alphas:
		print a,len(alphaAttrs[a]), diffs[a]
	bestAlpha= max(diffs.iterkeys(), key=(lambda key: diffs[key]))
	print "Best alpha:", bestAlpha
	return alphaAttrs[bestAlpha]

def getBestAlpha(data_type, scale, yearStart):
	alphas=[0.0001,0.0005,0.001,0.005,0.01,0.05,0.1,0.5]
	data_type= 'league_ranks'
	scale= 'rescale'
	if data_type=="all_stats":
		attrDict= allStatDict
	elif data_type=="per_game":
		attrDict= perGameDict
	else:
		attrDict= leagueRankDict
	nums= []
	diffs= []
	bestsAlphas= {}
	alphaAttrs= {}
	alphaAttrNames= {}
	for a in alphas:
		for yr in range(yearStart,2014):
			csvToTrainTest('team_data/'+scale+'/'+data_type,'team_data/winPcts',yr)
			m,winList,numSeriesCorrect= baselinePlayoffs(yr)
			base=numSeriesCorrect

			csvToTrainTest('team_data/'+scale+'/'+data_type,'team_data/winPcts',yr)
			clf= lasso(attrs["train"],targets["train"],a)
			preds= []
			for attr in attrs["test"]: 
				#print urls["test"][j], targets["test"][j], clf.predict(attrs["test"][j])
				pred.append(clf.predict(attr))
			m,winList,numSeriesCorrect= playoffEngine(pred,yr)
			#print numSeriesCorrect
			nums.append(numSeriesCorrect)
			diffs.append(numSeriesCorrect-base)
		#print nums
		#print diffs, max(diffs)
		bestsAlphas[a]= sum(diffs)
		alphaAttrs[a]= []
		alphaAttrNames[a]= []
		for i,elem in enumerate(clf.coef_):
			if elem != 0:
				alphaAttrs[a].append(i)
				alphaAttrNames[a].append(attrDict[i])
		nums= []
		diffs= []
	#print alphaAttrs
	for a in alphas:
		print a,len(alphaAttrs[a]), bestsAlphas[a]
	bestAlpha= max(bestsAlphas.iterkeys(), key=(lambda key: bestsAlphas[key]))
	print "Best alpha:", bestAlpha
	return alphaAttrs[bestAlpha]


if __name__=="__main__":
	alphas=[0.0001,0.0005,0.001,0.005,0.01,0.05,0.1,0.5]
	data_type= 'league_ranks'
	scale= 'rescale'
	print getBestAttrs(data_type, scale, 2005)