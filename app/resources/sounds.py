import pygame
import os
from app.resources.directories import SOUND_DIR

class SoundManager:

    class __SoundManager:
        def __init__(self, settings):
            self.sounds = {}

            sound_files = os.listdir(SOUND_DIR)

            if settings == None:
                self.settings = {
                    "sound" :
                    {
                        "sound_volume":0.8,
                        "sound_enabled" : True
                    }
                }
            else:
                self.settings = settings

            self.volume  = self.settings['sound']['sound_volume']
            self.enabled = self.settings['sound']['sound_enabled']

            for sound_name in sound_files:
                self.sounds[os.path.splitext(sound_name)[0]] = pygame.mixer.Sound(os.path.join(SOUND_DIR, sound_name))
                self.sounds[os.path.splitext(sound_name)[0]].set_volume(self.volume)

            self.sound_effects = {
                'menu_move'  : 'menu_move',
                'menu_click' : 'menu_click',
                'menu_scroll': 'menu_scroll'
            }

        def play_sound(self, sound_name):
            if not self.enabled:
                return

            if sound_name not in self.sounds:
                print("Failed to load sound \"{}\"".format(sound_name))
                return

            self.sounds[sound_name].play()

        def set_volume(self, volume):
            self.volume = volume
            for sound in self.sounds:
                self.sounds[sound].set_volume(volume)

        def set_enabled(self, enabled):
            self.enabled = enabled

        def handle_settings_update(self, event):
            if self.volume != self.settings['sound']['sound_volume']:
                self.set_volume(self.settings['sound']['sound_volume'])

            if self.enabled != self.settings['sound']['sound_enabled']:
                self.enabled = self.settings['sound']['sound_enabled']

        def handle_sound_effect(self, event):
            self.play_sound(self.sound_effects[event.message])

        def still_playing(self):
            return pygame.mixer.get_busy()

    instance = None

    def __init__(self, settings = None):
        if SoundManager.instance == None:
            SoundManager.instance = SoundManager.__SoundManager(settings)

    def __getattr__(self, name):
        return getattr(self.instance, name)
