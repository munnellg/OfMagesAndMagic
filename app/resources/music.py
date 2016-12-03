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

            self.track_no     = 0
            self.cur_playlist = []
            self.default_volume = self.settings['sound']['music_volume']
            self.volume         = self.default_volume
            self.enabled        = self.settings['sound']['music_enabled']

            pygame.mixer.init()
            music_files = os.listdir(MUSIC_DIR)
            for music_name in music_files:
                self.music[os.path.splitext(music_name)[0]] = music_name

            self.soundtrack = {
                "main_menu" : [ "long_road" ],
                # "in_game"   : [ "preliator", "killers", "ff8", "skyrim" ]
            }

        def play_song(self, song_name, volume = -1, loops=1):
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
                pygame.mixer.music.play(loops)
                self.now_playing = song_name

        def load_playlist(self, playlist):
            if playlist in self.soundtrack:
                self.cur_playlist = self.soundtrack[playlist]
            else:
                self.cur_playlist = []
            self.track_no = -1

        def get_music_volume(self):
            return pygame.mixer.music.get_volume()

        def set_music_volume(self, volume):
            self.volume = volume
            pygame.mixer.music.set_volume(volume)

        def set_default_music_volume(self, volume):
            self.default_volume = volume

        def restore_music_volume(self):
            self.set_music_volume(self.default_volume)

        def set_enabled(self, enabled):
            self.enabled = enabled
            if not self.enabled:
                pygame.mixer.music.stop()
            else:
                self.load_next_song()

        def handle_settings_update(self, event):
            self.set_music_volume(self.settings['sound']['music_volume'])
            self.set_default_music_volume(self.settings['sound']['music_volume'])

            if self.enabled != self.settings['sound']['music_enabled']:
                self.set_enabled(self.settings['sound']['music_enabled'])

        def handle_song_stopped(self, event):
            self.load_next_song()

        def handle_state_change(self, event):
            self.set_music_volume(self.default_volume)
            self.load_playlist(event.state)
            self.load_next_song()

        def set_music_stopped_event(self, event):
            pygame.mixer.music.set_endevent(event)

        def load_next_song(self):
            if len(self.cur_playlist) > 0:
                self.track_no += 1
                self.track_no %= len(self.cur_playlist)
                self.play_song(self.cur_playlist[self.track_no])

    instance = None

    def __init__(self, settings = None):
        if MusicManager.instance == None:
            MusicManager.instance = MusicManager.__MusicManager(settings)

    def __getattr__(self, name):
        return getattr(self.instance, name)
