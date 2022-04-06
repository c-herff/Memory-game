#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 6.4.2022

@author: c-herff based on code by Emeline

Memory game with tkinter

Memory for one human players
Could be extended to two players (functions already in place)

"""
import random
import tkinter as tk

from pylsl import StreamInfo, StreamOutlet

class MemoryGui:

    # global variables
    turnedCards = 0 # Number of visible cards
    turnedCardsIm = [] # List of index of turned over cards
    turnedCardNb = [] # List of index of played cards
    foundCards = [] # List of index of found pairs
    cardsValues = [] # List of index of cards
    playersNb = 2
    scorePlayer1 = 0
    scorePlayer2 = 0
    idCurrentPlayer = 1
    rowNb = 5
    colNb = 4
    cardsNb = colNb * rowNb # Total number of cards
    pairsNb = cardsNb//2 # Number of different pairs
    themeList = ['Peanuts', 'Cartoon']
    #theme=random.choice(themeList)
    theme = 'Cartoon'
    
    def __init__(self, master):
        self.root = master
        self.root.title("Memory game")
        
        self.frame=tk.Frame(self.root,height=500,width=500)
        self.frame.pack(side=tk.TOP)
        self.frameCards=tk.Frame(self.root)
        self.frameCards.pack(side=tk.BOTTOM)

        #Initialize LSL
        info = StreamInfo('MemoryMarkerStream', 'Markers', 1, 0, 'string', 'emuidw22')
        # next make an outlet
        self.outlet = StreamOutlet(info)

        # menus
        self.top = tk.Menu(self.root)
        self.root.config(menu=self.top)
        self.game = tk.Menu(self.top, tearoff=False)
        self.top.add_cascade(label='Game', menu=self.game)
        self.submenu = tk.Menu(self.game, tearoff=False)
        self.game.add_cascade(label='New Game', menu=self.submenu)
        self.submenu.add_command(label='Dim 3x4', command=self.newGame3x4)
        self.submenu.add_command(label='Dim 5x4', command=self.newGame5x4)
        self.submenu.add_command(label='Dim 5x6', command=self.newGame5x6)
        self.submenu.add_command(label='Dim 5x8', command=self.newGame5x8)
        self.game.add_command(label='Close', command=self.root.destroy)


        ### Should we want to allow two player games
        #players_menu = tk.Menu(top,tearoff=False)
        #top.add_cascade(label='Players',menu=players_menu)
        #players_menu.add_command(label='1 player',command=onePlayer)
        #players_menu.add_command(label='2 players',command=twoPlayers)

        ### In case we want to switch themes
        #themeMenu = tk.Menu(top,tearoff=False)
        #top.add_command(label='Choose theme',command=frameTheme)

        # images 
        self.blankCard = tk.PhotoImage(file='Images/blankCard.gif')
        self.themeCards = [tk.PhotoImage(file=str('Images/'+theme+'/carte-1.gif')) for theme in self.themeList]
            
        # start-up
        #frameTheme()
        self.onePlayer()



    def resetGlobal(self):
        '''
        Resets scores
        
        Returns
        -------
        None.

        '''
        self.scorePlayer1 = 0
        self.scorePlayer2 = 0
        self.idCurrentPlayer = 1
        self.foundCards = []
    

    def reinit(self): 
        '''
        Hides all cards and resets the number of visible cards

        Returns
        -------
        None.

        '''
        for i in range(self.cardsNb):
            if i not in self.foundCards:
                self.but_cards[i].configure(image=self.hiddenCard)
        self.turnedCards = 0

    
    def load_cards(self):
        '''
        Returns
        -------
        memoryCards : list
            List containing unique cards (images) chosen randomly for the memory game  

        '''
        #chosenCards = []
        totalNb = 20
        idCard = [i for i in range(1,totalNb+1)]
        chosenCards = random.sample(idCard, k=self.pairsNb)
        memoryCards = [tk.PhotoImage(file=str('Images/'+self.theme+'/carte-'+str(card)+'.gif')) for card in chosenCards]
        return memoryCards

    def initiateGame(self):
        '''
        Returns
        -------
        mixedCards : list
            List of pairs of cards (images object) randomly mixed.

        '''
        memoryCards = self.load_cards() * 2
        random.shuffle(memoryCards)
        return memoryCards


    # Show visible face of cards 
    def show(self,item):
        self.outlet.push_sample(['showingCard;' + str(item) + ';row=' + str((item+1)//self.colNb) + ';column=' + str((item+1)%self.colNb) + ';img=' + str(self.cardsValues[item])])
        print(f'showingCard;{item};row={(item)//self.rowNb};column={(item)%self.rowNb};img={self.cardsValues[item]}')
        if item not in self.foundCards:
            if self.turnedCards == 0:
                self.but_cards[item].configure(image=self.cardsValues[item])
                self.turnedCards += 1
                self.turnedCardsIm.append(self.cardsValues[item])
                self.turnedCardNb.append(item)
            elif self.turnedCards == 1:
                if item!=self.turnedCardNb[len(self.turnedCardNb)-1]:
                    self.but_cards[item].configure(image=self.cardsValues[item])
                    self.turnedCards += 1
                    self.turnedCardsIm.append(self.cardsValues[item])
                    self.turnedCardNb.append(item)
        if self.turnedCards == 2:
            self.root.after(0, self.check)

    # Verify whether the chosen cards are identical
    def check(self):
        if self.turnedCardsIm[-1] == self.turnedCardsIm[-2]:
            #lsl found pair
            self.foundCards.append(self.turnedCardNb[-1])
            self.foundCards.append(self.turnedCardNb[-2])
            self.but_cards[self.turnedCardNb[-1]].configure(image=self.blankCard)
            self.but_cards[self.turnedCardNb[-2]].configure(image=self.blankCard)
            self.incrementScorePlayer()
        elif self.playersNb == 2:
            self.switchPlayers()
        self.after(2000)
        self.reinit()

    
    def incrementScorePlayer(self):
        '''
        Increments the score of the current player

        Returns
        -------
        None.

        '''
        if self.idCurrentPlayer == 1:
            self.scorePlayer1 += 1
            self.lab_scorePlayer1.configure(text=str(self.scorePlayer1))
        elif self.idCurrentPlayer == 2:
            self.scorePlayer2 += 1
            self.lab_scorePlayer2.configure(text=str(self.scorePlayer2))


    def switchPlayers(self):
        '''
        Switches current player

        Returns
        -------
        None.

        '''
        if self.idCurrentPlayer == 1:
            self.idCurrentPlayer = 2
            self.lab_Player1.configure(fg='black')
            self.lab_Player2.configure(fg='red')
        else:
            self.idCurrentPlayer = 1
            self.lab_Player2.configure(fg='black')
            self.lab_Player1.configure(fg='red')

    # Add a frame with hidden cards (buttons)
    def frameCardsButtons(self):
        filename = 'Images/'+self.theme+'/carte-0.gif'
        self.hiddenCard=tk.PhotoImage(file=filename)
        self.frameCards.destroy()
        self.frameCards = tk.Frame(self.root)
        self.frameCards.pack(side=tk.BOTTOM)
        self.but_cards = []
        for i in range(self.cardsNb):
            self.but_cards.append(tk.Button(self.frameCards, image=self.hiddenCard,command=lambda x=i:self.show(x)))    
        for count in range(self.cardsNb):
            self.but_cards[count].grid(row=count//self.rowNb, column=count%self.rowNb)

    def frameTheme(self):
        self.frameCards.destroy()
        self.frame.destroy()
        self.frame = tk.Frame(self.root, height=500, width=500)
        self.frame.pack(side=tk.TOP)
        self.lab_Message = tk.Label(self.frame, text="Choose the theme you want to play with ")
        self.lab_Message.grid(row=0, column=1)
        self.but_themes = []
        for count, themeCard in enumerate(self.themeCards):
            self.but_themes.append(tk.Button(self.frame, image=themeCard, command=lambda x=count: self.playTheme(x)))
        for count, but_theme in enumerate(self.but_themes):
            self.but_theme.grid(row=1, column=1+count)
            

    def newGame3x4(self):
        '''
        Sets grid dimensions to 5x4 and launches a new game

        Returns
        -------
        None.

        '''
        self.rowNb = 4
        self.colNb = 3
        self.gameCurrentDim()

    def newGame5x4(self):
        '''
        Sets grid dimensions to 5x4 and launches a new game

        Returns
        -------
        None.

        '''
        self.rowNb = 5
        self.colNb = 4
        self.gameCurrentDim()
        

    def newGame5x6(self):
        '''
        Sets grid dimensions to 5x6 and lauches a new game

        Returns
        -------
        None.

        '''
        self.rowNb = 6
        self.colNb = 5
        self.gameCurrentDim()

    def newGame5x8(self):
        '''
        Sets grid dimensions to 5x6 and lauches a new game

        Returns
        -------
        None.

        '''
        self.rowNb = 8
        self.colNb = 5
        self.gameCurrentDim()


    def onePlayer(self):
        '''
        Launches a new game for one player (solo mode)

        Returns
        -------
        None.

        '''
        self.playersNb = 1
        self.gameCurrentDim()
        

    def twoPlayers():
        '''
        Launches a new game for two players

        Returns
        -------
        None.

        '''
        self.playersNb = 2
        self.gameCurrentDim()

    
    def gameCurrentDim(self):
        '''
        Resets global variables and load a new memory to start a new game with current dimensions

        Returns
        -------
        None.

        '''
        if self.playersNb == 1:
            self.stat1player()
        else:
            self.displayScore()
        self.cardsNb = self.colNb*self.rowNb
        self.pairsNb = self.cardsNb//2
        self.cardsValues = self.initiateGame()
        self.resetGlobal()
        self.frameCardsButtons()

    def playTheme(self,x):
        self.theme = self.themeList[x]
        self.gameCurrentDim()

    def displayScore(self):
        self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP)
        self.lab_Player1 = tk.Label(self.frame, text='PLAYER 1 : ', font=("Helvetica",20), fg='red')
        self.lab_Player1.pack(side=tk.LEFT)
        
        self.lab_scorePlayer1 = tk.Label(self.frame,text='0', font=("Helvetica", 20))
        self.lab_scorePlayer1.pack(side=tk.LEFT)
        
        self.lab_Player2 = tk.Label(self.frame, text='  PLAYER 2 : ', font=("Helvetica",20), fg='black')
        self.lab_Player2.pack(side=tk.LEFT)
        
        self.lab_scorePlayer2 = tk.Label(self.frame,text='0', font=("Helvetica", 20))
        self.lab_scorePlayer2.pack(side=tk.LEFT)

    def stat1player(self):
        self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP)
        self.lab_Player1 = tk.Label(self.frame,text='Pairs of cards = ', font=("Helvetica",20), fg='black')
        self.lab_Player1.pack(side=tk.LEFT)
        self.lab_scorePlayer1 = tk.Label(self.frame,text='0', font=("Helvetica", 20))
        self.lab_scorePlayer1.pack(side=tk.LEFT)



    ############################################################################################

if __name__=='__main__':
    root = tk.Tk()
    my_gui = MemoryGui(root)
    root.mainloop()


