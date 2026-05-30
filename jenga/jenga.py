import pygame
import math
import random

# --- Configuration ---
WIDTH, HEIGHT = 900, 900
FPS = 60

# Colors
BACKGROUND = (18, 18, 24)
WOOD_TOP = (230, 200, 160)
WOOD_SIDE_L = (180, 150, 110)
WOOD_SIDE_R = (140, 110, 80)
ACCENT = (255, 80, 50)
GOLD = (255, 215, 0)
WHITE = (245, 245, 245)
SHADOW = (0, 0, 0, 80)

# Block dimensions (scaled down to fit better)
L = 150
W = 50
H = 30
GAP = 3

# Isometric settings
ISO_COS = 0.866
ISO_SIN = 0.5

# Camera settings
CAMERA_Y = 0

def project(x, y, z):
    """
    Projects 3D world coordinates (x, y, z) into 2D screen coordinates (screen_x, screen_y)
    using a classic isometric projection.
    
    Parameters:
        x (float): The X coordinate in world space.
        y (float): The Y coordinate in world space.
        z (float): The Z coordinate in world space (height).
        
    Returns:
        (int, int): The projected (X, Y) coordinates on the 2D screen.
    """
    # The reference floor Y position on screen where the bottom of the tower is anchored.
    floor_y = HEIGHT * 0.75
    
    # Calculate isometric X coordinate: X and Y map symmetrically in opposite directions.
    screen_x = WIDTH // 2 + (x - y) * ISO_COS
    
    # Calculate isometric Y coordinate: X and Y map symmetrically downwards,
    # and Z subtracts from the Y coordinate to project height vertically.
    # CAMERA_Y shifts everything vertically to keep the top of the tower in view.
    screen_y = (floor_y + CAMERA_Y) + (x + y) * ISO_SIN - z
    return int(screen_x), int(screen_y)

class Block:
    """
    Represents an individual Jenga block.
    Responsible for tracking its position, spatial state, visual attributes,
    grain calculation, rendering logic, and collision detection.
    """
    def __init__(self, level, index, orientation):
        """
        Initializes a Jenga block with its logical position and orientation.
        
        Parameters:
            level (int): The vertical level layer (0 is the bottom layer).
            index (int): The block position within its level (0, 1, or 2).
            orientation (int): The rotation of the layer (0 for parallel to X-axis, 1 for Y-axis).
        """
        self.level = level
        self.index = index
        self.orientation = orientation  # 0: Parallel to X, 1: Parallel to Y
        self.offset = 0.0               # How far the block has been slid out (used in animation & physics)
        self.state = "idle"             # Current state: "idle" (stationary), "sliding" (moving out), "flying" (flying to top)
        self.slide_dir = 1              # Direction of sliding (1: positive direction, -1: negative direction)
        self.slide_speed = 10.0         # Units per frame for the sliding animation
        self.hovered = False            # True when mouse cursor is pointing at this block
        self._cache_frame = -1          # Cache identifiers for potential render optimizations
        self._cached_corners = None
        self._cached_projected = None
        
        # Flight animation state variables
        self.flight_progress = 0.0      # Interpolation factor from 0.0 (start) to 1.0 (destination)
        self.flight_speed = 0.03        # Increment added to progress per frame
        self.flight_start_info = None   # Tuple of (x, y, z, angle) at departure
        self.flight_end_info = None     # Tuple of (x, y, z, angle) at arrival
        
        # Color palettes for block faces (wood shading)
        self.color_top = WOOD_TOP
        self.color_l = WOOD_SIDE_L
        self.color_r = WOOD_SIDE_R
        
        # Pre-calculated procedural wood grain texture lines for each visible face
        self.grain_lines = {
            "top": self._generate_grain(),
            "left": self._generate_grain(),
            "right": self._generate_grain()
        }

    def _generate_grain(self):
        """
        Generates procedural parameters for wood grain texture lines on a single face.
        Each grain line is defined by interpolation points, thickness, and transparency.
        
        Returns:
            list of tuple: List containing (t1, t2, side, width, alpha) for each line.
        """
        lines = []
        for _ in range(12):  # 12 grain lines per face for detailed, high-quality wood rendering
            t1 = random.random()
            t2 = random.random()
            # Determine if the grain line runs horizontally (0) or vertically (1) across the face
            side = random.choice([0, 1]) 
            width = random.uniform(0.5, 1.5)  # Randomized thickness
            alpha = random.randint(30, 70)    # Randomized opacity (out of 255) for subtle blending
            lines.append((t1, t2, side, width, alpha))
        return lines

    def get_world_corners(self, level, index, orientation, offset=0):
        """
        Calculates the 3D world space coordinates of the 8 corners of the block
        based on its static grid position, orientation, and slide offset.
        
        Parameters:
            level (int): Logical level height.
            index (int): Column index.
            orientation (int): Orientation layout.
            offset (float): Sliding offset.
            
        Returns:
            list of tuple: 8 points in (x, y, z) coordinates.
        """
        # Start coordinate offset to center the 3 blocks on the base
        start = -L / 2
        
        if orientation == 0:
            # Parallel to X: length runs along X-axis, width indexes along Y-axis
            cx = offset
            cy = start + index * (W + GAP) + W / 2
            angle = 0
        else:
            # Parallel to Y: width indexes along X-axis, length runs along Y-axis
            cx = start + index * (W + GAP) + W / 2
            cy = offset
            angle = 90
            
        # Middle Z coordinate of the block
        cz = level * H + H / 2
        return self.get_corners_from_params(cx, cy, cz, angle)

    def get_corners_from_params(self, cx, cy, cz, angle):
        """
        Calculates the 8 corner vertices in 3D world space given the block's
        center coordinates and rotation angle.
        
        Parameters:
            cx, cy, cz (float): Center point coordinates in world space.
            angle (float): Rotation angle in degrees around the Z axis.
            
        Returns:
            list of tuple: 8 corner coordinates in (x, y, z) order.
        """
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        hw, hl, hh = W/2, L/2, H/2
        
        # 8 local corner vertices centered at (0, 0, 0)
        # Vertices 0-3 form the bottom face, 4-7 form the top face
        local_corners = [
            (-hl, -hw, -hh), (hl, -hw, -hh), (hl, hw, -hh), (-hl, hw, -hh),
            (-hl, -hw, hh), (hl, -hw, hh), (hl, hw, hh), (-hl, hw, hh),
        ]
        
        world_corners = []
        for lx, ly, lz in local_corners:
            # Rotate local coordinates about Z-axis
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            # Translate to final world position
            world_corners.append((cx + rx, cy + ry, cz + lz))
        return world_corners

    def _get_current_corners(self):
        """
        Calculates the current 3D world corners of the block, taking into account
        whether the block is static, sliding, or flying.
        
        If the block is flying, its coordinates are interpolated using a smooth-step
        function (ease-in-out) and a sine arc offset is added to the Z coordinate to
        simulate a realistic lifting/tossing motion.
        
        Returns:
            list of tuple: 8 corner points in world space.
        """
        if self.state == "flying" and self.flight_start_info is not None:
            t = self.flight_progress
            # Smoothstep easing equation: y = 3t^2 - 2t^3
            smooth_t = t * t * (3 - 2 * t)
            
            s_x, s_y, s_z, s_a = self.flight_start_info
            e_x, e_y, e_z, e_a = self.flight_end_info
            
            # Linear interpolation of center position using the smooth step progress
            cx = s_x + (e_x - s_x) * smooth_t
            cy = s_y + (e_y - s_y) * smooth_t
            cz = s_z + (e_z - s_z) * smooth_t
            
            # Interpolate rotation angle
            angle = s_a + (e_a - s_a) * smooth_t
            
            # Add an arc height offset peaking in the middle of the flight trajectory (250 pixels max height)
            arc = math.sin(smooth_t * math.pi) * 250
            return self.get_corners_from_params(cx, cy, cz + arc, angle)
        
        # If not flying, return corners based on standard position + slide offset
        return self.get_world_corners(self.level, self.index, self.orientation, self.offset)

    def get_depth(self):
        """
        Calculates a depth key for the block to implement Painter's Algorithm.
        Blocks are rendered back-to-front. Greater vertical height (Z) and 
        further screen positions (X and Y in isometric space) dictate rendering order.
        
        Returns:
            float: A composite depth key where larger values represent blocks closer to the viewer.
        """
        corners = self._get_current_corners()
        avg_x = sum(c[0] for c in corners) / 8
        avg_y = sum(c[1] for c in corners) / 8
        avg_z = sum(c[2] for c in corners) / 8
        # Z has the highest priority in depth sorting for isometric layers,
        # followed by the sum of X and Y coordinates.
        return avg_z * 1000 + (avg_x + avg_y)

    def draw(self, surface):
        """
        Renders the Jenga block on the Pygame screen.
        Applies isometric projection, back-face culling via Shoelace winding,
        face coloring, procedural grain lines, and outer outlines/edge highlights.
        
        Parameters:
            surface (pygame.Surface): The Pygame screen or surface to draw on.
        """
        world_corners = self._get_current_corners()
        corners = [project(*c) for c in world_corners]
        
        # Define the corner index combinations that make up the 6 faces of the 3D block.
        # Corners 0-3 are the base (lower Z), 4-7 are the top (higher Z).
        # Top face: [4, 5, 6, 7], bottom: [1, 0, 3, 2], etc.
        face_configs = [
            ([4, 5, 6, 7], self.color_top, "top"),      # Top face (+z)
            ([5, 1, 2, 6], self.color_r, "right"),     # +X Face (End)
            ([6, 2, 3, 7], self.color_l, "left"),      # +Y Face (Side)
            ([7, 3, 0, 4], self.color_r, "right"),     # -X Face (End)
            ([4, 0, 1, 5], self.color_l, "left"),      # -Y Face (Side)
            ([1, 0, 3, 2], self.color_top, "top"),      # Bottom face (-z)
        ]
        
        for idxs, color, face_key in face_configs:
            face = [corners[i] for i in idxs]
            
            # Shoelace formula / Winding Order check to determine face visibility (back-face culling).
            # This prevents rendering faces that face away from the screen camera.
            # Area = 0.5 * sum(xi * yi+1 - xi+1 * yi)
            area = 0
            for i in range(len(face)):
                p1 = face[i]
                p2 = face[(i+1) % len(face)]
                area += (p1[0] * p2[1] - p2[0] * p1[1])
            
            if area > 0:  # If winding order area is positive, the face is visible
                # Determine final color: highlight top face with gold if hovered, or brighten side faces
                c = GOLD if (self.hovered and face_key == "top") else color
                if self.hovered:
                    # Apply hover highlight effect by brightening RGB values
                    c = tuple(min(255, val + 40) for val in c)
                
                # Draw the main polygon face
                pygame.draw.polygon(surface, c, face)
                
                # Procedural Wood Grain Drawing
                # Grain lines are slightly darker than the base color of the face
                grain_color = tuple(max(0, val - 30) for val in c)
                # Calculate vectors along the edges of the 2D projected polygon face
                v1 = (face[1][0] - face[0][0], face[1][1] - face[0][1])
                v2 = (face[3][0] - face[0][0], face[3][1] - face[0][1])
                
                for t1, t2, side, width, alpha in self.grain_lines[face_key]:
                    # Interpolate positions across the face to map the grain line endpoints
                    p1 = (face[0][0] + v1[0] * t1, face[0][1] + v1[1] * t1)
                    p2 = (face[3][0] + v1[0] * t2, face[3][1] + v1[1] * t2)
                    
                    # Blend the grain color with the background color using alpha to simulate transparency
                    ratio = alpha / 255.0
                    mixed = tuple(int(c[i] * (1 - ratio) + grain_color[i] * ratio) for i in range(3))
                    pygame.draw.line(surface, mixed, p1, p2, int(width))

                # Draw the face border outline to separate blocks visually
                pygame.draw.polygon(surface, (30, 25, 20), face, 2)

        # Draw extra light-colored highlights on the top edges (corners 4-7) for realistic 3D specular edge definition
        pygame.draw.line(surface, (255, 255, 255, 80), corners[4], corners[5], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[5], corners[6], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[6], corners[7], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[7], corners[4], 2)

    def update(self):
        """
        Updates the block's physical and animation state.
        
        Transitions:
            - If "sliding": Increment offset. Once slid past a threshold (1.5 * length),
              transition the block to the "flying" state.
            - If "flying": Increment flight progress. Once progress reaches 1.0,
              cap it and let the main game loop finalize its restacking onto the top.
        """
        if self.state == "sliding":
            self.offset += self.slide_dir * self.slide_speed
            # If the block has slid out far enough, launch it into the air
            if abs(self.offset) > L * 1.5:
                self.state = "flying"
                self.flight_progress = 0.0
        elif self.state == "flying":
            self.flight_progress += self.flight_speed
            if self.flight_progress >= 1.0:
                self.flight_progress = 1.0
                self.state = "idle"  # Will be processed and finalized by the game loop

    def is_clicked(self, mx, my):
        """
        Checks if the mouse cursor coordinates (mx, my) fall inside any of
        the visible projected faces of this block.
        
        Parameters:
            mx (int): Mouse X position on the screen.
            my (int): Mouse Y position on the screen.
            
        Returns:
            bool: True if the mouse clicked on this block, False otherwise.
        """
        world_corners = self._get_current_corners()
        corners = [project(*c) for c in world_corners]
        
        # Vertex combinations for all 6 faces of the block
        face_indices = [[4, 5, 6, 7], [5, 1, 2, 6], [6, 2, 3, 7], [7, 3, 0, 4], [4, 0, 1, 5], [1, 0, 3, 2]]
        for idxs in face_indices:
            face = [corners[i] for i in idxs]
            # Perform visibility check (only check faces facing the camera)
            area = 0
            for i in range(len(face)):
                p1 = face[i]
                p2 = face[(i+1) % len(face)]
                area += (p1[0] * p2[1] - p2[0] * p1[1])
            
            if area > 0:
                # If visible, check if mouse cursor is within the polygon boundaries
                if self.point_in_poly(mx, my, face):
                    return True
        return False

    def point_in_poly(self, x, y, poly):
        """
        Ray-casting algorithm (even-odd rule) to check if a 2D point (x, y)
        is inside a 2D polygon.
        
        Parameters:
            x (float): Target X coordinate.
            y (float): Target Y coordinate.
            poly (list of tuple): List of vertices defining the polygon.
            
        Returns:
            bool: True if inside, False otherwise.
        """
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(1, n + 1):
            p2x, p2y = poly[i % n]
            # Check if the ray intersects the polygon's edge
            if (p1y > y) != (p2y > y):  # Scanline crossings check
                # Calculate the X coordinate of the intersection point of the ray
                xints = (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x
                if x < xints:
                    inside = not inside
            p1x, p1y = p2x, p2y
        return inside

class JengaGame:
    """
    Main controller class for the Isometric Jenga Game.
    Manages initialization, window display, game state resets, camera controls,
    block restacking animations, continuous stability checking, and the game loop.
    """
    def __init__(self):
        """
        Initializes Pygame, setups the window screen, creates fonts, and resets state.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Isometric Jenga")
        self.clock = pygame.time.Clock()
        
        # Load custom fonts with fallbacks for UI styling
        self.font = pygame.font.SysFont("Outfit, Inter, Arial", 32)
        self.title_font = pygame.font.SysFont("Outfit, Inter, Arial", 64, bold=True)
        
        self.reset()

    def reset(self):
        """
        Resets the entire game state to start a new round.
        Re-initializes 12 layers of 3 blocks each, resetting scores, camera, and magic pulls.
        """
        self.blocks = []
        self.levels = 12
        # Initialize blocks layer by layer
        for level in range(self.levels):
            # Alternating orientation for each layer: 0 (X-axis) or 1 (Y-axis)
            orientation = level % 2
            for i in range(3):
                self.blocks.append(Block(level, i, orientation))
        
        self.game_over = False
        self.score = 0
        self.sliding_block = None
        self.target_camera_y = 0
        global CAMERA_Y
        CAMERA_Y = 0
        self.magic_pulls = 0
        self.magically_supported_levels = set()  # Tracks levels currently levitating
        self.magic_message_text = ""
        self.magic_message_timer = 0             # Countdown timer (frames) for showing banner notifications

    def get_top_info(self):
        """
        Finds the current maximum level of the tower and counts how many blocks
        are resting on that top level.
        
        Returns:
            (int, int): Tuple of (max_level_index, number_of_blocks_on_top_level).
        """
        max_level = -1
        for b in self.blocks:
            if b.level > max_level:
                max_level = b.level
        
        # Find all blocks currently residing on the highest level
        top_blocks = [b for b in self.blocks if b.level == max_level]
        return max_level, len(top_blocks)

    def prepare_flight(self, block):
        """
        Calculates and stores the start and end coordinates for a block's flight animation.
        A block flies from its slid-out position to the highest level, filling up empty
        slots or initiating a brand-new layer if the current one is full.
        
        Parameters:
            block (Block): The block to prepare flight parameters for.
        """
        max_level, count = self.get_top_info()
        
        # If the top level is incomplete (< 3 blocks), place the flying block there.
        # Otherwise, start a new level on top.
        if count < 3:
            target_level = max_level
            target_index = count
        else:
            target_level = max_level + 1
            target_index = 0
            
        # Capture current slid-out parameters to use as flight departure point
        start = -L / 2
        if block.orientation == 0:
            s_cx, s_cy, s_angle = block.offset, start + block.index * (W + GAP) + W / 2, 0
        else:
            s_cx, s_cy, s_angle = start + block.index * (W + GAP) + W / 2, block.offset, 90
        s_cz = block.level * H + H / 2
        block.flight_start_info = (s_cx, s_cy, s_cz, s_angle)
        
        # Calculate target destination coordinates on top of the tower
        target_orientation = target_level % 2
        if target_orientation == 0:
            e_cx, e_cy, e_angle = 0, start + target_index * (W + GAP) + W / 2, 0
        else:
            e_cx, e_cy, e_angle = start + target_index * (W + GAP) + W / 2, 0, 90
        e_cz = target_level * H + H / 2
        block.flight_end_info = (e_cx, e_cy, e_cz, e_angle)
        
        # Assign targets to block state
        block.target_level = target_level
        block.target_index = target_index
        block.target_orientation = target_orientation
        block.flight_progress = 0.0

    def finalize_restack(self, block):
        """
        Updates the block's logical state to its new position on top of the tower
        upon completing its flight, resets its offset, increases the player's score,
        and handles awarding new Magic Pulls.
        
        Parameters:
            block (Block): The block that finished flying.
        """
        block.level = block.target_level
        block.index = block.target_index
        block.orientation = block.target_orientation
        block.offset = 0
        block.state = "idle"
        self.score += 1
        
        # Earn a Magic Pull every 20 points
        if self.score > 0 and self.score % 20 == 0:
            self.magic_pulls += 1
            self.magic_message_text = "MAGIC PULL EARNED!"
            self.magic_message_timer = 180  # Display banner for 3 seconds (180 frames @ 60 FPS)

    def check_stability(self):
        """
        Calculates the center of mass (CoM) for each level to simulate tower stability.
        
        For each level l from the ground up:
            1. Skip the level check if it has levitation active (Magic Pull).
            2. Identify support blocks on level l. A block supports if it's not flying
               and not slid out past half of its length (|offset| < L/2).
            3. If zero support blocks exist on level l, the tower is unstable.
            4. Compute the combined center of mass (CoM) for all blocks above level l.
            5. Verify if the CoM projects within the support footprint of the blocks on level l.
               If it falls outside, the tower collapses.
               
        Returns:
            bool: True if the tower remains standing, False if it collapses.
        """
        max_level, _ = self.get_top_info()
        
        # We'll treat every block as mass 1.
        # Flying blocks have no mass (don't contribute to weight).
        
        for l in range(max_level):
            # Skip stability calculations for any level that is currently levitating
            if l in self.magically_supported_levels:
                continue
                
            # Filter blocks that are physically supporting level l
            # Blocks that have flown or have been pushed out more than L/2 are not supporting
            support_blocks = [b for b in self.blocks if b.level == l and b.state != "flying" and abs(b.offset) < L/2]
            if not support_blocks:
                # If there are no blocks supporting this level, the tower immediately collapses
                return False
            
            # Identify the collection of blocks whose weight rests on level l (levels above l)
            # We omit currently flying blocks since they are in the air and weightless
            supported_mass_blocks = [b for b in self.blocks if b.level > l and b.state != "flying"]
            if not supported_mass_blocks:
                continue  # If there are no blocks above this level, it cannot tip over
                
            # Calculate Center of Mass (CoM) of the aggregate stack of blocks above level l
            total_x = 0
            total_y = 0
            for b in supported_mass_blocks:
                # Find the center coordinates of each supported block
                start = -L / 2
                if b.orientation == 0:
                    cx, cy = b.offset, start + b.index * (W + GAP) + W / 2
                else:
                    cx, cy = start + b.index * (W + GAP) + W / 2, b.offset
                total_x += cx
                total_y += cy
            
            com_x = total_x / len(supported_mass_blocks)
            com_y = total_y / len(supported_mass_blocks)
            
            # Find the boundaries of the support base formed by the blocks on level l
            orientation = l % 2
            start = -L / 2
            if orientation == 0:
                # Level l blocks run parallel to X. Support is critical on the Y axis.
                min_y = min(start + b.index * (W + GAP) for b in support_blocks)
                max_y = max(start + b.index * (W + GAP) + W for b in support_blocks)
                
                # Check if Center of Mass Y-projection lies within support range [min_y, max_y]
                # We allow a small tolerance margin of 5 units to make gameplay feel fairer
                if com_y < min_y - 5 or com_y > max_y + 5:
                    return False
            else:
                # Level l blocks run parallel to Y. Support is critical on the X axis.
                min_x = min(start + b.index * (W + GAP) for b in support_blocks)
                max_x = max(start + b.index * (W + GAP) + W for b in support_blocks)
                
                # Check if Center of Mass X-projection lies within support range [min_x, max_x]
                if com_x < min_x - 5 or com_x > max_x + 5:
                    return False
        
        return True

    def draw_magic_field(self, l):
        """
        Renders a glowing, pulsating holographic levitation grid below a level
        that has been stabilized using a Magic Pull.
        
        Parameters:
            l (int): The level index (0-indexed height) to render the field for.
        """
        z = l * H
        magic_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Calculate a pulsating alpha transparency value using game runtime ticks
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 15 + 40
        
        # Define the boundary vertices of the levitation grid (slightly larger than block dimensions)
        magic_poly = [
            project(-L * 0.55, -L * 0.55, z),
            project(L * 0.55, -L * 0.55, z),
            project(L * 0.55, L * 0.55, z),
            project(-L * 0.55, L * 0.55, z)
        ]
        
        # Draw transparent turquoise filled polygon and a solid boundary line
        pygame.draw.polygon(magic_surf, (0, 255, 220, int(pulse)), magic_poly)
        pygame.draw.polygon(magic_surf, (0, 255, 220, 180), magic_poly, 3)
        
        # Draw concentric detail sub-grids inside the field for a sci-fi effect
        for scale in [0.2, 0.4, 0.6, 0.8]:
            scaled_poly = [
                project(-L * 0.55 * scale, -L * 0.55 * scale, z),
                project(L * 0.55 * scale, -L * 0.55 * scale, z),
                project(L * 0.55 * scale, L * 0.55 * scale, z),
                project(-L * 0.55 * scale, L * 0.55 * scale, z)
            ]
            pygame.draw.polygon(magic_surf, (0, 255, 220, 80), scaled_poly, 1)
            
        self.screen.blit(magic_surf, (0, 0))

    def run(self):
        """
        The main game loop. Handles FPS throttling, user mouse clicks, camera updates,
        state updates of Jenga blocks, rendering order, and display presentation.
        """
        running = True
        hovered_block = None
        while running:
            # Capture current mouse screen coordinates
            mx, my = pygame.mouse.get_pos()
            
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        # Reset game state if player clicks after a collapse
                        self.reset()
                    elif not self.sliding_block:
                        # Sort blocks by depth to interact with the front-most block under cursor first
                        sorted_blocks = sorted(self.blocks, key=lambda b: b.get_depth(), reverse=True)
                        for b in sorted_blocks:
                            # The top level of the tower is locked and cannot be pulled
                            max_l, _ = self.get_top_info()
                            if b.level == max_l:
                                continue
                            
                            if b.is_clicked(mx, my):
                                # Determine if this block is the only remaining support on its level
                                level_blocks = [x for x in self.blocks if x.level == b.level]
                                if len(level_blocks) == 1:
                                    # Consume a Magic Pull to levitate and save the level if available
                                    if self.magic_pulls > 0:
                                        self.magic_pulls -= 1
                                        self.magically_supported_levels.add(b.level)
                                        self.magic_message_text = f"LEVEL {b.level + 1} LEVITATION ACTIVATED!"
                                        self.magic_message_timer = 180
                                    else:
                                        # Tower will collapse when checked
                                        pass
                                
                                # Initiate sliding state
                                b.state = "sliding"
                                # Edge blocks slide away from center, center blocks slide randomly
                                if b.index == 0:
                                    b.slide_dir = -1
                                elif b.index == 2:
                                    b.slide_dir = 1
                                else:
                                    b.slide_dir = random.choice([1, -1])
                                self.sliding_block = b
                                break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Press 'R' to reset and start a new game manually
                        self.reset()

            # --- Camera Scrolling Update ---
            max_level, _ = self.get_top_info()
            # Calculate target camera offset to keep the top of the tower centered at y ~ 150px
            floor_y = HEIGHT * 0.75
            max_z = max_level * H
            self.target_camera_y = max(0, 150 - floor_y + max_z)
            
            # Apply smooth linear interpolation (Lerp) to slide the camera position
            global CAMERA_Y
            CAMERA_Y += (self.target_camera_y - CAMERA_Y) * 0.08

            # --- State Updates ---
            if not self.game_over:
                # Update block hover highlights (only hover front-most visible block under cursor)
                hovered_block = None
                if not self.sliding_block:
                    sorted_blocks = sorted(self.blocks, key=lambda b: b.get_depth(), reverse=True)
                    max_l, _ = self.get_top_info()
                    for b in sorted_blocks:
                        if b.level == max_l:
                            continue  # Top level cannot be clicked or hovered
                        if b.is_clicked(mx, my):
                            hovered_block = b
                            break

                for b in self.blocks:
                    b.hovered = (b == hovered_block)
                    
                    old_state = b.state
                    b.update()
                    
                    # Transition from sliding to flying when block exits tower bounds
                    if old_state == "sliding" and b.state == "flying":
                        self.prepare_flight(b)
                
                # Check if sliding block has completed its flight back onto the top
                if self.sliding_block and self.sliding_block.state == "idle":
                    self.finalize_restack(self.sliding_block)
                    self.sliding_block = None
                
                # Continuously monitor tower stability
                if not self.check_stability():
                    self.game_over = True

            # --- Drawing Pipeline ---
            self.screen.fill(BACKGROUND)
            
            # 1. Render floor shadow below the tower
            shadow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shadow_poly = [
                project(-L*0.6, -L*0.6, 0),
                project(L*0.6, -L*0.6, 0),
                project(L*0.6, L*0.6, 0),
                project(-L*0.6, L*0.6, 0)
            ]
            pygame.draw.polygon(shadow_surf, (0, 0, 0, 80), shadow_poly)
            self.screen.blit(shadow_surf, (0, 0))

            # 2. Render base platform/table structure
            base_poly = [
                project(-L*0.75, -L*0.75, 0),
                project(L*0.75, -L*0.75, 0),
                project(L*0.75, L*0.75, 0),
                project(-L*0.75, L*0.75, 0)
            ]
            pygame.draw.polygon(self.screen, (30, 30, 40), base_poly)
            pygame.draw.polygon(self.screen, (50, 50, 70), base_poly, 2)

            # 3. Sort drawables (blocks and magic fields) and render back-to-front
            drawables = []
            for b in self.blocks:
                drawables.append((b.get_depth(), b))
            for l in self.magically_supported_levels:
                # Place levitation field depths right around their respective levels
                depth = (l * H + H / 2) * 1000
                drawables.append((depth, ("magic_field", l)))
            
            # Sort by depth key (Painter's Algorithm)
            drawables.sort(key=lambda x: x[0])
            for _, item in drawables:
                if isinstance(item, Block):
                    item.draw(self.screen)
                else:
                    _, l = item
                    self.draw_magic_field(l)
            
            # 4. Render interactive mouse tooltip warnings
            if not self.game_over and hovered_block:
                level_blocks = [x for x in self.blocks if x.level == hovered_block.level]
                if len(level_blocks) == 1:
                    # Last block warning tooltip customization
                    if self.magic_pulls > 0:
                        tooltip_text = "Last Block! (Will use Magic Pull)"
                        tooltip_color = (0, 255, 200)
                    else:
                        tooltip_text = "WARNING: Last Block! (Will fall!)"
                        tooltip_color = ACCENT
                    
                    txt = self.font.render(tooltip_text, True, tooltip_color)
                    tooltip_w, tooltip_h = txt.get_size()
                    # Keep tooltip bounding box safely inside window edges
                    tx = min(mx + 15, WIDTH - tooltip_w - 20)
                    ty = min(my - 25, HEIGHT - tooltip_h - 20)
                    
                    tip_surf = pygame.Surface((tooltip_w + 16, tooltip_h + 8), pygame.SRCALPHA)
                    tip_surf.fill((18, 18, 24, 220))
                    pygame.draw.rect(tip_surf, tooltip_color, tip_surf.get_rect(), 1, border_radius=4)
                    
                    self.screen.blit(tip_surf, (tx, ty))
                    self.screen.blit(txt, (tx + 8, ty + 4))

            # 5. Render scores & game UI text
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (30, 30))
            
            # Render magic pull resources UI
            if self.magic_pulls > 0:
                pulse = int(127 + 128 * math.sin(pygame.time.get_ticks() * 0.01))
                magic_color = (0, pulse, 255)
                magic_text = self.font.render(f"Magic Pulls: {self.magic_pulls} (ACTIVE)", True, magic_color)
            else:
                magic_text = self.font.render(f"Magic Pulls: 0 (Earn at 20 pts)", True, (120, 120, 120))
            self.screen.blit(magic_text, (30, 70))
            
            # 6. Render levitation notification banners
            if self.magic_message_timer > 0:
                self.magic_message_timer -= 1
                banner_surf = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
                banner_surf.fill((0, 255, 220, 30))
                pygame.draw.line(banner_surf, (0, 255, 220, 180), (0, 0), (WIDTH, 0), 2)
                pygame.draw.line(banner_surf, (0, 255, 220, 180), (0, 58), (WIDTH, 58), 2)
                
                banner_text = self.font.render(self.magic_message_text, True, (0, 255, 220))
                banner_surf.blit(banner_text, (WIDTH // 2 - banner_text.get_width() // 2, 30 - banner_text.get_height() // 2))
                self.screen.blit(banner_surf, (0, 120))
            
            # 7. Render Game Over overlay / instructions
            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                self.screen.blit(overlay, (0, 0))
                
                msg = self.title_font.render("TOWER FELL!", True, ACCENT)
                self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
                
                retry = self.font.render("Click to Restart", True, WHITE)
                self.screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, HEIGHT // 2 + 50))
            else:
                instr = self.font.render("Click a block to push it out", True, WOOD_TOP)
                self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 60))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = JengaGame()
    game.run()
