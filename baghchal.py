from copy import deepcopy
from mcts import *

class Board():
    # create constructor (init board class instance)
    def __init__(self, board=None):
        # define players
        self.player_tiger = 0
        self.player_goat = 1
        self.empty_space = None
        self.player_turn = self.player_goat

        # define board position i.e. state of board
        self.position = [
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None],
                            [None, None, None, None, None]
                        ]
        
        # self.position = [
        #                     [0, 1, 1, None, 0],
        #                     [1, 1, 1, None, None],
        #                     [1, 1, 1, None, None],
        #                     [None, None, None, None, None],
        #                     [0, None, None, None, 0]
        #                 ]

        # init (reset board)
        self.init_board()

        # track the number of trapped tigers
        self.tigers = {
            'trapped': []
        }

        # stats for goat player
        self.goats = {
            # initially 20 goats are on hand
            'onHand': 20,
            # initially 0 goats are killed
            'killed': 0
        }

        # position of piece selected by player (inorder to find the next valid move for the player)
        # [-1, -1] signifies goats are still on hand and placing is on board of goat is left
        # self.selected_position = [-1, -1]
        self.selected_position = [-1, -1]

        # for the selected piece, store the valid moves
        self.valid_moves = []

        # create a copy of previous board state if available
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    # init (reset board)
    def init_board(self):
        # loop over board rows
        for row in range(5):
            # loop over board columns
            for col in range(5):
                # set board position
                if (row == 0 and col == 0) or (row == 0 and col == 4) or (row == 4 and col == 0) or (row == 4 and col == 4):
                    self.position[row][col] = self.player_tiger
                else:
                    self.position[row][col] = self.empty_space
    
    def make_move(self, row, col, kill=False,killrow=None, killcol=None):
        # create a new board instance
        board = Board(self)
        board.valid_moves = []

        # make move for player goat if on hand goat is left
        if (board.player_turn == board.player_goat) and (board.goats["onHand"] > 0):
            board.position[row][col] = board.player_goat
            board.goats["onHand"] -= 1
        elif (board.player_turn == board.player_goat) and (board.goats["onHand"] <=0 ):
            board.position[row][col] = board.player_goat
            board.position[board.selected_position[0]][board.selected_position[1]] = board.empty_space
            board.goats["killed"] += 1
        elif kill:
            board.position[row][col] = board.player_tiger
            board.position[board.selected_position[0]][board.selected_position[1]] = board.empty_space
            board.position[killrow][killcol] = board.empty_space
            board.goats["killed"] += 1
        else:
            board.position[row][col] = board.player_tiger
            board.position[board.selected_position[0]][board.selected_position[1]] = board.empty_space
        
        # change the player turn
        board.player_turn = board.player_goat if board.player_turn == board.player_tiger else board.player_tiger
        # print("This is what the board and moves look like: position and valid moves", board.position, board.valid_moves)
        return board
    
    # check for the position to be diagonal
    def check_diagonal(self, coordinate):
        if ((coordinate[0] + coordinate[1]) % 2) == 0:
            return True
        else:
            return False

    # check for valid positions for selected move and player
    def valid_strategies(self):

        directions = [
            { "row": -1, "col": 0 }, # up
            { "row": 1, "col": 0 }, # down
            { "row": 0, "col": -1 }, # left
            { "row": 0, "col": 1 }, # right
        ]

        directionsWithDiagonal = [
            { "row": -1, "col": 0 }, # up
            { "row": 1, "col": 0 }, # down
            { "row": 0, "col": -1 }, # left
            { "row": 0, "col": 1 }, # right
            { "row": -1, "col": -1 }, # top-left
            { "row": -1, "col": 1 }, # top-right
            { "row": 1, "col": -1 }, # bottom-left
            { "row": 1, "col": 1 }, # bottom-right
        ]

        # check if it's goat's turn and there are goats remained to be placed on board
        if (self.player_turn == self.player_goat) and (self.goats["onHand"] > 0):
            #  iterate over each row and column of the board
            for row in range(5):
                for col in range(5):
                    # check if the cell is empty(None) and add it as a valid move
                    if self.position[row][col] == self.empty_space:
                        print("appending valid moves @ " + str(row) + "row " + str(col) + "col")
                        self.valid_moves.append(self.make_move(row, col))
            return 0;

        # check valid moves for goat to reposition the goat after all goats are placed on board
        elif (self.player_turn == self.player_goat) and (self.goats["onHand"] <= 0) and (self.position[self.selected_position[0]][self.selected_position[1]] == self.player_goat):
            row = self.selected_position[0]
            col = self.selected_position[1]

            if self.check_diagonal(self.selected_position):
                # coordinates falling in diagonal has more valid moves
                directionChoice = directionsWithDiagonal
            else:
                directionChoice = directions

            for direction in directionChoice:
                newRow = row + direction["row"]
                newCol = col + direction["col"]

                # check if the position is within the bounds of the board
                if newRow >= 0 and newRow <= 4 and newCol >= 0 and newCol <= 4:
                    # check if the position is empty
                    if self.position[newRow][newCol] == self.empty_space:
                        self.valid_moves.append(self.make_move(row, col))
            return 0;

        # check valid moves for tiger
        else:
            row = self.selected_position[0]
            col = self.selected_position[1]

            if self.check_diagonal(self.selected_position):
                # coordinates falling in diagonal has more valid moves
                directionChoice = directionsWithDiagonal
            else:
                directionChoice = directions

            for direction in directionChoice:
                newRow = row + direction["row"]
                newCol = col + direction["col"]

                # check one more step in the straight line for kill action
                newKillRow = newRow + direction["row"]
                newKillCol = newCol + direction["col"]

                # check if the position is within the bounds of the board
                if newRow >= 0 and newRow <= 4 and newCol >= 0 and newCol <= 4:
                    # check if the new position is empty
                    if self.position[newRow][newCol] == self.empty_space:
                        self.valid_moves.append(self.make_move(newRow, newCol))
                    elif self.position[newRow][newCol] == self.player_goat:
                        if newKillRow >= 0 and newKillRow <= 4 and newKillCol >= 0 and newKillCol <= 4:
                            if self.position[newKillRow][newKillCol] == None:
                                self.valid_moves.append(self.make_move(newKillRow, newKillCol, True, newRow, newCol))
            return 0;
    
    # helper function to count trapped tigers
    def get_trapped_tigers(self):
        # reset trapped tigers
        self.tigers["trapped"] = []

        # get the positions of tigers
        tigers = self.get_player_position(self, self.player_tiger)

        # temporarily change the player turn
        temp_player_turn = self.player_turn
        self.player_turn = self.player_tiger

        # check if the tiger is trapped
        for tiger in tigers:
            
            self.selected_position = tiger
            self.valid_moves = []
            self.valid_strategies()
            
            if len(self.valid_moves) == 0:
                self.tigers["trapped"].append(tiger)

        self.player_turn = temp_player_turn

    # make game over function here
    def is_gameover(self):
        # 2 means tiger won
        # 1 means goat won
        # 0 means game is not over yet

        directions = [
            { "row": -1, "col": 0 }, # up
            { "row": 1, "col": 0 }, # down
            { "row": 0, "col": -1 }, # left
            { "row": 0, "col": 1 }, # right
        ]

        directionsWithDiagonal = [
            { "row": -1, "col": 0 }, # up
            { "row": 1, "col": 0 }, # down
            { "row": 0, "col": -1 }, # left
            { "row": 0, "col": 1 }, # right
            { "row": -1, "col": -1 }, # top-left
            { "row": -1, "col": 1 }, # top-right
            { "row": 1, "col": -1 }, # bottom-left
            { "row": 1, "col": 1 }, # bottom-right
        ]

        self.get_trapped_tigers()

        # check if all tigers are trapped
        if len(self.tigers["trapped"]) >= 4:
            return 1

        # check if all goats are killed
        if self.goats["killed"] >= 5:
            return 2
        
        # check if none of the goat has valid move
        if self.goats["onHand"] <= 0:
            validMoveNumberGoat = 0
            # check for the null positions
            empty_spaces = self.get_player_position(self, self.empty_space)
            for empty_space in empty_spaces:
                row = empty_space[0]
                col = empty_space[1]

                # check if the position is diagonal
                if self.check_diagonal(empty_space):
                    directionChoice = directionsWithDiagonal
                else:
                    directionChoice = directions

                for direction in directionChoice:
                    newRow = row + direction["row"]
                    newCol = col + direction["col"]

                    if newRow >= 0 and newRow <= 4 and newCol >= 0 and newCol <= 4 and self.position[newRow][newCol] == self.player_goat:
                        validMoveNumberGoat += 1
                        break
            if validMoveNumberGoat <= 0:
                return 2

        return 0

    # get the position of the given player in the board
    def get_player_position(self, board, searching_player):
        player_positions = []

        for row in range(5):
            for col in range(5):
                if board.position[row][col] == searching_player:
                    player_positions.append([row, col])
        
        return player_positions

# main driver
if __name__ == '__main__':
    # create board instance
    board = Board()

    # create mcts instance
    mcts = MCTS()
    # root = TreeNode(board)
    # print(mcts.select(root))

    # loop to play AI vs AI
    # while True:
    # find the best move
    best_move = mcts.search(board)

    # make the best move
    board = best_move.board

    # print the board
    print(board, "this might be the best move babe")

    input()
