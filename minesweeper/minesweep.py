import pygame
import random
import time
import sys
import math

# --- Configuration & Constants ---
MODES = {
    "Easy": {"grid": 10, "mines": 10, "cell_size": 45},
    "Medium": {"grid": 15, "mines": 35, "cell_size": 35},
    "Hard": {"grid": 20, "mines": 80, "cell_size": 30},
    "Extreme": {"grid": 25, "mines": 150, "cell_size": 25}
}

# Layout constants
WIDTH, HEIGHT = 600, 700
MARGIN = 5
TOP_BAR_HEIGHT = 100

# Colors (Modern Dark Theme Palette)
BG_COLOR = (12, 13, 18)        # Deep slate-black
GRID_BG_COLOR = (23, 24, 33)   # Container background
CELL_COLOR = (38, 41, 54)      # Unrevealed cell
CELL_HOVER = (51, 55, 74)      # Unrevealed hover cell
REVEALED_COLOR = (17, 18, 25)  # Revealed cell
MINE_COLOR = (239, 68, 68)     # Crimson Red
FLAG_COLOR = (245, 158, 11)    # Amber Orange
TEXT_COLOR = (243, 244, 246)   # Light grey
ACCENT_COLOR = (59, 130, 246)  # Accent blue

# Modern color palette for numbers 1-8
NUM_COLORS = {
    1: (59, 130, 246),   # Blue
    2: (16, 185, 129),   # Green
    3: (239, 68, 68),    # Red
    4: (139, 92, 246),   # Purple
    5: (245, 158, 11),   # Orange
    6: (6, 182, 212),    # Cyan
    7: (236, 72, 153),   # Pink
    8: (107, 114, 128)   # Grey
}

# --- Beautiful Custom Vector Drawing Functions ---

def draw_flag_icon(screen, x, y, size):
    """Draws a modern, clean flag icon centered at (x, y) with scaling."""
    h = size // 2
    w = size // 3
    # Pole (Silver gray)
    pygame.draw.line(screen, (209, 213, 219), (x - 2, y - h // 2), (x - 2, y + h // 2), 2)
    # Stand (Muted gray)
    pygame.draw.line(screen, (107, 114, 128), (x - 6, y + h // 2), (x + 2, y + h // 2), 2)
    # Flag cloth (Crimson Red)
    points = [
        (x - 2, y - h // 2),
        (x + w, y - h // 4),
        (x - 2, y)
    ]
    pygame.draw.polygon(screen, (239, 68, 68), points)

def draw_mine_icon(screen, rect, scale=1.0):
    """Draws a detailed naval mine icon with detonator spikes and glossy highlights."""
    x, y = rect.centerx, rect.centery
    size = int(rect.width * scale)
    r = max(2, size // 4)
    
    # Detonator spikes (drawn first, behind body)
    spike_color = (239, 68, 68) if r > 4 else (180, 50, 50)
    pygame.draw.line(screen, spike_color, (x - r - 3, y), (x + r + 3, y), 2)
    pygame.draw.line(screen, spike_color, (x, y - r - 3), (x, y + r + 3), 2)
    pygame.draw.line(screen, spike_color, (x - r - 2, y - r - 2), (x + r + 2, y + r + 2), 2)
    pygame.draw.line(screen, spike_color, (x + r + 2, y - r - 2), (x - r - 2, y + r + 2), 2)
    
    # Main circular body (Dark blue/gray)
    pygame.draw.circle(screen, (31, 41, 55), (x, y), r)
    pygame.draw.circle(screen, (55, 65, 81), (x, y), r - 1)
    
    # Specular glossy highlight
    if r > 4:
        pygame.draw.circle(screen, (255, 255, 255), (x - r // 2, y - r // 2), 2)

def draw_clock_icon(screen, x, y, size):
    """Draws a clean, modern clockface icon at (x, y)."""
    r = size // 2
    # Outer circle ring
    pygame.draw.circle(screen, (209, 213, 219), (x, y), r, 2)
    # Center dot
    pygame.draw.circle(screen, (209, 213, 219), (x, y), 2)
    # Clock hands (Hours/Minutes)
    pygame.draw.line(screen, (209, 213, 219), (x, y), (x, y - r + 4), 2)
    pygame.draw.line(screen, (209, 213, 219), (x, y), (x + r - 5, y), 2)

def draw_trophy_icon(screen, x, y, size):
    """Draws a golden victory trophy icon at (x, y)."""
    h = size // 2
    color = (245, 158, 11) # Gold
    # Stand base
    pygame.draw.line(screen, color, (x - h // 2, y + h // 2), (x + h // 2, y + h // 2), 3)
    # Stem
    pygame.draw.line(screen, color, (x, y + h // 4), (x, y + h // 2), 3)
    # Cup bowl
    cup_rect = pygame.Rect(x - h // 3, y - h // 2, (h // 3) * 2, h // 2)
    pygame.draw.arc(screen, color, cup_rect, 3.1415, 0, 3)
    pygame.draw.line(screen, color, (x - h // 3, y - h // 2), (x + h // 3, y - h // 2), 3)
    # Handles (Left & Right arcs)
    pygame.draw.arc(screen, color, (x - h // 2, y - h // 3, h // 3, h // 3), 1.57, 4.71, 2)
    pygame.draw.arc(screen, color, (x + h // 6, y - h // 3, h // 3, h // 3), 4.71, 1.57, 2)

def draw_home_icon(screen, x, y, size):
    """Draws a clean house icon for HUD navigation."""
    h = size
    # Roof (light silver)
    points = [
        (x, y - h // 2),
        (x - h // 2, y),
        (x + h // 2, y)
    ]
    pygame.draw.polygon(screen, (209, 213, 219), points)
    # House body
    pygame.draw.rect(screen, (209, 213, 219), (x - h // 3, y, (h // 3) * 2, h // 2 - 2))
    # Closed Door (cuts out to transparent background color)
    pygame.draw.rect(screen, (23, 24, 33), (x - h // 8, y + h // 4, h // 4, h // 4))

def draw_reset_icon(screen, x, y, size):
    """Draws a circular reset arrow icon."""
    r = size // 3
    rect = pygame.Rect(x - r, y - r, r * 2, r * 2)
    # Circular arc
    pygame.draw.arc(screen, (209, 213, 219), rect, 0.5, 5.8, 3)
    # Arrowhead at top-right
    points = [
        (x + r - 4, y - 6),
        (x + r + 4, y - 6),
        (x + r, y + 2)
    ]
    pygame.draw.polygon(screen, (209, 213, 219), points)


# --- Particle Engine Class ---

class Particle:
    def __init__(self, x, y, dx, dy, color, size, lifetime, p_type="spark"):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.p_type = p_type  # "spark", "confetti"

    def update(self):
        self.lifetime -= 1
        if self.p_type == "spark":
            self.x += self.dx
            self.y += self.dy
            self.dy += 0.15      # Gravity
            self.dx *= 0.98      # Air drag
            self.dy *= 0.98
        elif self.p_type == "confetti":
            self.x += self.dx
            self.y += self.dy
            self.dy += 0.05      # Gentle gravity
            self.dx += random.uniform(-0.1, 0.1) # Wind flutter

    def draw(self, screen):
        alpha_ratio = max(0.0, min(1.0, self.lifetime / self.max_lifetime))
        r, g, b = self.color
        drawn_color = (int(r * alpha_ratio), int(g * alpha_ratio), int(b * alpha_ratio))
        
        # Draw physical circles fading out
        pygame.draw.circle(screen, drawn_color, (int(self.x), int(self.y)), max(1, int(self.size * alpha_ratio)))


# --- Main Menu Animated Background Bubbles ---

class MenuBubble:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.r = random.randint(15, 45)
        self.speed = random.uniform(0.3, 0.8)
        self.alpha = random.randint(10, 22)
        self.color = (38, 41, 54) # Grid element color

    def update(self, width, height):
        self.y -= self.speed
        if self.y < -self.r:
            self.y = height + self.r
            self.x = random.randint(0, width)

    def draw(self, screen):
        # Draw soft translucent circles using a temp surface
        surf = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, self.alpha), (self.r, self.r), self.r)
        screen.blit(surf, (int(self.x - self.r), int(self.y - self.r)))


# --- Minesweeper Cell Class ---

class Cell:
    def __init__(self, r, c, grid_size, cell_size, width):
        self.r = r
        self.c = c
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
        self.rect = pygame.Rect(
            c * (cell_size + MARGIN) + (width - (grid_size * (cell_size + MARGIN))) // 2,
            r * (cell_size + MARGIN) + TOP_BAR_HEIGHT + MARGIN,
            cell_size,
            cell_size
        )
        self.hover_progress = 0.0 # Fluid color interpolation
        self.reveal_scale = 0.0   # Scale animation when revealed

    def draw(self, screen, font, game_over, won, cell_size):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)

        # Smooth hover interpolation
        if is_hover and not game_over and not won:
            self.hover_progress = min(1.0, self.hover_progress + 0.15)
        else:
            self.hover_progress = max(0.0, self.hover_progress - 0.15)

        # Handle reveal popping scale
        if self.is_revealed:
            self.reveal_scale = min(1.0, self.reveal_scale + 0.12)
            color = REVEALED_COLOR
        else:
            # Linear color interpolation for hover color
            r_c = int(CELL_COLOR[0] + (CELL_HOVER[0] - CELL_COLOR[0]) * self.hover_progress)
            g_c = int(CELL_COLOR[1] + (CELL_HOVER[1] - CELL_COLOR[1]) * self.hover_progress)
            b_c = int(CELL_COLOR[2] + (CELL_HOVER[2] - CELL_COLOR[2]) * self.hover_progress)
            color = (r_c, g_c, b_c)

        # Draw cell background
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        
        # Subtle cell inner borders
        if not self.is_revealed:
            border_color = (
                int(CELL_COLOR[0] + 12),
                int(CELL_COLOR[1] + 12),
                int(CELL_COLOR[2] + 15)
            )
            pygame.draw.rect(screen, border_color, self.rect, width=1, border_radius=4)

        # Draw cell contents
        if self.is_revealed:
            if self.is_mine:
                draw_mine_icon(screen, self.rect, self.reveal_scale)
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, NUM_COLORS.get(self.adjacent_mines, TEXT_COLOR))
                if self.reveal_scale < 1.0:
                    w, h = text.get_size()
                    scaled_text = pygame.transform.scale(text, (int(w * self.reveal_scale), int(h * self.reveal_scale)))
                    text_rect = scaled_text.get_rect(center=self.rect.center)
                    screen.blit(scaled_text, text_rect)
                else:
                    text_rect = text.get_rect(center=self.rect.center)
                    screen.blit(text, text_rect)
        elif self.is_flagged:
            draw_flag_icon(screen, self.rect.centerx, self.rect.centery, cell_size)

        # If lost, reveal all other unrevealed mines in a faded gray/red look
        if game_over and self.is_mine and not self.is_revealed:
            draw_mine_icon(screen, self.rect, 0.75)


# --- Core Game Controller Class ---

class Minesweeper:
    def __init__(self):
        pygame.init()
        self.state = "MENU"
        self.current_mode = "Medium"
        self.grid_size = MODES[self.current_mode]["grid"]
        self.num_mines = MODES[self.current_mode]["mines"]
        self.cell_size = MODES[self.current_mode]["cell_size"]
        self.width = 600
        self.height = 700
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper Premium")
        
        # Fonts
        self.font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.ui_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.menu_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.sub_font = pygame.font.SysFont("Segoe UI", 16)
        self.sub_font_bold = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.button_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", 56, bold=True)
        
        self.clock = pygame.time.Clock()
        
        # Menu parallax bubbles
        self.bubbles = [MenuBubble(self.width, self.height) for _ in range(15)]
        
        # Custom Mode settings
        self.custom_grid_size = 15
        self.custom_num_mines = 30

        # Hover states
        self.menu_hover_progress = {mode: 0.0 for mode in MODES}
        self.menu_hover_progress["Custom"] = 0.0
        self.hud_home_hover = 0.0
        self.hud_reset_hover = 0.0
        self.modal_play_hover = 0.0
        self.modal_menu_hover = 0.0
        self.custom_grid_minus_hover = 0.0
        self.custom_grid_plus_hover = 0.0
        self.custom_mines_minus_hover = 0.0
        self.custom_mines_plus_hover = 0.0
        self.custom_play_hover = 0.0
        self.custom_back_hover = 0.0
        
        # Transitions
        self.transition_alpha = 0
        self.transition_target_state = None
        self.transition_state = "IDLE" # "FADING_OUT", "FADING_IN", "IDLE"
        
        # Particle Engine
        self.particles = []
        self.overlay_alpha = 0
        
        self.reset()

    def select_mode(self, mode_name):
        """Initiates a smooth fade transition to start the chosen game mode."""
        if mode_name == "Custom":
            self.transition_target_state = "CUSTOM_SETUP"
        else:
            self.transition_target_state = f"PLAYING_{mode_name}"
        self.transition_state = "FADING_OUT"

    def select_mode_immediate(self, mode_name):
        """Instantly updates dimensions and screen mode at the midpoint of transition."""
        self.current_mode = mode_name
        if mode_name == "Custom":
            self.grid_size = self.custom_grid_size
            self.num_mines = self.custom_num_mines
            self.cell_size = max(16, min(50, 600 // self.grid_size))
        else:
            self.grid_size = MODES[mode_name]["grid"]
            self.num_mines = MODES[mode_name]["mines"]
            self.cell_size = MODES[mode_name]["cell_size"]
        
        # Calculate optimal size dynamically
        grid_pixel_width = self.grid_size * (self.cell_size + MARGIN) - MARGIN
        self.width = max(600, grid_pixel_width + 40)
        self.height = grid_pixel_width + TOP_BAR_HEIGHT + 40
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.state = "PLAYING"
        self.reset()

    def go_to_menu(self):
        """Initiates a smooth fade transition to return to the main menu."""
        self.transition_target_state = "MENU"
        self.transition_state = "FADING_OUT"

    def go_to_menu_immediate(self):
        """Returns to menu layout instantly at the midpoint of transition."""
        self.state = "MENU"
        self.width, self.height = 600, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.reset()

    def reset(self):
        self.grid = [[Cell(r, c, self.grid_size, self.cell_size, self.width) for c in range(self.grid_size)] for r in range(self.grid_size)]
        self.mines_placed = False
        self.game_over = False
        self.won = False
        self.start_time = None
        self.elapsed_time = 0
        self.flags_used = 0
        self.particles = []
        self.overlay_alpha = 0

    def place_mines(self, start_r, start_c):
        cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        safe_zone = [(start_r + dr, start_c + dc) for dr in range(-1, 2) for dc in range(-1, 2)]
        cells = [cell for cell in cells if cell not in safe_zone]
        
        mine_pos = random.sample(cells, self.num_mines)
        for r, c in mine_pos:
            self.grid[r][c].is_mine = True

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.grid[r][c].is_mine:
                    count = 0
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size and self.grid[nr][nc].is_mine:
                                count += 1
                    self.grid[r][c].adjacent_mines = count
        
        self.mines_placed = True
        self.start_time = time.time()

    def reveal(self, r, c):
        if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
            return
        cell = self.grid[r][c]
        if cell.is_revealed or cell.is_flagged:
            return

        cell.is_revealed = True
        
        # Tactile click puff particles
        self.spawn_puff(cell.rect.centerx, cell.rect.centery)

        if cell.is_mine:
            self.game_over = True
            # Spawn mine explosion particles
            self.spawn_explosion(cell.rect.centerx, cell.rect.centery)
            return

        if cell.adjacent_mines == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    self.reveal(r + dr, c + dc)

    def check_win(self):
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                cell = self.grid[r][c]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    # --- Particles Physics Helpers ---

    def spawn_explosion(self, x, y):
        """Generates dynamic flame and ash particles spreading from the explosion center."""
        for _ in range(45):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            color = random.choice([
                (255, 230, 100), # Hot Yellow
                (255, 120, 30),  # Fire Orange
                (220, 50, 50),   # Crimson
                (100, 100, 100)  # Smoke Grey
            ])
            size = random.uniform(3, 7)
            lifetime = random.randint(20, 45)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime, "spark"))

    def spawn_confetti(self):
        """Spawns falling celebration confetti lines from the top of the grid."""
        for _ in range(80):
            px = random.randint(0, self.width)
            py = random.randint(-50, -10)
            dx = random.uniform(-1, 1)
            dy = random.uniform(1.5, 4.0)
            color = random.choice([
                (59, 130, 246),  # Blue
                (16, 185, 129),  # Green
                (239, 68, 68),   # Red
                (245, 158, 11),  # Gold
                (139, 92, 246),  # Purple
                (236, 72, 153)   # Pink
            ])
            size = random.uniform(4, 7)
            lifetime = random.randint(120, 220)
            self.particles.append(Particle(px, py, dx, dy, color, size, lifetime, "confetti"))

    def spawn_puff(self, x, y):
        """Spawns minor gray sparks representing click physical dust."""
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            color = (200, 200, 200)
            size = random.uniform(2, 4)
            lifetime = random.randint(10, 20)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime, "spark"))

    def update_particles(self):
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

    # --- UI Drawing Functions ---

    def draw_ui(self):
        """Draws the main top HUD bar containing game details and action buttons."""
        pygame.draw.rect(self.screen, BG_COLOR, (0, 0, self.width, TOP_BAR_HEIGHT))
        pygame.draw.line(self.screen, (38, 41, 54), (0, TOP_BAR_HEIGHT), (self.width, TOP_BAR_HEIGHT), 2)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Setup home and restart rects
        home_btn_rect = pygame.Rect(self.width // 2 - 85, 25, 50, 50)
        restart_btn_rect = pygame.Rect(self.width // 2 - 25, 25, 50, 50)
        
        # Calculate hover state
        if home_btn_rect.collidepoint(mouse_pos) and not self.game_over and not self.won:
            self.hud_home_hover = min(1.0, self.hud_home_hover + 0.15)
        else:
            self.hud_home_hover = max(0.0, self.hud_home_hover - 0.15)
            
        if restart_btn_rect.collidepoint(mouse_pos) and not self.game_over and not self.won:
            self.hud_reset_hover = min(1.0, self.hud_reset_hover + 0.15)
        else:
            self.hud_reset_hover = max(0.0, self.hud_reset_hover - 0.15)
            
        # Draw Home button
        home_color = (
            int(23 + (38 - 23) * self.hud_home_hover),
            int(24 + (41 - 24) * self.hud_home_hover),
            int(33 + (54 - 33) * self.hud_home_hover)
        )
        pygame.draw.rect(self.screen, home_color, home_btn_rect, border_radius=10)
        draw_home_icon(self.screen, self.width // 2 - 60, 50, 24)
        
        # Draw Restart button
        reset_color = (
            int(23 + (38 - 23) * self.hud_reset_hover),
            int(24 + (41 - 24) * self.hud_reset_hover),
            int(33 + (54 - 33) * self.hud_reset_hover)
        )
        pygame.draw.rect(self.screen, reset_color, restart_btn_rect, border_radius=10)
        draw_reset_icon(self.screen, self.width // 2, 50, 24)
        
        # Mine counter pill container
        mine_rect = pygame.Rect(20, 25, 140, 50)
        pygame.draw.rect(self.screen, GRID_BG_COLOR, mine_rect, border_radius=12)
        draw_flag_icon(self.screen, 45, 50, 32)
        mine_text = self.ui_font.render(f"{max(0, self.num_mines - self.flags_used)}", True, TEXT_COLOR)
        mine_text_rect = mine_text.get_rect(midleft=(75, 50))
        self.screen.blit(mine_text, mine_text_rect)

        # Timer pill container
        if self.start_time and not self.game_over and not self.won:
            self.elapsed_time = int(time.time() - self.start_time)
        
        timer_rect = pygame.Rect(self.width - 160, 25, 140, 50)
        pygame.draw.rect(self.screen, GRID_BG_COLOR, timer_rect, border_radius=12)
        draw_clock_icon(self.screen, self.width - 135, 50, 24)
        timer_text = self.ui_font.render(f"{self.elapsed_time}s", True, TEXT_COLOR)
        timer_text_rect = timer_text.get_rect(midleft=(self.width - 105, 50))
        self.screen.blit(timer_text, timer_text_rect)

    def draw_modal(self):
        """Fades in a highly polished summary dialog when the game finishes."""
        if not (self.game_over or self.won):
            return
            
        self.overlay_alpha = min(185, self.overlay_alpha + 12)
        
        # Translucent fade-in overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 11, 16, self.overlay_alpha))
        self.screen.blit(overlay, (0, 0))
        
        if self.overlay_alpha > 50:
            w, h = 360, 320
            modal_x = self.width // 2 - w // 2
            modal_y = self.height // 2 - h // 2
            modal_rect = pygame.Rect(modal_x, modal_y, w, h)
            
            # Modal rounded box
            pygame.draw.rect(self.screen, GRID_BG_COLOR, modal_rect, border_radius=16)
            pygame.draw.rect(self.screen, (51, 55, 74), modal_rect, width=2, border_radius=16)
            
            # Modal header & custom icon
            if self.won:
                header_text = self.ui_font.render("VICTORY!", True, (52, 211, 153))
                draw_trophy_icon(self.screen, self.width // 2, modal_y + 40, 40)
                header_y = modal_y + 75
            else:
                header_text = self.ui_font.render("GAME OVER", True, (239, 68, 68))
                mine_box = pygame.Rect(self.width // 2 - 20, modal_y + 20, 40, 40)
                draw_mine_icon(self.screen, mine_box, 1.0)
                header_y = modal_y + 75
                
            header_rect = header_text.get_rect(center=(self.width // 2, header_y))
            self.screen.blit(header_text, header_rect)
            
            # Inner details statistics table
            stats_rect = pygame.Rect(modal_x + 25, modal_y + 115, w - 50, 110)
            pygame.draw.rect(self.screen, REVEALED_COLOR, stats_rect, border_radius=10)
            
            y_offset = stats_rect.y + 15
            stats_list = [
                ("Difficulty", self.current_mode),
                ("Time Taken", f"{self.elapsed_time}s"),
                ("Flags Placed", f"{self.flags_used} / {self.num_mines}")
            ]
            
            for label, val in stats_list:
                lbl_surf = self.sub_font.render(label, True, (156, 163, 175))
                val_surf = self.sub_font_bold.render(val, True, TEXT_COLOR)
                self.screen.blit(lbl_surf, (stats_rect.x + 15, y_offset))
                self.screen.blit(val_surf, (stats_rect.right - 15 - val_surf.get_width(), y_offset))
                y_offset += 30
                
            # Interactivity for modal buttons
            mouse_pos = pygame.mouse.get_pos()
            play_btn = pygame.Rect(modal_x + 25, modal_rect.bottom - 70, 140, 45)
            menu_btn = pygame.Rect(modal_x + 195, modal_rect.bottom - 70, 140, 45)
            
            if play_btn.collidepoint(mouse_pos):
                self.modal_play_hover = min(1.0, self.modal_play_hover + 0.15)
            else:
                self.modal_play_hover = max(0.0, self.modal_play_hover - 0.15)
                
            if menu_btn.collidepoint(mouse_pos):
                self.modal_menu_hover = min(1.0, self.modal_menu_hover + 0.15)
            else:
                self.modal_menu_hover = max(0.0, self.modal_menu_hover - 0.15)
                
            # Draw interactive Play Again button
            play_color = (
                int(38 + (59 - 38) * self.modal_play_hover),
                int(41 + (130 - 41) * self.modal_play_hover),
                int(54 + (246 - 54) * self.modal_play_hover)
            )
            pygame.draw.rect(self.screen, play_color, play_btn, border_radius=8)
            play_text = self.button_font.render("Play Again", True, TEXT_COLOR)
            self.screen.blit(play_text, play_text.get_rect(center=play_btn.center))
            
            # Draw interactive Main Menu button
            menu_color = (
                int(38 + (59 - 38) * self.modal_menu_hover),
                int(41 + (130 - 41) * self.modal_menu_hover),
                int(54 + (246 - 54) * self.modal_menu_hover)
            )
            pygame.draw.rect(self.screen, menu_color, menu_btn, border_radius=8)
            menu_text = self.button_font.render("Main Menu", True, TEXT_COLOR)
            self.screen.blit(menu_text, menu_text.get_rect(center=menu_btn.center))

    def draw_menu(self):
        """Draws the animated main menu with parallax floating bubbles."""
        self.screen.fill(BG_COLOR)
        
        # Update and draw floating bubbles
        for b in self.bubbles:
            b.update(self.width, self.height)
            b.draw(self.screen)
            
        # Draw glowing titles
        title_text = self.title_font.render("MINESWEEPER", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 115))
        self.screen.blit(title_text, title_rect)

        subtitle_text = self.sub_font.render("P R E M I U M", True, ACCENT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        y_offset = 210
        mouse_pos = pygame.mouse.get_pos()
        self.menu_buttons = {}

        # Draw custom interactive cards
        all_modes = list(MODES.keys()) + ["Custom"]
        for mode in all_modes:
            rect = pygame.Rect(self.width // 2 - 150, y_offset, 300, 68)
            
            is_hover = rect.collidepoint(mouse_pos)
            if is_hover:
                self.menu_hover_progress[mode] = min(1.0, self.menu_hover_progress[mode] + 0.12)
            else:
                self.menu_hover_progress[mode] = max(0.0, self.menu_hover_progress[mode] - 0.12)
                
            # Blend backgrounds
            card_color = (
                int(23 + (38 - 23) * self.menu_hover_progress[mode]),
                int(24 + (41 - 24) * self.menu_hover_progress[mode]),
                int(33 + (54 - 33) * self.menu_hover_progress[mode])
            )
            # Blend outline highlights
            border_color = (
                int(38 + (59 - 38) * self.menu_hover_progress[mode]),
                int(41 + (130 - 41) * self.menu_hover_progress[mode]),
                int(54 + (246 - 54) * self.menu_hover_progress[mode])
            )
            
            pygame.draw.rect(self.screen, card_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=12)
            
            # Setup textual specifications
            if mode == "Custom":
                mode_text = self.font.render(mode, True, (255, 255, 255))
                specs_str = f"{self.custom_grid_size} × {self.custom_grid_size} • {self.custom_num_mines} Mines"
                specs_text = self.sub_font.render(specs_str, True, (156, 163, 175))
            else:
                mode_text = self.font.render(mode, True, (255, 255, 255))
                specs_str = f"{MODES[mode]['grid']} × {MODES[mode]['grid']} • {MODES[mode]['mines']} Mines"
                specs_text = self.sub_font.render(specs_str, True, (156, 163, 175))
            
            self.screen.blit(mode_text, (rect.x + 20, rect.y + 10))
            self.screen.blit(specs_text, (rect.x + 20, rect.y + 38))
            
            # Draw dynamic directional chevron
            arrow_color = border_color
            arrow_center_y = rect.y + 34
            arrow_x = rect.right - 25
            pygame.draw.line(self.screen, arrow_color, (arrow_x - 4, arrow_center_y - 6), (arrow_x + 2, arrow_center_y), 3)
            pygame.draw.line(self.screen, arrow_color, (arrow_x + 2, arrow_center_y), (arrow_x - 4, arrow_center_y + 6), 3)
            
            self.menu_buttons[mode] = rect
            y_offset += 82

    def draw_custom_setup(self):
        """Draws the custom mode setup/configuration menu."""
        self.screen.fill(BG_COLOR)
        
        # Update and draw floating background bubbles
        for b in self.bubbles:
            b.update(self.width, self.height)
            b.draw(self.screen)
            
        # Draw Title
        title_text = self.title_font.render("CUSTOM SETUP", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 90))
        self.screen.blit(title_text, title_rect)

        subtitle_text = self.sub_font_bold.render("DESIGN YOUR BOARD", True, ACCENT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 135))
        self.screen.blit(subtitle_text, subtitle_rect)

        mouse_pos = pygame.mouse.get_pos()

        # --- Card 1: Grid Size (100, 175, 400, 115) ---
        grid_card_rect = pygame.Rect(100, 175, 400, 115)
        pygame.draw.rect(self.screen, GRID_BG_COLOR, grid_card_rect, border_radius=12)
        pygame.draw.rect(self.screen, (38, 41, 54), grid_card_rect, width=2, border_radius=12)
        
        grid_lbl = self.sub_font_bold.render("GRID SIZE", True, ACCENT_COLOR)
        self.screen.blit(grid_lbl, (grid_card_rect.x + 20, grid_card_rect.y + 12))
        
        # Minus & Plus button rects for grid
        self.grid_minus_rect = pygame.Rect(grid_card_rect.x + 30, grid_card_rect.y + 48, 40, 40)
        self.grid_plus_rect = pygame.Rect(grid_card_rect.right - 70, grid_card_rect.y + 48, 40, 40)
        
        # Update hover states
        if self.grid_minus_rect.collidepoint(mouse_pos):
            self.custom_grid_minus_hover = min(1.0, self.custom_grid_minus_hover + 0.15)
        else:
            self.custom_grid_minus_hover = max(0.0, self.custom_grid_minus_hover - 0.15)
            
        if self.grid_plus_rect.collidepoint(mouse_pos):
            self.custom_grid_plus_hover = min(1.0, self.custom_grid_plus_hover + 0.15)
        else:
            self.custom_grid_plus_hover = max(0.0, self.custom_grid_plus_hover - 0.15)
            
        # Draw minus button
        minus_color = (
            int(38 + (59 - 38) * self.custom_grid_minus_hover),
            int(41 + (130 - 41) * self.custom_grid_minus_hover),
            int(54 + (246 - 54) * self.custom_grid_minus_hover)
        )
        pygame.draw.rect(self.screen, minus_color, self.grid_minus_rect, border_radius=8)
        minus_text = self.ui_font.render("-", True, TEXT_COLOR)
        minus_rect_text = minus_text.get_rect(center=(self.grid_minus_rect.centerx, self.grid_minus_rect.centery - 2))
        self.screen.blit(minus_text, minus_rect_text)
        
        # Draw plus button
        plus_color = (
            int(38 + (59 - 38) * self.custom_grid_plus_hover),
            int(41 + (130 - 41) * self.custom_grid_plus_hover),
            int(54 + (246 - 54) * self.custom_grid_plus_hover)
        )
        pygame.draw.rect(self.screen, plus_color, self.grid_plus_rect, border_radius=8)
        plus_text = self.ui_font.render("+", True, TEXT_COLOR)
        plus_rect_text = plus_text.get_rect(center=(self.grid_plus_rect.centerx, self.grid_plus_rect.centery - 2))
        self.screen.blit(plus_text, plus_rect_text)
        
        # Draw current grid size text
        grid_val_str = f"{self.custom_grid_size} × {self.custom_grid_size}"
        grid_val_text = self.ui_font.render(grid_val_str, True, TEXT_COLOR)
        self.screen.blit(grid_val_text, grid_val_text.get_rect(center=(grid_card_rect.centerx, grid_card_rect.y + 68)))

        # --- Card 2: Mine Count (100, 305, 400, 115) ---
        mines_card_rect = pygame.Rect(100, 305, 400, 115)
        pygame.draw.rect(self.screen, GRID_BG_COLOR, mines_card_rect, border_radius=12)
        pygame.draw.rect(self.screen, (38, 41, 54), mines_card_rect, width=2, border_radius=12)
        
        mines_lbl = self.sub_font_bold.render("MINE COUNT", True, ACCENT_COLOR)
        self.screen.blit(mines_lbl, (mines_card_rect.x + 20, mines_card_rect.y + 12))
        
        # Minus & Plus button rects for mines
        self.mines_minus_rect = pygame.Rect(mines_card_rect.x + 30, mines_card_rect.y + 48, 40, 40)
        self.mines_plus_rect = pygame.Rect(mines_card_rect.right - 70, mines_card_rect.y + 48, 40, 40)
        
        # Update hover states
        if self.mines_minus_rect.collidepoint(mouse_pos):
            self.custom_mines_minus_hover = min(1.0, self.custom_mines_minus_hover + 0.15)
        else:
            self.custom_mines_minus_hover = max(0.0, self.custom_mines_minus_hover - 0.15)
            
        if self.mines_plus_rect.collidepoint(mouse_pos):
            self.custom_mines_plus_hover = min(1.0, self.custom_mines_plus_hover + 0.15)
        else:
            self.custom_mines_plus_hover = max(0.0, self.custom_mines_plus_hover - 0.15)
            
        # Draw minus button
        pygame.draw.rect(self.screen, minus_color, self.mines_minus_rect, border_radius=8)
        self.screen.blit(minus_text, minus_text.get_rect(center=(self.mines_minus_rect.centerx, self.mines_minus_rect.centery - 2)))
        
        # Draw plus button
        pygame.draw.rect(self.screen, plus_color, self.mines_plus_rect, border_radius=8)
        self.screen.blit(plus_text, plus_text.get_rect(center=(self.mines_plus_rect.centerx, self.mines_plus_rect.centery - 2)))
        
        # Draw current mine count text
        mines_val_str = f"{self.custom_num_mines}"
        mines_val_text = self.ui_font.render(mines_val_str, True, TEXT_COLOR)
        self.screen.blit(mines_val_text, mines_val_text.get_rect(center=(mines_card_rect.centerx, mines_card_rect.y + 68)))

        # --- Card 3: Density Info (100, 435, 400, 100) ---
        density_card_rect = pygame.Rect(100, 435, 400, 100)
        pygame.draw.rect(self.screen, GRID_BG_COLOR, density_card_rect, border_radius=12)
        pygame.draw.rect(self.screen, (38, 41, 54), density_card_rect, width=2, border_radius=12)
        
        # Calculate mine density
        total_cells = self.custom_grid_size * self.custom_grid_size
        density_pct = (self.custom_num_mines / total_cells) * 100
        
        # Determine rating and color
        if density_pct < 10.0:
            rating = "Easy"
            rating_color = (59, 130, 246)  # Blue
        elif density_pct <= 20.0:
            rating = "Recommended"
            rating_color = (16, 185, 129)  # Green
        elif density_pct <= 30.0:
            rating = "Challenging"
            rating_color = (245, 158, 11)  # Orange
        else:
            rating = "Extreme"
            rating_color = (239, 68, 68)   # Red
            
        density_lbl = self.sub_font_bold.render("MINE DENSITY PREVIEW", True, ACCENT_COLOR)
        self.screen.blit(density_lbl, (density_card_rect.x + 20, density_card_rect.y + 12))
        
        # Render rating and percentage text
        density_str = f"{density_pct:.1f}% — {rating}"
        density_val_text = self.sub_font_bold.render(density_str, True, rating_color)
        self.screen.blit(density_val_text, (density_card_rect.right - 20 - density_val_text.get_width(), density_card_rect.y + 12))
        
        # Draw custom visual density progress bar
        bar_x = density_card_rect.x + 20
        bar_y = density_card_rect.y + 48
        bar_w = density_card_rect.width - 40
        bar_h = 10
        pygame.draw.rect(self.screen, REVEALED_COLOR, (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        
        # Fill proportion (clamped between 0 and 1)
        fill_w = int(bar_w * min(1.0, density_pct / 50.0))  # Max 50% density represented on bar
        pygame.draw.rect(self.screen, rating_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
        
        # Helper tip text inside card
        tip_text = self.sub_font.render("* Tip: Hold Shift to change values by 5", True, (107, 114, 128))
        self.screen.blit(tip_text, tip_text.get_rect(center=(density_card_rect.centerx, density_card_rect.y + 78)))

        # --- Play & Back Buttons (100, 560, 400, 50) ---
        self.custom_play_btn = pygame.Rect(100, 560, 185, 50)
        self.custom_back_btn = pygame.Rect(315, 560, 185, 50)
        
        if self.custom_play_btn.collidepoint(mouse_pos):
            self.custom_play_hover = min(1.0, self.custom_play_hover + 0.15)
        else:
            self.custom_play_hover = max(0.0, self.custom_play_hover - 0.15)
            
        if self.custom_back_btn.collidepoint(mouse_pos):
            self.custom_back_hover = min(1.0, self.custom_back_hover + 0.15)
        else:
            self.custom_back_hover = max(0.0, self.custom_back_hover - 0.15)
            
        # Draw Play Button
        play_color = (
            int(38 + (59 - 38) * self.custom_play_hover),
            int(41 + (130 - 41) * self.custom_play_hover),
            int(54 + (246 - 54) * self.custom_play_hover)
        )
        pygame.draw.rect(self.screen, play_color, self.custom_play_btn, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR if self.custom_play_hover > 0 else (51, 55, 74), self.custom_play_btn, width=2, border_radius=8)
        
        play_text = self.button_font.render("START GAME", True, TEXT_COLOR)
        self.screen.blit(play_text, play_text.get_rect(center=self.custom_play_btn.center))
        
        # Draw Back Button
        back_color = (
            int(23 + (38 - 23) * self.custom_back_hover),
            int(24 + (41 - 24) * self.custom_back_hover),
            int(33 + (54 - 33) * self.custom_back_hover)
        )
        pygame.draw.rect(self.screen, back_color, self.custom_back_btn, border_radius=8)
        pygame.draw.rect(self.screen, (51, 55, 74), self.custom_back_btn, width=2, border_radius=8)
        
        back_text = self.button_font.render("BACK", True, TEXT_COLOR)
        self.screen.blit(back_text, back_text.get_rect(center=self.custom_back_btn.center))

    # --- Transitions and Execution Loop ---

    def handle_transition_and_overlay(self):
        """Manages screen state transition fades."""
        if self.transition_state != "IDLE":
            if self.transition_state == "FADING_OUT":
                self.transition_alpha = min(255, self.transition_alpha + 18)
                if self.transition_alpha >= 255:
                    self.transition_alpha = 255
                    # Perform structural swap at maximum opacity
                    if self.transition_target_state.startswith("PLAYING_"):
                        mode = self.transition_target_state.split("_")[1]
                        self.select_mode_immediate(mode)
                    elif self.transition_target_state == "CUSTOM_SETUP":
                        self.state = "CUSTOM_SETUP"
                        self.width, self.height = 600, 700
                        self.screen = pygame.display.set_mode((self.width, self.height))
                        self.custom_grid_minus_hover = 0.0
                        self.custom_grid_plus_hover = 0.0
                        self.custom_mines_minus_hover = 0.0
                        self.custom_mines_plus_hover = 0.0
                        self.custom_play_hover = 0.0
                        self.custom_back_hover = 0.0
                    elif self.transition_target_state == "MENU":
                        self.go_to_menu_immediate()
                    self.transition_state = "FADING_IN"
            elif self.transition_state == "FADING_IN":
                self.transition_alpha = max(0, self.transition_alpha - 18)
                if self.transition_alpha <= 0:
                    self.transition_alpha = 0
                    self.transition_state = "IDLE"

            # Draw transition mask
            mask = pygame.Surface((self.width, self.height))
            mask.fill(BG_COLOR)
            mask.set_alpha(self.transition_alpha)
            self.screen.blit(mask, (0, 0))

    def run(self):
        running = True
        while running:
            # Clean and standard Pygame events flow
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                # Freeze user interactions during transition animation
                if self.transition_state != "IDLE":
                    continue
                
                if self.state == "MENU":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for mode, rect in self.menu_buttons.items():
                                if rect.collidepoint(event.pos):
                                    self.select_mode(mode)
                elif self.state == "CUSTOM_SETUP":
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            self.transition_target_state = "MENU"
                            self.transition_state = "FADING_OUT"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            mx, my = event.pos
                            shift_held = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                            step = 5 if shift_held else 1
                            
                            # Grid Minus
                            if self.grid_minus_rect.collidepoint(mx, my):
                                self.custom_grid_size = max(5, self.custom_grid_size - step)
                                max_mines = (self.custom_grid_size * self.custom_grid_size) - 9
                                self.custom_num_mines = min(self.custom_num_mines, max_mines)
                                self.spawn_puff(mx, my)
                            
                            # Grid Plus
                            elif self.grid_plus_rect.collidepoint(mx, my):
                                self.custom_grid_size = min(30, self.custom_grid_size + step)
                                self.spawn_puff(mx, my)
                                
                            # Mines Minus
                            elif self.mines_minus_rect.collidepoint(mx, my):
                                self.custom_num_mines = max(1, self.custom_num_mines - step)
                                self.spawn_puff(mx, my)
                                
                            # Mines Plus
                            elif self.mines_plus_rect.collidepoint(mx, my):
                                max_mines = (self.custom_grid_size * self.custom_grid_size) - 9
                                self.custom_num_mines = min(max_mines, self.custom_num_mines + step)
                                self.spawn_puff(mx, my)
                                
                            # Start Game button
                            elif self.custom_play_btn.collidepoint(mx, my):
                                self.transition_target_state = "PLAYING_Custom"
                                self.transition_state = "FADING_OUT"
                                
                            # Back button
                            elif self.custom_back_btn.collidepoint(mx, my):
                                self.transition_target_state = "MENU"
                                self.transition_state = "FADING_OUT"
                else:
                    # In-Game State events
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset()
                        elif event.key == pygame.K_m:
                            self.go_to_menu()
                    
                    if self.game_over or self.won:
                        # Modal click options
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                mx, my = event.pos
                                modal_x = self.width // 2 - 180
                                modal_y = self.height // 2 - 160
                                modal_bottom = modal_y + 320
                                
                                play_btn = pygame.Rect(modal_x + 25, modal_bottom - 70, 140, 45)
                                menu_btn = pygame.Rect(modal_x + 195, modal_bottom - 70, 140, 45)
                                
                                if play_btn.collidepoint(mx, my):
                                    self.reset()
                                elif menu_btn.collidepoint(mx, my):
                                    self.go_to_menu()
                    else:
                        # Game in progress grid clicks
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
                            
                            # HUD button checks
                            home_btn_rect = pygame.Rect(self.width // 2 - 85, 25, 50, 50)
                            restart_btn_rect = pygame.Rect(self.width // 2 - 25, 25, 50, 50)
                            
                            if event.button == 1:
                                if home_btn_rect.collidepoint(mx, my):
                                    self.go_to_menu()
                                    continue
                                elif restart_btn_rect.collidepoint(mx, my):
                                    self.reset()
                                    continue
                            
                            # Grid cell checks
                            for r in range(self.grid_size):
                                for c in range(self.grid_size):
                                    cell = self.grid[r][c]
                                    if cell.rect.collidepoint(mx, my):
                                        if event.button == 1: # Left Click
                                            if not cell.is_flagged:
                                                if not self.mines_placed:
                                                    self.place_mines(r, c)
                                                self.reveal(r, c)
                                                if self.check_win():
                                                    self.won = True
                                                    self.spawn_confetti()
                                        elif event.button == 3: # Right Click
                                            if not cell.is_revealed:
                                                cell.is_flagged = not cell.is_flagged
                                                self.flags_used += 1 if cell.is_flagged else -1
                                                self.spawn_puff(cell.rect.centerx, cell.rect.centery)

            # Render current Frame
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "CUSTOM_SETUP":
                self.draw_custom_setup()
            else:
                self.screen.fill(BG_COLOR)
                
                # Draw a rounded frame around the active playing board grid
                grid_pixel_width = self.grid_size * (self.cell_size + MARGIN) - MARGIN
                grid_x = (self.width - grid_pixel_width) // 2
                grid_y = TOP_BAR_HEIGHT + MARGIN
                grid_frame = pygame.Rect(grid_x - 10, grid_y - 10, grid_pixel_width + 20, grid_pixel_width + 20)
                pygame.draw.rect(self.screen, GRID_BG_COLOR, grid_frame, border_radius=12)
                pygame.draw.rect(self.screen, (38, 41, 54), grid_frame, width=2, border_radius=12)
                
                self.draw_ui()

                # Render playing grid
                for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        self.grid[r][c].draw(self.screen, self.font, self.game_over, self.won, self.cell_size)

            # Update & Draw particles on top of visual states
            self.update_particles()
            for p in self.particles:
                p.draw(self.screen)

            # Spawn ongoing celebratory confetti
            if self.state == "PLAYING" and self.won and random.random() < 0.22:
                for _ in range(3):
                    px = random.randint(0, self.width)
                    py = -10
                    dx = random.uniform(-0.5, 0.5)
                    dy = random.uniform(1.2, 3.0)
                    color = random.choice([
                        (59, 130, 246), (16, 185, 129), (239, 68, 68),
                        (245, 158, 11), (139, 92, 246), (236, 72, 153)
                    ])
                    size = random.uniform(4, 7)
                    lifetime = random.randint(120, 180)
                    self.particles.append(Particle(px, py, dx, dy, color, size, lifetime, "confetti"))

            # Render End Game statistics overlay modal
            if self.state == "PLAYING":
                self.draw_modal()

            # Process state transitions mask overlays
            self.handle_transition_and_overlay()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()
