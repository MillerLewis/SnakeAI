import pygame

import math

sign = lambda x: 1 if x > 0 else -1 if x < 0 else 0


class Snake:
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)

    def __init__(self, pos, snake_dims):
        self.snake_dims = snake_dims
        self.pos = pos
        self.heading = (1, 0)

        self.alive = True

        self.tail_pieces = [pos]

        self.colour = (255, 255, 255)

    def __len__(self):
        return len(self.tail_pieces)

    def draw(self, screen):
        for tail_piece in self.tail_pieces:
            pygame.draw.rect(screen, self.colour, pygame.Rect(*tail_piece, *self.snake_dims))

    def move(self, screen_dims):
        if self.alive:
            self.pos = (self.pos[0] + self.heading[0] * self.snake_dims[0],
                        self.pos[1] + self.heading[1] * self.snake_dims[1])

            if self.will_die(screen_dims):
                self.die()
                return

            self.tail_pieces.pop()
            last_tail_piece = self.pos
            self.tail_pieces.insert(0, last_tail_piece)

    def will_die(self, screen_dims):
        if self.pos in self.tail_pieces[1:]:
            return True
        if self.pos[0] < 0 or self.pos[0] > screen_dims[0] - self.snake_dims[0] \
                or self.pos[1] < 0 or self.pos[1] > screen_dims[1] - self.snake_dims[1]:
            return True
        else:
            return False

    def die(self):
        self.alive = False
        self.colour = (128, 128, 128)

    def grow(self):
        self.tail_pieces.append((-100, -100))

    def change_heading(self, direction):
        if direction == Snake.RIGHT and self.heading != Snake.LEFT:
            self.heading = direction
        elif direction == Snake.LEFT and self.heading != Snake.RIGHT:
            self.heading = direction
        elif direction == Snake.UP and self.heading != Snake.DOWN:
            self.heading = direction
        elif direction == Snake.DOWN and self.heading != Snake.UP:
            self.heading = direction

    def food_direction(self, food):
        return [food.pos[0] - self.pos[0], food.pos[1] - self.pos[1]]

    def is_food_ahead(self, food):
        direction_to_food = self.food_direction(food)
        direction_equal_to_heading = [sign(heading_dir) == sign(direction_dir) for
                                      heading_dir, direction_dir in zip(self.heading, direction_to_food)]

        return any(direction_equal_to_heading)

    def is_food_left(self, food):
        direction_to_food = self.food_direction(food)

        normalised_direction = list(map(sign, direction_to_food))

        if self.heading == Snake.LEFT:
            return normalised_direction[1] == 1
        elif self.heading == Snake.RIGHT:
            return normalised_direction[1] == -1
        elif self.heading == Snake.UP:
            return normalised_direction[0] == -1
        elif self.heading == Snake.DOWN:
            return normalised_direction[0] == 1

    def is_food_right(self, food):
        direction_to_food = self.food_direction(food)

        normalised_direction = list(map(sign, direction_to_food))

        if self.heading == Snake.LEFT:
            return normalised_direction[1] == 1
        elif self.heading == Snake.RIGHT:
            return normalised_direction[1] == -1
        elif self.heading == Snake.UP:
            return normalised_direction[0] == -1
        elif self.heading == Snake.DOWN:
            return normalised_direction[0] == 1

    def will_hit_self(self):
        for tail_piece in self.tail_pieces[1:]:
            if self.will_hit_tail_piece(tail_piece):
                return True
        return False

    def will_hit_tail_piece(self, tail_piece):
        normalised_direction_to_tail_piece = (sign(tail_piece[0] - self.pos[0]), sign(tail_piece[1] - self.pos[1]))

        if self.heading == Snake.RIGHT:
            return normalised_direction_to_tail_piece == (1, 0)
        elif self.heading == Snake.LEFT:
            return normalised_direction_to_tail_piece == (-1, 0)
        elif self.heading == Snake.UP:
            return normalised_direction_to_tail_piece == (0, -1)
        elif self.heading == Snake.DOWN:
            return normalised_direction_to_tail_piece == (0, 1)
        else:
            return False

    def dist_to_tail_piece(self, tail_piece):
        normalised_direction_to_tail_piece = (sign(tail_piece[0] - self.pos[0]), sign(tail_piece[1] - self.pos[1]))

        if self.heading == Snake.RIGHT and normalised_direction_to_tail_piece == (1, 0):
            return abs(tail_piece[0] - self.pos[0])
        elif self.heading == Snake.LEFT and normalised_direction_to_tail_piece == (-1, 0):
            return abs(tail_piece[0] - self.pos[0])
        elif self.heading == Snake.UP and normalised_direction_to_tail_piece == (0, -1):
            return abs(tail_piece[1] - self.pos[1])
        elif self.heading == Snake.DOWN and normalised_direction_to_tail_piece == (0, 1):
            return abs(tail_piece[1] - self.pos[1])
        else:
            return math.inf

    def distance_to_death(self, screen_dims):
        dist_to_death = None
        if self.heading == Snake.RIGHT:
            dist_to_death = screen_dims[0] - self.pos[0]
        elif self.heading == Snake.LEFT:
            dist_to_death = self.pos[0]
        elif self.heading == Snake.UP:
            dist_to_death = self.pos[1]
        elif self.heading == Snake.DOWN:
            dist_to_death = screen_dims[1] - self.pos[1]

        for tail_piece in self.tail_pieces[1:]:
            dist_to_death = min(dist_to_death, self.dist_to_tail_piece(tail_piece))

        return dist_to_death



if __name__ == "__main__":
    SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    test_snake = Snake((0, 0), (10, 10))
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        screen.fill((0, 0, 0))
        test_snake.draw(screen)

        pygame.display.flip()
