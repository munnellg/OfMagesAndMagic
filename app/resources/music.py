import pygame
import os
from app.resources.directories import MUSIC_DIR

class MusicManager:

    class __MusicManager:
        def __init__(self, settings):
            self.music = {}
            self.now_playing = ""

            if settings == None:
                self.settings = {
                    "sound" :
                    {
                        "sound_volume":0.3,
                        "sound_enabled" : True
                    }
                }
            else:
                self.settings = settings

            self.volume  = self.settings['sound']['music_volume']
            self.enabled = self.settings['sound']['music_enabled']

            pygame.mixer.init()
            music_files = os.listdir(MUSIC_DIR)
            for music_name in music_files:
                self.music[os.path.splitext(music_name)[0]] = music_name

            self.soundtrack = {
                "main_menu" : "long_road",
                "in_game" : "preliator"
            }

        def play_song(self, song_name, volume = -1):
            if not self.enabled:
                return

            if volume < 0:
                pygame.mixer.music.set_volume(self.volume)
            else:
                pygame.mixer.music.set_volume(volume)

            if song_name not in self.music:
                print("Failed to load song \"{}\"".format(song_name))
                pygame.mixer.music.stop()
                return

            if self.now_playing != song_name or not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(os.path.join(MUSIC_DIR, self.music[song_name]))
                pygame.mixer.music.play(-1)
                self.now_playing = song_name

        def get_music_volume(self):
            return pygame.mixer.music.get_volume()

        def set_music_volume(self, volume):
            self.volume = volume
            pygame.mixer.music.set_volume(volume)

        def set_enabled(self, enabled):
            self.enabled = enabled
            if not self.enabled:
                pygame.mixer.music.stop()
            else:
                self.play_song(self.now_playing)

        def handle_settings_update(self, event):
            if self.volume != self.settings['sound']['music_volume']:
                self.set_music_volume(self.settings['sound']['music_volume'])

            if self.enabled != self.settings['sound']['music_enabled']:
                self.set_enabled(self.settings['sound']['music_enabled'])

        def handle_state_change(self, event):
            if event.state in self.soundtrack:
                self.play_song(self.soundtrack[event.state])

    instance = None

    def __init__(self, settings = None):
        if MusicManager.instance == None:
            MusicManager.instance = MusicManager.__MusicManager(settings)

    def __getattr__(self, name):
        return getattr(self.instance, name)
