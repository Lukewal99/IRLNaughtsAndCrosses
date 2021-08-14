#Imports
import math
import random
import copy

#Global Variables
Board = [["1","2","3"],["4","5","6"],["7","8","9"]]
O = True 
Victory = False
TurnNum = 0
OWin = 0
XWin = 0
Draw = 0

#ToDO
# Change O to Player=O|X
# Change board to 1d array


#Functions
def Display():
    if int(NumOfTurns) < 3:
        print("")
        for i in range(0,3):
            print(Board[i])

        
def PlayTurn(O):
    global Board
    
    ValidTurn = False

    if O:
        Mark = "O"
    else:
        Mark = "X"
    
    while ValidTurn == False: 
        j = input("Player " + Mark + " input number of square to replace: ")
        if (j.isnumeric() == True):
            j = int(j)
            if (j <= 9) and (j >= 1):
                
                x = (j%3)-1  # Calculate Board array position from entered grid position
                if x == -1:
                    x += 3
                    
                y = math.ceil(j/3)-1

                if Board[y][x].isnumeric():  # Check position not already taken
                    ValidTurn = True

    # ToDo Replace 4 lines below with 1 line?          
    if O == True:
        Board[y][x] = "O"
    else:
        Board[y][x] = "X"


def ComputerRandomTurn(O):
    global Board
    
    ValidTurn = False

    if O:
        Mark = "O"
    else:
        Mark = "X"
    
    while ValidTurn == False:
        RandPos = random.randint(1,9)
        
        x = (RandPos%3)-1  # Calculate Board array position from entered grid position
        if x == -1:
             x += 3
                    
        y = math.ceil(RandPos/3)-1
    
        if Board[y][x].isnumeric():  # Check position not already taken
            ValidTurn = True

    # ToDo Replace 4 lines below with 1 line?        
    if O == True:
        Board[y][x] = "O"
    else:
        Board[y][x] = "X"
        
    if int(NumOfTurns) < 3:
        print("Computer " + Mark + " input number of square to replace: " + str(RandPos))


def ComputerCalculatedTurn(O):
    global Board
    
    if O:
        Mark = "O"
    else:
        Mark = "X"

    # Will we win on this square? If so - take the square   
    for n in range (0,3):
        for m in range (0,3): # Cycle through all squares
            
            TempBoard = copy.deepcopy(Board) # Take a copy of the board
            CurrentSquare = TempBoard[n][m]
                
            if (CurrentSquare.isnumeric() == True): # Is the square empty
                TempBoard[n][m] = Mark
                Victory, WinMark = WinCondition(O, TempBoard)
                if Victory:
                    if int(NumOfTurns) < 3:
                        print("Win " + str(n) + " " + str(m))
                    Board[n][m] = Mark # If taking this square wins, then take this square
                    return False # ComputerCalculatedTurn Complete
    if int(NumOfTurns) < 3:
        print("Cant win on this turn")

    # Will the enemy win on this square? If so - take the square        
    if O:
        EnemyMark = "X"
    else:
        EnemyMark = "O"
        
    for n in range (0,3):
        for m in range (0,3): # Cycle through all squares
            
            TempBoard = copy.deepcopy(Board) # Take a copy of the board
            CurrentSquare = TempBoard[n][m]
                
            if (CurrentSquare.isnumeric() == True): # Is the square empty
                TempBoard[n][m] = EnemyMark
                Victory, WinMark = WinCondition(not O, TempBoard)
                if Victory:
                    Board[n][m] = Mark # If taking this square stops yuor opoppnent winning, then take this square
                    if int(NumOfTurns) < 3:
                        print("Stop Win " + str(n) + " " + str(m))
                        print("This square is stopping opponent victory")
                    return False # ComputerCalculatedTurn Complete
    if int(NumOfTurns) < 3:
        print("Cant lose on this turn")

    # If the middle square is free - take it   
    if (Board[1][1].isnumeric() == True): # Is the square empty
        Board[1][1] = Mark
        if int(NumOfTurns) < 3:
            print("This is a critical square")
        return False
    if int(NumOfTurns) < 3:
        print("Cant take centre square")
    
    ComputerRandomTurn(O) # If we haven't found any other better turn, take a random turn.
    if int(NumOfTurns) < 3:
        print("So take a random turn")
    
    
def NextPlayer():
    global O
    O = not O


def ChoosePlayers():
    Valid = False
    while Valid == False:
        pO = input("Player O: Human[1] Easy Computer[2] Hard Computer[3] \n")
        if pO == "1":
            Valid = True
            pO = "Human"
        elif pO == "2":
             Valid = True
             pO = "Easy Computer"
        elif pO == "3":
             Valid = True
             pO = "Hard Computer"
             
    Valid = False
    while Valid == False:
        pX = input("Player X: Human[1] Easy Computer[2] Hard Computer[3] \n")
        if pX == "1":
             Valid = True
             pX = "Human"
        elif pX == "2":
             Valid = True
             pX = "Easy Computer"
        elif pX == "3":
             Valid = True
             pX = "Hard Computer"

    Valid = False
    while Valid == False:
        NumOfTurns = input("How many turns do you want to take? ")
        if (Board[1][1].isnumeric() == True):
            Valid = True
            
    return pO, pX, NumOfTurns


def WinCondition(O, LocalBoard):
    if O == True:
        Mark = "O"
    else:
        Mark = "X"

    #print("DEBUG: LocalBoard: ")
    #print(*LocalBoard)
    
    if (LocalBoard[1][1] == Mark):
        if (LocalBoard[0][0] == Mark and LocalBoard[2][2] == Mark):
            return(True, Mark)
        if (LocalBoard[0][1] == Mark and LocalBoard[2][1] == Mark):
            return(True, Mark)
        if (LocalBoard[0][2] == Mark and LocalBoard[2][0] == Mark):
            return(True, Mark)
        if (LocalBoard[1][0] == Mark and LocalBoard[1][2] == Mark):
            return(True, Mark)
        
    if (LocalBoard[0][0] == Mark):
        if (LocalBoard[0][1] == Mark and LocalBoard[0][2] == Mark):
            return(True, Mark)
        if (LocalBoard[1][0] == Mark and LocalBoard[2][0] == Mark):
            return(True, Mark)
        
    if (LocalBoard[2][2] == Mark):
        if (LocalBoard[1][2] == Mark and LocalBoard[0][2] == Mark):
            return(True, Mark)
        if (LocalBoard[2][0] == Mark and LocalBoard[2][1] == Mark):
            return(True, Mark)
        
    return(False, Mark)

# Main Game
def main():
    # Check if player O and player X are humans or randomcomputers
    pO, pX, NumOfTurns = ChoosePlayers()

    for t in range (0,int(NumOfTurns)):
        
        Board = [["1","2","3"],["4","5","6"],["7","8","9"]]
        O = True 
        Victory = False
        TurnNum = 0

        while (TurnNum < 9) and (Victory == False):
            Display()
            if O:
                if pO == "Human":
                    PlayTurn(O)
                elif pO == "Easy Computer":
                   ComputerRandomTurn(O)
                elif pO == "Hard Computer":
                    ComputerCalculatedTurn(O)
            else:
                if pX == "Human":
                    PlayTurn(O)
                elif pX == "Easy Computer":
                    ComputerRandomTurn(O)
                elif pX == "Hard Computer":
                    ComputerCalculatedTurn(O)
                    
            Victory, Mark = WinCondition(O, Board)
            NextPlayer()
            TurnNum += 1
            Display()

        if Victory and Mark == "O":
            print("You Win O!")
            OWin +=1
        elif Victory and Mark == "X":
            print("You Win X!")
            XWin +=1
        else:
            print("The game is a Draw")
            Draw +=1
            
    print("O won " + str(OWin) + " times")
    print("X won " + str(XWin) + " times")
    print("They drew " + str(Draw) + " times")


if __name__ == '__main__':
    main()
