# Geometry Dash Clone (GD.py)

## Overview
**GD.py** is a fully-featured, physics-based Geometry Dash-inspired platformer built using Python and Pygame. It features customizable player shapes with distinct collision physics and jumping mechanics, an interactive level builder with real-time silhouette previews, custom save/load slots, and dynamic terrain interaction.

---

## Key Features

### 1. Shape-Based Player Customization
Players can select from four unique character shapes, each offering distinct gameplay characteristics and physics profiles:
- **Cube (Green / Default)**:
  - **Dimensions**: 30 x 30 pixels
  - **Jump Strength**: 36
  - **Physics**: Rotates 90 degrees in the air upon jumping, snapping to the ground.
- **Circle (Blue)**:
  - **Dimensions**: 30 x 30 pixels
  - **Jump Strength**: 45 (Highest jump capability)
  - **Physics**: Rotates continuously (rolls) along the ground based on horizontal velocity and direction.
- **Rectangle (Red)**:
  - **Dimensions**: 40 x 20 pixels
  - **Jump Strength**: 28 (Lowest jump capability)
  - **Physics**: Handles collision with a wider horizontal profile.
- **Triangle (Yellow / Face)**:
  - **Dimensions**: 30 x 30 pixels
  - **Jump Strength**: 32 (Moderate jump capability)
  - **Physics**: Uses custom mask collision detection to align with slopes.

*Visual custom styles include Green, Red, Blue, and Yellow (Face) variants.*

### 2. Advanced Physics & Collision Engine
- **Pixel-Perfect Mask Detection**: Collision is handled via Pygame's `Mask` system, allowing precise overlap check during high-speed rotations and on angled surfaces.
- **Terrain Snapping & Ceiling Bumping**: The player snaps smoothly to platforms when landing and gets pushed down or blocked when colliding with ceilings or solid walls.
- **Slope Scaling (Ramps)**: Smart step-up collision logic allows the player to seamlessly ascend ramps and low obstacles (up to 25 pixels high) without losing horizontal velocity.

### 3. Interactive Level Builder
- **Accordion UI Sidebar**: Level items are organized into collapsible categories:
  - **Blocks**: Standard Block, thin Platform, Tall Platform, ground Floor, and angled Ramp.
  - **Enemy**: 1x Spike, 2x Spikes, and 3x Spikes for custom-made obstacle courses.
  - **Misc**: Start Node (Spawn) and End Node.
- **Holographic Preview Silhouette**: Displays a semi-transparent, color-coded preview of the selected block at the grid position aligned to the mouse cursor before placement.
- **Menu Hover Protection**: Prevents accidental block placement or erasure while interacting with UI panels, category buttons, or options.

### 4. Custom Saves & Level Navigation
- **Local Level Storage**: Levels are saved as JSON structures in the project directory (`maps_*.json`).
- **Load Menu**: Lists all available map save files, allowing players to scroll through them and load their custom creations using the keyboard.
- **Tries Counter**: Displays and tracks the number of attempts taken to complete the level.

---

## Controls Reference

### Main Menu & Navigation
- **Mouse Left-Click**: Select menu buttons.
- **Escape Key (`ESC`)**: Go back / Cancel action.
- **Up / Down Arrows**: Navigate the level load list.
- **Enter Key (`ENTER`)**: Confirm level selection in the load menu.

### Gameplay Mode
- **Jump**: `SPACEBAR` (only when grounded).
- **Horizontal Movement**: Left/Right Arrow keys or `A`/`D` keys.
- **Go Back**: Click `Back` button to return to the main menu.

### Level Builder Mode
- **Camera Panning**: Press/Hold `A` and `D` keys to scroll the editor camera left and right.
- **Place Object**: Mouse Left-Click on the grid.
- **Erase Object**: Mouse Right-Click on any placed block or spike.
- **Save Level**: Click the `Save` button (top right) to enter a custom level name and press `ENTER` to save. Alternatively, press `ENTER` directly to save to the default `maps.json`.
- **Clear Canvas**: Click the `Clear` button (top left/center) to remove all objects from the workspace.

#### Build Mode Quick Selection Hotkeys:
| Category | Element | Hotkey | Dimensions |
| :--- | :--- | :---: | :---: |
| **Blocks** | Block | `B` | 60 x 60 px |
| | Platform | `P` | 60 x 20 px |
| | Tall Platform | `H` | 60 x 180 px |
| | Floor | `F` | 800 x 40 px |
| | Ramp | `R` | 60 x 60 px |
| **Enemy** | 1x Spike | `S` | 60 x 60 px |
| | 2x Spikes | `2` | 90 x 60 px |
| | 3x Spikes | `3` | 120 x 60 px |
| **Misc** | Spawn Point | `T` | Snap Point |
| | End Node | `E` | Glow Radius |

---

## Getting Started

### Prerequisites
- Python 3.x
- Pygame library. Install via:
  ```bash
  pip install pygame
  ```

### Running the Game
1. Open terminal and navigate to the project directory:
   ```bash
   cd GD
   ```
2. Run the game script:
   ```bash
   python GD.py
   ```
3. Use the main menu to customize your character style, build custom levels, or load existing maps to play!