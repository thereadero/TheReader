# Isometric Jenga Game Documentation

This project is an isometric 3D-style Jenga simulation built with Python and `pygame`.
The player pushes blocks out of a tower, and the game restacks them at the top while checking tower stability.

## Overview

- The tower is built from 12 alternating layers of wooden blocks.
- Each layer alternates orientation between X and Y axes.
- The player can click a non-top-level block to slide it outward.
- If a slide completes, the block flies to the top of the stack and becomes part of a new level.
- The game ends when the tower becomes unstable and collapses.

## Controls

- `Left click` on a block to push it out.
- `R` key resets the game at any time.
- `Click` after game over to restart.

## Gameplay

1. Hover over a selectable block to highlight it.
2. Click to begin sliding the block out of the tower.
3. The block slides outward and then flies to the next available top position.
4. The game score increases each time a block successfully restacks.
5. The tower is continuously checked for support, and collapse ends the game.

## Features

- **Isometric rendering** of 3D block faces using custom projection.
- **Alternating block orientation** for authentic Jenga tower structure.
- **Block hover highlighting** and click-based interaction.
- **Dynamic camera scroll** as the tower grows taller.
- **Support-based collapse detection** using a simplified center-of-mass stability check.
- **Smooth animation** for sliding and flying blocks.

## Requirements

- Python 3.x
- `pygame` (`pip install pygame`)

## How to run

1. Open a terminal in the `jenga` folder.
2. Run `python jenga.py`.

## Technical details

### Isometric projection

- The game projects 3D block corner coordinates into 2D screen space using an isometric transform.
- `project(x, y, z)` converts world coordinates to screen coordinates.

### Block states

Each block can be in one of the following states:

- `idle`: The block is part of the stable stack.
- `sliding`: The player pushed the block outward.
- `flying`: The block is moving to its new top-level position.

### Stability check

- The game verifies support for each level below the tallest.
- It computes the center-of-mass of blocks above a given level.
- If the center-of-mass falls outside the supporting blocks on that level, the tower collapses.
- A small margin is included for better game feel.

### Code structure

- `Block` class handles geometry, rendering, hover detection, and animation.
- `JengaGame` class manages game state, input, camera movement, tower reset, and stability.
- The main loop updates block state, checks stability, and renders the scene.

## Customization

You can adjust constants in `jenga.py` to change gameplay and visuals:

- `WIDTH`, `HEIGHT`: Window size.
- `FPS`: Frame rate.
- `L`, `W`, `H`, `GAP`: Block size and spacing.
- `ISO_COS`, `ISO_SIN`: Isometric projection factors.
- `slide_speed`, `flight_speed`: Block animation speed.
