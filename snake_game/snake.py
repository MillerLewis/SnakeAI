import pygame


class Snake:
    # speed = 0.1
    SNAKE_DIMS = (50, 50)

    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)

    def __init__(self, pos, screen):
        self.pos = pos
        self.screen = screen
        self.heading = (1, 0)

        self.tail_pieces = []

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(*self.pos, *self.SNAKE_DIMS))

        for tail_piece in self.tail_pieces:
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(*tail_piece, *self.SNAKE_DIMS))

    def move(self):
        self.pos = (self.pos[0] + self.heading[0] * Snake.SNAKE_DIMS[0], self.pos[1] + self.heading[1] * Snake.SNAKE_DIMS[1])


    def eat(self, food):
        self.tail_pieces.append(self.pos)
        self.pos = food.pos

    def change_heading(self, direction):
        if direction == Snake.RIGHT and self.heading != Snake.LEFT:
            self.heading = direction
        elif direction == Snake.LEFT and self.heading != Snake.RIGHT:
            self.heading = direction
        elif direction == Snake.UP and self.heading != Snake.DOWN:
            self.heading = direction
        elif direction == Snake.DOWN and self.heading != Snake.UP:
            self.heading = direction
