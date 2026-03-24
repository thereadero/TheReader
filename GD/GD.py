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
        self.world_x = 250
        self.screen_x = WIDTH // 2
        self.y = 200
        self.width = 30
        self.height = 30
        self.vel = 15
        self.vel_y = 0
        self.gravity = 4.0
        self.jump_strength = 22  # calibrated for block-top reach
        self.floor_y = HEIGHT - self.height
        self.tries = 0
        self.on_ground = False
        self.rotation = 0
        self.target_rotation = 0
        self.rotation_speed = 5
        self.rotating = False

    def update_rotation(self):
        if not self.rotating:
            return
        diff = (self.target_rotation - self.rotation) % 360
        if diff == 0:
            self.rotating = False
            return
        step = min(self.rotation_speed, diff)
        self.rotation = (self.rotation + step) % 360
        if (self.target_rotation - self.rotation) % 360 == 0:
            self.rotation = self.target_rotation
            self.rotating = False

    def draw(self, win):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 255, 0), (0, 0, self.width, self.height))
        rotated = pygame.transform.rotate(surf, self.rotation)
        rect = rotated.get_rect(center=(self.screen_x + self.width // 2, self.y + self.height // 2))
        win.blit(rotated, rect)

def draw_text(surface, text, color, pos, center=False):
    rendered = FONT.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)

def draw_grid(surface, camera_x=0, grid_size=40):
    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (WIDTH, y))


def draw_objects(surface, objects, camera_x=0):
    for obj in objects:
        draw_x = obj['x'] - camera_x
        if obj['type'] == 'block':
            pygame.draw.rect(surface, (0, 0, 255), (draw_x, obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'platform':
            pygame.draw.rect(surface, (0, 255, 0), (draw_x, obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'tall_platform':
            pygame.draw.rect(surface, (0, 200, 200), (draw_x, obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'floor':
            pygame.draw.rect(surface, (100, 100, 100), (draw_x, obj['y'], obj['w'], obj['h']))
        elif obj['type'] == 'spike':
            points = [
                (draw_x + obj['w'] / 2, obj['y']),
                (draw_x, obj['y'] + obj['h']),
                (draw_x + obj['w'], obj['y'] + obj['h'])
            ]
            pygame.draw.polygon(surface, (255, 0, 0), points)

def save_map(objects, path='TheReader/GD/maps.json'):
    with open(path, 'w') as f:
        json.dump(objects, f)


def load_map(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return json.load(f)


def list_save_files():
    saves = []
    for fn in os.listdir('TheReader/GD'):
        if fn.startswith('maps_') and fn.endswith('.json'):
            saves.append(fn)
    saves.sort()
    return saves

start_button = Button((300, 180, 200, 50), "Start")
saves_button = Button((300, 250, 200, 50), "Saves")
back_button = Button((30, 40, 100, 40), "back")
build_button = Button((300, 320, 200, 50), "Build")
save_button = Button((WIDTH - 120, 40, 100, 40), "Save")
clear_button = Button((140, 40, 100, 40), "Clear")


def main():
    global selected_type, objects
    pygame.init()
    clock = pygame.time.Clock()

    state = "menu"  # menu, game, saves, build, save_name
    cube = Cube()
    save_name = ""
    selected_save_index = 0

    run = True
    while run:
        camera_x = cube.world_x - cube.screen_x
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if state == "menu":
                if start_button.is_clicked(event):
                    state = "game"
                if saves_button.is_clicked(event):
                    save_list = list_save_files()
                    if save_list:
                        selected_save_index = 0
                    state = "saves"
                if build_button.is_clicked(event):
                    state = "build"

            if state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and cube.on_ground:
                    cube.vel_y = -cube.jump_strength
                    cube.target_rotation = (cube.target_rotation + 90) % 360
                    cube.rotating = True

            if state == "save_name":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        save_name = save_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        final_name = save_name.strip().replace(' ', '_') or 'default'
                        path = f"TheReader/GD/maps_{final_name}.json"
                        save_map(objects, path)
                        objects = load_map(path)
                        state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        state = "build"
                    else:
                        if len(save_name) < 20 and event.unicode.isprintable():
                            save_name += event.unicode

            if state == "saves":
                if event.type == pygame.KEYDOWN:
                    save_list = list_save_files()
                    if event.key == pygame.K_UP:
                        selected_save_index = max(0, selected_save_index - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_save_index = min(len(save_list) - 1, selected_save_index + 1)
                    elif event.key == pygame.K_RETURN and save_list:
                        selected = save_list[selected_save_index]
                        objects = load_map(os.path.join('TheReader/GD', selected))
                        state = "game"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"

            if state == "build":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        cube.world_x -= cube.vel
                    elif event.key == pygame.K_d:
                        cube.world_x += cube.vel

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_button.is_clicked(event):
                        state = "menu"
                    elif clear_button.is_clicked(event):
                        objects.clear()
                    elif save_button.is_clicked(event):
                        save_name = ""
                        state = "save_name"
                    else:
                        mx, my = event.pos
                        grid_size = 20
                        world_x = ((mx + cube.world_x - cube.screen_x) // grid_size) * grid_size
                        world_y = (my // grid_size) * grid_size

                        if selected_type == 'platform':
                            h = 20
                            w = 60
                        elif selected_type == 'tall_platform':
                            h = 60
                            w = 60
                        elif selected_type == 'floor':
                            h = 40
                            w = 800
                            world_x = cube.world_x - cube.screen_x
                            world_y = HEIGHT - h
                        elif selected_type == 'spike':
                            h = 60
                            w = 60
                        else:
                            h = 60
                            w = 60

                        objects.append({'type': selected_type, 'x': world_x, 'y': world_y, 'w': w, 'h': h})

        if state == "menu":
                draw_text(WIN, "geometry dash", (255, 255, 255), (WIDTH // 2, 60), center=True)
                start_button.draw(WIN)
                saves_button.draw(WIN)
                build_button.draw(WIN)

        if state == "save_name":
                draw_text(WIN, "Enter save name:", (255, 255, 255), (WIDTH//2, HEIGHT//2 - 40), center=True)
                draw_text(WIN, save_name + "_", (255, 255, 0), (WIDTH//2, HEIGHT//2), center=True)
                draw_text(WIN, "Press Enter to save, Esc to cancel", (180, 180, 180), (WIDTH//2, HEIGHT//2 + 40), center=True)

        if state == "saves":
                draw_text(WIN, "Select save to load", (255, 255, 255), (WIDTH//2, 40), center=True)
                save_list = list_save_files()
                for i, filename in enumerate(save_list):
                    color = (255, 255, 0) if i == selected_save_index else (255, 255, 255)
                    draw_text(WIN, filename, color, (WIDTH//2 - 150, 100 + i * 30))
                draw_text(WIN, "Use Up/Down, Enter to load, Esc to cancel", (180, 180, 180), (WIDTH//2, HEIGHT-40), center=True)

        if state == "game":
            cube.on_ground = False
            cube.update_rotation()
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= cube.vel
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += cube.vel

            new_world_x = cube.world_x + dx
            new_rect = pygame.Rect(new_world_x, cube.y, cube.width, cube.height)
            collision = False
            for obj in objects:
                if obj['type'] in ['block', 'platform', 'tall_platform', 'floor']:
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if new_rect.colliderect(obj_rect):
                        collision = True
                        break
            if not collision:
                cube.world_x = new_world_x

            # Apply gravity (vertical movement independent from horizontal camera scroll)
            cube.vel_y += cube.gravity
            new_y = cube.y + cube.vel_y
            new_rect = pygame.Rect(cube.world_x, new_y, cube.width, cube.height)
            collision = False
            for obj in objects:
                if obj['type'] in ['block', 'platform', 'tall_platform', 'floor']:
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
            cube_rect = pygame.Rect(cube.world_x, cube.y, cube.width, cube.height)
            for obj in objects:
                if obj['type'] == 'spike':
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if cube_rect.colliderect(obj_rect):
                        cube.tries += 1
                        cube.world_x = 250
                        cube.y = 200
                        cube.vel_y = 0
                        cube.on_ground = False
                        break

            camera_x = cube.world_x - cube.screen_x
            draw_objects(WIN, objects, camera_x)
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
            if keys[pygame.K_h]:
                selected_type = 'tall_platform'
            if keys[pygame.K_f]:
                selected_type = 'floor'
            if keys[pygame.K_s]:
                selected_type = 'spike'
            if keys[pygame.K_a]:
                cube.world_x -= cube.vel
            if keys[pygame.K_d]:
                cube.world_x += cube.vel
            if keys[pygame.K_RETURN]:
                save_map(objects)

            draw_grid(WIN, camera_x)
            draw_objects(WIN, objects, camera_x)

            menu_x = 10
            menu_y = 70
            menu_gap = 55
            build_items = [
                ('block', 'Block'),
                ('platform', 'Platform'),
                ('tall_platform', 'Tall'),
                ('floor', 'Floor'),
                ('spike', 'Spike')
            ]
            for i, (t, label) in enumerate(build_items):
                y = menu_y + i * menu_gap
                text_color = (255, 255, 0) if selected_type == t else (255, 255, 255)
                key_labels = {
                    'block': 'B',
                    'platform': 'P',
                    'tall_platform': 'H',
                    'floor': 'F',
                    'spike': 'S'
                }
                draw_text(WIN, f"{key_labels[t]} - {label}", text_color, (menu_x, y))
                icon_x = menu_x + 150
                icon_y = y + 5
                if t == 'block':
                    pygame.draw.rect(WIN, (0, 0, 255), (icon_x, icon_y, 30, 30))
                elif t == 'platform':
                    pygame.draw.rect(WIN, (0, 255, 0), (icon_x, icon_y + 10, 50, 10))
                elif t == 'tall_platform':
                    pygame.draw.rect(WIN, (0, 200, 200), (icon_x, icon_y, 30, 50))
                elif t == 'floor':
                    pygame.draw.rect(WIN, (100, 100, 100), (icon_x, icon_y + 15, 70, 20))
                elif t == 'spike':
                    pygame.draw.polygon(WIN, (255, 0, 0), [(icon_x + 15, icon_y), (icon_x, icon_y + 30), (icon_x + 30, icon_y + 30)])

            draw_text(WIN, f"Selected: {selected_type}", (255, 255, 255), (10, 20))
            draw_text(WIN, "B:Block P:Platform H:Tall F:Floor S:Spike, Enter:Save", (255, 255, 255), (10, 40))
            back_button.draw(WIN)
            clear_button.draw(WIN)
            save_button.draw(WIN)
            if back_button.is_clicked(event):
                state = "menu"

        pygame.display.update()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
