# GD Project

## Overview
GD is a Geometry Dash-inspired platformer game built using Python and the Pygame library. Players control a cube navigating through custom-built levels with various obstacles, platforms, and hazards.

## Features
- **Player Character**: A green cube with physics-based movement (gravity, jumping)
- **Tries System**: Limited attempts (3 tries) that reset on game restart
- **Build Mode**: Level editor for creating custom maps
- **Multiple Object Types**:
  - Blocks (blue): Solid platforms with full collision
  - Platforms (green): Thin horizontal platforms
  - Spikes (red rectangles): Damage hazards
  - Triangles (red triangles): Damage hazards
- **Collision System**: Full collision detection for solid objects, damage on hazard contact
- **Save/Load Maps**: Maps saved to JSON file for persistence
- **User Interface**: Menu with Start/Build buttons, in-game back button, build mode clear button

## Requirements
- Python 3.x
- Pygame library (`pip install pygame`)

## How to Run
1. Ensure Python and Pygame are installed.
2. Navigate to the GD directory.
3. Run the game with: `python GD.py`

## Controls
- **Gameplay**: Arrow keys or WASD for movement, SPACE to jump
- **Build Mode**:
  - B: Select Block
  - P: Select Platform
  - S: Select Spike
  - T: Select Triangle
  - Left-click: Place object
  - Enter: Save map
  - Clear button: Remove all objects

## Project Structure
- `GD.py`: Main game script with classes (Button, Cube), game states, and physics
- `maps.json`: Saved map data (created automatically)
- `GD_projekt.md`: This documentation

## Status
Fully functional platformer with level editor. Features complete collision physics, multiple object types, and persistent map saving.

## Future Improvements
- Add more object types (moving platforms, portals)
- Implement scoring and level progression
- Add sound effects and background music
- Create predefined level packs
- Add particle effects for jumps and collisions