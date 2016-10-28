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

        def get_image(self, image_name):
            return self.images[image_name]

    instance = None

    def __init__(self):
        if ImageManager.instance == None:
            ImageManager.instance = ImageManager.__ImageManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)
