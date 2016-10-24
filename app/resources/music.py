import pygame
import os
from directories import MUSIC_DIR

class MusicManager:

    class __MusicManager:
        def __init__(self):
            self.music = {}
            self.now_playing = ""
            pygame.mixer.init()
            music_files = os.listdir(MUSIC_DIR)
            for music_name in music_files:
                self.music[os.path.splitext(music_name)[0]] = music_name

            self.soundtrack = {
                "main_menu" : "long_road"
            }

        def play_song(self, song_name, volume = 0.3):
            pygame.mixer.music.set_volume(volume)

            if song_name not in self.music:
                print("Failed to load song \"{}\"".format(song_name))
                pygame.mixer.music.stop()
                return

            if self.now_playing != song_name:
                pygame.mixer.music.load(os.path.join(MUSIC_DIR, self.music[song_name]))
                pygame.mixer.music.play(-1)
                self.now_playing = song_name

        def get_music_volume(self):
            return pygame.mixer.music.get_volume()

        def set_music_volume(self, volume):
            pygame.mixer.music.set_volume(volume)

        def handle_state_change(self, event):
            self.play_song(self.soundtrack[event.state])

    instance = None

    def __init__(self):
        if MusicManager.instance == None:
            MusicManager.instance = MusicManager.__MusicManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)
