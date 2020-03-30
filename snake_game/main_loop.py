import math

import pygame

from snake_game import food
from snake_game import snake
from snake_game.game_state import Game

from snake_game.helper_functions import random_square

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

# Update once every x milliseconds
clock = pygame.time.Clock()
time_elapsed_since_last_tick = 0

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
done = False

food_pieces = [food.Food(random_square(screen.get_width(),
                                       screen.get_height(),
                                       10, 10), (10, 10)) for _ in range(1)]
snake_test = snake.Snake((0, 0), (10, 10))

game_test = Game((50, 50), (10, 10), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (10, 10),
                     (SCREEN_WIDTH, SCREEN_HEIGHT), 100)

for _ in range(40):
    snake_test.tail_pieces.append((-100, -100))

new_direction = None

if __name__ == "__main__":
    while not done and game_test.snake.alive:
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

        if game_test.update([SCREEN_WIDTH, SCREEN_HEIGHT]):
            game_test.snake.change_heading(new_direction)

        if game_test.snake.alive:
            game_test.update(screen)
            game_test.draw(screen)

        pygame.display.flip()

