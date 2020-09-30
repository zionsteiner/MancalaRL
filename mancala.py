import copy
import sys
from enum import Enum, auto
import time

GOAL_INDEX = 6
TIE = -1

PLAYER1 = 1
PLAYER2 = 2


# Options
class Opponent(Enum):
    HUMAN = auto()
    MINIMAX = auto()
    # MONTECARLO = auto()
    # RL = auto()


class InvalidMove(Exception):
    pass


class Player:
    def __init__(self, player_id):
        self.player_id = player_id

    def make_move(self, board):
        raise NotImplementedError('method `make_move` must be implemented')


# should get valid input options from board or game, should not know them itself
class TextPlayer(Player):
    def make_move(self, board):
        cell = input(f'Select a pit to move: <0 - {GOAL_INDEX - 1}>')
        print()

        valid_input = False
        while not valid_input:
            try:
                cell = int(cell)
                valid_input = True
            except ValueError:
                print(f'Invalid input, must be an integer <0 - {GOAL_INDEX - 1}>')
                print()
                cell = input(f'Select a pit to move: <0 - {GOAL_INDEX - 1}>')
                print()

        return cell


class MinimaxPlayer(Player):
    def __init__(self, player_id, depth=4):
        super().__init__(player_id)
        self.board = None
        self.MAX_PLAYER = PLAYER1
        self.MIN_PLAYER = PLAYER2
        self.depth = depth

    def make_move(self, board):
        self.board = copy.deepcopy(board)

        start = time.time()
        _, cell = self.min(self.depth, -100, 100)
        end = time.time()

        print(f'Eval time: {end-start}s')

        return cell

    def max(self, depth, alpha, beta):
        max_score = -sys.maxsize

        cell_index = None

        winner = self.is_game_over()

        score_diff = self.get_p1_score() - self.get_p2_score()
        if winner == PLAYER1 or winner == PLAYER2:
            return (score_diff, 0)
        elif winner == TIE:
            assert score_diff == 0
            return (score_diff, 0)

        if depth == 0:
            return score_diff, 0

        # Find best move
        for i, cell in enumerate(self.board[self.MAX_PLAYER - 1][:GOAL_INDEX]):
            if cell > 0:
                prev_board_state = copy.deepcopy(self.board)

                if self.move(self.MAX_PLAYER, i):
                    child_score_diff, child_cell_index = self.max(depth-1, alpha, beta)
                else:
                    child_score_diff, child_cell_index = self.min(depth-1, alpha, beta)

                if child_score_diff > max_score:
                    max_score = child_score_diff
                    cell_index = i

                self.board = prev_board_state

                if max_score >= beta:
                    return (max_score, cell_index)
                if max_score > alpha:
                    alpha = max_score

        return max_score, cell_index

    def min(self, depth, alpha, beta):
        min_score = sys.maxsize

        cell_index = None

        winner = self.is_game_over()

        score_diff = self.get_p1_score() - self.get_p2_score()
        if winner == PLAYER1 or winner == PLAYER2:
            return (score_diff, 0)
        elif winner == TIE:
            return (0, 0)

        if depth == 0:
            return score_diff, 0

        # find best move
        for i, bead_count in enumerate(self.board[self.MIN_PLAYER - 1][:GOAL_INDEX]):
            if bead_count > 0:
                prev_board_state = copy.deepcopy(self.board)

                if self.move(self.MIN_PLAYER, i):
                    child_score_diff, child_cell_index = self.min(depth-1, alpha, beta)
                else:
                    child_score_diff, child_cell_index = self.max(depth-1, alpha, beta)

                if child_score_diff < min_score:
                    min_score = child_score_diff
                    cell_index = i

                self.board = prev_board_state

                if min_score <= alpha:
                    return (min_score, cell_index)
                if min_score < beta:
                    beta = min_score

        return min_score, cell_index

    def move(self, player, cell):
        """
        Process the given move on the gameboard
        :param player: 1 for player one, 2 for player two
        :param cell: cell index, 0 - 6
        :return: True if player gets another turn, else False
        """
        player_index = player - 1
        bead_count = self.board[player_index][cell]
        self.board[player_index][cell] = 0

        curr_side = player_index
        curr_cell = cell
        another_turn = False
        while bead_count:
            curr_cell += 1

            on_goal_cell = curr_cell == GOAL_INDEX
            if not (on_goal_cell and curr_side != player_index):
                self.board[curr_side][curr_cell] += 1
                bead_count -= 1

                # check for special rules
                if bead_count == 0:
                    # if last stone put in empty pit on player's turn
                    if curr_side == player_index and not on_goal_cell and self.board[curr_side][curr_cell] == 1:
                        opponent_side = 1 if player_index == 0 else 0
                        opponent_cell_index = len(self.board[opponent_side]) - 1 - 1 - curr_cell
                        bounty = self.board[opponent_side][opponent_cell_index]
                        self.board[opponent_side][opponent_cell_index] = 0

                        bounty += 1
                        self.board[curr_side][curr_cell] = 0

                        self.board[player_index][GOAL_INDEX] += bounty
                    # last stone put in goal, get another turn
                    elif on_goal_cell and curr_side == player_index:
                        another_turn = True

            # switch side of board
            if on_goal_cell:
                curr_side = 1 if player_index == 0 else 0
                curr_cell = -1  # 0 when incremented by next iteration

        return True if another_turn else False

    def roundup_beads(self):
        for side in self.board:
            bead_sum = 0
            for cell_count in side[:-1]:
                bead_sum += cell_count
            side[-1] += bead_sum

    def get_p1_score(self):
        return self.board[PLAYER1 - 1][GOAL_INDEX]

    def get_p2_score(self):
        return self.board[PLAYER2 - 1][GOAL_INDEX]

    def is_game_over(self):
        for i, board_side in enumerate(self.board):
            if sum(board_side[:-1]) == 0:
                self.roundup_beads()

                p1_score = self.get_p1_score()
                p2_score = self.get_p2_score()
                if p1_score > p2_score:
                    return PLAYER1
                elif p1_score < p2_score:
                    return PLAYER2
                else:
                    return TIE

        return None


class Game:
    def __init__(self, config=None):
        self.p1 = TextPlayer(player_id=PLAYER1)

        # Defaults
        if not config:
            config = {'opponent': Opponent.HUMAN}

        if config['opponent'] == Opponent.HUMAN:
            self.p2 = TextPlayer(player_id=PLAYER2)
        elif config['opponent'] == Opponent.MINIMAX:
            self.p2 = MinimaxPlayer(player_id=PLAYER2)

        self.curr_turn = self.p1.player_id

        self.__board = [[4, 4, 4, 4, 4, 4, 0],
                        [4, 4, 4, 4, 4, 4, 0]]

        self.__is_game_over = False

    def p1_score(self):
        return self.__board[0][-1]

    def p2_score(self):
        return self.__board[1][-1]

    def __validate_move(self, player, cell):
        if not PLAYER1 <= player <= PLAYER2:
            raise InvalidMove('Invalid player: valid options are 1, 2')

        if not 0 <= cell <= GOAL_INDEX - 1:
            raise InvalidMove(f'Invalid cell: cell value must be one of 0 - {GOAL_INDEX - 1}')

        player_index = player - 1
        if not self.__board[player_index][cell] > 0:
            raise InvalidMove('Cell must hold at least one bead')

    # check the "move again when the game is over" case
    def move(self, player, cell):
        """
        Process the given move on the gameboard
        :param player: 1 for player one, 2 for player two
        :param cell: cell index, 0 - 5
        :return: True if player gets another turn, else False
        """
        self.__validate_move(player, cell)

        player_index = player - 1
        bead_count = self.__board[player_index][cell]
        self.__board[player_index][cell] = 0

        curr_side = player_index
        curr_cell = cell
        another_turn = False
        while bead_count:
            curr_cell += 1

            on_goal_cell = curr_cell == GOAL_INDEX
            if not (on_goal_cell and curr_side != player_index):
                self.__board[curr_side][curr_cell] += 1
                bead_count -= 1

                # check for special rules
                if bead_count == 0:
                    # if last stone put in empty pit on player's turn
                    if curr_side == player_index and not on_goal_cell and self.__board[curr_side][curr_cell] == 1:
                        opponent_side = 1 if player_index == 0 else 0
                        opponent_cell_index = len(self.__board[opponent_side]) - 1 - 1 - curr_cell
                        bounty = self.__board[opponent_side][opponent_cell_index]
                        self.__board[opponent_side][opponent_cell_index] = 0

                        bounty += 1
                        self.__board[curr_side][curr_cell] = 0

                        self.__board[player_index][GOAL_INDEX] += bounty
                        print(f'Won {bounty} bead bounty')
                        print()
                    # last stone put in goal, get another turn
                    elif on_goal_cell and curr_side == player_index:
                        another_turn = True

            # switch side of board
            if on_goal_cell:
                curr_side = 1 if player_index == 0 else 0
                curr_cell = -1  # 0 when incremented by next iteration

        print('Result:')
        print()
        self.print_board(player)
        print()

        return True if another_turn else False

    def calculate_is_game_over(self):
        for board_side in self.__board:
            if sum(board_side[:-1]) == 0:
                self.__is_game_over = True

    def is_game_over(self):
        return self.__is_game_over

    def roundup_beads(self):
        for side in self.__board:
            bead_sum = 0
            for cell_count in side[:-1]:
                bead_sum += cell_count
            side[-1] += bead_sum

        print('Final result:')
        self.print_board(1)

    def get_board(self):
        return self.__board

    def set_board(self, board):
        self.__board = board

    def print_board(self, player_pov):
        own_index = (PLAYER1 - 1) if player_pov == PLAYER1 else (PLAYER2 - 1)
        opponent_index = (PLAYER2 - 1) if player_pov == PLAYER1 else (PLAYER1 - 1)

        opponent_cells_str = ''
        for x in self.__board[opponent_index][:-1][::-1]:
            opponent_cells_str += f'{x} '

        opponent_goal = f'{self.__board[opponent_index][-1]}'

        own_cells_str = ''
        for x in self.__board[own_index][:-1]:
            own_cells_str += f'{x} '

        own_goal = f'{self.__board[own_index][-1]}'

        print(f'|--------P{opponent_index + 1}-------|')
        print(f'|   {opponent_cells_str}  |')
        print(f'| {opponent_goal}             {own_goal} |')
        print(f'|   {own_cells_str}  |')
        print(f'|--------P{own_index + 1}-------|')

    def next_turn(self):
        turn_over = False
        another_turn = False

        while not turn_over:
            print(f"Player {self.curr_turn}'s turn")
            print()
            self.print_board(self.curr_turn)

            if self.curr_turn == self.p1.player_id:
                cell = self.p1.make_move(self.__board)
            else:
                cell = self.p2.make_move(self.__board)

            try:
                another_turn = self.move(self.curr_turn, cell)
                turn_over = True
            except InvalidMove as e:
                print(e)
                print('Make another move')
                print()

        self.calculate_is_game_over()
        if another_turn and not self.is_game_over():
            print('Bonus turn, go again')
            print()
        else:
            self.curr_turn = PLAYER2 if self.curr_turn == PLAYER1 else PLAYER1

    def results(self):
        return {'p1_score': self.p1_score(),
                'p2_score': self.p2_score()}


def play_game(config):
    game = Game(config)

    while not game.is_game_over():
        game.next_turn()

    game.roundup_beads()
    results = game.results()

    print('game over! results:')
    print(results)


def config_prompt():
    # Prompt for and collect optional input
    print('Options')
    print('--------')
    print('Play against: ')
    print('1. A human player')
    print('2. Minimax')
    # Add other algorithms here

    is_valid_choice = False

    choice = None
    while not is_valid_choice:
        choice = int(input('Make a selection'))
        if 1 <= choice <= len(Opponent):
            is_valid_choice = True
        else:
            print('Invalid choice\n')

    opponent = Opponent(choice)

    return {'opponent': opponent}


if __name__ == '__main__':
    config = config_prompt()
    play_game(config)
