import pygame

from snake_game import food
from snake_game import snake

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

# Update once every x milliseconds
TICK_RATE = 1000
clock = pygame.time.Clock()
time_elapsed_since_last_tick = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
done = False

food_test = food.Food((screen.get_width() / 2, screen.get_height() / 2), screen)
snake_test = snake.Snake((0, 0), screen)

snake_test.tail_pieces.append((100,100))

new_direction = None

while not done:
    dt = clock.tick()
    time_elapsed_since_last_tick += dt

    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        new_direction = snake.Snake.UP
    if keys[pygame.K_DOWN]:
        new_direction = snake.Snake.DOWN
    if keys[pygame.K_RIGHT]:
        new_direction = snake.Snake.RIGHT
    if keys[pygame.K_LEFT]:
        new_direction = snake.Snake.LEFT

    if time_elapsed_since_last_tick >= TICK_RATE:
        snake_test.change_heading(new_direction)

        food_test.draw()
        snake_test.move()
        snake_test.draw()

        pygame.display.flip()

        time_elapsed_since_last_tick = 0

    # print(snake_test.pos)
