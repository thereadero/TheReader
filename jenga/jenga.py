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
L = 160
W = 50
H = 30
GAP = 3

# Isometric settings
ISO_COS = 0.866
ISO_SIN = 0.5

def project(x, y, z):
    # Shift floor down to 75% of screen height to allow room for growth
    screen_x = WIDTH // 2 + (x - y) * ISO_COS
    screen_y = HEIGHT * 0.75 + (x + y) * ISO_SIN - z
    return int(screen_x), int(screen_y)

class Block:
    def __init__(self, level, index, orientation):
        self.level = level
        self.index = index
        self.orientation = orientation  # 0: Parallel to X, 1: Parallel to Y
        self.offset = 0.0
        self.state = "idle"  # "idle", "sliding", "flying"
        self.slide_dir = 1 # 1 or -1
        self.slide_speed = 10.0
        self.hovered = False
        
        # Animation data
        self.flight_progress = 0.0
        self.flight_speed = 0.03
        self.flight_start_info = None # (x, y, z, angle)
        self.flight_end_info = None   # (x, y, z, angle)
        
        self.color_top = WOOD_TOP
        self.color_l = WOOD_SIDE_L
        self.color_r = WOOD_SIDE_R
        
        # Pre-calculate grain lines for each face
        self.grain_lines = {
            "top": self._generate_grain(),
            "left": self._generate_grain(),
            "right": self._generate_grain()
        }

    def _generate_grain(self):
        lines = []
        for _ in range(6):
            t1 = random.random()
            t2 = random.random()
            side = random.choice([0, 1]) # Which sides to connect
            lines.append((t1, t2, side))
        return lines

    def get_world_corners(self, level, index, orientation, offset=0):
        # Calculate center and angle
        start = -L / 2
        if orientation == 0:
            cx = offset
            cy = start + index * (W + GAP) + W / 2
            angle = 0
        else:
            cx = start + index * (W + GAP) + W / 2
            cy = offset
            angle = 90
        cz = level * H + H / 2
        return self.get_corners_from_params(cx, cy, cz, angle)

    def get_corners_from_params(self, cx, cy, cz, angle):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        hw, hl, hh = W/2, L/2, H/2
        # Local coordinates (centered)
        local_corners = [
            (-hl, -hw, -hh), (hl, -hw, -hh), (hl, hw, -hh), (-hl, hw, -hh),
            (-hl, -hw, hh), (hl, -hw, hh), (hl, hw, hh), (-hl, hw, hh),
        ]
        
        world_corners = []
        for lx, ly, lz in local_corners:
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            world_corners.append((cx + rx, cy + ry, cz + lz))
        return world_corners

    def get_corners(self):
        if self.state == "flying" and self.flight_start_info is not None:
            t = self.flight_progress
            smooth_t = t * t * (3 - 2 * t)
            
            s_x, s_y, s_z, s_a = self.flight_start_info
            e_x, e_y, e_z, e_a = self.flight_end_info
            
            # Interpolate
            cx = s_x + (e_x - s_x) * smooth_t
            cy = s_y + (e_y - s_y) * smooth_t
            cz = s_z + (e_z - s_z) * smooth_t
            # Handle rotation (always take shortest path)
            angle = s_a + (e_a - s_a) * smooth_t
            
            # Parabolic arc
            arc = math.sin(smooth_t * math.pi) * 250
            
            return self.get_corners_from_params(cx, cy, cz + arc, angle)

        return self.get_world_corners(self.level, self.index, self.orientation, self.offset)

    def get_depth(self):
        corners = self.get_corners()
        avg_x = sum(c[0] for c in corners) / 8
        avg_y = sum(c[1] for c in corners) / 8
        avg_z = sum(c[2] for c in corners) / 8
        # Higher Z is always on top. Within the same level, higher X+Y is closer.
        return avg_z * 1000 + (avg_x + avg_y)

    def draw(self, surface):
        corners = [project(*c) for c in self.get_corners()]
        
        # Faces
        face_top = [corners[4], corners[5], corners[6], corners[7]]
        face_left = [corners[3], corners[2], corners[6], corners[7]]
        face_right = [corners[1], corners[2], corners[6], corners[5]]
        
        c_top = GOLD if self.hovered else self.color_top
        c_left = self.color_l
        c_right = self.color_r
        
        if self.hovered:
            c_left = tuple(min(255, c + 30) for c in c_left)
            c_right = tuple(min(255, c + 30) for c in c_right)

        # Draw faces with texture effect
        faces_info = [
            (face_right, c_right, "right"),
            (face_left, c_left, "left"),
            (face_top, c_top, "top")
        ]
        
        for face, color, face_key in faces_info:
            pygame.draw.polygon(surface, color, face)
            
            # Draw pre-calculated grain lines
            grain_color = tuple(max(0, c - 20) for c in color)
            v1 = (face[1][0] - face[0][0], face[1][1] - face[0][1])
            v2 = (face[3][0] - face[0][0], face[3][1] - face[0][1])
            
            for t1, t2, side in self.grain_lines[face_key]:
                # Connect points on opposite edges for a grain look
                p1 = (face[0][0] + v1[0] * t1, face[0][1] + v1[1] * t1)
                p2 = (face[3][0] + v1[0] * t2, face[3][1] + v1[1] * t2)
                pygame.draw.line(surface, grain_color, p1, p2, 1)

        # Highlights (edges)
        pygame.draw.line(surface, (255, 255, 255, 60), corners[4], corners[5], 2)
        pygame.draw.line(surface, (255, 255, 255, 60), corners[4], corners[7], 2)

        # Outlines
        pygame.draw.polygon(surface, (40, 30, 20), face_top, 1)
        pygame.draw.polygon(surface, (40, 30, 20), face_left, 1)
        pygame.draw.polygon(surface, (40, 30, 20), face_right, 1)

    def update(self):
        if self.state == "sliding":
            self.offset += self.slide_dir * self.slide_speed
            if abs(self.offset) > L * 1.5:
                self.state = "flying"
                self.flight_progress = 0.0
        elif self.state == "flying":
            self.flight_progress += self.flight_speed
            if self.flight_progress >= 1.0:
                self.flight_progress = 1.0
                self.state = "idle" # Will be finalized by game logic

    def is_clicked(self, mx, my):
        corners = [project(*c) for c in self.get_corners()]
        faces = [
            [corners[4], corners[5], corners[6], corners[7]],
            [corners[3], corners[2], corners[6], corners[7]],
            [corners[1], corners[2], corners[6], corners[5]]
        ]
        for face in faces:
            if self.point_in_poly(mx, my, face):
                return True
        return False

    def point_in_poly(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

class JengaGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Isometric Jenga")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Outfit, Inter, Arial", 32)
        self.title_font = pygame.font.SysFont("Outfit, Inter, Arial", 64, bold=True)
        
        self.reset()

    def reset(self):
        self.blocks = []
        self.levels = 12
        for level in range(self.levels):
            orientation = level % 2
            for i in range(3):
                self.blocks.append(Block(level, i, orientation))
        
        self.game_over = False
        self.score = 0
        self.sliding_block = None

    def get_top_info(self):
        max_level = -1
        for b in self.blocks:
            if b.level > max_level:
                max_level = b.level
        
        # Count blocks at top level
        top_blocks = [b for b in self.blocks if b.level == max_level]
        return max_level, len(top_blocks)

    def prepare_flight(self, block):
        max_level, count = self.get_top_info()
        
        if count < 3:
            target_level = max_level
            target_index = count
        else:
            target_level = max_level + 1
            target_index = 0
            
        # Start info (current)
        start = -L / 2
        if block.orientation == 0:
            s_cx, s_cy, s_angle = block.offset, start + block.index * (W + GAP) + W / 2, 0
        else:
            s_cx, s_cy, s_angle = start + block.index * (W + GAP) + W / 2, block.offset, 90
        s_cz = block.level * H + H / 2
        block.flight_start_info = (s_cx, s_cy, s_cz, s_angle)
        
        # End info (target)
        target_orientation = target_level % 2
        if target_orientation == 0:
            e_cx, e_cy, e_angle = 0, start + target_index * (W + GAP) + W / 2, 0
        else:
            e_cx, e_cy, e_angle = start + target_index * (W + GAP) + W / 2, 0, 90
        e_cz = target_level * H + H / 2
        block.flight_end_info = (e_cx, e_cy, e_cz, e_angle)
        
        block.target_level = target_level
        block.target_index = target_index
        block.target_orientation = target_orientation
        block.flight_progress = 0.0

    def finalize_restack(self, block):
        block.level = block.target_level
        block.index = block.target_index
        block.orientation = block.target_orientation
        block.offset = 0
        block.state = "idle"
        self.score += 1

    def check_stability(self):
        max_level, _ = self.get_top_info()
        for l in range(max_level):
            # Blocks that are sliding still provide some support, but flying ones don't.
            level_blocks = [b for b in self.blocks if b.level == l and b.state != "flying"]
            if len(level_blocks) == 0:
                return False
            if len(level_blocks) == 1 and level_blocks[0].index != 1:
                return False
        return True

    def run(self):
        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if self.sliding_block: continue
                    
                    # Sort blocks by depth to pick the front-most one
                    sorted_blocks = sorted(self.blocks, key=lambda b: b.get_depth(), reverse=True)
                    for b in sorted_blocks:
                        # Cannot pick from top level
                        max_l, _ = self.get_top_info()
                        if b.level == max_l: continue
                        
                        if b.is_clicked(mx, my):
                            b.state = "sliding"
                            # Slide direction: outer blocks slide out, middle slides random
                            if b.index == 0: b.slide_dir = -1
                            elif b.index == 2: b.slide_dir = 1
                            else: b.slide_dir = random.choice([1, -1])
                            self.sliding_block = b
                            break
                    
                    if self.game_over:
                        self.reset()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()

            # Update
            if not self.game_over:
                for b in self.blocks:
                    b.hovered = b.is_clicked(mx, my) and not self.sliding_block
                    
                    old_state = b.state
                    b.update()
                    
                    # Transition from sliding to flying
                    if old_state == "sliding" and b.state == "flying":
                        self.prepare_flight(b)
                
                if self.sliding_block and self.sliding_block.state == "idle":
                    # Finished flying
                    self.finalize_restack(self.sliding_block)
                    self.sliding_block = None
                
                # Continuous stability check
                if not self.check_stability():
                    self.game_over = True

            # Draw
            self.screen.fill(BACKGROUND)
            
            # Draw Floor Shadow
            shadow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shadow_poly = [
                project(-L*0.6, -L*0.6, 0),
                project(L*0.6, -L*0.6, 0),
                project(L*0.6, L*0.6, 0),
                project(-L*0.6, L*0.6, 0)
            ]
            pygame.draw.polygon(shadow_surf, (0, 0, 0, 80), shadow_poly)
            self.screen.blit(shadow_surf, (0, 0))

            # Draw Base/Table
            base_poly = [
                project(-L*0.75, -L*0.75, 0),
                project(L*0.75, -L*0.75, 0),
                project(L*0.75, L*0.75, 0),
                project(-L*0.75, L*0.75, 0)
            ]
            pygame.draw.polygon(self.screen, (30, 30, 40), base_poly)
            pygame.draw.polygon(self.screen, (50, 50, 70), base_poly, 2)

            # Sort and draw blocks
            sorted_blocks = sorted(self.blocks, key=lambda b: b.get_depth())
            for b in sorted_blocks:
                b.draw(self.screen)
            
            # UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (30, 30))
            
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
