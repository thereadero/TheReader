# Isometric Jenga Game Documentation

An interactive, physics-inspired isometric 3D Jenga simulation built using Python and `pygame`. 

The game combines traditional Jenga mechanics with visual depth projection, smooth trajectory animation, stability/center-of-mass calculations, and a special "Magic Pull" mechanic that lets players stabilize critical levels.

---

## Game Overview & Gameplay Loop

1. **Tower Structure**: 
   - The tower initializes with **12 layers** of wooden blocks.
   - Each level contains **3 blocks** aligned parallel to either the X-axis (even levels) or Y-axis (odd levels).
2. **Block Interactions**:
   - Hovering over a selectable block highlights it.
   - Left-clicking a block slides it out of the tower. 
     - Outer blocks slide outwards in their respective direction.
     - Middle blocks slide in a random direction.
     - The top-level blocks are locked and cannot be pulled.
3. **Restacking Mechanics**:
   - Once a block is pushed completely out of the tower, it transitions into a **flying** state.
   - The block travels along a parabolic arc to the top of the tower, completing a new layer.
   - Each successful restack increases the player's **Score** by `1`.
4. **Game Over**:
   - The game continuously checks the stability of the tower.
   - If the center of mass of the stack above any level falls outside its support base, the tower collapses, triggering a game over.
   - Pressing **`R`** resets the game at any time, and clicking after a game over restarts it.

---

## Features

* **3D Isometric Projection**: Custom-built projection transforming 3D coordinates `(x, y, z)` into 2D screen space.
* **Realistic Textures**: Pre-calculated wood grain styling, side/top face shading, outlines, and edge highlighting for an authentic wooden aesthetic.
* **Smooth Camera Scrolling**: Dynamic camera scroll that tracks the tower height, smoothly centering the active play area as the tower grows.
* **Center-of-Mass Stability Check**: Simulates weight distribution by determining if the aggregate center of mass of the upper blocks lies within the footprint of the supporting blocks on each level.
* **Interactive Tooltips**: Highlights dangerous moves (e.g., pulling the last block from a level) and shows real-time status.
* **Magic Pull & Levitation**: A gameplay mechanic allowing players to levitate levels and bypass stability checks.

---

## Controls

* **Mouse Hover**: Select and highlight blocks.
* **Left Click**: Pull/slide a block out, or restart the game when in the Game Over state.
* **`R` Key**: Reset the tower and score to start a new game.

---

## Advanced Mechanics

### 1. Magic Pulls & Level Levitation
* **Earning Pulls**: Players earn `1` **Magic Pull** for every **20 points** scored. A banner notification appears on the screen upon earning.
* **Activating Levitation**: 
  - If you attempt to pull the **last block** of a level:
    - **With a Magic Pull**: The Magic Pull is consumed, and that level becomes **magically levitated**. A glowing turquoise levitation grid is rendered below the level, and it is permanently exempted from all stability checks.
    - **Without a Magic Pull**: A red warning tooltip is shown, and pulling the block will cause the tower to collapse.
* **Tooltips**:
  - `Last Block! (Will use Magic Pull)` (Turquoise text) if a magic pull is available.
  - `WARNING: Last Block! (Will fall!)` (Red text) if no magic pulls are available.

### 2. Physics & Stability Simulation
The stability check runs continuously:
* For each level $l$ from the bottom up to the top:
  * If the level has **Levitation** active, it is skipped.
  * The game determines all *supporting* blocks at level $l$ (blocks that have not flown and are not slid outward past half their length, i.e., $|\text{offset}| < L/2$).
  * If zero support blocks remain, the tower collapses.
  * The center of mass (CoM) is computed for all blocks above level $l$:
    $$\text{CoM}_x = \frac{\sum x_i}{N}, \quad \text{CoM}_y = \frac{\sum y_i}{N}$$
  * Depending on the orientation of level $l$:
    * **X-Orientation (Parallel to X)**: The support is critical along the Y-axis. The tower remains stable if:
      $$\text{min\_y} - 5 \le \text{CoM}_y \le \text{max\_y} + 5$$
    * **Y-Orientation (Parallel to Y)**: The support is critical along the X-axis. The tower remains stable if:
      $$\text{min\_x} - 5 \le \text{CoM}_x \le \text{max\_x} + 5$$
  * If the center of mass falls outside these bounds, the tower collapses.

### 3. Flight Interpolation
When a block is flying to the top, its position is interpolated using a smooth-step easing function:
$$t_{\text{smooth}} = t^2 \times (3 - 2t) \quad \text{where } t \in [0, 1]$$
An arc offset is added to the Z coordinate to create a smooth lifting motion:
$$\text{arc} = \sin(t_{\text{smooth}} \times \pi) \times 250$$

---

## Technical Details

### Code Architecture
The code in [jenga.py] is structured around two main classes:

1. **`Block`**:
   - Manages block states (`idle`, `sliding`, `flying`).
   - Computes world space and screen coordinates of its 8 vertices.
   - Uses Shoelace winding order to perform back-face culling (ensuring only visible faces are drawn).
   - Generates randomized wood grain lines for the top, left, and right faces.
   - Detects clicks and mouse hovers using ray-casting/polygon-collision algorithms.
2. **`JengaGame`**:
   - Manages game state (score, game over state, magic pulls, and active camera).
   - Handles the Pygame event loop, updating and rendering base platforms, shadows, blocks, magic fields, and UI text elements.
   - Evaluates stability checks.

### File Requirements & Execution
* **Dependencies**: Python 3.x and `pygame`.
* **Installation**:
  ```bash
  pip install pygame
  ```
* **Execution**:
  Run the script from the directory containing the file:
  ```bash
  python jenga.py
  ```

---

## Customization Constants

You can tweak the constants at the top of [jenga.py] to change the game's visuals or difficulty:

* `L`, `W`, `H`, `GAP`: Block dimensions (Length, Width, Height) and spacing.
* `slide_speed` (inside `Block`): Speed at which blocks slide outward (default: `10.0`).
* `flight_speed` (inside `Block`): Step size for flight interpolation (default: `0.03`).
* `ISO_COS`, `ISO_SIN`: Isometric angles for visual rendering adjustments.
