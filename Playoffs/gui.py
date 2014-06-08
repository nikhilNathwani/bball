import Tkinter as tk
from neighbors import *
from model import *
import math
import sys

class Coords:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right= right
        self.top= top
        self.bottom= bottom

class GUI(tk.Frame):
    def __init__(self, parent, pt, numRounds, squareWidth, length, color="white"):
        '''size is the size of a square, in pixels'''
        self.playoff_tree= pt
        self.rows = numRounds
        self.columns = int(math.pow(2,(numRounds-1)))
        self.size = squareWidth
        self.length= length
        self.color = color

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=length, height=length, background="white")
        self.canvas.pack(side="top", fill="both", expand=True, padx=0, pady=0)

        # this binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)

    def showScore(self, t):
        return self.teamName(t)+": "+str(t.score)[:-5]+"\n"

    def toString(self, t1, t2, a1, a2):
        predicted_winner= t1 if t1.score>t2.score else t2
        actual_winner= a1 if a1.true_label > a2.true_label else a2
        correct= "RIGHT" if predicted_winner==actual_winner else "WRONG"
        return self.showScore(t1)+self.showScore(t2)+"\nWinner: " + self.teamName(predicted_winner)+"\nActual: " + self.teamName(actual_winner) + "\n" + correct

    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        pad= (self.length-(self.size*self.columns))/(self.columns+1)
        gap= pad
        matchups= []
        games= [self.playoff_tree.games[x] for x in rearrage]
        actual_games= [self.playoff_tree.actuals[x] for x in rearrage]
        ind= 0
        for row in range(self.rows):
            matchup= []

            #draw the top row of playoff matchups
            if row==0:
                for col in range(self.columns):
                    x1 = pad+col*(self.size+pad)
                    y1 = (row * self.size)+10
                    x2 = x1 + self.size
                    y2 = y1 + self.size
                    matchup += [Coords(x1,x2,y1,y2)]
                    if col%2==1:
                        matchups += [matchup]
                        matchup= []
                    s= self.toString(games[ind][0], games[ind][1], actual_games[ind][0], actual_games[ind][1])
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=s, font="Times 16", tags="matchup")
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=self.color, tags="square")
                    ind+=1

            #draw the squares in remaining rows of playoff matchups by averaging coordinates of previous rows
            else: 
                m= len(matchups)
                for i in range(m):
                    team1, team2= matchups[0]
                    matchups= matchups[1:]
                    x1= float(team1.left+team2.left)/2
                    y1= team1.bottom+33
                    x2= float(team1.right+team2.right)/2
                    y2= y1 + self.size
                    matchup += [Coords(x1,x2,y1,y2)]
                    if i%2==1:
                        matchups += [matchup]
                        matchup= []
                    s= self.toString(games[ind][0], games[ind][1], actual_games[ind][0], actual_games[ind][1])
                    self.canvas.create_text((x1+x2)/2, (y1+y2)/2,text=s, font="Times 16", tags="matchup")
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=self.color, tags="square")
                    ind+=1
        self.canvas.tag_raise("matchup")
        self.canvas.tag_lower("square")


if __name__ == "__main__":
    if len(sys.argv)<=2:
        raise Exception("Must provide k value and test year!")
    k= int(sys.argv[1])
    year= int(sys.argv[2])
    data= knn.csvToTrainTest("/Users/nikhilnathwani/Desktop/BBall/Playoffs/team_data/rescale/all_stats_rescale", year)
    [train,test]= [data["train"], data["test"]]
    print len(test), len(train)
    for team in test:
        print "\n-------------------------"
        print k, "Closest neighbors of:", team.url
        print knn.weightedKNN(k, train, team)
        print "-------------------------\n"
    pt= knn.setPlayoffTree(year, test)
    knn.simPlayoffs(pt)
    knn.numSeriesCorrect(test)
    root = tk.Tk()
    gui = GUI(root, pt, 4, 140, 1280)
    gui.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    root.mainloop()