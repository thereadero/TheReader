import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 800, 800
FPS = 60

# Colors
BACKGROUND = (26, 26, 26)
WOOD_LIGHT = (210, 180, 140)
WOOD_DARK = (139, 69, 19)
GOLD = (255, 215, 0)
WHITE = (245, 245, 245)
ACCENT = (255, 100, 50)

# Block settings
BLOCK_WIDTH = 200
BLOCK_HEIGHT = 40
TOWER_LEVELS = 12
BLOCKS_PER_LEVEL = 1  # In 2D side view, each level is one "wide" or "3 narrow"
# To simulate Jenga better in 2D, we alternate between "Front View" (1 wide block) 
# and "Side View" (3 narrow blocks).

GRAVITY = 0.5
FRICTION = 0.95
DRAG_STRENGTH = 0.2

class Block:
    def __init__(self, x, y, w, h, is_static=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.vx = 0.0
        self.vy = 0.0
        self.is_static = is_static
        self.color = WOOD_LIGHT if not is_static else WOOD_DARK
        self.dragged = False
        self.hovered = False

    def update(self):
        if not self.is_static and not self.dragged:
            self.vy += GRAVITY
            self.vx *= FRICTION
            
            self.x += self.vx
            self.y += self.vy
            
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface):
        color = self.color
        if self.hovered:
            color = GOLD
        if self.dragged:
            color = ACCENT
            
        # Main body
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        # Detail / Grain
        pygame.draw.rect(surface, (0, 0, 0, 50), self.rect, width=2, border_radius=4)
        
        # Subtle gradient highlight
        highlight_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h // 3)
        pygame.draw.rect(surface, (255, 255, 255, 30), highlight_rect, border_radius=2)

class JengaGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Physics Jenga")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Inter, Arial", 32)
        self.title_font = pygame.font.SysFont("Inter, Arial", 64, bold=True)
        
        self.reset()

    def reset(self):
        self.blocks = []
        # Base/Table
        base = Block(100, HEIGHT - 50, WIDTH - 200, 50, is_static=True)
        self.blocks.append(base)
        
        # Build Tower
        start_y = HEIGHT - 50 - BLOCK_HEIGHT
        for level in range(TOWER_LEVELS):
            y = start_y - (level * BLOCK_HEIGHT)
            if level % 2 == 0:
                # Wide block (simulates 3 blocks side-by-side facing us)
                self.blocks.append(Block(WIDTH // 2 - BLOCK_WIDTH // 2, y, BLOCK_WIDTH, BLOCK_HEIGHT))
            else:
                # 3 narrow blocks (simulates blocks oriented away from us)
                gap = 4
                w = (BLOCK_WIDTH - (gap * 2)) // 3
                for i in range(3):
                    self.blocks.append(Block(WIDTH // 2 - BLOCK_WIDTH // 2 + i * (w + gap), y, w, BLOCK_HEIGHT))
        
        self.dragged_block = None
        self.game_over = False
        self.score = 0
        self.highest_y = start_y

    def handle_collisions(self):
        # Very simple AABB collision response
        for _ in range(3): # Multiple iterations for stability
            for i, b1 in enumerate(self.blocks):
                for j, b2 in enumerate(self.blocks):
                    if i >= j: continue
                    if b1.is_static and b2.is_static: continue
                    
                    if b1.rect.colliderect(b2.rect):
                        # Calculate overlap
                        overlap_x = min(b1.rect.right, b2.rect.right) - max(b1.rect.left, b2.rect.left)
                        overlap_y = min(b1.rect.bottom, b2.rect.bottom) - max(b1.rect.top, b2.rect.top)
                        
                        if overlap_x < overlap_y:
                            # Push horizontally
                            dx = b1.rect.centerx - b2.rect.centerx
                            push = overlap_x / 2
                            if not b1.is_static: b1.x += push if dx > 0 else -push
                            if not b2.is_static: b2.x += push if dx < 0 else -push
                            b1.vx *= 0.8
                            b2.vx *= 0.8
                        else:
                            # Push vertically
                            dy = b1.rect.centery - b2.rect.centery
                            push = overlap_y / 2
                            if not b1.is_static: 
                                b1.y += push if dy > 0 else -push
                                b1.vy = 0 if dy < 0 else b1.vy
                            if not b2.is_static: 
                                b2.y += push if dy < 0 else -push
                                b2.vy = 0 if dy > 0 else b2.vy
                        
                        b1.rect.x, b1.rect.y = int(b1.x), int(b1.y)
                        b2.rect.x, b2.rect.y = int(b2.x), int(b2.y)

    def run(self):
        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        self.reset()
                    else:
                        for b in self.blocks:
                            if not b.is_static and b.rect.collidepoint(mx, my):
                                self.dragged_block = b
                                b.dragged = True
                                break
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.dragged_block:
                        self.dragged_block.dragged = False
                        self.dragged_block = None

            # Update
            if not self.game_over:
                if self.dragged_block:
                    # Apply drag force
                    target_x = mx - self.dragged_block.w // 2
                    target_y = my - self.dragged_block.h // 2
                    self.dragged_block.vx = (target_x - self.dragged_block.x) * DRAG_STRENGTH
                    self.dragged_block.vy = (target_y - self.dragged_block.y) * DRAG_STRENGTH
                    self.dragged_block.x += self.dragged_block.vx
                    self.dragged_block.y += self.dragged_block.vy
                
                for b in self.blocks:
                    b.hovered = b.rect.collidepoint(mx, my) and not b.is_static
                    b.update()
                
                self.handle_collisions()
                
                # Check for collapse
                tower_fallen = False
                for b in self.blocks:
                    if not b.is_static:
                        if b.y > HEIGHT or b.x < -100 or b.x > WIDTH + 100:
                            tower_fallen = True
                            break
                
                if tower_fallen:
                    self.game_over = True

            # Draw
            self.screen.fill(BACKGROUND)
            
            for b in self.blocks:
                b.draw(self.screen)
            
            # UI
            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                msg = self.title_font.render("TOWER COLLAPSED!", True, ACCENT)
                self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
                
                retry = self.font.render("Click to Restart", True, WHITE)
                self.screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, HEIGHT // 2 + 50))
            else:
                title = self.font.render("Physics Jenga", True, WHITE)
                self.screen.blit(title, (20, 20))
                instr = self.font.render("Drag blocks to remove them", True, WOOD_LIGHT)
                self.screen.blit(instr, (20, 60))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = JengaGame()
    game.run()
