import json
import os
import pygame
import random

pygame.init()
# window settings
WIDTH, HEIGHT = 800, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

FONT = pygame.font.SysFont("Arial", 32)

SAVE_FILE = os.path.join(os.path.dirname(__file__), "saves.json")

# button settings
class Button:
    def __init__(self, rect, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, self.hover_color if is_hover else self.color, self.rect)
        draw_text(surface, self.text, (255, 255, 255), self.rect.center, center=True)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# character starting pos.
GRID_SIZE = 20

class Snake:
    def __init__(self):
        self.body = [(240, 240)] # list of (x, y) coordinates for body segments
        self.direction = (GRID_SIZE, 0)
        self.width = GRID_SIZE
        self.height = GRID_SIZE

    # properties for compatibility with saves
    @property
    def x(self):
        return self.body[0][0]
    
    @x.setter
    def x(self, value):
        self.body[0] = (value, self.body[0][1])

    @property
    def y(self):
        return self.body[0][1]

    @y.setter
    def y(self, value):
        self.body[0] = (self.body[0][0], value)

    def draw(self, win):
        for segment in self.body:
            pygame.draw.rect(win, (0, 255, 0), (segment[0], segment[1], self.width, self.height))

class Food:
    def __init__(self):
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.new_pos()

    def new_pos(self):
        # Generate random position aligned to grid
        self.x = random.randint(0, (WIDTH - self.width) // GRID_SIZE) * GRID_SIZE
        self.y = random.randint(0, (HEIGHT - self.height) // GRID_SIZE) * GRID_SIZE

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, self.width, self.height))

def draw_text(surface, text, color, pos, center=False):
    rendered = FONT.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)

 # loading saves
def load_saves():
    if not os.path.exists(SAVE_FILE):
        return {}
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(name, state):
    saves = load_saves()
    saves[name] = state
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(saves, f, indent=2)


def main():
    pygame.init()
    clock = pygame.time.Clock()

    state = "menu"  # menu, game, upgrades, saves, save_name, settings, achievements
    snake = Snake()
    food = Food()
    score = 0
    move_timer = 0
    move_delay = 150 # ms per movement
    wall_wrap_upgrade = False

    # buttons
    start_button = Button((300, 200, 200, 50), "Start")
    upgrades_button = Button((40, 430, 200, 50), "Upgrades Tree")
    wall_wrap_button = Button((250, 200, 300, 50), "Wall Wrap (Cost: 200)")
    saves_button = Button((300, 260, 200, 50), "Saves")
    exit_button = Button((300, 320, 200, 50), "Exit")
    achievement_button = Button((560, 430, 200, 50), "achievements")
    back_button = Button((20, 20, 120, 40), "Back")
    settings_button = Button((560, 40, 200, 50), "settings")

    selected_save = None

    run = True
    while run:
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            # button states
            if state == "menu":
                if start_button.is_clicked(event):
                    state = "game"
                elif upgrades_button.is_clicked(event):
                    state = "upgrades"
                elif saves_button.is_clicked(event):
                    state = "saves"
                elif settings_button.is_clicked(event):
                    state = "settings"
                elif achievement_button.is_clicked(event):
                    state = "achievements"
                elif exit_button.is_clicked(event):
                    run = False
            elif state == "game":
                if back_button.is_clicked(event):
                    state = "menu"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        state = "save_state"
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and snake.direction[0] == 0:
                        snake.direction = (-GRID_SIZE, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and snake.direction[0] == 0:
                        snake.direction = (GRID_SIZE, 0)
                    elif event.key in (pygame.K_UP, pygame.K_w) and snake.direction[1] == 0:
                        snake.direction = (0, -GRID_SIZE)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and snake.direction[1] == 0:
                        snake.direction = (0, GRID_SIZE)
                # allow saving using L key
                #if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                   # save_state("quick", {"x": snake.x, "y": snake.y})
            elif state == "upgrades":
                if back_button.is_clicked(event):
                    state = "menu"
                if not wall_wrap_upgrade and wall_wrap_button.is_clicked(event):
                    if score >= 200:
                        score -= 200
                        wall_wrap_upgrade = True
                        wall_wrap_button.text = "Wall Wrap (Purchased!)"
                        wall_wrap_button.color = (50, 150, 50) # make it green to show it's active
            elif state == "achievements":
                if back_button.is_clicked(event):
                    state = "menu"
            elif state == "settings":
                if back_button.is_clicked(event):
                    state = "menu" 
            elif state == "saves":
                if back_button.is_clicked(event):
                    state = "menu"
                # saves creation function
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    saves = load_saves()
                    for idx, key in enumerate(sorted(saves.keys())):
                        rect = pygame.Rect(150, 120 + idx * 45, 200, 40)
                        if rect.collidepoint(event.pos):
                            data = saves[key]
                            snake.x = data.get("x", snake.x)
                            snake.y = data.get("y", snake.y)
                            state = "game"
                            break
        # buttons visible in menu
        if state == "menu":
            draw_text(WIN, "Snake Game", (255, 255, 255), (WIDTH // 2, 60), center=True)
            start_button.draw(WIN)
            upgrades_button.draw(WIN)
            saves_button.draw(WIN)
            achievement_button.draw(WIN)
            exit_button.draw(WIN)
            settings_button.draw(WIN)
        elif state == "game":
            # Grid pattern drawing
            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(WIN, (30, 30, 30), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(WIN, (30, 30, 30), (0, y), (WIDTH, y))

            # timer-based movement
            dt = clock.get_time()
            move_timer += dt
            if move_timer >= move_delay:
                move_timer = 0
                head_x, head_y = snake.body[0]
                new_head = (head_x + snake.direction[0], head_y + snake.direction[1])
                
                # Apply wall wrap upgrade physics
                if wall_wrap_upgrade:
                    nx, ny = new_head
                    if nx < 0:
                        nx = WIDTH - GRID_SIZE
                    elif nx >= WIDTH:
                        nx = 0
                        
                    if ny < 0:
                        ny = HEIGHT - GRID_SIZE
                    elif ny >= HEIGHT:
                        ny = 0
                    new_head = (nx, ny)

                snake.body.insert(0, new_head)
                
                # Check collision with food
                if (new_head[0] < food.x + food.width and new_head[0] + snake.width > food.x and
                    new_head[1] < food.y + food.height and new_head[1] + snake.height > food.y):
                    score += 1
                    food.new_pos()
                else:
                    snake.body.pop() # remove tail if no food eaten

            # text messages
            draw_text(WIN, f"Score: {score}", (255, 255, 255), (WIDTH - 150, 10))
            draw_text(WIN, "Press L to save quick slot", (200, 200, 200), (10, HEIGHT - 30))
            back_button.draw(WIN)
            food.draw(WIN)
            snake.draw(WIN)
        elif state == "achievements":
            draw_text(WIN, "achievements", (255, 255, 255), (WIDTH // 2, 60), center=True)
            back_button.draw(WIN)
        elif state == "upgrades":
            draw_text(WIN, f"Upgrades Tree (Points Available: {score})", (255, 255, 255), (WIDTH // 2, 60), center=True)
            wall_wrap_button.draw(WIN)
            back_button.draw(WIN)
        elif state == "settings":
            back_button.draw(WIN)
            draw_text(WIN,"fps \n (placeholders) \n color",(255, 255, 255), (WIDTH // 2, 60), center=True)
        elif state == "save_state":
            draw_text(WIN, "name the save", (255, 255, 255), (WIDTH // 2, 60), center=True)
        elif state == "saves":
            draw_text(WIN, "Saves", (255, 255, 255), (WIDTH // 2, 60), center=True)
            saves = load_saves()
            if not saves:
                draw_text(WIN, "No saves yet. Press L in-game to save.", (200, 200, 200), (WIDTH // 2, 150), center=True)
            else:
                for idx, key in enumerate(sorted(saves.keys())):
                    rect = pygame.Rect(150, 120 + idx * 45, 200, 40)
                    pygame.draw.rect(WIN, (100, 100, 100), rect)
                    draw_text(WIN, key, (255, 255, 255), rect.center, center=True)
                draw_text(WIN, "Click a save to load it.", (200, 200, 200), (WIDTH // 2, HEIGHT - 40), center=True)
            back_button.draw(WIN)

        pygame.display.update()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
