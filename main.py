# CS1571 -- last updated 10/1/2011
# El Juego de las Amazonas in Python 3.2
# For more information about the game itself, please refer to:
#      http://en.wikipedia.org/wiki/Game_of_the_Amazons
#
# This file provides some basic support for you to develop your automatic Amazons player.
# It gives everyone a common starting point, and it will make it easier for us to set your players
# to play against each other. Therefore, you should NOT make any changes to the provided code unless
# directed otherwise. If you find a bug, please email me.

# This implementation includes two class definitions, some utility functions,
# and a function for a human player ("human").
# The two classes are:
# - The Amazons class: the main game controller
# - The Board class: contains info about the current board configuration.
#   It is through the Board class that the game controller
#   passes information to your player function.
# More details about these two classes are provided in their class definitions

# Your part: Write an automatic player function for the Game of the Amazons.
# * your automatic player MUST have your email userID as its function name (e.g., reh23)
# * The main game controller will call your function at each turn with
#   a copy of the current board as the input argument.
# * Your function's return value should be your next move.
#   It must be expressed as a tuple of three tuples: e.g., ((0, 3), (1,3), (8,3))
#    - the start location of the queen you want to move (in row, column)
#    - the queen's move-to location,
#    - the arrow's landing location.
#   If you have no valid moves left, the function should return False.

# As usual, we won't spend much time on the user interface.
# Updates of the game board are drawn with simple ascii characters.
#
# - Below is a standard initial board configuration:
#   * The board is a 10x10 grid. (It is advisable to use a smaller board during development/debugging)
#   * Each side has 4 queens. The white queens are represented as Q's; the black queens are represented as q's
#
#      a b c d e f g h i j
#   9  . . . q . . q . . .
#   8  . . . . . . . . . .
#   7  . . . . . . . . . .
#   6  q . . . . . . . . q
#   5  . . . . . . . . . .
#   4  . . . . . . . . . .
#   3  Q . . . . . . . . Q
#   2  . . . . . . . . . .
#   1  . . . . . . . . . .
#   0  . . . Q . . Q . . .
#
# - During a player's turn, one of the player's queens must be moved, then an arrow must be shot from the moved queen.
# - the arrow is represented as 'x'
# - neither the queens nor their arrows can move past another queen or an arrow
#
# - The objective of the game is to minimze your opponent's queens' movement.
# - The game technically ends when one side's queens have no more legal moves,
#   but the game practically ends when the queens from the two sides have been
#   segregated. We will just count up the territories owned by each side and
#   the side with the larger territory will be declared the winner

############################################

import copy
import re
import sys
import time


# The Amazons class controls the flow of the game.
# Its data include:
# * size -- size of board: assume it's <= 10
# * time_limit -- # of seconds a mchine is allowed to take (<30)
# * playerW -- name of the player function who'll play white
# * playerB -- name of the player function who'll play black
# * wqs -- initial positions of the white queens
# * bqs -- initial positions of the black queens
# * board -- current board configuration (see class def for Board)
# Its main functions are:
# * play: the main control loop of a game, which would:
#   - turn taking management: calls each auto player's minimax function (or "human")
#   - check for the validity of the player's move:
#     an auto player loses a turn if an invalid move is returned or if it didn't return a move in the alloted time
#   - check for end game condition
#   - declare the winner
# * update: this function tries out the move on a temporary board.
#   if the move is valid, the real board will be updated.
# * end_turn: just get the score from the board class


class Amazons:
    def __init__(self, fname):
        fin = open(fname, 'r')
        self.time_limit = int(fin.readline())
        self.size = int(fin.readline())
        self.playerW = fin.readline().strip()
        self.wqs = tuple(map(ld2rc, fin.readline().split()))
        self.playerB = fin.readline().strip()
        self.bqs = tuple(map(ld2rc, fin.readline().split()))
        self.board = Board(self.size, self.wqs, self.bqs)

    def update(self, move):
        try:
            (src, dst, adst) = move
        except:
            return False

        # try out the move on a temp board
        tmp_board = copy.deepcopy(self.board)
        if tmp_board.valid_path(src, dst):
            tmp_board.move_queen(src, dst)
            if tmp_board.valid_path(dst, adst):
                # the move is good. make the real board point to it
                tmp_board.shoot_arrow(adst)
                del self.board
                self.board = tmp_board
                return True
        # move failed.
        del tmp_board
        return False

    def end_turn(self):
        return self.board.end_turn()

    def play(self):
        bPlay = True
        wscore = bscore = 0
        while (bPlay):
            for p in [self.playerW, self.playerB]:
                # send player a copy of the current board
                tmp_board = copy.deepcopy(self.board)
                tstart = time.clock()
                tmp_board.time_limit = tstart + self.time_limit
                move = eval("%s(tmp_board)" % p)
                tstop = time.clock()
                del tmp_board

                print(p, ": move:", move, "time:", tstop - tstart, "seconds")
                if not move:
                    # if move == False --> player resigned
                    if self.board.bWhite:
                        (wscore, bscore) = (-1, 0)
                    else:
                        (wscore, bscore) = (0, -1)
                    bPlay = False
                    break

                # only keep clock for auto players
                if p != "human" and (tstop - tstart) > self.time_limit:
                    print(p, ": took too long -- lost a turn")
                elif not self.update(move):
                    print(p, ": invalid move", move, " lost a turn")

                # at the end of the turn, check whether the game ended
                # and update whether white is playing next
                (wscore, bscore) = self.end_turn()
                if wscore and bscore:
                    continue
                else:
                    bPlay = False
                    break
        # print final board
        self.board.print_board()
        if wscore == -1:
            print(self.playerW, "(white) resigned.", self.playerB, "(black) wins")
        elif bscore == -1:
            print(self.playerB, "(black) resigned.", self.playerW, "(white) wins")
        elif not wscore:
            print(self.playerB, "(black) wins by a margin of", bscore)
        else:
            print(self.playerW, "(white) wins by a margin of", wscore)


##############################################
# The Board class stores basic information about the game configuration.
#
# NOTE: The amount of info stored in this class is kept to a minimal. This
# is on purpose. This is just set up as a way for the game controller to
# pass information to your automatic player. Although you cannot change
# the definition of the Board class, you are not constrained to use the
# Board class as your main state reprsentation. You can define your own
# State class and copy/transform from Board the info you need.

# The Board class contains the following data:
#  * config: the board configuration represented as a list of lists.
#    The assumed convention is (row, column) so config[0][1] = "b0"
#  * bWhite: binary indicator -- True if it's white's turn to play
#  * time_limit: deadline by which an auto move has to be made
# The Board class supports the following methods:
#  * print_board: prints the current board configuration
#  * valid_path: takes two location tuples (in row, column format) and returns
#    whether the end points describe a valid path (for either the queen or the arrow)
#  * move_queen: takes two location tuples (in row, column format)
#    and updates the board configuration to reflect the queen moving
#    from src to dst
#  * shoot_arrow: takes one location tuple (in row, column format)
#    and updates the board configuration to include the shot arrow
#  * end_turn: This function does some end of turn accounting: update whose
#    turn it is and determine whether the game ended
#  * count_areas: This is a helper function for end_turn. It figures out
#    whether we can end the game. This function has a known bug: for special
#    small "defective regions" -- for example:
#
#          x x x
#        x x Q x x
#        x . x . x
#        x x x x x
#
#    the floodfill method will count the number of territory as 2
#    but in fact, if the queen moves to one side, it must give up the space
#    on the other side. Theoretically, it has been shown that the problem of
#    determining the number of moves for a given territory is NP-complete
#    (Muller and Tegos, 2002). For practical uses of declarining a winner,
#    the area counting program should be sufficient. We can always have
#    your players fight to the bitter end if the margin of win is close.
#
class Board:
    def __init__(self, size, wqs, bqs):
        self.bWhite = True
        self.time_limit = None
        self.config = [['.' for c in range(size)] for r in range(size)]
        for (r, c) in wqs:
            self.config[r][c] = 'Q'
        for (r, c) in bqs:
            self.config[r][c] = 'q'

    def print_board(self):
        size = len(self.config)
        print("     Black")
        tmp = "  " + " ".join(map(lambda x: chr(x + ord('a')), range(size)))
        print(tmp)
        for r in range(size - 1, -1, -1):
            print(r, " ".join(self.config[r]), r)
        print(tmp)
        print("     White")

    def valid_path(self, src, dst):
        (srcr, srcc) = src
        (dstr, dstc) = dst

        srcstr = rc2ld(src)
        dststr = rc2ld(dst)

        symbol = self.config[srcr][srcc]
        if (self.bWhite and symbol != 'Q') or (not self.bWhite and symbol != 'q'):
            print("invalid move: cannot find queen at src:", srcstr)
            return False

        h = dstr - srcr
        w = dstc - srcc
        if h and w and abs(h / w) != 1:
            print("invalid move: not a straight line")
            return False
        if not h and not w:
            print("invalid move: same star-end")
            return False

        if not h:
            op = (0, int(w / abs(w)))
        elif not w:
            op = (int(h / abs(h)), 0)
        else:
            op = (int(h / abs(h)), int(w / abs(w)))

        (r, c) = (srcr, srcc)
        while (r, c) != (dstr, dstc):
            (r, c) = (r + op[0], c + op[1])
            if (self.config[r][c] != '.'):
                print("invalid move: the path is not cleared between", srcstr, dststr)
                return False
        return True

    def move_queen(self, src, dst):
        self.config[dst[0]][dst[1]] = self.config[src[0]][src[1]]
        self.config[src[0]][src[1]] = '.'

    def shoot_arrow(self, dst):
        self.config[dst[0]][dst[1]] = 'x'

    def end_turn(self):
        # count up each side's territories
        (w, b) = self.count_areas()
        # if none of the queens of either side can move, the player who just
        # played wins, since that player claimed the last free space.
        if b == w and b == 0:
            if self.bWhite:
                w = 1
            else:
                b = 1
        # switch player
        self.bWhite = not self.bWhite
        return (w, b)

    # adapted from standard floodfill method to count each player's territories
    # - if a walled-off area with queens from one side belongs to that side
    # - a walled-off area with queens from both side is neutral
    # - a walled-off area w/ no queens is deadspace
    def count_areas(self):
        # replace all blanks with Q/q/n/-
        def fill_area(replace):
            count = 0
            for r in range(size):
                for c in range(size):
                    if status[r][c] == '.':
                        count += 1
                        status[r][c] = replace
            return count

        # find all blank cells connected to the seed blank at (seedr, seedc)
        def proc_area(seedr, seedc):
            symbols = {}  # keeps track of types of symbols encountered in this region
            connected = [(seedr, seedc)]  # a stack for df traversal on the grid
            while connected:
                (r, c) = connected.pop()
                status[r][c] = '.'
                for ops in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    (nr, nc) = (r + ops[0], c + ops[1])
                    if nr < 0 or nr >= size or nc < 0 or nc >= size:
                        continue
                    # if it's a new blank, need to process it; also add to seen
                    if self.config[nr][nc] == '.' and status[nr][nc] == '?':
                        status[nr][nc] = '.'
                        connected.append((nr, nc))
                    # if it's a queen or an arrow; just mark as seen
                    elif self.config[nr][nc] != '.':
                        status[nr][nc] = 'x'
                        symbols[self.config[nr][nc]] = 1

            if 'Q' in symbols and not 'q' in symbols:  # area belongs to white
                return (fill_area('Q'), 0, 0)
            elif 'q' in symbols and not 'Q' in symbols:  # area belongs to black
                return (0, fill_area('q'), 0)
            elif 'q' in symbols and 'Q' in symbols:  # area is neutral
                return (0, 0, fill_area('n'))
            else:  # deadspace -- still have to fill but don't return its area value
                fill_area('-')
                return (0, 0, 0)

        size = len(self.config)
        # data structure for keeping track of seen locations
        status = [['?' for i in range(size)] for j in range(size)]
        wtot = btot = ntot = 0
        for r in range(size):
            for c in range(size):
                # if it's an empty space and we haven't seen it before, process it
                if self.config[r][c] == '.' and status[r][c] == '?':
                    (w, b, n) = proc_area(r, c)
                    wtot += w
                    btot += b
                    ntot += n
                # if it's anything else, but we haven't seen it before, just mark it as seen and move on
                elif status[r][c] == '?':
                    status[r][c] = 'x'

        if ntot == 0:  # no neutral space left -- should end game
            if wtot > btot:
                return (wtot - btot, 0)
            else:
                return (0, btot - wtot)
        else:
            return (wtot + ntot, btot + ntot)


# utility functions:
# ld2rc -- takes a string of the form, letter-digit (e.g., "a3")
# and returns a tuple in (row, column): (3,0)
# rc2ld -- takes a tuple of the form (row, column) -- e.g., (3,0)
# and returns a string of the form, letter-digit (e.g., "a3")

def ld2rc(raw_loc):
    return (int(raw_loc[1]), ord(raw_loc[0]) - ord('a'))


def rc2ld(tup_loc):
    return chr(tup_loc[1] + ord('a')) + str(tup_loc[0])


# get next move from a human player
# The possible return values are the same as an automatic player:
# Usually, the next move should be returned. It must be specified in the following format:
# [(queen-start-row, queen-start-col), (queen-end-row,queen-end-col), (arrow-end-row, arrow-end-col)]
# To resign from the game, return False

def human(board):
    board.print_board()

    if board.bWhite:
        print("You're playing White (Q)")
    else:
        print("You're playing Black (q)")

    print("Options:")
    print('* To move, type "<loc-from> <loc-to>" (e.g., "a3-d3")')
    print('* To resign, type "<return>"')
    while True:  # loop to get valid queen move from human
        while True:  # loop to check for valid input syntax first
            raw_move = input("Input please: ").split()
            if not raw_move:  # human resigned
                return False
            # if they typed "a3-d3"
            elif re.match("^[a-j][0-9]\-[a-j][0-9]$", raw_move[0]):
                break
            else:
                print(str(raw_move), "is not a valid input format")
        (src, dst) = map(ld2rc, raw_move[0].split('-'))
        if board.valid_path(src, dst):
            board.move_queen(src, dst)
            break

    board.print_board()
    print("Options:")
    print('* To shoot, type "<loc-to>" (e.g., "h3")')
    print('* To resign, type "<return>"')
    while True:  # loop to get valid move from human
        while True:  # loop to check for valid syntax first
            raw_move = input("Input please: ")
            if not raw_move:
                return False
            if re.match("^[a-j][0-9]$", raw_move):
                break
            else:
                print(raw_move, "is not a valid input")
        adst = ld2rc(raw_move)
        if board.valid_path(dst, adst):
            return (src, dst, adst)


###################### Your code between these two comment lines ####################################
import os
import random
import numpy as np
import pickle
from math import log, sqrt


class ejw45_Board:
    def __init__(self, board):
        self.board = np.array(board)
        self.player_symbols = {True: 'Q', False: 'q'}

    def moves(self, player):
        """
        :param is_white: if the player in question is white or black
        :return: a set of all possible moves in the form of (queen_start, queen_end, arrow)
        """
        boards = []
        moves = []

        queen_moves = self.queen_moves(player.white)

        for queen_move in queen_moves:
            source, destination = queen_move
            moved_board = self.move_queen(self.board, source, destination)

            arrows = self.arrow_moves(moved_board, destination)

            for arrow in arrows:
                moves.append((source, destination, arrow))
                boards.append(self.shoot_arrow(moved_board.board, arrow))

        return boards, moves

    def get_spot(self, start_position, direction):
        height, width = self.board.shape
        r, c = start_position

        r -= direction.count('n')
        r += direction.count('s')
        c += direction.count('e')
        c -= direction.count('w')

        if 0 <= r < height and 0 <= c < width:
            return self.board[r, c], (r, c)
        else:
            return 'X', (r, c)

    def position_moves(self, spot):
        directions = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
        moves = []

        for direction in directions:
            location = spot
            dir = direction

            obstruction = False

            while not obstruction:
                piece, new_spot = self.get_spot(location, dir)

                if piece == '.':
                    moves.append((spot, new_spot))
                    dir += direction
                else:
                    obstruction = True

        return moves

    def queen_moves(self, is_white):
        moves = []
        height, width = self.board.shape

        for r in range(height):
            for c in range(width):

                if self.board[r, c] == self.player_symbols[is_white]:
                    moves += self.position_moves((r, c))

        return moves

    def arrow_moves(self, board, queen_end):
        return [move[1] for move in board.position_moves(queen_end)]

    @staticmethod
    def move_queen(board, src, dst):
        copy = np.copy(board)
        copy[dst] = copy[src]
        copy[src] = '.'
        return ejw45_Board(copy)

    @staticmethod
    def shoot_arrow(board, dst):
        copy = np.copy(board)
        copy[dst] = 'x'
        return ejw45_Board(copy)

    def __eq__(x, y):
        return np.array_equal(x.board, y.board)

    def __hash__(self):
        return hash(str(self.board))


class MonteCarlo:
    class Player:
        def __init__(self, white):
            self.path = []
            self.white = white
            self.other_player = None

        def update(self, state):
            self.path.append(state)

        def clear(self):
            self.path = []

        def other(self):
            return self.other_player

    def __init__(self, training_iterations=0):

        self.start = ejw45_Board(np.array([['.', '.', '.', 'q', '.', '.', 'q', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['q', '.', '.', '.', '.', '.', '.', '.', '.', 'q'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['Q', '.', '.', '.', '.', '.', '.', '.', '.', 'Q'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                           ['.', '.', '.', 'Q', '.', '.', 'Q', '.', '.', '.']]))

        self.white_player = MonteCarlo.Player(True)
        self.black_player = MonteCarlo.Player(False)
        self.white_player.other_player = self.black_player
        self.black_player.other_player = self.white_player

        self.explored = dict()

        if os.path.isfile('ejw45_amazon.pickle'):
            print('reading in from file')
            with open('ejw45_amazon.pickle', 'rb') as handle:
                self.explored = pickle.load(handle)

        if training_iterations > 0:
            self.train(training_iterations)

    def train(self, iterations):
        while iterations > 0:
            self.simulate()
            iterations -= 1

            if iterations % 10 == 0:
                print('{}: {}'.format(iterations, len(self.explored)))
                self.write_to_file('ejw45_amazon.pickle')

    def write_to_file(self, path):
        with open(path, 'wb') as handle:
            pickle.dump(self.explored, handle)

    def select(self, current_state, player):

        max_state = None
        max_score = None

        child_boards, _ = current_state.moves(player)

        # Return the next unexplored node. If none exist, recurse on the best scoring child
        for child in child_boards:

            # If you've found an unexplored node
            if child not in self.explored:
                player.update(current_state)
                return current_state, player

            wins, plays = self.explored[child]
            if max_score is None or wins / plays > max_score:
                max_score = (wins / plays) + (1.4 * sqrt(log(plays) / plays))
                max_state = child

        player.update(max_state)

        return self.select(max_state, player.other())

    def expand(self, current_state, player):
        shuffled, _ = current_state.moves(player)
        random.shuffle(shuffled)
        for child in shuffled:
            if child not in self.explored:
                player.update(child)
                return child, player.other()

    def simulate(self):
        selected, player = self.select(self.start, self.white_player)
        expand, player = self.expand(selected, player)

        current = expand
        game_end = False

        loser = None
        winner = None

        while not game_end:
            boards, _ = current.moves(player)

            if not boards:
                loser = player
                winner = player.other()
                break

            current = random.choice(boards)
            player.update(current)

            player = player.other()

        for state in loser.path:
            if state in self.explored:
                wins, plays = self.explored[state]
            else:
                wins = plays = 0

            plays += 1

            self.explored[state] = (wins, plays)

        for state in winner.path:
            if state in self.explored:
                wins, plays = self.explored[state]
            else:
                wins = plays = 0

            wins += 1
            plays += 1
            self.explored[state] = (wins, plays)


ejw45_mc = MonteCarlo(100)


def ejw45_bot(board):
    is_white = board.bWhite

    board = ejw45_Board(np.array(board.config))
    player = MonteCarlo.Player(is_white)

    # Set a random move to be chosen if none of children boards are known
    boards, moves = board.moves(player)

    max_move = random.choice(moves)
    max_score = 0.0

    for index, board in enumerate(boards):
        move = moves[index]

        if board in ejw45_mc.explored:
            win_count, play_count = ejw45_mc.explored[board]
            score = float(win_count) / float(play_count)

            if score > max_score:
                max_score = score
                max_move = move

    return max_move


###################### Your code between these two comment lines ####################################

def main():
    if len(sys.argv) == 2:
        fname = sys.argv[1]
    else:
        fname = input("setup file name?")

    while True:
        game = Amazons(fname)
        game.play()


if __name__ == "__main__":
    main()
