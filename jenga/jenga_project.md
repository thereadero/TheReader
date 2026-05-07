# Physics Jenga Documentation

This project is a 2D physics-based simulation of the classic Jenga game, built using Python and the `pygame` library.

## Overview
The game simulates a tower of wooden blocks that the player can interact with. The goal is to remove blocks from the tower without causing it to collapse. The simulation uses a custom AABB (Axis-Aligned Bounding Box) physics engine to handle gravity, friction, and collisions.

## Features
- **Custom Physics**: Simple but effective 2D rigid body simulation.
- **Alternating Layers**: Simulates the 3D structure of Jenga by alternating between "Front View" (single wide block) and "Side View" (three narrow blocks).
- **Interactive Dragging**: Players can grab and pull blocks using the mouse.
- **Visual Feedback**: Blocks highlight when hovered or dragged.
- **Game State Management**: Detects tower collapse and provides a restart option.

## Requirements
- Python 3.x
- Pygame (`pip install pygame`)

## How to Play
1. **Launch the game**: Run `python jenga.py`.
2. **Interact**: 
   - Hover over a block to see it highlight in gold.
   - Click and hold a block to drag it.
   - Pull the block out of the tower carefully.
3. **Restart**: If the tower falls (any block goes off-screen), click anywhere to reset the game.

## Code Structure

### 1. Configuration (Lines 5-27)
Defines constants for the window size, FPS, colors, and physics parameters like `GRAVITY` and `FRICTION`.

### 2. `Block` Class (Lines 29-68)
Represents a single block in the game.
- **Attributes**:
  - `rect`: A `pygame.Rect` for collision and drawing.
  - `x, y`: Float coordinates for smooth movement.
  - `vx, vy`: Velocity components.
  - `is_static`: If true, the block doesn't move (used for the base table).
- **Methods**:
  - `update()`: Applies gravity and friction, updates position.
  - `draw(surface)`: Renders the block with textures and highlights.

### 3. `JengaGame` Class (Lines 70-224)
The main controller for the game.
- **`reset()`**: Initializes the tower structure.
- **`handle_collisions()`**: The core physics routine. It iterates through all blocks and resolves overlaps using AABB logic. It runs multiple passes per frame to improve stability.
- **`run()`**: The main game loop handling events, updates, and rendering.

## Physics Implementation Details
The game uses a **Position-Based Dynamics** approach for collisions:
1. **Overlap Detection**: Calculates how much two blocks overlap on the X and Y axes.
2. **Resolution**: Pushes the blocks apart along the axis of least penetration.
3. **Friction**: Horizontal velocity is reduced over time to simulate resistance.
4. **Stability**: The `handle_collisions` method runs 3 iterations per frame to prevent "sinking" and jittering in the stack.

## Customization
You can modify the game behavior by changing constants in `jenga.py`:
- `TOWER_LEVELS`: Increase for a taller, more unstable tower.
- `BLOCK_WIDTH / BLOCK_HEIGHT`: Changes block dimensions.
- `GRAVITY`: Adjust to change how fast things fall.
- `DRAG_STRENGTH`: Controls how "heavy" the blocks feel when dragging.
