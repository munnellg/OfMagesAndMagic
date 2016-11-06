import pygame
import os
from directories import IMAGE_DIR

class ImageManager:

    class __ImageManager:
        def __init__(self):
            self.images = {}

            image_files = os.listdir(IMAGE_DIR)

            for image_name in image_files:
                self.images[os.path.splitext(image_name)[0]] = pygame.image.load(os.path.join(IMAGE_DIR, image_name))

            self.tile_size = 100

        def get_image(self, image_name):
            if image_name not in self.images:
                s = pygame.Surface((self.tile_size,self.tile_size))
                s.fill((0,0,0))
                return s
            return self.images[image_name]

        def get_tile(self, image_name, clip_x, clip_y):
            if image_name not in self.images:
                s = pygame.Surface((self.tile_size,self.tile_size))
                s.fill((0,0,0))
                return s
                
            surface = self.images[image_name]

            rect = pygame.Rect(
                (
                    clip_x*self.tile_size,
                    clip_y*self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
            )
            image = pygame.Surface(rect.size, pygame.SRCALPHA)
            image.fill((0,0,0,0))

            image.blit(surface, (0, 0), rect)
            return image

    instance = None

    def __init__(self):
        if ImageManager.instance == None:
            ImageManager.instance = ImageManager.__ImageManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)
