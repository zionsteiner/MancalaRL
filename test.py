import unittest
from mancala import Game, PLAYER1, PLAYER2, GOAL_INDEX


class TestMoveLogic(unittest.TestCase):
    def test_regular_player1_cell0(self):
        game = Game()
        game.move(PLAYER1, 0)

        board = game.get_board()

        exp_board = [[0, 5, 5, 5, 5, 4, 0],
                     [4, 4, 4, 4, 4, 4, 0]]

        self.assertListEqual(board, exp_board)

    def test_regular_player2_cell0(self):
        game = Game()
        game.move(PLAYER2, 0)

        board = game.get_board()

        exp_board = [[4, 4, 4, 4, 4, 4, 0],
                     [0, 5, 5, 5, 5, 4, 0]]

        self.assertListEqual(board, exp_board)

    def test_regular_player1_cell5(self):
        game = Game()
        game.move(PLAYER1, 5)

        board = game.get_board()

        exp_board = [[4, 4, 4, 4, 4, 0, 1],
                     [5, 5, 5, 4, 4, 4, 0]]

        self.assertListEqual(board, exp_board)

    def test_another_turn(self):
        game = Game()
        another_turn = game.move(PLAYER1, 2)

        self.assertTrue(another_turn)

    def test_bounty(self):
        game = Game()
        game.move(PLAYER1, 5)
        game.move(PLAYER2, 0)
        game.move(PLAYER1, 1)

        board = game.get_board()
        player1_index = PLAYER1 - 1
        p1_score = board[player1_index][GOAL_INDEX]

        self.assertEqual(p1_score, 2)

    def test_game_over(self):
        game = Game()
        game.set_board([[0, 0, 0, 0, 0, 0, 25],
                        [0, 0, 0, 0, 0, 0, 23]])

        game.calculate_is_game_over()
        self.assertTrue(game.is_game_over())

if __name__ == '__main__':
    unittest.main()
