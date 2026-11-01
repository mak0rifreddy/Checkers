"""Board representation and move generation for Checkers."""

from typing import Optional
from constants import BOARD_SIZE, WHITE, BLACK, EMPTY
from piece import Piece


class Move:
    """Represents a checkers move or jump."""

    def __init__(
        self,
        from_pos: tuple[int, int],
        to_pos: tuple[int, int],
        captured_pos: Optional[tuple[int, int]] = None,
        promoted: bool = False,
    ):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured_pos = captured_pos
        self.promoted = promoted

    @property
    def is_jump(self) -> bool:
        return self.captured_pos is not None

    def __repr__(self) -> str:
        fr, fc = self.from_pos
        tr, tc = self.to_pos
        col_names = "ABCDEFGH"
        from_str = f"{col_names[fc]}{8 - fr}"
        to_str = f"{col_names[tc]}{8 - tr}"
        action = "x" if self.is_jump else "-"
        return f"{from_str}{action}{to_str}"


class Board:
    """Manages the 8x8 checkers board state."""

    def __init__(self, init_pieces: bool = True):
        self.grid: list[list[Optional[Piece]]] = [
            [None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        if init_pieces:
            self._setup_initial_board()

    def _setup_initial_board(self) -> None:
        """Place 12 Black pieces at the top and 12 White pieces at the bottom."""
        # Black pieces: rows 0, 1, 2 on dark squares
        for r in range(3):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece(BLACK, r, c)

        # White pieces: rows 5, 6, 7 on dark squares
        for r in range(5, 8):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 1:
                    self.grid[r][c] = Piece(WHITE, r, c)

    @staticmethod
    def is_valid_square(row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    @staticmethod
    def is_dark_square(row: int, col: int) -> bool:
        return (row + col) % 2 == 1

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if not self.is_valid_square(row, col):
            return None
        return self.grid[row][col]

    def set_piece(self, row: int, col: int, piece: Optional[Piece]) -> None:
        if self.is_valid_square(row, col):
            self.grid[row][col] = piece
            if piece is not None:
                piece.row = row
                piece.col = col

    def remove_piece(self, row: int, col: int) -> Optional[Piece]:
        if not self.is_valid_square(row, col):
            return None
        piece = self.grid[row][col]
        self.grid[row][col] = None
        return piece

    def get_all_pieces(self, color: int) -> list[Piece]:
        pieces = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None and p.color == color:
                    pieces.append(p)
        return pieces

    def count_pieces(self, color: int) -> tuple[int, int]:
        """Return (total_count, kings_count) for the given color."""
        total = 0
        kings = 0
        for p in self.get_all_pieces(color):
            total += 1
            if p.is_king:
                kings += 1
        return total, kings

    def get_piece_jumps(self, piece: Piece) -> list[Move]:
        """Find all capture jumps available for the specified piece."""
        jumps = []
        row_dirs = piece.get_forward_directions()
        col_dirs = [-1, 1]

        for dr in row_dirs:
            for dc in col_dirs:
                mid_r = piece.row + dr
                mid_c = piece.col + dc
                land_r = piece.row + 2 * dr
                land_c = piece.col + 2 * dc

                if not self.is_valid_square(land_r, land_c):
                    continue

                if self.get_piece(land_r, land_c) is not None:
                    continue

                mid_piece = self.get_piece(mid_r, mid_c)
                if mid_piece is not None and piece.is_opponent(mid_piece):
                    jumps.append(
                        Move(
                            from_pos=(piece.row, piece.col),
                            to_pos=(land_r, land_c),
                            captured_pos=(mid_r, mid_c),
                        )
                    )
        return jumps

    def get_piece_steps(self, piece: Piece) -> list[Move]:
        """Find regular 1-step diagonal moves for the specified piece."""
        steps = []
        row_dirs = piece.get_forward_directions()
        col_dirs = [-1, 1]

        for dr in row_dirs:
            for dc in col_dirs:
                to_r = piece.row + dr
                to_c = piece.col + dc
                if self.is_valid_square(to_r, to_c) and self.get_piece(to_r, to_c) is None:
                    steps.append(
                        Move(
                            from_pos=(piece.row, piece.col),
                            to_pos=(to_r, to_c),
                        )
                    )
        return steps

    def get_all_jumps_for_color(self, color: int) -> list[Move]:
        """Return all jump moves available across all pieces for the player."""
        all_jumps = []
        for piece in self.get_all_pieces(color):
            all_jumps.extend(self.get_piece_jumps(piece))
        return all_jumps

    def get_all_moves_for_color(self, color: int, enforce_mandatory_jumps: bool = True) -> list[Move]:
        """Return all legal moves for the player."""
        jumps = self.get_all_jumps_for_color(color)
        if enforce_mandatory_jumps and jumps:
            return jumps

        moves = list(jumps)
        for piece in self.get_all_pieces(color):
            moves.extend(self.get_piece_steps(piece))
        return moves

    def execute_move(self, move: Move) -> Optional[Piece]:
        """Execute a move on the board.
        Returns the captured Piece if any was captured, else None.
        Updates the move.promoted flag if the piece became a king.
        """
        fr, fc = move.from_pos
        tr, tc = move.to_pos
        piece = self.remove_piece(fr, fc)
        if piece is None:
            return None

        # Handle capture
        captured_piece = None
        if move.captured_pos is not None:
            cr, cc = move.captured_pos
            captured_piece = self.remove_piece(cr, cc)

        # Place piece at new position
        self.set_piece(tr, tc, piece)

        # King promotion check
        promoted = False
        if not piece.is_king:
            if piece.color == WHITE and tr == 0:
                piece.make_king()
                promoted = True
            elif piece.color == BLACK and tr == BOARD_SIZE - 1:
                piece.make_king()
                promoted = True

        move.promoted = promoted
        return captured_piece

    def clone(self) -> "Board":
        """Return a deep copy of the board."""
        new_board = Board(init_pieces=False)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None:
                    new_board.grid[r][c] = p.clone()
        return new_board
