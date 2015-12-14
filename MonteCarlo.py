import os
import random
import numpy as np
import pickle


class Board:
    def __init__(self, board):
        self.board = board
        self.player_symbols = {True: 'Q', False: 'q'}

    def is_win(self):
        white = self.moves(True)
        black = self.moves(False)

        if len(white) == 0:
            return -1
        elif len(black) == 0:
            return 1

        return 0

    def moves(self, is_white=True):
        """
        :param is_white: if the player in question is white or black
        :return: a set of all possible moves in the form of (queen_start, queen_end, arrow)
        """
        boards = []

        queen_moves = self.queen_moves(is_white)

        for queen_move in queen_moves:
            source, destination = queen_move
            arrows = self.arrow_moves(destination)

            for arrow in arrows:
                boards.append(self.move_queen(source, destination).shoot_arrow(arrow))

        return boards

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

    def arrow_moves(self, queen_end):
        return [move[1] for move in self.position_moves(queen_end)]

    def move_queen(self, src, dst):
        copy = np.copy(self.board)
        copy[dst[0], dst[1]] = copy[src[0], src[1]]
        copy[src[0], src[1]] = '.'
        return Board(copy)

    def shoot_arrow(self, dst):
        copy = np.copy(self.board)
        copy[dst[0], dst[1]] = 'x'
        return Board(copy)

    def __hash__(self):
        return hash(self.board.data.tobytes())


class MonteCarlo:
    def __init__(self):

        self.start = Board(np.array([['.', '.', '.', 'q', '.', '.', 'q', '.', '.', '.'],
                                     ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                     ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                     ['q', '.', '.', '.', '.', '.', '.', '.', '.', 'q'],
                                     ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                     ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                     ['Q', '.', '.', '.', '.', '.', '.', '.', '.', 'Q'],
                                     ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                     ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                                     ['.', '.', '.', 'Q', '.', '.', 'Q', '.', '.', '.']]))
        self.frontier = [self.start]
        self.explored = dict()

    def select(self, current_state, path):

        max_state = None
        max_score = None

        for child in current_state.moves():
            if child not in self.explored:
                return child, path + [child]

            wins, plays = self.explored[child]

            if max_score is None or wins / plays > max_score:
                max_score = wins / plays

                max_state = child

        path = path + [current_state]
        return self.select(max_state, path), path

    def expand(self, current_state, path):
        shuffled = current_state.moves()
        random.shuffle(shuffled)
        for child in shuffled:
            if child not in self.explored:
                return child, path + [child]
        return None

    def simulate(self):
        selected, path = self.select(self.start, path=[])
        expand, path = self.expand(selected, path)

        current = expand

        is_win = False
        white_turn = True

        while not is_win:
            current = random.choice(current.moves(white_turn))

            game_state = current.is_win()
            is_win = game_state == 1 or game_state == -1

            path += [current]
            white_turn = not white_turn

        for state in path:

            if state in self.explored:
                wins, plays = self.explored[state]
            else:
                wins = plays = 0

            if current.is_win() == 1:
                wins += 1

            plays += 1

            self.explored[state] = (wins, plays)


def main():
    mc = MonteCarlo()

    if os.path.isfile('amazon.pickle'):
        print('reading in from file')
        with open('amazon.pickle', 'rb') as handle:
            mc.explored = pickle.load(handle)

    simulations = 0

    while True:

        mc.simulate()
        simulations += 1

        if simulations % 10 == 0:
            with open('amazon.pickle', 'wb') as handle:
                pickle.dump(mc.explored, handle)

        print(len(mc.explored))

if __name__ == '__main__':
    main()
