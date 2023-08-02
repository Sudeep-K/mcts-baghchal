import math
import random
from baghchal import Board

# tree class definition
class TreeNode():
    # class constructor (create tree node structure)
    def __init__(self, board, parent=None):
        # init associated board state
        self.board = Board(board)

        # is node terminal flag
        if self.board.is_gameover():
            self.is_terminal = True

        # otherwise
        else:
            # we have non terminal node
            self.is_terminal = False
        
        # init is fully expanded flag
        self.is_fully_expanded = self.is_terminal

        # init parent node if available
        self.parent = parent

        # init the number of node visits
        self.visits = 0

        # init the total score of the node
        self.score = 0

        # init current node's children
        self.children = {}

# MCTS class definition
class MCTS():
    # search for the best move in the current position
    def search(self, initial_state):
        # create a root node
        self.root = TreeNode(initial_state, None)

        # walk through 1000 iterations
        for iteration in range(2):
            # select a node (selection phase)
            node = self.select(self.root)
            print(node.board.__dict__, "node")

            # score current node (simulation phase)
            score = self.rollout(node.board)
            # print(score, "score")

            # backpropagate results
            self.backpropagate(node, score)

        # pick up the best move in the current position
        try:
            return self.get_best_move(self.root, 0)
        except:
            pass

    # select the most promising node
    def select(self, node):
        # make sure that we are dealing with non terminal node
        while not node.is_terminal:
            # case where node is fully expanded
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)

            # case where node is not fully expanded
            else:
                # otherwise expand the node
                return self.expand(node)
            
        # return terminal node
        return node
    
    # expand the node
    def expand(self, node):
        # generate legal moves for the given node
        print("\n\n\n\nI am currently expanding")
        if (node.board.player_turn == node.board.player_goat) and (node.board.goats["onHand"] > 0):
            node.board.valid_moves = []
            node.board.valid_strategies()
            states = node.board.valid_moves

            for state in states:
                # make sure that current state (move) is not present in child nodes
                if str(state.position) not in node.children:
                    # create a new node
                    new_node = TreeNode(state, node)

                    # add child node to the parent's node children list (dict)
                    node.children[str(state.position)] = new_node

                    # case when node is fully expanded
                    if len(states) == len(node.children):
                        node.is_fully_expanded = True

                    # return newly created node
                    return new_node
        else:
            for row in range(5):
                for col in range(5):
                    if (node.board.player_turn == node.board.player_goat) and (node.board.position[row][col] == node.board.player_goat):
                        node.board.selected_position = [row, col]
                        node.board.valid_moves = []
                        node.board.valid_strategies()
                        states = node.board.valid_moves
                            
                    elif (node.board.player_turn == node.board.player_tiger) and (node.board.position[row][col] == node.board.player_tiger):
                        node.board.selected_position = [row, col]
                        node.board.valid_moves = []
                        node.board.valid_strategies()
                        states = node.board.valid_moves

                    for state in states:
                        # make sure that current state (move) is not present in child nodes
                        if str(state.position) not in node.children:
                            # create a new node
                            new_node = TreeNode(state, node)

                            # add child node to the parent's node children list (dict)
                            node.children[str(state.position)] = new_node

                            # return newly created node
                            return new_node

            # case when node is fully expanded
            node.is_fully_expanded = True

    # rollout (simulate) the game from the current position via making random moves until the game is finished
    def rollout(self, board):
        print("\n\n\n\t\t\t\tI am rolling out")
        # make random moves for both sides until terminal state of the game is reached
        while not board.is_gameover():
            # choose random piece to make move
            print("\t\t\t\tThis is the board")
            for row in board.position:
                print("\t\t\t\t", row)
            print("\t\t\t\tThis is current player turn", board.player_turn)
            if (board.player_turn == board.player_goat) and (board.goats["onHand"] > 0):
                print("no need to select a position")
            else:
                # i need to check for the players and on selected position to have valid moves
                random_position = random.choice(board.get_player_position(board, board.player_turn))
                board.selected_position = random_position
                print("\t\t\t\tThis is the randomly selected position to play", random_position)
            board.valid_moves = []
            board.valid_strategies()
            board = random.choice(board.valid_moves)
            print("\t\t\t\tThis is the board after making a move")
            for row in board.position:
                print("\t\t\t\t", row)
            print("\t\t\t\tThis is the state of game whether it is gameover or not", board.is_gameover())
        print("\t\t\t\tGame over state after roll out", board.is_gameover())
        # return score from the player goat perspective
        if board.player_turn == board.player_goat: return 1
        if board.player_turn == board.player_tiger: return -1

    # backpropagate the number of visits and score up to the root node
    def backpropagate(self, node, score):
        # update nodes's up to root node
        while node is not None:
            # update node's visits
            node.visits += 1
            
            # update node's score
            node.score += score
            
            # set node to parent
            node = node.parent

    # select the best node based on the UCB1 formula
    def get_best_move(self, node, exploration_value):
        # define best move and best score
        best_score = float('-inf')
        best_moves = []

        # loop over child nodes
        for child_node in node.children.values():
            # define current player
            if child_node.board.player_turn == child_node.board.player_tiger: current_player = -1
            elif child_node.board.player_turn == child_node.board.player_goat: current_player = 1

            # get move score using UCB1 formula
            move_score = current_player * child_node.score / child_node.visits + exploration_value * math.sqrt(math.log(node.visits) / child_node.visits)

            # better move has been found
            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]

            # found as good move as already available
            elif move_score == best_score:
                best_moves.append(child_node)

        # return random best move
        return random.choice(best_moves)