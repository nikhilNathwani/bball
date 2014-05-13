import string

#method of getting last initial probably has corner cases that I'm missing!
def getPlayerFilename(player):
  lastInitial= player[1+string.find(player," ")]
  #remove punctuation
  filename= player.translate(string.maketrans("",""), string.punctuation)
  #remove space
  filename= filename.replace(" ", "")
  return "PlayerTotals/"+lastInitial+"/"+filename+"_Totals_CSV"

#-By convention, seasons are referred-to by the year in which
# they end, e.g. the 2003-04 season is referred to by 2003
#-If the player was traded mid-season, season totals are returned
def getSeasonLine(player, season):
  filename= getPlayerFilename(player)
  with open(filename) as f: 
    for line in f:
      if len(line)>1:
        ind= string.find(line, '-')
        year= int(line[:ind])
        if year==(season-1):
          return line.strip().split(',')
        #this check might just be added inefficiency since most players careers
        #take up <20 lines, so checking this for every line might not be worth
        #it. It might be better to just raise the exception after the for loop.
        if year > (season-1): 
          raise Exception(player + " didn't play in " + str(season-1) + "-" + str(season) + " season.") 
  raise Exception(player + " didn't play in " + str(season-1) + "-" + str(season) + " season.") 


#Need error handling here, probably
#points= stats[-1], games= stats[5], need to document the 
#what each of the "stats" entries represents
def getPPG(player, season):
  stats= getSeasonLine(player, season)
  return float(stats[-1])/float(stats[5])


if __name__=="__main__":
  import time
  start= time.time()
  print getPPG("Shaquille O'Neal",2007)
  print "Time taken:", time.time()-start