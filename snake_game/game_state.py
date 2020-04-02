from snake_game.snake import Snake
from snake_game.food import Food

from snake_game.helper_functions import random_square

import pygame

from snake_game.tick_updater import TickUpdater

sign = lambda x: 1 if x > 0 else -1 if x < 0 else 0

class Game(TickUpdater):
    def __init__(self, snake_pos, snake_dims, food_pos, food_dims, screen_dims, tick_rate, life_time=200):
        super().__init__(tick_rate)

        self.snake = Snake(snake_pos, snake_dims)
        self.food = Food(food_pos, food_dims)
        self.dims = screen_dims

        self.life_time = life_time
        self.ticks_since_eaten = 0

    @property
    def score(self):
        return len(self.snake) * self.ticks_since_start

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
        return [self.food.pos[0] - self.snake.pos[0], self.food.pos[1] - self.snake.pos[1]]

    def food_direction_normalised(self):
        dir_to_food = self.food_direction()
        magnitude = sum([val ** 2 for val in dir_to_food]) ** 0.5
        return [val / magnitude if magnitude != 0 else 0 for val in dir_to_food]

    def food_direction_inverse(self):
        return [1 / val if val != 0 else val for val in self.food_direction()]

    def is_food_ahead(self):
        direction_to_food = self.food_direction()
        direction_equal_to_heading = [sign(heading_dir) == sign(direction_dir) for
                                      heading_dir, direction_dir in zip(self.snake.heading, direction_to_food)]

        return any(direction_equal_to_heading)

    def is_food_left(self):
        return int(self.snake.pos[0] >= self.food.pos[0])

    def is_food_right(self):
        return int(self.snake.pos[0] <= self.food.pos[0])

    def is_food_up(self):
        return int(self.snake.pos[1] <= self.food.pos[1])

    def is_food_down(self):
        return int(self.snake.pos[1] >= self.food.pos[1])

    # def is_food_left(self):
    #     direction_to_food = self.food_direction()
    #
    #     normalised_direction = list(map(sign, direction_to_food))
    #
    #     if self.snake.heading == Snake.LEFT:
    #         return normalised_direction[1] == 1
    #     elif self.snake.heading == Snake.RIGHT:
    #         return normalised_direction[1] == -1
    #     elif self.snake.heading == Snake.UP:
    #         return normalised_direction[0] == -1
    #     elif self.snake.heading == Snake.DOWN:
    #         return normalised_direction[0] == 1

    # def is_food_right(self):
    #     direction_to_food = self.food_direction()
    #
    #     normalised_direction = list(map(sign, direction_to_food))
    #
    #     if self.snake.heading == Snake.LEFT:
    #         return normalised_direction[1] == 1
    #     elif self.snake.heading == Snake.RIGHT:
    #         return normalised_direction[1] == -1
    #     elif self.snake.heading == Snake.UP:
    #         return normalised_direction[0] == -1
    #     elif self.snake.heading == Snake.DOWN:
    #         return normalised_direction[0] == 1



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
