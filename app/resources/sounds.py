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
                'menu_move'       : 'menu_move',
                'menu_click'      : 'menu_click',
                'menu_scroll'     : 'menu_scroll',
                'revenge_of_tesla': 'revenge_of_tesla',
                'jolt'            : 'jolt',
                'lightning_bolt'  : 'lightning_bolt',
                'lightning_blade' : 'lightning_blade',
                'thunder_storm'   : 'thunder_storm',
                'voltage_slam'    : 'voltage_slam',
                'charge'          : 'charge',
                'shattering_bolt' : 'shattering_bolt',
                'stalactite_drop' : 'stalactite_drop',
                'bassault'        : 'bassault',
                'rock_smash'      : 'rock_smash',
                'earthquake'      : 'earthquake',
                'fracture'        : 'fracture',
                'landslide'       : 'landslide',
                'granite_armour'  : 'granite_armour',
                'faint'           : 'faint',
                'quicksand'       : 'quicksand',
                'blizzard'        : 'blizzard',
                'frost_storm'     : 'frost_storm',
                'glacier'         : 'glacier',
                'ice_cage'        : 'ice_cage',
                'frostbite'       : 'frost_bite',
                'chill_strike'    : 'chill_strike',
                'ice_breaker'     : 'ice_breaker',
                'ice_wall'        : 'ice_wall',
                'drop_mixtape'    : 'drop_mixtape',
                'blazing_salvo'   : 'blazing_salvo',
                'fireball'        : 'fireball',
                'lava_storm'      : 'lava_storm',
                'flame_wave'      : 'flame_wave',
                'backdraft'       : 'backdraft',
                'solar_blaze'     : 'solar_blaze',
                'unmake'          : 'unmake',
                'power_swirl'     : 'power_swirl',
                'monsoon'         : 'monsoon',
                'healing_wave'    : 'healing_wave',
                'absorb'          : 'absorb',
                'nope'            : 'nope',
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
            self.set_volume(self.settings['sound']['sound_volume'])

            if self.enabled != self.settings['sound']['sound_enabled']:
                self.enabled = self.settings['sound']['sound_enabled']

        def handle_sound_effect(self, event):
            if event.message in self.sound_effects:
                self.play_sound(self.sound_effects[event.message])

        def still_playing(self):
            return pygame.mixer.get_busy()

    instance = None

    def __init__(self, settings = None):
        if SoundManager.instance == None:
            SoundManager.instance = SoundManager.__SoundManager(settings)

    def __getattr__(self, name):
        return getattr(self.instance, name)
