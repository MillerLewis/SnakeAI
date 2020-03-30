import pygame


class TickUpdater:
    def __init__(self, tick_rate):
        self.clock = pygame.time.Clock()
        self.tick_rate = tick_rate
        self.time_elapsed_since_tick = 0

        self.ticks_since_start = 0

    def update(self):
        dt = self.clock.tick()
        self.time_elapsed_since_tick += dt

        if self.time_elapsed_since_tick >= self.tick_rate:
            self.time_elapsed_since_tick = 0
            return True
