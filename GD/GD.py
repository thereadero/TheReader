import json
import pygame
import os

pygame.init()
# window setting
WIDTH, HEIGHT = 800, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Arial", 32)

objects = []
selected_type = 'block'

try:
    with open('TheReader/GD/maps.json', 'r') as f:
        objects = json.load(f)
except:
    objects = []



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
    
class Cube:
    def __init__(self):
        self.x = 250
        self.y = 200
        self.width = 30
        self.height = 30
        self.vel = 15
        self.vel_y = 0
        self.gravity = 1.5
        self.jump_strength = 30
        self.floor_y = HEIGHT - self.height
        self.tries = 0
        self.on_ground = False
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

def draw_objects(surface, objects):
    for obj in objects:
        if obj['type'] == 'block':
            pygame.draw.rect(surface, (0, 0, 255), (obj['x'], obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'platform':
            pygame.draw.rect(surface, (0, 255, 0), (obj['x'], obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'spike':
            pygame.draw.rect(surface, (255, 0, 0), (obj['x'], obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'triangle':
            points = [(obj['x'] + obj['w']/2, obj['y']), (obj['x'], obj['y'] + obj['h']), (obj['x'] + obj['w'], obj['y'] + obj['h'])]
            pygame.draw.polygon(surface, (255, 0, 0), points)

def save_map(objects):
    with open('TheReader/GD/maps.json', 'w') as f:
        json.dump(objects, f)

start_button = Button((300, 200, 200, 50), "Start")
back_button = Button((30, 40, 100, 40), "back")
build_button = Button((300, 270, 200, 50), "Build")
clear_button = Button((140, 40, 100, 40), "Clear")


def main():
    global selected_type, objects
    pygame.init()
    clock = pygame.time.Clock()

    state = "menu"  # menu, game, upgrades, saves, save_name
    cube = Cube()


    run = True
    while run:
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if state == "menu":
                if start_button.is_clicked(event):
                    state = "game"
                if build_button.is_clicked(event):
                    state = "build"

            if state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and cube.on_ground:
                    cube.vel_y = -cube.jump_strength

            if state == "build":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    h = 20 if selected_type == 'platform' else 60
                    objects.append({'type': selected_type, 'x': mx, 'y': my, 'w': 60, 'h': h})
                if clear_button.is_clicked(event):
                    objects.clear()

        if state == "menu":
                draw_text(WIN, "geometry dash", (255, 255, 255), (WIDTH // 2, 60), center=True)
                start_button.draw(WIN)
                build_button.draw(WIN)

        if state == "game":
            cube.on_ground = False
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= cube.vel
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += cube.vel

            new_x = cube.x + dx
            new_rect = pygame.Rect(new_x, cube.y, cube.width, cube.height)
            collision = False
            for obj in objects:
                if obj['type'] in ['block', 'platform']:
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if new_rect.colliderect(obj_rect):
                        collision = True
                        break
            if not collision:
                cube.x = new_x

            # Apply gravity
            cube.vel_y += cube.gravity
            new_y = cube.y + cube.vel_y
            new_rect = pygame.Rect(cube.x, new_y, cube.width, cube.height)
            collision = False
            for obj in objects:
                if obj['type'] in ['block', 'platform']:
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if new_rect.colliderect(obj_rect):
                        if cube.vel_y > 0:  # falling down
                            cube.y = obj['y'] - cube.height
                            cube.vel_y = 0
                            cube.on_ground = True
                        elif cube.vel_y < 0:  # moving up
                            cube.y = obj['y'] + obj['h']
                            cube.vel_y = 0
                        collision = True
                        break
            if not collision:
                cube.y = new_y

            # Floor collision
            if cube.y + cube.height > cube.floor_y:
                cube.y = cube.floor_y - cube.height
                cube.vel_y = 0
                cube.on_ground = True

            # Check spike collision
            cube_rect = pygame.Rect(cube.x, cube.y, cube.width, cube.height)
            for obj in objects:
                if obj['type'] in ['spike', 'triangle']:
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if cube_rect.colliderect(obj_rect):
                        cube.tries += 1
                        cube.x = 250
                        cube.y = 200
                        cube.vel_y = 0
                        break

            draw_objects(WIN, objects)
            draw_text(WIN, f"Tries: {cube.tries}", (255, 255, 255), (10, 10))
            back_button.draw(WIN)
            cube.draw(WIN)
            if back_button.is_clicked(event):
                state = "menu"

        if state == "build":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_b]:
                selected_type = 'block'
            if keys[pygame.K_p]:
                selected_type = 'platform'
            if keys[pygame.K_s]:
                selected_type = 'spike'
            if keys[pygame.K_t]:
                selected_type = 'triangle'
            if keys[pygame.K_RETURN]:
                save_map(objects)

            draw_objects(WIN, objects)
            draw_text(WIN, f"Selected: {selected_type}", (255, 255, 255), (10, 10))
            draw_text(WIN, "Press B/P/S/T for Block/Platform/Spike/Triangle, Enter to Save", (255, 255, 255), (10, 40))
            back_button.draw(WIN)
            clear_button.draw(WIN)
            if back_button.is_clicked(event):
                state = "menu"

        pygame.display.update()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
