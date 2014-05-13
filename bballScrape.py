import re
import string
import csv
import time
import os
import urllib2
from bs4 import BeautifulSoup

#returns list of urls of players whose last name starts with chr
def getPlayersStartingWith(char):
	url= "http://www.basketball-reference.com/players/" + char
	usock= urllib2.urlopen(url)
	data= usock.read()
	usock.close()
	query_soup= BeautifulSoup(data)
	#print query_soup.prettify()
	links= query_soup.find_all('a', {"href" : re.compile("^/players/[a-z]/[a-z]")})
	urlSuffixes= {}
 	for link in links:
		urlSuffixes[link.text.encode("ascii","ignore")] = link["href"].encode("ascii","ignore")
	return urlSuffixes

#player= name of player, e.g. "Dwayne Wade" (needed for filename)
#urlSuffix= link to player's info, append to "http://www.basketball-reference.com"
#tableType= something in {totals, perGame, per36, advanced}
#Known issues: repeat names get overwritten (e.g. "Dan Anderson")
def createPlayerStatCSV(player,urlSuffix,tableType,folder):
	usock= urllib2.urlopen("http://www.basketball-reference.com"+urlSuffix)
	data= usock.read()
	usock.close()
	query_soup= BeautifulSoup(data)
	#print query_soup.prettify()
	regSeasonStats= []
	tables= query_soup.find_all('tr', {"id" : re.compile("^totals")})
	for regularSeason in tables:
		statLine= []
		for stat in regularSeason.find_all('td'):
			statLine += [stat.text.encode("ascii","ignore")]
		regSeasonStats+= [statLine]
	filename= re.sub('[^a-zA-z]*|[^a-zA-Z]*','',player)+"_"+tableType[0].upper()+tableType[1:]+"_CSV"
	#print filename
	playerCSV = open('/Users/nikhilnathwani/Desktop/PlayerTotals/'+folder+'/'+filename, 'wb')
	wr = csv.writer(playerCSV)
	for season in regSeasonStats:
		wr.writerow(season)
	

if __name__=="__main__":
	totalStart= time.time()
	for i in range(len(string.lowercase)):
		start= time.time()
		nameUrls= getPlayersStartingWith(string.lowercase[i])
		for name,url in nameUrls.iteritems():
			createPlayerStatCSV(name, url, "totals", string.uppercase[i])
		print "Done with", string.uppercase[i], ". Time taken:", time.time()-start, "secs"
		time.sleep(120)
	print "Total time taken:", time.time()-totalStart, "secs"
