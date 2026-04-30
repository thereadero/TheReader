import pygame
import random
import time
import sys

# --- Configuration & Constants ---
WIDTH, HEIGHT = 600, 700
GRID_SIZE = 15  # 15x15 grid
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
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
        self.rect = pygame.Rect(
            c * (CELL_SIZE + MARGIN) + (WIDTH - (GRID_SIZE * (CELL_SIZE + MARGIN))) // 2,
            r * (CELL_SIZE + MARGIN) + TOP_BAR_HEIGHT + MARGIN,
            CELL_SIZE,
            CELL_SIZE
        )

    def draw(self, screen, font, game_over, won):
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
                pygame.draw.circle(screen, MINE_COLOR, self.rect.center, CELL_SIZE // 3)
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
            pygame.draw.circle(screen, (100, 0, 0), self.rect.center, CELL_SIZE // 4)

class Minesweeper:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Minesweeper Premium")
        self.font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.ui_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.mines_placed = False
        self.game_over = False
        self.won = False
        self.start_time = None
        self.elapsed_time = 0
        self.flags_used = 0

    def place_mines(self, start_r, start_c):
        cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        # Don't place mine on the first clicked cell or its neighbors
        safe_zone = [(start_r + dr, start_c + dc) for dr in range(-1, 2) for dc in range(-1, 2)]
        cells = [cell for cell in cells if cell not in safe_zone]
        
        mine_pos = random.sample(cells, NUM_MINES)
        for r, c in mine_pos:
            self.grid[r][c].is_mine = True

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if not self.grid[r][c].is_mine:
                    count = 0
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and self.grid[nr][nc].is_mine:
                                count += 1
                    self.grid[r][c].adjacent_mines = count
        
        self.mines_placed = True
        self.start_time = time.time()

    def reveal(self, r, c):
        if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
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
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell = self.grid[r][c]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    def draw_ui(self):
        # Top Bar Background
        pygame.draw.rect(self.screen, (25, 25, 25), (0, 0, WIDTH, TOP_BAR_HEIGHT))
        
        # Mine Counter
        mine_text = self.ui_font.render(f"Mines: {NUM_MINES - self.flags_used}", True, FLAG_COLOR)
        self.screen.blit(mine_text, (30, 30))

        # Timer
        if self.start_time and not self.game_over and not self.won:
            self.elapsed_time = int(time.time() - self.start_time)
        
        timer_text = self.ui_font.render(f"Time: {self.elapsed_time}s", True, TEXT_COLOR)
        timer_rect = timer_text.get_rect(right=WIDTH - 30, top=30)
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
        status_rect = status_text.get_rect(center=(WIDTH // 2, TOP_BAR_HEIGHT // 2))
        self.screen.blit(status_text, status_rect)

        # Restart Instruction
        if self.game_over or self.won:
            restart_font = pygame.font.SysFont("Segoe UI", 16)
            restart_text = restart_font.render("Press R to Restart", True, (150, 150, 150))
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, TOP_BAR_HEIGHT - 15))
            self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            self.screen.fill(BG_COLOR)
            self.draw_ui()

            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self.grid[r][c].draw(self.screen, self.font, self.game_over, self.won)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()

                if not self.game_over and not self.won:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        for r in range(GRID_SIZE):
                            for c in range(GRID_SIZE):
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
