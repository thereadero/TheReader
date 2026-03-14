import json
import os
import pygame

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
class Snake:
    def __init__(self):
        self.x = 250
        self.y = 250
        self.width = 10
        self.height = 10
        self.vel = 5

    def draw(self, win):
        pygame.draw.rect(win, (0, 255, 0), (self.x, self.y, self.width, self.height))


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

    state = "menu"  # menu, game, upgrades, saves
    snake = Snake()

    # buttons
    start_button = Button((300, 200, 200, 50), "Start")
    upgrades_button = Button((40, 430, 200, 50), "Upgrades Tree")
    saves_button = Button((300, 260, 200, 50), "Saves")
    exit_button = Button((300, 320, 200, 50), "Exit")
    achievement_button = Button((560, 430, 200, 50), "achievements")
    back_button = Button((20, 20, 120, 40), "Back")

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
                elif achievement_button.is_clicked(event):
                    state = "achievements"
                elif exit_button.is_clicked(event):
                    run = False
            elif state == "game":
                if back_button.is_clicked(event):
                    state = "menu"
                # allow saving using L key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    save_state("quick", {"x": snake.x, "y": snake.y})
            elif state == "upgrades":
                if back_button.is_clicked(event):
                    state = "menu"
            elif state == "saves":
                if back_button.is_clicked(event):
                    state = "menu"
            elif state == "achievements":
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
        # keys for moving the character
        elif state == "game":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                snake.x -= snake.vel
            if keys[pygame.K_a]:
                snake.x -= snake.vel
            if keys[pygame.K_RIGHT]:
                snake.x += snake.vel
            if keys[pygame.K_d]:
                snake.x += snake.vel
            if keys[pygame.K_UP]:
                snake.y -= snake.vel
            if keys[pygame.K_w]:
                snake.y -= snake.vel
            if keys[pygame.K_DOWN]:
                snake.y += snake.vel
            if keys[pygame.K_s]:
                snake.y += snake.vel
            # text messages
            draw_text(WIN, "Press L to save quick slot", (200, 200, 200), (10, HEIGHT - 30))
            back_button.draw(WIN)
            snake.draw(WIN)
        elif state == "achievements":
            draw_text(WIN, "achievements", (255, 255, 255), (WIDTH // 2, 60), center=True)
            back_button.draw(WIN)
        elif state == "upgrades":
            draw_text(WIN, "Upgrades Tree (placeholder)", (255, 255, 255), (WIDTH // 2, 60), center=True)
            draw_text(WIN, "- No upgrades implemented yet.\n- Use this screen to add upgrades.", (200, 200, 200), (WIDTH // 2, 150), center=True)
            back_button.draw(WIN)
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
