"""Tkinter graphical user interface for Checkers."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from constants import (
    BOARD_SIZE,
    SQUARE_SIZE,
    WHITE,
    BLACK,
    PLAYER_NAMES,
    COLOR_LIGHT_SQUARE,
    COLOR_DARK_SQUARE,
    COLOR_BOARD_BORDER,
    COLOR_WHITE_PIECE,
    COLOR_WHITE_INNER,
    COLOR_WHITE_OUTLINE,
    COLOR_BLACK_PIECE,
    COLOR_BLACK_INNER,
    COLOR_BLACK_OUTLINE,
    COLOR_SELECTION,
    COLOR_VALID_MOVE,
    COLOR_VALID_JUMP,
    COLOR_LAST_MOVE,
    COLOR_CROWN_GOLD,
    COLOR_CROWN_DARK,
    BG_MAIN,
    BG_PANEL,
    BG_CARD,
    TEXT_COLOR,
    TEXT_MUTED,
    ACCENT_COLOR,
    ACCENT_HOVER,
)
from piece import Piece
from board import Move
from game import CheckersGame


class CheckersGUI:
    """Checkers graphical user interface built with Tkinter."""

    BORDER_OFFSET = 24  # Space for board coordinate labels (A-H, 1-8)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Checkers - Two Player Game (White vs Black)")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)

        self.game = CheckersGame(starting_player=BLACK, enforce_mandatory_jumps=True)
        self.mandatory_jumps_var = tk.BooleanVar(value=True)

        self._setup_layout()
        self.draw_board()
        self.update_ui_state()

    def _setup_layout(self) -> None:
        """Create main container and sub-panels."""
        main_frame = tk.Frame(self.root, bg=BG_MAIN, padx=16, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Board container
        board_container = tk.Frame(
            main_frame,
            bg=COLOR_BOARD_BORDER,
            bd=3,
            relief=tk.RIDGE,
            padx=2,
            pady=2,
        )
        board_container.pack(side=tk.LEFT, padx=(0, 16))

        canvas_dim = BOARD_SIZE * SQUARE_SIZE + (self.BORDER_OFFSET * 2)
        self.canvas = tk.Canvas(
            board_container,
            width=canvas_dim,
            height=canvas_dim,
            bg=COLOR_BOARD_BORDER,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_hover)

        # Right side: Control and info panel
        sidebar = tk.Frame(main_frame, bg=BG_PANEL, width=320, padx=16, pady=16)
        sidebar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Header title
        title_label = tk.Label(
            sidebar,
            text="CHECKERS",
            font=("Segoe UI", 20, "bold"),
            bg=BG_PANEL,
            fg=TEXT_COLOR,
        )
        title_label.pack(anchor="w", pady=(0, 2))

        sub_label = tk.Label(
            sidebar,
            text="Two Player Classic Game",
            font=("Segoe UI", 10),
            bg=BG_PANEL,
            fg=TEXT_MUTED,
        )
        sub_label.pack(anchor="w", pady=(0, 14))

        # Turn indicator card
        self.turn_card = tk.Frame(sidebar, bg=BG_CARD, bd=1, relief=tk.SOLID, padx=12, pady=10)
        self.turn_card.pack(fill=tk.X, pady=(0, 12))

        turn_header = tk.Label(
            self.turn_card,
            text="CURRENT TURN",
            font=("Segoe UI", 8, "bold"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
        )
        turn_header.pack(anchor="w")

        turn_display_frame = tk.Frame(self.turn_card, bg=BG_CARD)
        turn_display_frame.pack(fill=tk.X, pady=(6, 0))

        self.turn_canvas_badge = tk.Canvas(
            turn_display_frame,
            width=30,
            height=30,
            bg=BG_CARD,
            highlightthickness=0,
        )
        self.turn_canvas_badge.pack(side=tk.LEFT, padx=(0, 10))

        self.turn_text_label = tk.Label(
            turn_display_frame,
            text="Black's Turn",
            font=("Segoe UI", 13, "bold"),
            bg=BG_CARD,
            fg=TEXT_COLOR,
        )
        self.turn_text_label.pack(side=tk.LEFT)

        # Score / Piece count card
        score_card = tk.Frame(sidebar, bg=BG_CARD, bd=1, relief=tk.SOLID, padx=12, pady=10)
        score_card.pack(fill=tk.X, pady=(0, 12))

        score_title = tk.Label(
            score_card,
            text="PIECES REMAINING",
            font=("Segoe UI", 8, "bold"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
        )
        score_title.pack(anchor="w", pady=(0, 6))

        # Black status row
        black_row = tk.Frame(score_card, bg=BG_CARD)
        black_row.pack(fill=tk.X, pady=2)
        b_badge = tk.Canvas(black_row, width=16, height=16, bg=BG_CARD, highlightthickness=0)
        b_badge.pack(side=tk.LEFT, padx=(0, 8))
        b_badge.create_oval(1, 1, 15, 15, fill=COLOR_BLACK_PIECE, outline=COLOR_BLACK_OUTLINE)
        self.black_count_label = tk.Label(
            black_row,
            text="Black: 12 pieces (0 Kings)",
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=TEXT_COLOR,
        )
        self.black_count_label.pack(side=tk.LEFT)

        # White status row
        white_row = tk.Frame(score_card, bg=BG_CARD)
        white_row.pack(fill=tk.X, pady=2)
        w_badge = tk.Canvas(white_row, width=16, height=16, bg=BG_CARD, highlightthickness=0)
        w_badge.pack(side=tk.LEFT, padx=(0, 8))
        w_badge.create_oval(1, 1, 15, 15, fill=COLOR_WHITE_PIECE, outline=COLOR_WHITE_OUTLINE)
        self.white_count_label = tk.Label(
            white_row,
            text="White: 12 pieces (0 Kings)",
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=TEXT_COLOR,
        )
        self.white_count_label.pack(side=tk.LEFT)

        # Status Message Box
        self.msg_card = tk.Frame(sidebar, bg=BG_CARD, bd=1, relief=tk.SOLID, padx=10, pady=8)
        self.msg_card.pack(fill=tk.X, pady=(0, 12))

        self.status_label = tk.Label(
            self.msg_card,
            text=self.game.status_message,
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg="#FFE082",
            wraplength=270,
            justify=tk.LEFT,
        )
        self.status_label.pack(anchor="w")

        # Move History Section
        history_frame = tk.Frame(sidebar, bg=BG_PANEL)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        hist_title = tk.Label(
            history_frame,
            text="MOVE LOG",
            font=("Segoe UI", 8, "bold"),
            bg=BG_PANEL,
            fg=TEXT_MUTED,
        )
        hist_title.pack(anchor="w", pady=(0, 4))

        list_container = tk.Frame(history_frame, bg=BG_CARD)
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(
            list_container,
            height=6,
            bg=BG_CARD,
            fg=TEXT_COLOR,
            selectbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Options: Mandatory jumps toggle
        opt_frame = tk.Frame(sidebar, bg=BG_PANEL)
        opt_frame.pack(fill=tk.X, pady=(0, 10))

        self.mandatory_check = tk.Checkbutton(
            opt_frame,
            text="Enforce Mandatory Jumps",
            variable=self.mandatory_jumps_var,
            command=self._on_toggle_mandatory,
            bg=BG_PANEL,
            fg=TEXT_COLOR,
            selectcolor=BG_CARD,
            activebackground=BG_PANEL,
            activeforeground=TEXT_COLOR,
            font=("Segoe UI", 9),
        )
        self.mandatory_check.pack(anchor="w")

        # Action Buttons
        btn_frame = tk.Frame(sidebar, bg=BG_PANEL)
        btn_frame.pack(fill=tk.X, pady=(0, 4))

        self.undo_btn = tk.Button(
            btn_frame,
            text="↺ Undo Move",
            command=self._on_undo,
            bg=BG_CARD,
            fg=TEXT_COLOR,
            activebackground="#505050",
            activeforeground=TEXT_COLOR,
            relief=tk.GROOVE,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
            cursor="hand2",
        )
        self.undo_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.new_game_btn = tk.Button(
            btn_frame,
            text="★ New Game",
            command=self._on_new_game,
            bg=ACCENT_COLOR,
            fg=TEXT_COLOR,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_COLOR,
            relief=tk.GROOVE,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
            cursor="hand2",
        )
        self.new_game_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        help_btn = tk.Button(
            sidebar,
            text="? How to Play & Rules",
            command=self._show_rules_dialog,
            bg=BG_PANEL,
            fg=TEXT_MUTED,
            activebackground=BG_CARD,
            activeforeground=TEXT_COLOR,
            bd=0,
            font=("Segoe UI", 8, "underline"),
            cursor="hand2",
        )
        help_btn.pack(anchor="center", pady=(6, 0))

    def _on_toggle_mandatory(self) -> None:
        self.game.enforce_mandatory_jumps = self.mandatory_jumps_var.get()
        if self.game.selected_piece is not None:
            self.game._update_valid_moves()
        self.draw_board()
        self.update_ui_state()

    def _on_undo(self) -> None:
        if self.game.undo():
            self.draw_board()
            self.update_ui_state()

    def _on_new_game(self) -> None:
        if messagebox.askyesno("New Game", "Are you sure you want to start a new match?"):
            self.game.reset()
            self.game.enforce_mandatory_jumps = self.mandatory_jumps_var.get()
            self.draw_board()
            self.update_ui_state()

    def _show_rules_dialog(self) -> None:
        rules_text = (
            "CHECKERS RULES (American Checkers / Draughts):\n\n"
            "1. Movement:\n"
            "  - Normal pieces move forward diagonally 1 square onto an empty dark square.\n"
            "  - Black starts at the top and moves downwards.\n"
            "  - White starts at the bottom and moves upwards.\n\n"
            "2. Captures (Jumping):\n"
            "  - Jump diagonally over an adjacent opponent piece to an empty square behind it.\n"
            "  - Captured pieces are removed from the board.\n"
            "  - Multi-Jumps: If another jump is available from the landing square, you must continue jumping with the same piece.\n\n"
            "3. Kings:\n"
            "  - When a piece reaches the opponent's back rank, it is crowned King.\n"
            "  - Kings can move and jump both forwards and backwards diagonally.\n"
            "  - In standard rules, reaching the king row finishes the turn.\n\n"
            "4. Winning:\n"
            "  - You win by capturing all opponent pieces, or leaving your opponent with no legal moves."
        )
        messagebox.showinfo("Rules & How to Play", rules_text)

    def _pos_to_canvas(self, row: int, col: int) -> tuple[int, int]:
        """Convert board row and col to canvas top-left pixel coordinates."""
        x = self.BORDER_OFFSET + (col * SQUARE_SIZE)
        y = self.BORDER_OFFSET + (row * SQUARE_SIZE)
        return x, y

    def _canvas_to_pos(self, x: int, y: int) -> Optional[tuple[int, int]]:
        """Convert canvas pixel coordinates to board (row, col) or None if in border."""
        bx = x - self.BORDER_OFFSET
        by = y - self.BORDER_OFFSET
        if 0 <= bx < (BOARD_SIZE * SQUARE_SIZE) and 0 <= by < (BOARD_SIZE * SQUARE_SIZE):
            col = bx // SQUARE_SIZE
            row = by // SQUARE_SIZE
            return int(row), int(col)
        return None

    def draw_board(self) -> None:
        """Render the complete checkerboard, highlights, and pieces."""
        self.canvas.delete("all")

        # Draw coordinate labels on borders
        col_names = "ABCDEFGH"
        for i in range(BOARD_SIZE):
            # Column letters on top and bottom
            cx = self.BORDER_OFFSET + (i * SQUARE_SIZE) + (SQUARE_SIZE // 2)
            self.canvas.create_text(
                cx,
                self.BORDER_OFFSET // 2,
                text=col_names[i],
                fill="#D4B996",
                font=("Segoe UI", 9, "bold"),
            )
            self.canvas.create_text(
                cx,
                self.BORDER_OFFSET + (BOARD_SIZE * SQUARE_SIZE) + (self.BORDER_OFFSET // 2),
                text=col_names[i],
                fill="#D4B996",
                font=("Segoe UI", 9, "bold"),
            )

            # Row numbers on left and right (8 down to 1)
            cy = self.BORDER_OFFSET + (i * SQUARE_SIZE) + (SQUARE_SIZE // 2)
            self.canvas.create_text(
                self.BORDER_OFFSET // 2,
                cy,
                text=str(8 - i),
                fill="#D4B996",
                font=("Segoe UI", 9, "bold"),
            )
            self.canvas.create_text(
                self.BORDER_OFFSET + (BOARD_SIZE * SQUARE_SIZE) + (self.BORDER_OFFSET // 2),
                cy,
                text=str(8 - i),
                fill="#D4B996",
                font=("Segoe UI", 9, "bold"),
            )

        # Draw squares
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = self._pos_to_canvas(r, c)
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE

                is_dark = (r + c) % 2 == 1
                color = COLOR_DARK_SQUARE if is_dark else COLOR_LIGHT_SQUARE

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline=color, tags=f"sq_{r}_{c}"
                )

        # Highlight last move (source and destination)
        if self.game.last_move is not None:
            for pos in [self.game.last_move.from_pos, self.game.last_move.to_pos]:
                lr, lc = pos
                x1, y1 = self._pos_to_canvas(lr, lc)
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                self.canvas.create_rectangle(
                    x1 + 2,
                    y1 + 2,
                    x2 - 2,
                    y2 - 2,
                    outline=COLOR_LAST_MOVE,
                    width=2,
                    dash=(4, 2),
                )

        # Draw selected piece highlight
        if self.game.selected_piece is not None:
            sr = self.game.selected_piece.row
            sc = self.game.selected_piece.col
            x1, y1 = self._pos_to_canvas(sr, sc)
            x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE

            self.canvas.create_rectangle(
                x1 + 3,
                y1 + 3,
                x2 - 3,
                y2 - 3,
                outline=COLOR_SELECTION,
                width=3,
            )

        # Draw valid move indicators
        for move in self.game.valid_moves:
            tr, tc = move.to_pos
            x1, y1 = self._pos_to_canvas(tr, tc)
            cx = x1 + SQUARE_SIZE // 2
            cy = y1 + SQUARE_SIZE // 2

            if move.is_jump:
                # Capture jump: red ring and crosshair dot
                self.canvas.create_oval(
                    cx - 16,
                    cy - 16,
                    cx + 16,
                    cy + 16,
                    outline=COLOR_VALID_JUMP,
                    width=3,
                )
                self.canvas.create_oval(
                    cx - 6,
                    cy - 6,
                    cx + 6,
                    cy + 6,
                    fill=COLOR_VALID_JUMP,
                    outline="",
                )
            else:
                # Quiet step: friendly green dot
                self.canvas.create_oval(
                    cx - 10,
                    cy - 10,
                    cx + 10,
                    cy + 10,
                    fill=COLOR_VALID_MOVE,
                    outline="",
                )

        # Draw pieces
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.game.board.get_piece(r, c)
                if piece is not None:
                    self._draw_piece(piece)

    def _draw_piece(self, piece: Piece) -> None:
        """Render a styled checker piece with drop shadow and crown if king."""
        x1, y1 = self._pos_to_canvas(piece.row, piece.col)
        cx = x1 + SQUARE_SIZE // 2
        cy = y1 + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 8

        is_white = piece.color == WHITE
        fill_color = COLOR_WHITE_PIECE if is_white else COLOR_BLACK_PIECE
        inner_color = COLOR_WHITE_INNER if is_white else COLOR_BLACK_INNER
        outline_color = COLOR_WHITE_OUTLINE if is_white else COLOR_BLACK_OUTLINE

        # 1. Subtle drop shadow
        self.canvas.create_oval(
            cx - radius + 3,
            cy - radius + 5,
            cx + radius + 3,
            cy + radius + 5,
            fill="#3B2613",
            outline="",
        )

        # 2. Main piece body
        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=fill_color,
            outline=outline_color,
            width=2,
        )

        # 3. Inner decorative ring for tactile checker look
        inner_r = radius - 6
        self.canvas.create_oval(
            cx - inner_r,
            cy - inner_r,
            cx + inner_r,
            cy + inner_r,
            fill=inner_color,
            outline=outline_color,
            width=1,
        )

        # 4. Center indent
        center_r = radius - 14
        self.canvas.create_oval(
            cx - center_r,
            cy - center_r,
            cx + center_r,
            cy + center_r,
            fill=fill_color,
            outline=outline_color,
            width=1,
        )

        # 5. Crown if King
        if piece.is_king:
            self._draw_crown(cx, cy, is_white)

    def _draw_crown(self, cx: int, cy: int, is_white_piece: bool) -> None:
        """Draw a majestic crown on a King piece."""
        crown_fill = COLOR_CROWN_GOLD
        crown_outline = COLOR_CROWN_DARK if is_white_piece else "#443000"

        # Coordinates for 5-point crown polygon
        # Base at cy + 7, peak at cy - 8
        crown_points = [
            cx - 13, cy + 7,  # Bottom left
            cx - 13, cy - 5,  # Left tip
            cx - 6,  cy + 1,  # Left valley
            cx,      cy - 9,  # Middle tip (highest)
            cx + 6,  cy + 1,  # Right valley
            cx + 13, cy - 5,  # Right tip
            cx + 13, cy + 7,  # Bottom right
        ]
        self.canvas.create_polygon(
            crown_points,
            fill=crown_fill,
            outline=crown_outline,
            width=1.5,
        )

        # Crown base band
        self.canvas.create_line(
            cx - 13, cy + 7,
            cx + 13, cy + 7,
            fill=crown_outline,
            width=2,
        )

        # Jewels on tips
        jewel_color = "#E53935" if is_white_piece else "#FFD54F"
        for jx, jy in [(cx - 13, cy - 5), (cx, cy - 9), (cx + 13, cy - 5)]:
            self.canvas.create_oval(
                jx - 2, jy - 2, jx + 2, jy + 2, fill=jewel_color, outline=""
            )

    def update_ui_state(self) -> None:
        """Update turn badge, score indicators, move history, and status text."""
        # Update turn badge
        is_black = self.game.current_player == BLACK
        turn_name = "Black's Turn" if is_black else "White's Turn"
        self.turn_text_label.config(text=turn_name)

        self.turn_canvas_badge.delete("all")
        badge_fill = COLOR_BLACK_PIECE if is_black else COLOR_WHITE_PIECE
        badge_outline = COLOR_BLACK_OUTLINE if is_black else COLOR_WHITE_OUTLINE
        self.turn_canvas_badge.create_oval(
            3, 3, 27, 27, fill=badge_fill, outline=badge_outline, width=2
        )

        # Update piece counts
        b_total, b_kings = self.game.board.count_pieces(BLACK)
        w_total, w_kings = self.game.board.count_pieces(WHITE)
        self.black_count_label.config(
            text=f"Black: {b_total} pieces ({b_kings} King{'s' if b_kings != 1 else ''})"
        )
        self.white_count_label.config(
            text=f"White: {w_total} pieces ({w_kings} King{'s' if w_kings != 1 else ''})"
        )

        # Update message
        self.status_label.config(text=self.game.status_message)
        if self.game.game_over:
            self.status_label.config(fg="#81C784")  # Green celebratory color
        elif "mandatory" in self.game.status_message.lower() or "capture" in self.game.status_message.lower():
            self.status_label.config(fg="#FF8A65")  # Warning coral
        else:
            self.status_label.config(fg="#FFE082")  # Warm yellow

        # Update undo button state
        if self.game.history and not self.game.game_over:
            self.undo_btn.config(state=tk.NORMAL)
        else:
            self.undo_btn.config(state=tk.DISABLED)

        # Update move log listbox
        self.history_listbox.delete(0, tk.END)
        for entry in self.game.move_log:
            self.history_listbox.insert(tk.END, entry)
        if self.game.move_log:
            self.history_listbox.see(tk.END)

        # Game over popup
        if self.game.game_over:
            winner_name = PLAYER_NAMES.get(self.game.winner, "Nobody")
            messagebox.showinfo(
                "Game Over!",
                f"Congratulations!\n\n{winner_name} has won the match!\n\nClick 'New Game' to play again.",
            )

    def _on_canvas_click(self, event: tk.Event) -> None:
        pos = self._canvas_to_pos(event.x, event.y)
        if pos is None:
            return

        row, col = pos
        changed = self.game.select_square(row, col)
        if changed:
            self.draw_board()
            self.update_ui_state()

    def _on_canvas_hover(self, event: tk.Event) -> None:
        pos = self._canvas_to_pos(event.x, event.y)
        if pos is None:
            self.canvas.config(cursor="arrow")
            return

        row, col = pos
        # If hovering over a valid move destination or a selectable piece, show hand cursor
        is_dest = any(move.to_pos == (row, col) for move in self.game.valid_moves)
        piece = self.game.board.get_piece(row, col)
        is_own_piece = piece is not None and piece.color == self.game.current_player

        if is_dest or is_own_piece:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="arrow")
