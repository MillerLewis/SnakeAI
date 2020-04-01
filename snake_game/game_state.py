from snake_game.snake import Snake
from snake_game.food import Food

from snake_game.helper_functions import random_square

import pygame

from snake_game.tick_updater import TickUpdater


class Game(TickUpdater):
    def __init__(self, snake_pos, snake_dims, food_pos, food_dims, screen_dims, tick_rate, life_time=100):
        super().__init__(tick_rate)

        self.snake = Snake(snake_pos, snake_dims)
        self.food = Food(food_pos, food_dims)
        self.dims = screen_dims

        self.life_time = life_time
        self.ticks_since_eaten = 0

    @property
    def score(self):
        return len(self.snake) ** 2 * self.ticks_since_start

    def draw(self, screen):
        self.snake.draw(screen)
        self.food.draw(screen)

    def eat(self, screen_dims):
        self.ticks_since_eaten = 0
        self.snake.grow()
        while self.food.pos in self.snake.tail_pieces:
            self.food.pos = random_square(screen_dims[0] - self.food.food_dims[0],
                                          screen_dims[1] - self.food.food_dims[1],
                                          self.food.food_dims[0],
                                          self.food.food_dims[1])

    def look_ahead_to_food(self, direction):
        looking_at = [self.snake.pos[0], self.snake.pos[1]]
        while looking_at[0] <= self.dims[0] \
                and looking_at[0] >= 0 \
                and looking_at[1] <= self.dims[1] \
                and looking_at[1] >= 0:
            looking_at = [looking_at[0] + self.food.food_dims[0] * direction[0],
                          looking_at[1] + self.food.food_dims[1] * direction[1]]
            if looking_at == self.food.pos:
                break
        return looking_at

    def look_ahead_to_food_inverse(self, direction):
        look_ahead = self.look_ahead_to_food(direction)
        look_ahead = [val if val != 0 else 1 for val in look_ahead]
        return [1 / look_ahead[0], 1 / look_ahead[1]]

    def food_direction(self):
        return self.snake.food_direction(self.food)

    def update(self, screen_dims):
        if self.snake.alive:
            if self.ticks_since_eaten > self.life_time:
                self.snake.die()
            if super().update():
                self.snake.move(screen_dims)
                self.ticks_since_eaten += 1
                if self.snake.pos == self.food.pos:
                    self.eat(screen_dims)
                return True

    def reset(self):
        self.snake.pos = (self.dims[0] // 2, self.dims[1] // 2)
        self.food.pos = random_square(self.dims[0], self.dims[1], *self.food.food_dims)
        self.snake.alive = True
        self.ticks_since_eaten = 0
        self.snake.colour = (255, 255, 255)
        self.snake.tail_pieces = [self.snake.pos]

    def deep_copy(self):
        return Game(
            self.snake.pos, self.snake.snake_dims, self.food.pos, self.food.food_dims, self.dims, self.tick_rate
        )

    def fresh_deep_copy(self):
        game = self.deep_copy()
        game.reset()
        return game


if __name__ == "__main__":
    SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    test_game = Game((50, 50), (10, 10), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), (10, 10),
                     (SCREEN_WIDTH, SCREEN_HEIGHT), 100)
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill((0, 0, 0))
        test_game.update([SCREEN_WIDTH, SCREEN_HEIGHT])
        test_game.draw(screen)

        pygame.display.flip()
