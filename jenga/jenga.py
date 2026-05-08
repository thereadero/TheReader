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

# Block dimensions
L = 200
W = 60
H = 40
GAP = 4

# Isometric settings
ISO_COS = 0.866
ISO_SIN = 0.5

def project(x, y, z):
    # Center of screen is world (0, 0, 0)
    screen_x = WIDTH // 2 + (x - y) * ISO_COS
    screen_y = HEIGHT // 2 + (x + y) * ISO_SIN - z
    return int(screen_x), int(screen_y)

class Block:
    def __init__(self, level, index, orientation):
        self.level = level
        self.index = index
        self.orientation = orientation  # 0: Parallel to X, 1: Parallel to Y
        self.offset = 0.0
        self.sliding = False
        self.slide_dir = 1 # 1 or -1
        self.slide_speed = 10.0
        self.pushed_out = False
        self.hovered = False
        
        self.color_top = WOOD_TOP
        self.color_l = WOOD_SIDE_L
        self.color_r = WOOD_SIDE_R

    def get_corners(self):
        # Base position (centered)
        # Footprint is LxL
        start = -L / 2
        
        if self.orientation == 0:
            # Parallel to X axis
            x0 = start + self.offset
            y0 = start + self.index * (W + GAP)
            dx, dy = L, W
        else:
            # Parallel to Y axis
            x0 = start + self.index * (W + GAP)
            y0 = start + self.offset
            dx, dy = W, L
            
        z0 = self.level * H
        
        return [
            (x0, y0, z0),           # 0
            (x0 + dx, y0, z0),      # 1
            (x0 + dx, y0 + dy, z0), # 2
            (x0, y0 + dy, z0),      # 3
            (x0, y0, z0 + H),       # 4
            (x0 + dx, y0, z0 + H),  # 5
            (x0 + dx, y0 + dy, z0 + H), # 6
            (x0, y0 + dy, z0 + H),  # 7
        ]

    def get_depth(self):
        corners = self.get_corners()
        # Sort by level first, then by X+Y (back-to-front)
        avg_x = sum(c[0] for c in corners) / 8
        avg_y = sum(c[1] for c in corners) / 8
        return self.level * 1000 + (avg_x + avg_y)

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

        pygame.draw.polygon(surface, c_right, face_right)
        pygame.draw.polygon(surface, c_left, face_left)
        pygame.draw.polygon(surface, c_top, face_top)
        
        # Highlights (edges)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[4], corners[5], 2)
        pygame.draw.line(surface, (255, 255, 255, 80), corners[4], corners[7], 2)

        # Outlines
        pygame.draw.polygon(surface, (40, 30, 20), face_top, 1)
        pygame.draw.polygon(surface, (40, 30, 20), face_left, 1)
        pygame.draw.polygon(surface, (40, 30, 20), face_right, 1)

    def update(self):
        if self.sliding:
            self.offset += self.slide_dir * self.slide_speed
            if abs(self.offset) > L * 1.5:
                self.pushed_out = True
                self.sliding = False

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

    def restack_block(self, block):
        max_level, count = self.get_top_info()
        
        # Determine target level and index
        if count < 3:
            target_level = max_level
            target_index = count
        else:
            target_level = max_level + 1
            target_index = 0
            
        block.level = target_level
        block.index = target_index
        block.orientation = target_level % 2
        block.offset = 0
        block.sliding = False
        block.pushed_out = False
        self.score += 1

    def check_stability(self):
        # Very simple stability: if a level (below the top) has 0 blocks, it falls.
        # Also check if it's leaning too much (not implemented yet, but let's do 0 blocks check)
        max_level, _ = self.get_top_info()
        for l in range(max_level):
            level_blocks = [b for b in self.blocks if b.level == l]
            if len(level_blocks) == 0:
                return False
            # Check center of mass support?
            # If only 1 block, it must be the middle one (index 1) or it might tip.
            # For simplicity: must have at least one block.
            # Better: if only one block and it's not index 1, it's unstable.
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
                            b.sliding = True
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
                    b.update()
                
                if self.sliding_block and self.sliding_block.pushed_out:
                    self.restack_block(self.sliding_block)
                    self.sliding_block = None
                    
                    if not self.check_stability():
                        self.game_over = True

            # Draw
            self.screen.fill(BACKGROUND)
            
            # Draw Floor Shadow
            shadow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shadow_poly = [
                project(-L*0.8, -L*0.8, 0),
                project(L*0.8, -L*0.8, 0),
                project(L*0.8, L*0.8, 0),
                project(-L*0.8, L*0.8, 0)
            ]
            pygame.draw.polygon(shadow_surf, (0, 0, 0, 100), shadow_poly)
            self.screen.blit(shadow_surf, (0, 0))

            # Draw Base/Table
            base_poly = [
                project(-L, -L, 0),
                project(L, -L, 0),
                project(L, L, 0),
                project(-L, L, 0)
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
