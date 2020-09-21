GOAL_INDEX = 6
PLAYER_1 = 1
PLAYER_2 = 2


class InvalidMove(Exception):
    pass


class Board:
    def __init__(self):
        self.__board = [[4, 4, 4, 4, 4, 4, 0],
                        [4, 4, 4, 4, 4, 4, 0]]

    def p1_score(self):
        return self.__board[0][-1]

    def p2_score(self):
        return self.__board[1][-1]

    def __validate_move(self, player, cell):
        if not PLAYER_1 <= player <= PLAYER_2:
            raise InvalidMove('Invalid player: valid options are 1, 2')

        if not 0 <= cell <= GOAL_INDEX - 1:
            raise InvalidMove(f'Invalid cell: cell value must be one of 0 - {GOAL_INDEX - 1}')

        if not self.__board[player][cell] > 0:
            raise InvalidMove('Cell must hold at least one bead')

    # check the "move again when the game is over" case
    def move(self, player, cell):
        """
        Process the given move on the gameboard
        :param player: 1 for player one, 2 for player two
        :param cell: cell index, 0 - 6
        :return: True if player gets another turn, else False
        """
        self.__validate_move(player, cell)

        player_index = player - 1
        bead_count = self.__board[player_index][cell]
        self.__board[player_index][cell] = 0

        curr_side = player_index
        curr_cell = cell
        on_goal_cell = False
        while bead_count:
            curr_cell += 1

            on_goal_cell = curr_cell > GOAL_INDEX - 1
            if not (on_goal_cell and curr_cell != player_index):
                self.__board[curr_side][curr_cell] += 1
                bead_count -= 1

                # check for special rules
                if bead_count == 0:
                    # if last stone put in empty pit on player's turn
                    if curr_side == player_index and not on_goal_cell and self.__board[curr_side][curr_cell] == 1:
                        opponent_side = 1 if player_index == 0 else 0
                        bounty = self.__board[opponent_side][curr_cell]
                        self.__board[opponent_side][curr_cell] = 0

                        bounty += 1
                        self.__board[curr_side][curr_cell] = 0

                        self.__board[player_index][GOAL_INDEX] += bounty
                    # last stone put in goal, get another turn
                    elif on_goal_cell and curr_cell == player_index:
                        return True

            # switch side of board
            if on_goal_cell:
                curr_side = 1 if player_index == 0 else 0
                curr_cell = -1  # 0 when incremented by next iteration

        return False

    def is_won(self):
        for board_side in self.__board:
            if sum(board_side[:-1]) == 0:
                return True

        return False

    def get_board(self):
        return self.__board

    def print_board(self, player_pov):
        opponent_side = PLAYER_2 if player_pov == PLAYER_1 else PLAYER_1
        top_str =
        top_goal = ''
        bot_str = ''
        bot_goal = ''

        print('|-----------------|')
        print(f'|   {top_str}  |')
        print(f'| {top_goal}             {bot_goal}   ')
        print(f'|   {bot_str}  |')
        print('|-----------------|')


class Player:
    def __init__(self, player_id):
        self.player_id = player_id

    def make_move(self, board):
        raise NotImplementedError('method `make_move` must be implemented')


class TextPlayer(Player):
    def make_move(self, board):
        board.print_board()

        cell = input(f'Select a pit to move: <0 - {GOAL_INDEX - 1}>')

        valid_input = False
        while not valid_input:
            try:
                cell = int(cell)
                valid_input = True
            except ValueError:
                print(f'Invalid input, must be an integer <0 - {GOAL_INDEX - 1}>')
                valid_input = False

        return cell

class Game:
    def __init__(self, p1=None, p2=None):
        if p1 is None:
            self.p1 = Player(player_id=PLAYER_1)
        if p2 is None:
            self.p2 = Player(player_id=PLAYER_2)

        self.curr_turn = p1.player_id

        self.board = Board()

    def is_won(self):
        return self.board.is_won()

    def next_turn(self):
        if self.p1 is self.curr_turn:
            cell = self.p1.make_move(self.board)
            while self.board.move(1, cell):
                cell = self.p1.make_move(self.board)
        else:
            cell = self.p2.make_move(self.board)
            while self.board.move(2, cell):
                cell = self.p2.make_move(self.board)

        self.curr_turn = PLAYER_2 if self.curr_turn == PLAYER_1 else PLAYER_1

    def results(self):
        return {'p1_score': self.board.p1_score(),
                'p2_score': self.board.p2_score()}


def play_game(config):
    game = Game()

    while not game.is_won():
        game.next_turn()

    results = game.results()

    print('game over! results:')
    print(results)


def config_prompt():
    # prompt for and collect optional input
    return {}


if __name__ == '__main__':
    config = config_prompt()
    play_game(config)
