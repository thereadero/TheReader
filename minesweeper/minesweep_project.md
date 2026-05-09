# Minesweeper Premium Documentation

This project is a high-quality implementation of the classic Minesweeper game, developed using Python and the `pygame` library. It features a modern dark-themed UI, multiple difficulty levels, and refined gameplay mechanics.

## Overview
The goal of Minesweeper is to reveal all cells on a grid that do not contain mines. Each revealed cell displays a number indicating how many mines are in the adjacent 8 cells. If a player clicks on a mine, the game is lost.

## Key Features
- **Multiple Difficulty Modes**: Four predefined modes ranging from "Easy" (10x10) to "Extreme" (25x25).
- **First-Click Safety**: The game guarantees that your first click will never be a mine and will always reveal an empty area.
- **Recursive Area Reveal**: Automatically reveals all connected empty cells when an empty cell (0 adjacent mines) is clicked.
- **Flagging System**: Players can flag suspected mine locations to keep track and prevent accidental clicks.
- **Interactive UI**:
    - **Top Bar**: Displays remaining mines, a live timer, and game status messages.
    - **Main Menu**: A dedicated selection screen to pick your difficulty level.
    - **Dynamic Scaling**: The window automatically resizes to accommodate different grid sizes.
- **Sleek Aesthetics**: Uses a custom "Premium" color palette with smooth hover effects and clean typography (Segoe UI).

## Requirements
- Python 3.x
- Pygame (`pip install pygame`)

## How to Play
1. **Launch**: Run `python minesweep.py`.
2. **Menu**: Select a difficulty level (Easy, Medium, Hard, or Extreme).
3. **Gameplay**:
   - **Left Click**: Reveal a cell.
   - **Right Click**: Toggle a flag on a cell.
   - **R Key**: Instantly restart the current level.
   - **M Key**: Return to the main menu.
4. **Victory**: Reveal all non-mine cells to win!

## Technical Structure

### 1. Data Structures
- **`MODES`**: A configuration dictionary defining grid dimensions, mine counts, and cell sizes for each difficulty.
- **`NUM_COLORS`**: A mapping of adjacent mine counts to specific colors for high readability.

### 2. Classes
- **`Cell`**: Represents a single tile on the grid.
  - Tracks state: `is_mine`, `is_revealed`, `is_flagged`.
  - Handles its own rendering logic, including hover states and flag graphics.
- **`Minesweeper`**: The core game controller.
  - **`place_mines()`**: Implements the safe-start logic.
  - **`reveal()`**: A recursive function that handles the flood-fill revealing of empty spaces.
  - **`check_win()`**: Validates if the player has successfully cleared the board.
  - **`run()`**: The main execution loop handling event processing and screen updates.

## Design Details
- **Frame Rate**: Optimized to run at 60 FPS for smooth interactions.
- **Visual Feedback**: Cells subtly change color when hovered, and the status message updates in real-time to provide context (e.g., "BOOM!", "VICTORY!").
