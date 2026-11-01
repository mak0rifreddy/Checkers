"""Main entry point for the Checkers game."""

import tkinter as tk
from gui import CheckersGUI


def center_window(root: tk.Tk, width: int = 1000, height: int = 700) -> None:
    """Center the game window on the screen."""
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def main() -> None:
    root = tk.Tk()
    root.title("Checkers - Two Player Game (White vs Black)")
    center_window(root, 1020, 710)

    # Initialize GUI
    app = CheckersGUI(root)

    # Start main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
