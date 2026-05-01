import pygame
import random
import time
import sys

# --- Configuration & Constants ---
MODES = {
    "Easy": {"grid": 10, "mines": 10, "cell_size": 45},
    "Medium": {"grid": 15, "mines": 35, "cell_size": 35},
    "Hard": {"grid": 20, "mines": 80, "cell_size": 30},
    "Extreme": {"grid": 25, "mines": 150, "cell_size": 25}
}

# Default initial values
WIDTH, HEIGHT = 600, 700
GRID_SIZE = 15
CELL_SIZE = 35
MARGIN = 5
TOP_BAR_HEIGHT = 100
NUM_MINES = 35

# Colors
BG_COLOR = (18, 18, 18)
CELL_COLOR = (45, 45, 45)
CELL_HOVER = (60, 60, 60)
REVEALED_COLOR = (30, 30, 30)
MINE_COLOR = (255, 60, 60)
FLAG_COLOR = (255, 200, 0)
TEXT_COLOR = (230, 230, 230)

# Number Colors
NUM_COLORS = {
    1: (66, 133, 244),   # Blue
    2: (52, 168, 83),    # Green
    3: (234, 67, 53),    # Red
    4: (123, 31, 162),   # Purple
    5: (255, 133, 0),    # Orange
    6: (0, 150, 136),    # Teal
    7: (0, 0, 0),        # Black
    8: (121, 85, 72)     # Brown
}

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

    def draw(self, screen, font, game_over, won, cell_size):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)

        color = CELL_COLOR
        if self.is_revealed:
            color = REVEALED_COLOR
        elif is_hover and not game_over and not won:
            color = CELL_HOVER

        pygame.draw.rect(screen, color, self.rect, border_radius=4)

        if self.is_revealed:
            if self.is_mine:
                pygame.draw.circle(screen, MINE_COLOR, self.rect.center, cell_size // 3)
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, NUM_COLORS.get(self.adjacent_mines, TEXT_COLOR))
                text_rect = text.get_rect(center=self.rect.center)
                screen.blit(text, text_rect)
        elif self.is_flagged:
            # Draw a simple flag
            points = [
                (self.rect.centerx - 5, self.rect.centery + 8),
                (self.rect.centerx - 5, self.rect.centery - 8),
                (self.rect.centerx + 8, self.rect.centery - 4),
                (self.rect.centerx - 5, self.rect.centery)
            ]
            pygame.draw.polygon(screen, FLAG_COLOR, points)
            pygame.draw.line(screen, FLAG_COLOR, (self.rect.centerx - 5, self.rect.centery - 8), (self.rect.centerx - 5, self.rect.centery + 10), 2)

        # Show mines if game lost
        if game_over and self.is_mine and not self.is_revealed:
            pygame.draw.circle(screen, (100, 0, 0), self.rect.center, cell_size // 4)

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
        self.font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.ui_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.menu_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.clock = pygame.time.Clock()
        self.reset()

    def select_mode(self, mode_name):
        self.current_mode = mode_name
        self.grid_size = MODES[mode_name]["grid"]
        self.num_mines = MODES[mode_name]["mines"]
        self.cell_size = MODES[mode_name]["cell_size"]
        
        # Calculate window size based on grid
        grid_pixel_width = self.grid_size * (self.cell_size + MARGIN) + MARGIN
        self.width = max(600, grid_pixel_width + 40)
        self.height = grid_pixel_width + TOP_BAR_HEIGHT + 40
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.state = "PLAYING"
        self.reset()

    def reset(self):
        self.grid = [[Cell(r, c, self.grid_size, self.cell_size, self.width) for c in range(self.grid_size)] for r in range(self.grid_size)]
        self.mines_placed = False
        self.game_over = False
        self.won = False
        self.start_time = None
        self.elapsed_time = 0
        self.flags_used = 0

    def place_mines(self, start_r, start_c):
        cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        # Don't place mine on the first clicked cell or its neighbors
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

        if cell.is_mine:
            self.game_over = True
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

    def draw_ui(self):
        # Top Bar Background
        pygame.draw.rect(self.screen, (25, 25, 25), (0, 0, self.width, TOP_BAR_HEIGHT))
        
        # Mine Counter
        mine_text = self.ui_font.render(f"Mines: {self.num_mines - self.flags_used}", True, FLAG_COLOR)
        self.screen.blit(mine_text, (30, 30))

        # Timer
        if self.start_time and not self.game_over and not self.won:
            self.elapsed_time = int(time.time() - self.start_time)
        
        timer_text = self.ui_font.render(f"Time: {self.elapsed_time}s", True, TEXT_COLOR)
        timer_rect = timer_text.get_rect(right=self.width - 30, top=30)
        self.screen.blit(timer_text, timer_rect)

        # Status Message
        if self.game_over:
            msg = "BOOM! Game Over"
            color = MINE_COLOR
        elif self.won:
            msg = "VICTORY!"
            color = (0, 255, 0)
        else:
            msg = "Minesweeper"
            color = TEXT_COLOR
        
        status_text = self.ui_font.render(msg, True, color)
        status_rect = status_text.get_rect(center=(self.width // 2, TOP_BAR_HEIGHT // 2))
        self.screen.blit(status_text, status_rect)

        # Restart Instruction
        if self.game_over or self.won:
            restart_font = pygame.font.SysFont("Segoe UI", 16)
            restart_text = restart_font.render("Press R to Restart | M for Menu", True, (150, 150, 150))
            restart_rect = restart_text.get_rect(center=(self.width // 2, TOP_BAR_HEIGHT - 15))
            self.screen.blit(restart_text, restart_rect)

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        title = self.menu_font.render("Minesweeper Premium", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title, title_rect)

        y_offset = 280
        mouse_pos = pygame.mouse.get_pos()
        self.menu_buttons = {}

        for mode in MODES:
            color = CELL_COLOR
            text_color = TEXT_COLOR
            rect = pygame.Rect(self.width // 2 - 100, y_offset, 200, 50)
            
            if rect.collidepoint(mouse_pos):
                color = CELL_HOVER
                text_color = (255, 255, 255)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            mode_text = self.font.render(mode, True, text_color)
            mode_rect = mode_text.get_rect(center=rect.center)
            self.screen.blit(mode_text, mode_rect)
            
            self.menu_buttons[mode] = rect
            y_offset += 70

    def run(self):
        running = True
        while running:
            if self.state == "MENU":
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for mode, rect in self.menu_buttons.items():
                                if rect.collidepoint(event.pos):
                                    self.select_mode(mode)
            else:
                self.screen.fill(BG_COLOR)
                self.draw_ui()

                for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        self.grid[r][c].draw(self.screen, self.font, self.game_over, self.won, self.cell_size)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset()
                        if event.key == pygame.K_m:
                            self.state = "MENU"
                            self.width, self.height = 600, 700
                            self.screen = pygame.display.set_mode((self.width, self.height))

                    if not self.game_over and not self.won:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
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
                                        elif event.button == 3: # Right Click
                                            if not cell.is_revealed:
                                                cell.is_flagged = not cell.is_flagged
                                                self.flags_used += 1 if cell.is_flagged else -1

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()
