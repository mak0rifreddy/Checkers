"""Unit tests for the Checkers game logic."""

import unittest
from constants import WHITE, BLACK
from piece import Piece
from board import Board, Move
from game import CheckersGame


class TestCheckersLogic(unittest.TestCase):
    def test_initial_board_setup(self):
        board = Board()
        black_count, black_kings = board.count_pieces(BLACK)
        white_count, white_kings = board.count_pieces(WHITE)

        self.assertEqual(black_count, 12)
        self.assertEqual(black_kings, 0)
        self.assertEqual(white_count, 12)
        self.assertEqual(white_kings, 0)

        # Check piece colors on dark squares
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    p = board.get_piece(r, c)
                    self.assertIsNotNone(p)
                    self.assertEqual(p.color, BLACK)
                else:
                    self.assertIsNone(board.get_piece(r, c))

        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    p = board.get_piece(r, c)
                    self.assertIsNotNone(p)
                    self.assertEqual(p.color, WHITE)
                else:
                    self.assertIsNone(board.get_piece(r, c))

    def test_simple_step_move(self):
        game = CheckersGame(starting_player=BLACK)
        # Select black piece at (2, 1) - valid step moves to (3, 0) and (3, 2)
        self.assertTrue(game.select_square(2, 1))
        self.assertEqual(len(game.valid_moves), 2)

        # Execute move to (3, 2)
        self.assertTrue(game.select_square(3, 2))
        self.assertIsNone(game.board.get_piece(2, 1))
        p = game.board.get_piece(3, 2)
        self.assertIsNotNone(p)
        self.assertEqual(p.color, BLACK)
        self.assertEqual(game.current_player, WHITE)

    def test_capture_jump(self):
        board = Board(init_pieces=False)
        # White piece at (4, 3), Black piece at (3, 2)
        board.set_piece(4, 3, Piece(WHITE, 4, 3))
        board.set_piece(3, 2, Piece(BLACK, 3, 2))

        game = CheckersGame(starting_player=WHITE)
        game.board = board

        # White piece at (4, 3) jumps over (3, 2) to (2, 1)
        jumps = board.get_piece_jumps(board.get_piece(4, 3))
        self.assertEqual(len(jumps), 1)
        self.assertEqual(jumps[0].to_pos, (2, 1))
        self.assertEqual(jumps[0].captured_pos, (3, 2))

        # Select and move
        game.select_square(4, 3)
        game.select_square(2, 1)

        # Black piece at (3, 2) should be removed
        self.assertIsNone(game.board.get_piece(3, 2))
        self.assertIsNotNone(game.board.get_piece(2, 1))
        self.assertEqual(game.board.get_piece(2, 1).color, WHITE)

    def test_king_promotion(self):
        board = Board(init_pieces=False)
        white_piece = Piece(WHITE, 1, 2)
        board.set_piece(1, 2, white_piece)

        game = CheckersGame(starting_player=WHITE)
        game.board = board

        game.select_square(1, 2)
        # Move to row 0 (promotion row)
        game.select_square(0, 1)

        promoted_piece = game.board.get_piece(0, 1)
        self.assertIsNotNone(promoted_piece)
        self.assertTrue(promoted_piece.is_king)

    def test_multi_jump_sequence(self):
        board = Board(init_pieces=False)
        # White piece at (6, 1)
        # Black pieces at (5, 2) and (3, 4)
        board.set_piece(6, 1, Piece(WHITE, 6, 1))
        board.set_piece(5, 2, Piece(BLACK, 5, 2))
        board.set_piece(3, 4, Piece(BLACK, 3, 4))

        game = CheckersGame(starting_player=WHITE)
        game.board = board

        # First jump: (6, 1) -> (4, 3) capturing (5, 2)
        game.select_square(6, 1)
        game.select_square(4, 3)

        # Should be in multi-jump mode, still WHITE's turn
        self.assertTrue(game.in_multi_jump)
        self.assertEqual(game.current_player, WHITE)
        self.assertIsNone(game.board.get_piece(5, 2))

        # Second jump: (4, 3) -> (2, 5) capturing (3, 4)
        game.select_square(2, 5)

        # Multi-jump complete, turn switches to BLACK
        self.assertFalse(game.in_multi_jump)
        self.assertEqual(game.current_player, BLACK)
        self.assertIsNone(game.board.get_piece(3, 4))
        self.assertIsNotNone(game.board.get_piece(2, 5))

    def test_undo_functionality(self):
        game = CheckersGame(starting_player=BLACK)
        game.select_square(2, 1)
        game.select_square(3, 2)

        self.assertEqual(game.current_player, WHITE)
        self.assertTrue(len(game.history) == 1)

        # Undo
        self.assertTrue(game.undo())
        self.assertEqual(game.current_player, BLACK)
        self.assertIsNotNone(game.board.get_piece(2, 1))
        self.assertIsNone(game.board.get_piece(3, 2))


if __name__ == "__main__":
    unittest.main()
