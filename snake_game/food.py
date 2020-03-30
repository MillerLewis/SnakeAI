import pygame


class Food:

    def __init__(self, pos, food_dims):
        self.food_dims = food_dims
        self.pos = pos

    def draw(self, screen):
        pygame.draw.rect(screen, (128, 0, 0), pygame.Rect(*self.pos, *self.food_dims))

