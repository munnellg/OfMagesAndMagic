import pygame

class Timer:
    def __init__(self):
        self.start_time = 0
        self.stop_time = 0
        self.is_paused = True

    def start(self):
        self.reset()
        self.is_paused = False

    def get_elapsed(self):
        if self.is_paused:
            return self.stop_time - self.start_time
        else:
            return pygame.time.get_ticks() - self.start_time

    def pause(self):
        self.stop_time = pygame.time.get_ticks()
        self.is_paused = True

    def unpause(self):
        self.start_time = pygame.time.get_ticks() - (self.stop_time - self.start_time)

    def reset(self):
        self.start_time = pygame.time.get_ticks()
        self.stop_time = self.start_time

    def fast_forward(self, duration):
        self.start_time -= duration

    def rewind(self, duration):
        self.start_time += duration
