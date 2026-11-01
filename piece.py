"""Checkers piece representation."""

from constants import WHITE, BLACK


class Piece:
    """Represents a single checker piece on the board."""

    def __init__(self, color: int, row: int, col: int, is_king: bool = False):
        self.color = color
        self.row = row
        self.col = col
        self.is_king = is_king

    def make_king(self) -> None:
        """Promote this piece to King."""
        self.is_king = True

    def get_forward_directions(self) -> list[int]:
        """Return row step directions: -1 (upwards) for White, +1 (downwards) for Black.
        Kings can move in both directions (+1 and -1).
        """
        if self.is_king:
            return [-1, 1]
        return [-1] if self.color == WHITE else [1]

    def is_opponent(self, other: "Piece") -> bool:
        """Check if another piece belongs to the opposing player."""
        return other is not None and other.color != self.color

    def clone(self) -> "Piece":
        """Return a copy of this piece."""
        return Piece(self.color, self.row, self.col, self.is_king)

    def __repr__(self) -> str:
        color_name = "White" if self.color == WHITE else "Black"
        rank = "King" if self.is_king else "Man"
        return f"<{color_name} {rank} at ({self.row}, {self.col})>"
