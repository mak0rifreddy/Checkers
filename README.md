# Checkers (Two-Player Game)

A desktop implementation of the classic Checkers (English Draughts) game built with Python and Tkinter.

---

## Features

- **Two-Player Local Gameplay**: Play head-to-head on the same screen (Player 1: Black vs Player 2: White).
- **Clean Graphical Interface**:
  - Classic 8x8 checkerboard with coordinates (A-H, 1-8).
  - Tactile piece rendering with drop shadows, decorative insets, and gleaming gold crowns for Kings.
  - Visual move indicators (green dots for quiet moves, red target rings for capture jumps).
  - Selection highlights and previous-move dashed markers.
- **Accurate Checkers Rules**:
  - Diagonal forward moves for regular pieces.
  - Capture jumping over opponent pieces.
  - **Multi-jump chaining**: Automatic continuation when multiple captures are available.
  - **King Promotion**: Reaching the opposite end crowns a piece into a King, enabling backwards movement and jumping.
  - **Mandatory Jump Enforcement**: Optional toggle to enforce official capture rules or play casually.
- **Game Controls**:
  - **Undo Move (↺)**: Step back previous turns if a mistake is made.
  - **New Game (★)**: Instantly start a fresh match.
  - **Move Log**: Live algebraic notation tracking all moves (e.g. `B: C3-D4`, `W: D6xC4`).
  - **Status & Counter Panel**: Live count of remaining men and kings for both players.

---

## How to Run

1. Open PowerShell or Command Prompt.
2. Navigate to the `Checkers` folder:
   ```powershell
   cd C:\Users\mak0ri\Checkers
   ```
3. Run the game using Python:
   ```powershell
   python main.py
   ```

---

## How to Play

1. **Starting Side**: Black pieces start first.
2. **Select a Piece**: Click on one of your pieces. Legal destination squares will be highlighted with dots/rings.
3. **Move / Jump**: Click on a highlighted target square to move your piece.
4. **Mandatory Jumps**: If a capture jump is available, players must capture (unless unchecked in the options panel).
5. **Crowning Kings**: When a White piece reaches rank 8 (row 0) or a Black piece reaches rank 1 (row 7), it becomes a King!
6. **Winning**: A player wins when they capture all opponent pieces, or when the opponent has no legal moves left on their turn.

---

## File Structure

- `main.py`: Entry point for launching the application window.
- `gui.py`: Tkinter graphical user interface, board canvas, piece styling, and user interaction.
- `game.py`: Game controller handling turn states, mandatory captures, multi-jumps, undo history, and win detection.
- `board.py`: Board representation, piece tracking, diagonal movement, and jump generation.
- `piece.py`: Checker piece class tracking color, position, and king status.
- `constants.py`: Theme colors, board dimensions, and player constants.
- `test_checkers.py`: Automated unit tests for rule validation and game logic.
