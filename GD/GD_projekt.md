# Geometry Dash Clone (GD.py)

## Overview
GD is a fully-featured Geometry Dash-inspired platformer built using Python and Pygame. Players control a fully customizable shape navigating through custom-built levels with various hazards, platforms, blocks, and dynamic physics including shape-specific collision and continuous rotation.

## Features

### Player Customization
- **Shapes (`cube`, `circle`, `rectangle`, `triangle`)**: Each shape handles collision differently and has a unique hit profile. For instance, the circle handles rotation while rolling.
- **Unique Jump Strengths**: Different jumping profiles based on the selected shape.
- **Visual Styles**: Customizable color themes including green, red, blue, and a special "face" model.

### Advanced Physics & Collision
- **Pixel-perfect Collision Detection**: Custom mask-based overlap detection for highly precise collision during rotation and movement in complex terrain.
- **Terrain Interaction**: Handling for slopes, ramps, stepping up small blocks, ceiling bumping, and ground snapping.

### Interactive Level Builder
- **Categorized UI Accordion Menu**: Items are structured into nested categories logic (Blocks, Enemy, Miscellaneous).
  - *Blocks*: Block, Platform, Tall Platform, Floor, Ramp.
  - *Enemy*: 1x Spike, 2x Spikes, 3x Spikes.
  - *Misc*: Start Node, End Node.
- **Collision Silhouette Preview**: Real-time holographic projection of where a block will be placed before confirming it.
- **Smart Editor Interaction**: Prevent accidental block placement behind UI elements.

### Progress and Map Flow
- **Save/Load System**: Multiple distinct maps and save files tracking in the local JSON data (`maps_*.json`).
- **Tries Counter**: Tracks how many attempts a level has taken.

## Requirements
- Python 3.x
- Pygame (`pip install pygame`)

## How to Run
1. Navigate to the `GD` project directory.
2. Run the executable file:
   ```cmd
   python GD.py
   ```
3. Use the interactive menu to `Start` a level, select `Build` mode to create your own maps, manage `Saves`, or `Customize` your player character.

## Controls
- **Gameplay**:
  - Main Menu Navigation: Mouse Left-Click.
  - Interaction / Jump: `SPACE`
  - Horizontal Movement: `Arrow Keys` or `A`/`D`
- **Build Mode**:
  - Hotkeys for quick selection (`B` for block, `P` for platform, `S` for spikes, `R` for ramp, etc.).
  - Left-Click to place an object.
  - Right-Click to erase an object.
  - Drag over UI menus to select categorical items.
  - `Enter` to save the map context.