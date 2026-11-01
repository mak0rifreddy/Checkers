"""Game state controller and rules engine for Checkers."""

from typing import Optional, Tuple
from constants import WHITE, BLACK, PLAYER_NAMES
from piece import Piece
from board import Board, Move


class GameStateSnapshot:
    """Snapshot of game state used for undo."""

    def __init__(
        self,
        board: Board,
        current_player: int,
        in_multi_jump: bool,
        multi_jump_pos: Optional[Tuple[int, int]],
        last_move: Optional[Move],
        status_message: str,
        move_notation: str,
    ):
        self.board = board
        self.current_player = current_player
        self.in_multi_jump = in_multi_jump
        self.multi_jump_pos = multi_jump_pos
        self.last_move = last_move
        self.status_message = status_message
        self.move_notation = move_notation


class CheckersGame:
    """Manages the two-player checkers match, turns, and moves."""

    def __init__(self, starting_player: int = BLACK, enforce_mandatory_jumps: bool = True):
        self.starting_player = starting_player
        self.enforce_mandatory_jumps = enforce_mandatory_jumps
        self.board = Board()
        self.current_player = starting_player
        self.selected_piece: Optional[Piece] = None
        self.valid_moves: list[Move] = []
        self.in_multi_jump = False
        self.multi_jump_piece: Optional[Piece] = None
        self.winner: Optional[int] = None
        self.game_over = False
        self.status_message = f"{PLAYER_NAMES[self.current_player]}'s turn to move."
        self.last_move: Optional[Move] = None
        self.history: list[GameStateSnapshot] = []
        self.move_log: list[str] = []

    def reset(self) -> None:
        """Reset the match to initial state."""
        self.board = Board()
        self.current_player = self.starting_player
        self.selected_piece = None
        self.valid_moves = []
        self.in_multi_jump = False
        self.multi_jump_piece = None
        self.winner = None
        self.game_over = False
        self.last_move = None
        self.history.clear()
        self.move_log.clear()
        self.status_message = f"New Game! {PLAYER_NAMES[self.current_player]}'s turn to move."

    @property
    def opponent(self) -> int:
        return WHITE if self.current_player == BLACK else BLACK

    def get_movable_pieces(self) -> list[Piece]:
        """Return pieces of current player that are legally allowed to move."""
        if self.in_multi_jump and self.multi_jump_piece is not None:
            return [self.multi_jump_piece]

        player_jumps = self.board.get_all_jumps_for_color(self.current_player)
        if self.enforce_mandatory_jumps and player_jumps:
            # Only pieces with jumps can be moved
            jump_pieces = []
            for piece in self.board.get_all_pieces(self.current_player):
                if self.board.get_piece_jumps(piece):
                    jump_pieces.append(piece)
            return jump_pieces

        # Any piece with legal steps or jumps
        movable = []
        for piece in self.board.get_all_pieces(self.current_player):
            if self.board.get_piece_jumps(piece) or self.board.get_piece_steps(piece):
                movable.append(piece)
        return movable

    def select_square(self, row: int, col: int) -> bool:
        """Handle player clicking on a square at (row, col).
        Returns True if board state changed and needs visual refresh.
        """
        if self.game_over:
            return False

        piece = self.board.get_piece(row, col)

        # If a piece is already selected, check if user clicked on a valid destination
        if self.selected_piece is not None:
            for move in self.valid_moves:
                if move.to_pos == (row, col):
                    self._execute_player_move(move)
                    return True

        # If in the middle of a multi-jump, player cannot select another piece
        if self.in_multi_jump:
            if piece is self.multi_jump_piece:
                # Already selected
                return False
            self.status_message = "Mandatory multi-jump! You must complete the capture."
            return True

        # Clicking own piece
        if piece is not None and piece.color == self.current_player:
            movable_pieces = self.get_movable_pieces()
            if piece not in movable_pieces:
                if self.enforce_mandatory_jumps and self.board.get_all_jumps_for_color(self.current_player):
                    self.status_message = "Capture is mandatory! Select a piece that can jump."
                else:
                    self.status_message = "This piece has no legal moves."
                return True

            # Select this piece
            self.selected_piece = piece
            self._update_valid_moves()
            self.status_message = f"Selected {PLAYER_NAMES[self.current_player]} piece at {self._pos_to_notation(row, col)}."
            return True

        # Clicking elsewhere (deselect)
        if self.selected_piece is not None and not self.in_multi_jump:
            self.selected_piece = None
            self.valid_moves = []
            self.status_message = f"{PLAYER_NAMES[self.current_player]}'s turn."
            return True

        return False

    def _update_valid_moves(self) -> None:
        """Calculate valid moves for the currently selected piece."""
        if self.selected_piece is None:
            self.valid_moves = []
            return

        jumps = self.board.get_piece_jumps(self.selected_piece)

        # If mandatory jump applies and any jump exists across board, only jumps count
        all_board_jumps = self.board.get_all_jumps_for_color(self.current_player)
        if self.enforce_mandatory_jumps and all_board_jumps:
            self.valid_moves = jumps
        else:
            steps = self.board.get_piece_steps(self.selected_piece)
            self.valid_moves = jumps + steps

    def _execute_player_move(self, move: Move) -> None:
        """Execute the chosen move, handling captures, multi-jumps, and turn changes."""
        # Save snapshot for undo before modifying state
        notation = self._generate_move_notation(move)
        snapshot = GameStateSnapshot(
            board=self.board.clone(),
            current_player=self.current_player,
            in_multi_jump=self.in_multi_jump,
            multi_jump_pos=(self.multi_jump_piece.row, self.multi_jump_piece.col) if self.multi_jump_piece else None,
            last_move=self.last_move,
            status_message=self.status_message,
            move_notation=notation,
        )
        self.history.append(snapshot)
        self.move_log.append(f"{len(self.move_log) + 1}. {PLAYER_NAMES[self.current_player][0]}: {notation}")

        captured_piece = self.board.execute_move(move)
        self.last_move = move

        # Check multi-jump continuation:
        # Standard rule: if a piece jumped and was NOT crowned this turn, and has more jumps,
        # it must continue jumping.
        moved_piece = self.board.get_piece(move.to_pos[0], move.to_pos[1])

        if move.is_jump and not move.promoted and moved_piece is not None:
            further_jumps = self.board.get_piece_jumps(moved_piece)
            if further_jumps:
                self.in_multi_jump = True
                self.multi_jump_piece = moved_piece
                self.selected_piece = moved_piece
                self.valid_moves = further_jumps
                self.status_message = f"Multi-jump available! {PLAYER_NAMES[self.current_player]} must capture again."
                return

        # Turn finished
        self.in_multi_jump = False
        self.multi_jump_piece = None
        self.selected_piece = None
        self.valid_moves = []

        promotion_note = " (Crowned King!)" if move.promoted else ""

        # Switch player
        self.current_player = self.opponent

        # Check game over conditions
        legal_moves = self.board.get_all_moves_for_color(
            self.current_player, enforce_mandatory_jumps=self.enforce_mandatory_jumps
        )
        pieces_count, _ = self.board.count_pieces(self.current_player)

        if pieces_count == 0 or len(legal_moves) == 0:
            self.game_over = True
            self.winner = self.opponent
            if pieces_count == 0:
                self.status_message = f"Game Over! {PLAYER_NAMES[self.winner]} wins by capturing all pieces!"
            else:
                self.status_message = f"Game Over! {PLAYER_NAMES[self.winner]} wins! {PLAYER_NAMES[self.current_player]} has no legal moves."
        else:
            jumps_available = self.board.get_all_jumps_for_color(self.current_player)
            if self.enforce_mandatory_jumps and jumps_available:
                self.status_message = f"{PLAYER_NAMES[self.current_player]}'s turn{promotion_note}. [Capture is available!]"
            else:
                self.status_message = f"{PLAYER_NAMES[self.current_player]}'s turn{promotion_note}."

    def undo(self) -> bool:
        """Undo the last move."""
        if not self.history:
            return False

        snapshot = self.history.pop()
        self.board = snapshot.board
        self.current_player = snapshot.current_player
        self.in_multi_jump = snapshot.in_multi_jump
        if snapshot.multi_jump_pos is not None:
            r, c = snapshot.multi_jump_pos
            self.multi_jump_piece = self.board.get_piece(r, c)
            self.selected_piece = self.multi_jump_piece
            self._update_valid_moves()
        else:
            self.multi_jump_piece = None
            self.selected_piece = None
            self.valid_moves = []

        self.last_move = snapshot.last_move
        self.status_message = f"Move undone. {PLAYER_NAMES[self.current_player]}'s turn."
        self.game_over = False
        self.winner = None

        if self.move_log:
            self.move_log.pop()

        return True

    @staticmethod
    def _pos_to_notation(row: int, col: int) -> str:
        col_name = "ABCDEFGH"[col]
        row_name = str(8 - row)
        return f"{col_name}{row_name}"

    def _generate_move_notation(self, move: Move) -> str:
        from_str = self._pos_to_notation(*move.from_pos)
        to_str = self._pos_to_notation(*move.to_pos)
        sep = "x" if move.is_jump else "-"
        promo = "(K)" if move.promoted else ""
        return f"{from_str}{sep}{to_str}{promo}"
