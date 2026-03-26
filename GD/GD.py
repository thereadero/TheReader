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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

spawn_x = 250
spawn_y = 200

try:
    with open(os.path.join(SCRIPT_DIR, 'maps.json'), 'r') as f:
        objects = json.load(f)
        for obj in objects:
            if obj['type'] == 'spawn':
                spawn_x = obj['x']
                spawn_y = obj['y']
                break
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
        self.jump_strength = 36  # 25% more than 22
        self.floor_y = HEIGHT - self.height
        self.tries = 0
        self.on_ground = False
        self.rotation = 0
        self.target_rotation = 0
        self.rotation_speed = 5
        self.rotating = False
        self.style = "green"
        self.shape = "cube"

    def update_rotation(self):
        if not self.rotating:
            return
        if self.rotation > self.target_rotation:
            self.rotation = max(self.target_rotation, self.rotation - self.rotation_speed)
        elif self.rotation < self.target_rotation:
            self.rotation = min(self.target_rotation, self.rotation + self.rotation_speed)
            
        if self.rotation == self.target_rotation:
            self.rotating = False
            self.rotation %= 360
            self.target_rotation %= 360

    def draw(self, win):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if getattr(self, 'style', 'green') == "green":
            color = (0, 255, 0)
        elif self.style == "red":
            color = (255, 0, 0)
        elif self.style == "blue":
            color = (0, 150, 255)
        elif self.style == "face":
            color = (255, 255, 0)
        else:
            color = (0, 255, 0)

        shape = getattr(self, 'shape', 'cube')
        w, h = self.width, self.height
        if shape == 'circle':
            pygame.draw.circle(surf, color, (w//2, h//2), w//2)
        elif shape == 'triangle':
            pygame.draw.polygon(surf, color, [(w//2, 0), (0, h), (w, h)])
        elif shape == 'rectangle':
            pygame.draw.rect(surf, color, (0, 0, w, h))
        else:
            pygame.draw.rect(surf, color, (0, 0, w, h))

        if shape == 'triangle':
            pygame.draw.rect(surf, (0, 0, 0), (int(w*0.35), int(h*0.4), int(w*0.1), int(h*0.15)))
            pygame.draw.rect(surf, (0, 0, 0), (int(w*0.55), int(h*0.4), int(w*0.1), int(h*0.15)))
            pygame.draw.rect(surf, (0, 0, 0), (int(w*0.3), int(h*0.7), int(w*0.4), int(h*0.1)))
        else:
            pygame.draw.rect(surf, (0, 0, 0), (int(w*0.2), int(h*0.25), int(w*0.2), int(h*0.2)))
            pygame.draw.rect(surf, (0, 0, 0), (int(w*0.6), int(h*0.25), int(w*0.2), int(h*0.2)))
            pygame.draw.rect(surf, (0, 0, 0), (int(w*0.2), int(h*0.65), int(w*0.6), int(h*0.15)))

        rotated = pygame.transform.rotate(surf, self.rotation)
        rect = rotated.get_rect(center=(self.screen_x + self.width // 2, self.y + self.height // 2))
        win.blit(rotated, rect)

def get_shape_mask_and_rect(cube, x, y):
    surf = pygame.Surface((cube.width, cube.height), pygame.SRCALPHA)
    shape = getattr(cube, 'shape', 'cube')
    w, h = cube.width, cube.height
    if shape == 'circle':
        pygame.draw.circle(surf, (255, 255, 255), (w//2, h//2), w//2)
    elif shape == 'triangle':
        pygame.draw.polygon(surf, (255, 255, 255), [(w//2, 0), (0, h), (w, h)])
    elif shape == 'rectangle':
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, w, h))
    else:
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, w, h))
    
    rotated = pygame.transform.rotate(surf, cube.rotation)
    mask = pygame.mask.from_surface(rotated)
    rect = rotated.get_rect(center=(int(x + cube.width // 2), int(y + cube.height // 2)))
    return mask, rect

def draw_text(surface, text, color, pos, center=False):
    rendered = FONT.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)

def draw_grid(surface, camera_x=0, grid_size=30):
    offset_x = -camera_x % grid_size
    for x in range(int(offset_x), WIDTH, grid_size):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (WIDTH, y))


def draw_objects(surface, objects, camera_x=0, show_spawn=True):
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
        elif obj['type'] == 'spawn' and show_spawn:
            draw_text(surface, "SPAWN", (0, 255, 255), (draw_x + 30, obj['y']))
        elif obj['type'] == 'end':
            glow_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 0, 80), (150, 150), 80)
            pygame.draw.circle(glow_surf, (255, 255, 0, 40), (150, 150), 100)
            surface.blit(glow_surf, (draw_x + obj['w']//2 - 150, obj['y'] + obj['h']//2 - 150))
            draw_text(surface, "END", (255, 255, 255), (draw_x + obj['w']//2, obj['y'] + obj['h']//2), center=True)
        elif obj['type'] == 'ramp':
            points = [
                (draw_x, obj['y'] + obj['h']),
                (draw_x + obj['w'], obj['y'] + obj['h']),
                (draw_x + obj['w'], obj['y'])
            ]
            pygame.draw.polygon(surface, (0, 150, 0), points)

def save_map(objects, path='maps.json'):
    full_path = os.path.join(SCRIPT_DIR, path)
    with open(full_path, 'w') as f:
        json.dump(objects, f)


def load_map(path):
    full_path = os.path.join(SCRIPT_DIR, path)
    if not os.path.exists(full_path):
        return []
    with open(full_path, 'r') as f:
        return json.load(f)


def list_save_files():
    saves = []
    for fn in os.listdir(SCRIPT_DIR):
        if fn.startswith('maps_') and fn.endswith('.json'):
            saves.append(fn)
    saves.sort()
    return saves

start_button = Button((300, 160, 200, 50), "Start")
saves_button = Button((300, 230, 200, 50), "Saves")
build_button = Button((300, 300, 200, 50), "Build")
cust_button = Button((300, 370, 200, 50), "Customize")
back_button = Button((10, 10, 100, 40), "Back")
save_button = Button((WIDTH - 110, 10, 100, 40), "Save")
clear_button = Button((120, 10, 100, 40), "Clear")

btn_green = Button((150, 220, 100, 50), "Green", color=(0, 200, 0), hover_color=(0, 255, 0))
btn_red = Button((270, 220, 100, 50), "Red", color=(200, 0, 0), hover_color=(255, 0, 0))
btn_blue = Button((390, 220, 100, 50), "Blue", color=(0, 100, 200), hover_color=(0, 150, 255))
btn_face = Button((510, 220, 100, 50), "Yellow (Face)", color=(200, 200, 0), hover_color=(255, 255, 0))

btn_shape_cube = Button((150, 280, 100, 50), "Cube", color=(100, 100, 100))
btn_shape_circle = Button((270, 280, 100, 50), "Circle", color=(100, 100, 100))
btn_shape_rect = Button((390, 280, 100, 50), "Rect", color=(100, 100, 100))
btn_shape_tri = Button((510, 280, 100, 50), "Triangle", color=(100, 100, 100))

build_cat_blocks = Button((10, 70, 120, 40), "Blocks", color=(50, 50, 100))
build_cat_enemy = Button((10, 120, 120, 40), "Enemy", color=(100, 50, 50))
build_cat_misc = Button((10, 170, 120, 40), "Misc", color=(50, 100, 50))

def main():
    global selected_type, objects, spawn_x, spawn_y
    pygame.init()
    clock = pygame.time.Clock()

    state = "menu"  # menu, game, saves, build, save_name
    cube = Cube()
    save_name = ""
    selected_save_index = 0
    current_build_category = 'blocks'

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
                if cust_button.is_clicked(event):
                    state = "customize"

            elif state == "customize":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_button.is_clicked(event):
                        state = "menu"
                    if btn_green.is_clicked(event):
                        cube.style = "green"
                    if btn_red.is_clicked(event):
                        cube.style = "red"
                    if btn_blue.is_clicked(event):
                        cube.style = "blue"
                    if btn_face.is_clicked(event):
                        cube.style = "face"
                        
                    if btn_shape_cube.is_clicked(event):
                        cube.shape = 'cube'
                        cube.width = 30
                        cube.height = 30
                        cube.jump_strength = 36
                        cube.floor_y = HEIGHT - cube.height
                    if btn_shape_circle.is_clicked(event):
                        cube.shape = 'circle'
                        cube.width = 30
                        cube.height = 30
                        cube.jump_strength = 45
                        cube.floor_y = HEIGHT - cube.height
                    if btn_shape_rect.is_clicked(event):
                        cube.shape = 'rectangle'
                        cube.width = 40
                        cube.height = 20
                        cube.jump_strength = 28
                        cube.floor_y = HEIGHT - cube.height
                    if btn_shape_tri.is_clicked(event):
                        cube.shape = 'triangle'
                        cube.width = 30
                        cube.height = 30
                        cube.jump_strength = 32
                        cube.floor_y = HEIGHT - cube.height

            elif state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and cube.on_ground:
                    cube.vel_y = -cube.jump_strength
                    cube.target_rotation -= 90
                    cube.rotating = True

            elif state == "save_name":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        save_name = save_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        final_name = save_name.strip().replace(' ', '_') or 'default'
                        path = f"maps_{final_name}.json"
                        save_map(objects, path)
                        objects = load_map(path)
                        state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        state = "build"
                    else:
                        if len(save_name) < 20 and event.unicode.isprintable():
                            save_name += event.unicode

            elif state == "saves":
                if event.type == pygame.KEYDOWN:
                    save_list = list_save_files()
                    if event.key == pygame.K_UP:
                        selected_save_index = max(0, selected_save_index - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_save_index = min(len(save_list) - 1, selected_save_index + 1)
                    elif event.key == pygame.K_RETURN and save_list:
                        selected = save_list[selected_save_index]
                        objects = load_map(selected)
                        state = "game"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_button.is_clicked(event):
                        state = "menu"

            elif state == "build":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        cube.world_x -= cube.vel
                    elif event.key == pygame.K_d:
                        cube.world_x += cube.vel

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if back_button.is_clicked(event):
                            state = "menu"
                        elif build_cat_blocks.is_clicked(event):
                            if current_build_category == 'blocks':
                                current_build_category = None
                            else:
                                current_build_category = 'blocks'
                                selected_type = 'block'
                        elif build_cat_enemy.is_clicked(event):
                            if current_build_category == 'enemy':
                                current_build_category = None
                            else:
                                current_build_category = 'enemy'
                                selected_type = 'spike'
                        elif build_cat_misc.is_clicked(event):
                            if current_build_category == 'miscellaneous':
                                current_build_category = None
                            else:
                                current_build_category = 'miscellaneous'
                                selected_type = 'spawn'
                        elif clear_button.is_clicked(event):
                            objects.clear()
                        elif save_button.is_clicked(event):
                            save_name = ""
                            state = "save_name"
                        else:
                            mx, my = event.pos
                            grid_size = 30
                            world_x = ((mx + camera_x) // grid_size) * grid_size
                            world_y = (my // grid_size) * grid_size

                            if selected_type == 'platform':
                                w = 60
                                h = 20
                            elif selected_type == 'tall_platform':
                                w = 60
                                h = 60
                            elif selected_type == 'floor':
                                w = 800
                                h = 40
                                x = world_x
                                y = HEIGHT - h
                                objects.append({'type': selected_type, 'x': x, 'y': y, 'w': w, 'h': h})
                                continue
                            elif selected_type == 'spike':
                                w = 60
                                h = 60
                            elif selected_type == 'spawn':
                                w = 60
                                h = 60
                            elif selected_type == 'end':
                                w = 60
                                h = 60
                            elif selected_type == 'ramp':
                                w = 60
                                h = 60
                            else:  # block
                                w = 60
                                h = 60

                            x = world_x
                            y = world_y
                            if selected_type == 'spawn':
                                spawn_x = world_x
                                spawn_y = world_y
                            objects.append({'type': selected_type, 'x': x, 'y': y, 'w': w, 'h': h})
                    elif event.button == 3:
                        mx, my = event.pos
                        world_x = mx + camera_x
                        world_y = my
                        # Find and remove object at this position
                        for i, obj in enumerate(objects):
                            if obj['x'] <= world_x < obj['x'] + obj['w'] and obj['y'] <= world_y < obj['y'] + obj['h']:
                                del objects[i]
                                break

        if state == "menu":
                draw_text(WIN, "geometry dash", (255, 255, 255), (WIDTH // 2, 60), center=True)
                start_button.draw(WIN)
                saves_button.draw(WIN)
                build_button.draw(WIN)
                cust_button.draw(WIN)

        if state == "customize":
                draw_text(WIN, "Select Character Style", (255, 255, 255), (WIDTH // 2, 70), center=True)
                btn_green.draw(WIN)
                btn_red.draw(WIN)
                btn_blue.draw(WIN)
                btn_face.draw(WIN)
                
                btn_shape_cube.draw(WIN)
                btn_shape_circle.draw(WIN)
                btn_shape_rect.draw(WIN)
                btn_shape_tri.draw(WIN)
                
                back_button.draw(WIN)
                
                # Preview
                w, h = cube.width, cube.height
                st = getattr(cube, 'style', 'green')
                shape = getattr(cube, 'shape', 'cube')
                
                if st == "green":
                    color = (0, 255, 0)
                elif st == "red":
                    color = (255, 0, 0)
                elif st == "blue":
                    color = (0, 150, 255)
                elif st == "face":
                    color = (255, 255, 0)
                else:
                    color = (0, 255, 0)
                
                preview_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                if shape == 'circle':
                    pygame.draw.circle(preview_surf, color, (w//2, h//2), w//2)
                elif shape == 'triangle':
                    pygame.draw.polygon(preview_surf, color, [(w//2, 0), (0, h), (w, h)])
                elif shape == 'rectangle':
                    pygame.draw.rect(preview_surf, color, (0, 0, w, h))
                else:
                    pygame.draw.rect(preview_surf, color, (0, 0, w, h))
                    
                if shape == 'triangle':
                    pygame.draw.rect(preview_surf, (0, 0, 0), (int(w*0.35), int(h*0.4), int(w*0.1), int(h*0.15)))
                    pygame.draw.rect(preview_surf, (0, 0, 0), (int(w*0.55), int(h*0.4), int(w*0.1), int(h*0.15)))
                    pygame.draw.rect(preview_surf, (0, 0, 0), (int(w*0.3), int(h*0.7), int(w*0.4), int(h*0.1)))
                else:
                    pygame.draw.rect(preview_surf, (0, 0, 0), (int(w*0.2), int(h*0.25), int(w*0.2), int(h*0.2)))
                    pygame.draw.rect(preview_surf, (0, 0, 0), (int(w*0.6), int(h*0.25), int(w*0.2), int(h*0.2)))
                    pygame.draw.rect(preview_surf, (0, 0, 0), (int(w*0.2), int(h*0.65), int(w*0.6), int(h*0.15)))
                
                rect = preview_surf.get_rect(center=(WIDTH // 2, 400))
                WIN.blit(preview_surf, rect)

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
                back_button.draw(WIN)

        if state == "game":
            if getattr(cube, 'finished', False):
                camera_x = getattr(cube, 'locked_camera_x', 0)
                cube.vel_y = 0
                target_y = HEIGHT // 2
                if cube.y > target_y:
                    cube.y -= max(1.0, (cube.y - target_y) * 0.1)
                elif cube.y < target_y:
                    cube.y += max(1.0, (target_y - cube.y) * 0.1)
                cube.world_x += 15
                cube.rotation -= 15
                if cube.world_x > camera_x + WIDTH + 50:
                    state = "menu"
                    cube.finished = False
                    cube.world_x = spawn_x
                    cube.y = spawn_y
                    cube.vel_y = 0
                    cube.rotation = 0
                    cube.target_rotation = 0
                
                draw_objects(WIN, objects, camera_x, show_spawn=False)
                cube.draw(WIN)
                pygame.display.update()
                clock.tick(30)
                continue

            cube.on_ground = False
            cube.update_rotation()
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= cube.vel
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += cube.vel

            new_world_x = cube.world_x + dx
            cube_mask, new_rect = get_shape_mask_and_rect(cube, new_world_x, cube.y)
            collision = False
            for obj in objects:
                if obj['type'] in ['block', 'platform', 'tall_platform', 'floor', 'ramp']:
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if new_rect.colliderect(obj_rect):
                        if obj['type'] == 'ramp':
                            ramp_surf = pygame.Surface((obj['w'], obj['h']), pygame.SRCALPHA)
                            pygame.draw.polygon(ramp_surf, (255, 255, 255), [(0, obj['h']), (obj['w'], obj['h']), (obj['w'], 0)])
                            obj_mask = pygame.mask.from_surface(ramp_surf)
                        else:
                            obj_mask = pygame.Mask((obj['w'], obj['h']), fill=True)
                            
                        offset = (int(obj['x'] - new_rect.x), int(obj['y'] - new_rect.y))
                        if cube_mask.overlap(obj_mask, offset):
                            collision = True
                            break
            if not collision:
                cube.world_x = new_world_x

            # Vertical
            cube.vel_y += cube.gravity
            new_y = cube.y + cube.vel_y
            cube_mask, new_rect = get_shape_mask_and_rect(cube, cube.world_x, new_y)
            collision = False
            
            for obj in objects:
                if obj['type'] in ['block', 'platform', 'tall_platform', 'floor', 'ramp']:
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if new_rect.colliderect(obj_rect):
                        if obj['type'] == 'ramp':
                            ramp_surf = pygame.Surface((obj['w'], obj['h']), pygame.SRCALPHA)
                            pygame.draw.polygon(ramp_surf, (255, 255, 255), [(0, obj['h']), (obj['w'], obj['h']), (obj['w'], 0)])
                            obj_mask = pygame.mask.from_surface(ramp_surf)
                        else:
                            obj_mask = pygame.Mask((obj['w'], obj['h']), fill=True)
                            
                        offset = (int(obj['x'] - new_rect.x), int(obj['y'] - new_rect.y))
                        if cube_mask.overlap(obj_mask, offset):
                            if cube.vel_y > 0:  # falling down
                                while cube_mask.overlap(obj_mask, (int(obj['x'] - new_rect.x), int(obj['y'] - new_rect.y))):
                                    new_y -= 1
                                    new_rect.y -= 1
                                cube.y = new_y
                                cube.vel_y = 0
                                cube.on_ground = True
                                collision = True
                            elif cube.vel_y < 0:  # moving up
                                while cube_mask.overlap(obj_mask, (int(obj['x'] - new_rect.x), int(obj['y'] - new_rect.y))):
                                    new_y += 1
                                    new_rect.y += 1
                                cube.y = new_y
                                cube.vel_y = 0
                                collision = True
                            break
                            
            if not collision:
                cube.y = new_y

            # Floor collision
            cube_mask, current_rect = get_shape_mask_and_rect(cube, cube.world_x, cube.y)
            box = cube_mask.get_bounding_rects()
            if box:
                lowest_y = current_rect.y + box[0].bottom
                if lowest_y > HEIGHT:
                    cube.y -= (lowest_y - HEIGHT)
                    cube.vel_y = 0
                    cube.on_ground = True
                    
            if cube.shape == 'circle' and dx != 0 and cube.on_ground:
                cube.rotation -= (dx / (cube.width / 2)) * 30
                cube.rotation %= 360
                cube.target_rotation = cube.rotation

            # Check spike collision
            cube_mask, current_rect = get_shape_mask_and_rect(cube, cube.world_x, cube.y)
            for obj in objects:
                if obj['type'] == 'spike':
                    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['w'], obj['h'])
                    if current_rect.colliderect(obj_rect):
                        spike_surf = pygame.Surface((obj['w'], obj['h']), pygame.SRCALPHA)
                        pygame.draw.polygon(spike_surf, (255, 255, 255), [(obj['w']/2, 0), (0, obj['h']), (obj['w'], obj['h'])])
                        spike_mask = pygame.mask.from_surface(spike_surf)
                        
                        offset = (int(obj['x'] - current_rect.x), int(obj['y'] - current_rect.y))
                        if cube_mask.overlap(spike_mask, offset):
                            cube.tries += 1
                            cube.world_x = spawn_x
                            cube.y = spawn_y
                            cube.vel_y = 0
                            cube.on_ground = False
                            cube.rotation = 0
                            cube.target_rotation = 0
                            break

            for obj in objects:
                if obj['type'] == 'end':
                    radius = 100
                    if cube.world_x > obj['x'] + obj['w']//2 - radius:
                        cube.finished = True
                        cube.locked_camera_x = cube.world_x - cube.screen_x
                        break

            camera_x = cube.world_x - cube.screen_x
            draw_objects(WIN, objects, camera_x, show_spawn=False)
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
            if keys[pygame.K_t]:
                selected_type = 'spawn'
            if keys[pygame.K_e]:
                selected_type = 'end'
            if keys[pygame.K_r]:
                selected_type = 'ramp'
            if keys[pygame.K_a]:
                cube.world_x -= cube.vel
            if keys[pygame.K_d]:
                cube.world_x += cube.vel
            if keys[pygame.K_RETURN]:
                save_map(objects)

            draw_grid(WIN, camera_x)
            draw_objects(WIN, objects, camera_x)

            # Draw silhouette
            mx, my = pygame.mouse.get_pos()
            grid_size = 30
            sil_world_x = ((mx + camera_x) // grid_size) * grid_size
            sil_world_y = (my // grid_size) * grid_size
            sil_draw_x = sil_world_x - camera_x

            sil_surf = pygame.Surface((WIN.get_width(), WIN.get_height()), pygame.SRCALPHA)
            if selected_type == 'block':
                pygame.draw.rect(sil_surf, (0, 0, 255, 128), (sil_draw_x, sil_world_y, 60, 60))
            elif selected_type == 'platform':
                pygame.draw.rect(sil_surf, (0, 255, 0, 128), (sil_draw_x, sil_world_y, 60, 20))
            elif selected_type == 'tall_platform':
                pygame.draw.rect(sil_surf, (0, 200, 200, 128), (sil_draw_x, sil_world_y, 60, 60))
            elif selected_type == 'floor':
                pygame.draw.rect(sil_surf, (100, 100, 100, 128), (sil_draw_x, HEIGHT - 40, 800, 40))
            elif selected_type == 'spike':
                points = [
                    (sil_draw_x + 30, sil_world_y),
                    (sil_draw_x, sil_world_y + 60),
                    (sil_draw_x + 60, sil_world_y + 60)
                ]
                pygame.draw.polygon(sil_surf, (255, 0, 0, 128), points)
            elif selected_type == 'spawn':
                draw_text(sil_surf, "SPAWN", (0, 255, 255, 128), (sil_draw_x + 2, sil_world_y + 15))
            elif selected_type == 'end':
                draw_text(sil_surf, "END", (255, 255, 0, 128), (sil_draw_x + 10, sil_world_y + 15))
            elif selected_type == 'ramp':
                points = [(sil_draw_x, sil_world_y + 60), (sil_draw_x + 60, sil_world_y + 60), (sil_draw_x + 60, sil_world_y)]
                pygame.draw.polygon(sil_surf, (0, 150, 0, 128), points)
            WIN.blit(sil_surf, (0, 0))

            menu_data = [
                ('blocks', build_cat_blocks, [
                    ('block', 'Block'), ('platform', 'Platform'), ('floor', 'Floor'), 
                    ('ramp', 'Ramp'), ('tall_platform', 'Tall')
                ]),
                ('enemy', build_cat_enemy, [
                    ('spike', 'Spike')
                ]),
                ('miscellaneous', build_cat_misc, [
                    ('spawn', 'Start'), ('end', 'End')
                ])
            ]

            menu_x = 10
            current_y = 70
            key_labels = {
                'block': 'B', 'platform': 'P', 'tall_platform': 'H',
                'floor': 'F', 'spike': 'S', 'spawn': 'T', 'end': 'E', 'ramp': 'R'
            }

            for cat_id, cat_btn, items in menu_data:
                cat_btn.rect.x = menu_x
                cat_btn.rect.y = current_y
                cat_btn.draw(WIN)
                current_y += 50
                
                if current_build_category == cat_id:
                    for t, label in items:
                        text_color = (255, 255, 0) if selected_type == t else (255, 255, 255)
                        draw_text(WIN, f"{key_labels[t]} - {label}", text_color, (menu_x, current_y))
                        icon_x = menu_x + 150
                        icon_y = current_y + 5
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
                        elif t == 'end':
                            draw_text(WIN, "E", (255, 255, 0), (icon_x, icon_y))
                        elif t == 'ramp':
                            pygame.draw.polygon(WIN, (0, 150, 0), [(icon_x, icon_y + 30), (icon_x + 30, icon_y + 30), (icon_x + 30, icon_y)])
                        current_y += 55

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
