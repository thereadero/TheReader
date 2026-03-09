import pygame
# velikost okna
width, height = 500, 500
win = pygame.display.set_mode((width, height))
# startovací pozice hada
class Snake:
    def __init__(self):
        self.x = 250
        self.y = 250
        self.width = 10
        self.height = 10
        self.vel = 10

    def draw(self, win):
        pygame.draw.rect(win, (0,255,0), (self.x, self.y, self.width, self.height))
def main():
    run = True
    snake = Snake()
    while run:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
# ovládání        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            snake.x -= snake.vel
        if keys[pygame.K_RIGHT]:
            snake.x += snake.vel
        if keys[pygame.K_UP]:
            snake.y -= snake.vel
        if keys[pygame.K_DOWN]:
            snake.y += snake.vel
        win.fill((0,0,0))
        snake.draw(win)
        pygame.display.update()
    pygame.quit()
if __name__ == "__main__":    main()
