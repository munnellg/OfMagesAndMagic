import pygame
import os
from app.resources.directories import SOUND_DIR

class SoundManager:

    class __SoundManager:
        def __init__(self):
            self.sounds = {}

            sound_files = os.listdir(SOUND_DIR)

            for sound_name in sound_files:
                self.sounds[os.path.splitext(sound_name)[0]] = pygame.mixer.Sound(os.path.join(SOUND_DIR, sound_name))
                self.sounds[os.path.splitext(sound_name)[0]].set_volume(0.8)

            self.sound_effects = {
                'menu_move'  : 'menu_move',
                'menu_click' : 'menu_click'
            }

        def play_sound(self, sound_name):
            if sound_name not in self.sounds:
                print("Failed to load sound \"{}\"".format(sound_name))
                return

            self.sounds[sound_name].play()

        def handle_sound_effect(self, event):
            self.play_sound(self.sound_effects[event.message])

        def still_playing(self):
            return pygame.mixer.get_busy()

    instance = None

    def __init__(self):
        if SoundManager.instance == None:
            SoundManager.instance = SoundManager.__SoundManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)
