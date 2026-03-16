import json
import pygame
import os

pygame.init()
# window setting
WIDTH, HEIGHT = 800, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("Arial", 32)



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


def main():
    pygame.init()
    clock = pygame.time.Clock()


    run = True
    while run:
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        pygame.display.update()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
