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
    # Base floor Y coordinate
    floor_y = HEIGHT * 0.75
    screen_x = WIDTH // 2 + (x - y) * ISO_COS
    # Apply camera scroll
    screen_y = (floor_y + CAMERA_Y) + (x + y) * ISO_SIN - z
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
        self._cache_frame = -1
        self._cached_corners = None
        self._cached_projected = None
        
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
        for _ in range(12): # More lines for richness
            t1 = random.random()
            t2 = random.random()
            # Randomly pick if the line is vertical-ish or horizontal-ish
            side = random.choice([0, 1]) 
            width = random.uniform(0.5, 1.5)
            alpha = random.randint(30, 70)
            lines.append((t1, t2, side, width, alpha))
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

    def _get_current_corners(self):
        # We'll use a simple internal state or just call it.
        # For now, let's keep it simple but avoid redundant project() calls.
        if self.state == "flying" and self.flight_start_info is not None:
            t = self.flight_progress
            smooth_t = t * t * (3 - 2 * t)
            
            s_x, s_y, s_z, s_a = self.flight_start_info
            e_x, e_y, e_z, e_a = self.flight_end_info
            
            cx = s_x + (e_x - s_x) * smooth_t
            cy = s_y + (e_y - s_y) * smooth_t
            cz = s_z + (e_z - s_z) * smooth_t
            angle = s_a + (e_a - s_a) * smooth_t
            arc = math.sin(smooth_t * math.pi) * 250
            return self.get_corners_from_params(cx, cy, cz + arc, angle)
        
        return self.get_world_corners(self.level, self.index, self.orientation, self.offset)

    def get_depth(self):
        corners = self._get_current_corners()
        avg_x = sum(c[0] for c in corners) / 8
        avg_y = sum(c[1] for c in corners) / 8
        avg_z = sum(c[2] for c in corners) / 8
        return avg_z * 1000 + (avg_x + avg_y)

    def draw(self, surface):
        world_corners = self._get_current_corners()
        corners = [project(*c) for c in world_corners]
        
        # All 6 potential faces (indices of corners)
        # 0: (-,-,-) 1: (+,-,-) 2: (+,+,-) 3: (-,+,-) 
        # 4: (-,-,+) 5: (+,-,+) 6: (+,+,+) 7: (-,+,+)
        face_configs = [
            ([4, 5, 6, 7], self.color_top, "top"),      # Top (+z)
            ([5, 1, 2, 6], self.color_r, "right"),     # +x Face (End)
            ([6, 2, 3, 7], self.color_l, "left"),      # +y Face (Side)
            ([7, 3, 0, 4], self.color_r, "right"),     # -x Face (End)
            ([4, 0, 1, 5], self.color_l, "left"),      # -y Face (Side)
            ([1, 0, 3, 2], self.color_top, "top"),      # Bottom (-z)
        ]
        
        for idxs, color, face_key in face_configs:
            face = [corners[i] for i in idxs]
            
            # Visibility check (Shoelace / Winding order)
            # Area = 0.5 * sum(xi*yi+1 - xi+1*yi)
            area = 0
            for i in range(len(face)):
                p1 = face[i]
                p2 = face[(i+1) % len(face)]
                area += (p1[0] * p2[1] - p2[0] * p1[1])
            
            if area > 0: # Visible in our projection
                c = GOLD if (self.hovered and face_key == "top") else color
                if self.hovered:
                    # Lighten sides too if hovered
                    c = tuple(min(255, val + 40) for val in c)
                
                pygame.draw.polygon(surface, c, face)
                
                # Grain
                grain_color = tuple(max(0, val - 30) for val in c)
                v1 = (face[1][0] - face[0][0], face[1][1] - face[0][1])
                # We need a vector for the other dimension to span the face
                v2 = (face[3][0] - face[0][0], face[3][1] - face[0][1])
                
                for t1, t2, side, width, alpha in self.grain_lines[face_key]:
                    p1 = (face[0][0] + v1[0] * t1, face[0][1] + v1[1] * t1)
                    p2 = (face[3][0] + v1[0] * t2, face[3][1] + v1[1] * t2)
                    
                    # Direct draw (fast!) - approximate alpha by mixing colors
                    # Since background is 'c', and grain is 'grain_color'
                    # mixed = c * (1-a) + grain * a
                    ratio = alpha / 255.0
                    mixed = tuple(int(c[i] * (1 - ratio) + grain_color[i] * ratio) for i in range(3))
                    pygame.draw.line(surface, mixed, p1, p2, int(width))

                # Outlines (Thicker for clarity)
                pygame.draw.polygon(surface, (30, 25, 20), face, 2)

        # Draw extra highlights on the top edges for better definition
        # Top edges are corners 4, 5, 6, 7
        pygame.draw.line(surface, (255, 255, 255, 80), corners[4], corners[5], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[5], corners[6], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[6], corners[7], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[7], corners[4], 2)

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
        world_corners = self._get_current_corners()
        corners = [project(*c) for c in world_corners]
        
        # Check all visible faces for click
        face_indices = [[4, 5, 6, 7], [5, 1, 2, 6], [6, 2, 3, 7], [7, 3, 0, 4], [4, 0, 1, 5], [1, 0, 3, 2]]
        for idxs in face_indices:
            face = [corners[i] for i in idxs]
            # Visibility check (Area > 0 for CW winding in Pygame)
            area = 0
            for i in range(len(face)):
                p1 = face[i]; p2 = face[(i+1)%len(face)]
                area += (p1[0]*p2[1] - p2[0]*p1[1])
            
            if area > 0:
                if self.point_in_poly(mx, my, face):
                    return True
        return False

    def point_in_poly(self, x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(1, n + 1):
            p2x, p2y = poly[i % n]
            if (p1y > y) != (p2y > y): # Crossing scanline
                xints = (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x
                if x < xints:
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
        self.target_camera_y = 0
        global CAMERA_Y
        CAMERA_Y = 0
        self.magic_pulls = 0
        self.magically_supported_levels = set()
        self.magic_message_text = ""
        self.magic_message_timer = 0

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
        if self.score > 0 and self.score % 20 == 0:
            self.magic_pulls += 1
            self.magic_message_text = "MAGIC PULL EARNED!"
            self.magic_message_timer = 180

    def check_stability(self):
        max_level, _ = self.get_top_info()
        
        # We'll treat every block as mass 1.
        # Flying blocks have no mass (don't contribute to weight).
        
        for l in range(max_level):
            if l in self.magically_supported_levels:
                continue
            # Support blocks at level l
            # A block only provides support if it's not flying and not slid too far out.
            support_blocks = [b for b in self.blocks if b.level == l and b.state != "flying" and abs(b.offset) < L/2]
            if not support_blocks:
                return False
            
            # Supported mass: everything at level l+1 and above
            # We exclude flying blocks as they are currently "in the air"
            supported_mass_blocks = [b for b in self.blocks if b.level > l and b.state != "flying"]
            if not supported_mass_blocks:
                continue # Nothing above to tip
                
            # Calculate Center of Mass (CoM) of the entire stack above level l
            total_x = 0
            total_y = 0
            for b in supported_mass_blocks:
                start = -L / 2
                if b.orientation == 0:
                    cx, cy = b.offset, start + b.index * (W + GAP) + W / 2
                else:
                    cx, cy = start + b.index * (W + GAP) + W / 2, b.offset
                total_x += cx
                total_y += cy
            
            com_x = total_x / len(supported_mass_blocks)
            com_y = total_y / len(supported_mass_blocks)
            
            # Support bounds at level l
            orientation = l % 2
            start = -L / 2
            if orientation == 0:
                # Level l blocks are parallel to X, support is critical on Y axis
                min_y = min(start + b.index * (W + GAP) for b in support_blocks)
                max_y = max(start + b.index * (W + GAP) + W for b in support_blocks)
                
                # Check if CoM.y is within the support range [min_y, max_y]
                # We allow a very tiny margin (5 units) for game feel
                if com_y < min_y - 5 or com_y > max_y + 5:
                    return False
            else:
                # Level l blocks are parallel to Y, support is critical on X axis
                min_x = min(start + b.index * (W + GAP) for b in support_blocks)
                max_x = max(start + b.index * (W + GAP) + W for b in support_blocks)
                
                if com_x < min_x - 5 or com_x > max_x + 5:
                    return False
        
        return True

    def draw_magic_field(self, l):
        z = l * H
        magic_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Pulse alpha/glow over time
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 15 + 40
        magic_poly = [
            project(-L * 0.55, -L * 0.55, z),
            project(L * 0.55, -L * 0.55, z),
            project(L * 0.55, L * 0.55, z),
            project(-L * 0.55, L * 0.55, z)
        ]
        pygame.draw.polygon(magic_surf, (0, 255, 220, int(pulse)), magic_poly)
        pygame.draw.polygon(magic_surf, (0, 255, 220, 180), magic_poly, 3)
        
        # Concentric detail lines
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
        running = True
        hovered_block = None
        while running:
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset()
                    elif not self.sliding_block:
                        # Sort blocks by depth to pick the front-most one
                        sorted_blocks = sorted(self.blocks, key=lambda b: b.get_depth(), reverse=True)
                        for b in sorted_blocks:
                            # Cannot pick from top level
                            max_l, _ = self.get_top_info()
                            if b.level == max_l: continue
                            
                            if b.is_clicked(mx, my):
                                # Check if it's the last block on its level
                                level_blocks = [x for x in self.blocks if x.level == b.level]
                                if len(level_blocks) == 1:
                                    if self.magic_pulls > 0:
                                        self.magic_pulls -= 1
                                        self.magically_supported_levels.add(b.level)
                                        self.magic_message_text = f"LEVEL {b.level + 1} LEVITATION ACTIVATED!"
                                        self.magic_message_timer = 180
                                    else:
                                        # Tower will fall normally
                                        pass
                                
                                b.state = "sliding"
                                # Slide direction: outer blocks slide out, middle slides random
                                if b.index == 0: b.slide_dir = -1
                                elif b.index == 2: b.slide_dir = 1
                                else: b.slide_dir = random.choice([1, -1])
                                self.sliding_block = b
                                break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()

            # Update Camera Target
            max_level, _ = self.get_top_info()
            # The top block's Z is max_level * H. 
            # We want that to be at screen_y ~ 150.
            # floor_y + CAMERA_Y - max_z = 150
            # CAMERA_Y = 150 - floor_y + max_z
            floor_y = HEIGHT * 0.75
            max_z = max_level * H
            self.target_camera_y = max(0, 150 - floor_y + max_z)
            
            # Smooth scroll
            global CAMERA_Y
            CAMERA_Y += (self.target_camera_y - CAMERA_Y) * 0.08

            # Update
            if not self.game_over:
                # Hover logic: only highlight the top-most block under cursor
                hovered_block = None
                if not self.sliding_block:
                    sorted_blocks = sorted(self.blocks, key=lambda b: b.get_depth(), reverse=True)
                    max_l, _ = self.get_top_info()
                    for b in sorted_blocks:
                        if b.level == max_l: continue # Cannot pick from top level
                        if b.is_clicked(mx, my):
                            hovered_block = b
                            break

                for b in self.blocks:
                    b.hovered = (b == hovered_block)
                    
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

            # Sort and draw blocks & magic fields
            drawables = []
            for b in self.blocks:
                drawables.append((b.get_depth(), b))
            for l in self.magically_supported_levels:
                depth = (l * H + H / 2) * 1000
                drawables.append((depth, ("magic_field", l)))
            
            drawables.sort(key=lambda x: x[0])
            for _, item in drawables:
                if isinstance(item, Block):
                    item.draw(self.screen)
                else:
                    _, l = item
                    self.draw_magic_field(l)
            
            # Draw tooltip for hovered block if it's the last on its level
            if not self.game_over and hovered_block:
                level_blocks = [x for x in self.blocks if x.level == hovered_block.level]
                if len(level_blocks) == 1:
                    if self.magic_pulls > 0:
                        tooltip_text = "Last Block! (Will use Magic Pull)"
                        tooltip_color = (0, 255, 200)
                    else:
                        tooltip_text = "WARNING: Last Block! (Will fall!)"
                        tooltip_color = ACCENT
                    
                    txt = self.font.render(tooltip_text, True, tooltip_color)
                    tooltip_w, tooltip_h = txt.get_size()
                    tx = min(mx + 15, WIDTH - tooltip_w - 20)
                    ty = min(my - 25, HEIGHT - tooltip_h - 20)
                    
                    tip_surf = pygame.Surface((tooltip_w + 16, tooltip_h + 8), pygame.SRCALPHA)
                    tip_surf.fill((18, 18, 24, 220))
                    pygame.draw.rect(tip_surf, tooltip_color, tip_surf.get_rect(), 1, border_radius=4)
                    
                    self.screen.blit(tip_surf, (tx, ty))
                    self.screen.blit(txt, (tx + 8, ty + 4))

            # UI
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (30, 30))
            
            # Draw Magic Pulls info
            if self.magic_pulls > 0:
                pulse = int(127 + 128 * math.sin(pygame.time.get_ticks() * 0.01))
                magic_color = (0, pulse, 255)
                magic_text = self.font.render(f"Magic Pulls: {self.magic_pulls} (ACTIVE)", True, magic_color)
            else:
                magic_text = self.font.render(f"Magic Pulls: 0 (Earn at 20 pts)", True, (120, 120, 120))
            self.screen.blit(magic_text, (30, 70))
            
            # Draw notification banner
            if self.magic_message_timer > 0:
                self.magic_message_timer -= 1
                banner_surf = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
                banner_surf.fill((0, 255, 220, 30))
                pygame.draw.line(banner_surf, (0, 255, 220, 180), (0, 0), (WIDTH, 0), 2)
                pygame.draw.line(banner_surf, (0, 255, 220, 180), (0, 58), (WIDTH, 58), 2)
                
                banner_text = self.font.render(self.magic_message_text, True, (0, 255, 220))
                banner_surf.blit(banner_text, (WIDTH // 2 - banner_text.get_width() // 2, 30 - banner_text.get_height() // 2))
                self.screen.blit(banner_surf, (0, 120))
            
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
