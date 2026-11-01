"""Constants for the Checkers game."""

# Board configuration
BOARD_SIZE = 8
SQUARE_SIZE = 75
BOARD_PIXELS = BOARD_SIZE * SQUARE_SIZE

# Player identifiers
EMPTY = 0
WHITE = 1
BLACK = 2

PLAYER_NAMES = {
    WHITE: "White",
    BLACK: "Black"
}

# Color palette
COLOR_LIGHT_SQUARE = "#F0D9B5"     # Warm parchment light square
COLOR_DARK_SQUARE = "#B58863"      # Classic wooden dark square
COLOR_BOARD_BORDER = "#6F4E37"     # Deep wood border

COLOR_WHITE_PIECE = "#FAFAFA"      # Crisp white piece
COLOR_WHITE_INNER = "#EDEDED"
COLOR_WHITE_OUTLINE = "#4A4A4A"

COLOR_BLACK_PIECE = "#222222"      # Deep charcoal black piece
COLOR_BLACK_INNER = "#333333"
COLOR_BLACK_OUTLINE = "#777777"

COLOR_SELECTION = "#FFD700"        # Gold ring for selected piece
COLOR_VALID_MOVE = "#4CAF50"       # Green dot for valid quiet move
COLOR_VALID_JUMP = "#E53935"       # Red/Orange ring for capture jump
COLOR_LAST_MOVE = "#FFE082"        # Soft yellow highlight for previous move

COLOR_CROWN_GOLD = "#FFC107"       # Gold crown on pieces
COLOR_CROWN_DARK = "#B78103"

# UI Colors
BG_MAIN = "#2B2B2B"
BG_PANEL = "#383838"
BG_CARD = "#454545"
TEXT_COLOR = "#FFFFFF"
TEXT_MUTED = "#CCCCCC"
ACCENT_COLOR = "#1976D2"
ACCENT_HOVER = "#1565C0"
