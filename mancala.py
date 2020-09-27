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

        player_index = player - 1
        if not self.__board[player_index][cell] > 0:
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

    def is_game_over(self):
        for board_side in self.__board:
            if sum(board_side[:-1]) == 0:
                return True

        return False

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

    def print_board(self, player_pov):
        own_index = (PLAYER_1 - 1) if player_pov == PLAYER_1 else (PLAYER_2 - 1)
        opponent_index = (PLAYER_2 - 1) if player_pov == PLAYER_1 else (PLAYER_1 - 1)

        opponent_cells_str = ''
        for x in self.__board[opponent_index][:-1][::-1]:
            opponent_cells_str += f'{x} '

        opponent_goal = f'{self.__board[opponent_index][-1]}'

        own_cells_str = ''
        for x in self.__board[own_index][:-1]:
            own_cells_str += f'{x} '

        own_goal = f'{self.__board[own_index][-1]}'

        print(f'|--------P{opponent_index+1}-------|')
        print(f'|   {opponent_cells_str}  |')
        print(f'| {opponent_goal}             {own_goal} |')
        print(f'|   {own_cells_str}  |')
        print(f'|--------P{own_index+1}-------|')


class Player:
    def __init__(self, player_id):
        self.player_id = player_id

    def make_move(self, board):
        raise NotImplementedError('method `make_move` must be implemented')

# should get valid input options from board or game, should not know them itself
class TextPlayer(Player):
    def make_move(self, board):
        print(f"Player {self.player_id}'s turn")
        print()
        board.print_board(self.player_id)

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


class Game:
    def __init__(self, p1=None, p2=None):
        if p1 is None:
            self.p1 = TextPlayer(player_id=PLAYER_1)
        if p2 is None:
            self.p2 = TextPlayer(player_id=PLAYER_2)

        self.curr_turn = self.p1.player_id

        self.board = Board()

        self.__is_game_over = False

    def is_game_over(self):
        return self.__is_game_over

    def finalize_game(self):
        self.board.roundup_beads()

    def next_turn(self):
        turn_over = False
        another_turn = False

        if self.p1.player_id == self.curr_turn:
            while not turn_over:
                cell = self.p1.make_move(self.board)

                try:
                    another_turn = self.board.move(1, cell)
                    turn_over = True
                except InvalidMove as e:
                    print(e)
                    print('Make another move')
                    print()
        else:
            while not turn_over:
                cell = self.p2.make_move(self.board)

                try:
                    another_turn = self.board.move(2, cell)
                    turn_over = True
                except InvalidMove as e:
                    print(e)
                    print('Make another move')
                    print()

        self.__is_game_over = self.board.is_game_over()

        if another_turn and not self.is_game_over():
            print('Bonus turn, go again')
            print()
        else:
            self.curr_turn = PLAYER_2 if self.curr_turn == PLAYER_1 else PLAYER_1

    def results(self):
        return {'p1_score': self.board.p1_score(),
                'p2_score': self.board.p2_score()}


def play_game(config):
    game = Game()

    while not game.is_game_over():
        game.next_turn()

    game.finalize_game()
    results = game.results()

    print('game over! results:')
    print(results)


def config_prompt():
    # prompt for and collect optional input
    return {}


if __name__ == '__main__':
    config = config_prompt()
    play_game(config)
