import pygame


class Food:
    FOOD_DIMS = (50, 50)

    def __init__(self, pos, screen):
        self.pos = pos
        self.screen = screen

    def draw(self):
        pygame.draw.rect(self.screen, (128, 0, 0), pygame.Rect(*self.pos, *Food.FOOD_DIMS))

