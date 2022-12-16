import numpy as np
import pandas as pd
import copy

# function for setting up the initial board for Othello
def initial_board():
        board = [["✙" for x in range(8)] for y in range(8)]
        board[3][4] = "O"
        board[4][3] = "O"
        board[3][3] = "0"
        board[4][4] = "0"
        return board

# an Othello class that includes it's own board configuration, as well as all other functions to interact with it
class Othello():
    def __init__(self, board):
        self.board = board
    
    # print board with Pandas dataframe 
    def print_board(self): 
        df = pd.DataFrame(self.board)
        print("Current Board: ")
        print(df)

    # function to make a move, taking in the move as a list of [x,y] and the player color
    def make_move(self, move, player):
        x, y = move
        flipped_tiles = self.check_valid(move, player) # check if the move is valid
        if flipped_tiles: # if the move results in any flipped tiles (i.e. is valid)
            self.board[x][y] = player # put tile on coordinate of move
            for tiles in flipped_tiles: # and replace the flipped tiles with its own
                i,j = tiles
                self.board[i][j] = player
            return True # return true if a move has been successfully made
        else: # if the move returns no flipped tiles, then let the user know and take no action
            print("That is not a valid move")
            self.print_board()
            return False # return false if the move was not valid

    # function that returns the valid moves for a player
    def valid_moves(self, player):
        val_moves = [] # start with empty list
        # iterate through all tiles and check if they are valid moves
        # if they are, append to valid moves list
        for i in range(8):
            for j in range(8):
                if self.check_valid([i,j], player): val_moves.append([i,j])
        return val_moves #return the list of valid moves

    # check if a move is valid by returning the number of tiles it flips
    # if no tiles are flipped, return an empty list
    def check_valid(self, move, player):
        # determine the player's and opponent's tile color
        if player == "0": opponent = "O"
        else: opponent = "0"
        x, y = move # take in x, y coordinate of move
        flipped_tiles = [] # initialize empty list of flipped tiles
         # if attempting to put tile on an occupied square, return empty list
        if self.board[x][y] != "✙":
            return flipped_tiles
        # make a list of all directions to search in
        directions = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]]
        for direction in directions: # check in each direction
            i, j = direction
            r, c = x + i, y + j
            # start checking the minimum requirement of being able to flip at least one tile:
            # if a square adjacent to the move is within bounds and is occupied by the opponent
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                temp_flipped = [[r, c]] # create a temporary list of flipped tiles
                r, c = r + i, c + j # check consecutive tile further along in current direction
                while 0 <= r < 8 and 0 <= c < 8: # while within bounds of board
                    # if the tile adjacent to opponent's tile is our own, opponent's tile can be flipped
                    if self.board[r][c] == player:
                        # add the temporary flipped tiles to actual flipped tiles
                        flipped_tiles.extend(temp_flipped)
                        break # break loop and look in next direction
                    # if the tile adjacent to opponent's tile is their own, check next tile with loop
                    elif self.board[r][c] == opponent:
                        temp_flipped.append([r,c])
                        r, c = r + i, c + j
                    # if met with an empty square, break the loop and look at the next direction
                    else:
                        break
        return flipped_tiles # return all the tiles that got flipped

    # return the black and white player's scores by iterating and counting all squares
    def score(self):
        black_tiles, white_tiles = 0, 0
        for row in self.board:
            for tile in row: 
                if tile == "0": black_tiles += 1
                elif tile == "O": white_tiles += 1
        return black_tiles, white_tiles

    # print the score of each player
    def print_score(self):
        black_tiles, white_tiles = self.score()
        print("Black (0) score: ", black_tiles)
        print("White (O) score: ", white_tiles)

    # return which player won using the score() function
    def won(self):
        black_tiles, white_tiles = self.score()
        if black_tiles > white_tiles:
            return "0"
        elif white_tiles > black_tiles:
            return "O"
        else:
            return False

# create a parent class for players
class Player():
    def __init__(self, color):
        self.color = color
    
    def get_move(self, game):
        pass

# create a subclass for a human player that takes in its color
class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color)

    # function to receive the move of of the human player
    def get_move(self, game):
        valid_input = False
        # check for valid input and continue asking for it while it is false
        while valid_input == False:
            print("Input row and column separated by comma & no space: e.g. 4,5")
            response = input("Where would you like to place your piece? ")
            try: # use try and exception to make sure input is valid
                r1, r2 = response.split(",") # split response into x and y coordinate
                move = [int(r1),int(r2)] # join response in a valid form of list
                if game.make_move(move, self.color): # if the move was succesfully made
                    valid_input = True # set valid input as True and break the loop
            except ValueError:
                print("Please input a valid move. Remember, no spaces. \n")
        return True

# create a subclass for a computer player that takes in the color, whether it is the maxplayer, 
# and how deep it should search; without a depth limit, the computation becomes unfeasible
class ComputerPlayer(Player):
    def __init__(self, color, maxplayer, depth):
        super().__init__(color)
        self.maxplayer = maxplayer
        self.depth = depth
    
    # get the computer's move by calling the minimax function
    def get_move(self, game):
        # set alpha and beta to -infinity and +infinity, respectively
        best = self.minimax(game, self.color, self.maxplayer, self.depth, -np.inf, np.inf)
        # make the move returned by minimax for the color
        game.make_move(best['move'], self.color)
        # print what move the computer made
        print("Computer (%s) placed tile on %s" % (self.color, best['move']))

    # the minimax function takes in the board, color, whether or not it's the maxplayer, the current depth,
    # and the alpha and beta values
    def minimax(self, game, color, maxplayer, depth, alpha, beta):
        # if the depth limit has been reached or there are no more valid moves, return evaluation/untility score
        if depth == 0 or not game.valid_moves(color):
            black_score, white_score = game.score()
            # if the maxplayer is black, the returned evaluation should be positive if black is winning
            if (maxplayer and color == "0") or (not maxplayer and color == "O"):
                score = black_score - white_score
                return {'move': None, 'score': score}
            # if the maxplayer is white, the returned evaluation should be negative if black is winning
            elif (maxplayer and color == "O") or (not maxplayer and color == "0"):
                score = white_score - black_score
                return {'move': None, 'score': score}

        # if currently the maxplayer, find and return the move with maximum utility/evaluation
        if maxplayer:
            max_eval = {'move': None, 'score': -np.inf} # initially set the max score as -inf
            # go through each valid move and update the max_eval to the move with the highest score
            for move in game.valid_moves(color):
                # deepcopy the board and call a new instance of the game so that current board is not affected
                child_board = copy.deepcopy(game.board)
                child_game = Othello(child_board)
                # make the move in the new child board
                child_game.make_move(move, color)
                # change the player color after move has been made
                dif_color = "0" if color == "O" else "O"
                # return the evaluation of the opponent's move using recursion; decrement depth by 1
                eval = self.minimax(child_game, dif_color, False, depth-1, alpha, beta)
                # if the minimzing opponent's lowest evaluation move is higher than the current greatest move, update max_eval
                if eval['score'] > max_eval['score']:
                    max_eval['move'] = move
                    max_eval['score'] = eval['score']
                    # update alpha if the updated score is higher
                    alpha = max(alpha, max_eval['score'])
                # if alpha (the maximum guaranteed score for max player) is greater than or equal to 
                # beta (the minimum guaranteed score for min player), then there is no need to 
                # evaluate the score of the other moves, as the min player will never choose a move with a score
                # higher than the current beta
                if beta <= alpha:
                    return max_eval # break out of the for loop and return the move and score for the max score
            return max_eval
        else:
            # same as above, for the min player, initialize the min eval as +infinity, copy the board,
            # and recursively evaluate the score of every valid move
            min_eval = {'move': None, 'score': np.inf}
            for move in game.valid_moves(color):
                child_board = copy.deepcopy(game.board)
                child_game = Othello(child_board)
                child_game.make_move(move, color)
                dif_color = "0" if color == "O" else "O"
                eval= self.minimax(child_game, dif_color, True, depth-1, alpha, beta)
                # update min_eval if there's a move that returns a lower score 
                if eval['score'] < min_eval['score']:
                    min_eval['move'] = move
                    min_eval['score'] = eval['score']
                    beta = min(beta, eval["score"])
                # if beta is less than or equal to alpha, prune all other branches, as the maxplayer will never
                # choose a move with a score lower than the current alpha
                if beta <= alpha:
                    return min_eval
            return min_eval

# the function that plays the game
def play(game, b_player, w_player):
    color = "0" # first player is black, as per Othello rules
    # keep getting the moves of the players as long as there are valid moves
    while game.valid_moves(color):
        # get black player's move if the current color to play is back
        if color == "0":
            print('\n')
            game.print_score()
            game.print_board()
            print("Black (0) to play")
            b_player.get_move(game)
            color = "O" # change the current color to play to opponent's
        elif color == "O":
            print('\n')
            game.print_score()
            game.print_board()
            print("White (O) to play")
            w_player.get_move(game)
            color = "0"
    # when there are no more valid moves, find the winner by calling the won() function
    winner = game.won()
    print("\n No more valid moves.")
    game.print_score() # print the score
    game.print_board() # print the board
    # announce who the winner is
    if winner == "0":
        print("The winner is Black (0)!")
    elif winner == "O":
        print("The winner is White (O)!")
    else:
        game.print_score()
        print("It's a tie! ")

# Introduce the rules of the game
print("\nHi! This is an Othello game using minimax with alpha-beta pruning. \
    \nIn Othello, you can convert the opponent's pieces by sandwiching them between your pieces. \
    \nA valid move is one that converts at least one tile. \
    \nWhen there are no more moves, the player with the most pieces wins. \
    \nYou can decide the depth of the minimax search, and therefore its difficulty. \
    \nKeep in mind, the deeper the algorithm searches, the longer it can take to make a move.")
while True:
    # ask for input desired depth of minimax search
    val = input("\nWhat is your desired level of difficulty (recommended between 1 ~ 8)? ")
    try: # keep asking for input until a valid input is recognized
        chosen_depth = int(val)
        break
    except ValueError:
        print("Please enter one number between 1 and 10.")
# create an empty, initial board 
in_board = initial_board()
# feed it into the Othello class 
game = Othello(in_board)
# set the black player as a human and the white player as a computer
# allow human-human or computer-computer plays by changing these accordingly
b_player = HumanPlayer("0")
w_player = ComputerPlayer("O", maxplayer=True, depth=chosen_depth)
play(game, b_player, w_player) # play the game