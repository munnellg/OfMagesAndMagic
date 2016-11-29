import pygame
import json
import sys
from app.resources import directories
from app.view import main_menu, in_game, announce_winners
from app.models.magic import SpellBook
from app.models.battle import Battle
from app.resources.music import MusicManager
from app.resources.sounds import SoundManager
from app.resources.images import ImageManager
from app.resources.event_handler import EventHandler, STATE_CHANGED, MUSIC_STOPPED
from app.models import team

class Walton:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()

        # Load settings from JSON file
        json_data=open(directories.SETTINGS_PATH).read()
        self.settings = json.loads(json_data)
        self.resolution_key = self.settings['screen']['resolution']
        resolution = self.settings['valid_resolutions'][self.resolution_key]
        self.resolution = (resolution['width'], resolution['height'])
        self.title = self.settings['title']

        self.winners = []

        self.event_handler = EventHandler()
        self.music_manager = MusicManager(self.settings)
        self.sound_manager = SoundManager(self.settings)
        self.image_manager = ImageManager()

        self.music_manager.set_music_stopped_event(MUSIC_STOPPED)

        self.event_handler.register_quit_listener(self.quit)
        self.event_handler.register_set_game_state_listener(self.update_state)
        self.event_handler.register_music_stopped_listener(self.music_manager.handle_song_stopped)
        self.event_handler.register_state_change_listener(self.music_manager.handle_state_change)
        self.event_handler.register_sound_effect_listener(self.sound_manager.handle_sound_effect)

        # self.event_handler.register_settings_update_listener(self.update_settings)
        self.event_handler.register_settings_update_listener(self.music_manager.handle_settings_update)
        self.event_handler.register_settings_update_listener(self.sound_manager.handle_settings_update)

        self.quit = False
        self.states = {
            'main_menu' : main_menu.MainMenu,
            'in_game'   : in_game.Game,
            'announce_winners' : announce_winners.AnnounceWinners
        }
        self.state_code = None
        SpellBook.load_spell_book(directories.MAGIC_PATH)
        self.teams = team.load_teams(directories.TEAM_PATH)

    def __game_loop(self):
        clock = pygame.time.Clock()
        time  = pygame.time.get_ticks()
        pygame.mouse.set_visible(False)

        # self.set_state('announce_winners', 'default')
        self.set_state('main_menu', 'intro')
        # self.set_state('in_game', 'battle_view')

        while not self.quit:
            # Regulate framerate
            clock.tick(60)

            for event in pygame.event.get():
                self.event_handler.handle_event(event)

            delta_t = pygame.time.get_ticks() - time
            time = pygame.time.get_ticks()
            self.state.update(delta_t)
            render = self.state.render()
            self.screen.blit(render, (0,0))
            pygame.display.flip()

    def __initialize_display(self):
        self.resolution_key = self.settings['screen']['resolution']
        resolution = self.settings['valid_resolutions'][self.resolution_key]
        self.resolution = (resolution['width'], resolution['height'])

        if self.settings['screen']['fullscreen']:
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF)
        pygame.display.set_caption(self.settings['title'])

    def set_state(self, state_code, state_seed=None):
        self.state_code = state_code
        if state_seed != None:
            self.state = self.states[self.state_code](self, state_seed)
        else:
            self.state = self.states[self.state_code](self)
        event = pygame.event.Event(STATE_CHANGED, state=state_code)
        pygame.event.post(event)

    def run(self):
        self.__initialize_display()
        self.__game_loop()

    def update_settings(self, event):
        if self.settings['screen']['resolution'] != self.resolution_key:
            self.__initialize_display()
            self.state.update_display()

    def start_game(self, event):
        self.set_state('in_game')

    def update_state(self, event):
        self.set_state(event.state, event.seed)

    def quit(self, event):
        with open(directories.SETTINGS_PATH, "w") as f:
            json.dump(
                self.settings,
                f,
                indent = 4,
                ensure_ascii=False
            )

        # Wait for any sound effects to stop playing
        while self.sound_manager.still_playing():
            continue

        self.quit = True
