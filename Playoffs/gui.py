import Tkinter as tk
import knn
import math

class Coords:
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right= right
        self.top= top
        self.bottom= bottom

class GUI(tk.Frame):
    def __init__(self, parent, numRounds, squareWidth, length, color="white"):
        '''size is the size of a square, in pixels'''
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
        
    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        #self.canvas.delete("square")
        #self.canvas.delete("nums")
        pad= (self.length-(self.size*self.columns))/(self.columns+1)
        gap= pad
        matchups= []
        for row in range(self.rows):
            matchup= []
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
                    self.canvas.create_text(x1+self.size/32+21/2,y1+self.size/16+21/2,text="HI", font="Times 21", tags="nums")
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=self.color, tags="square")
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
                    self.canvas.create_text(x1+self.size/32+21/2,y1+self.size/16+21/2,text="HI", font="Times 21", tags="nums")
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=self.color, tags="square")
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")


if __name__ == "__main__":
    root = tk.Tk()
    board = GUI(root, 4, 140, 1280)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    root.mainloop()
