import pygame
import json
import sys
from app.resources import directories
from app.view import main_menu
from app.models.magic import SpellBook
from app.models.league import build_league
from app.models.battle import Battle
from app.resources.music import MusicManager
from app.resources.sounds import SoundManager
from app.resources.event_handler import EventHandler, STATE_CHANGED

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

        self.event_handler = EventHandler()
        self.music_manager = MusicManager(self.settings)
        self.sound_manager = SoundManager(self.settings)
        self.event_handler.register_quit_listener(self.quit)
        self.event_handler.register_state_change_listener(self.music_manager.handle_state_change)
        self.event_handler.register_sound_effect_listener(self.sound_manager.handle_sound_effect)

        # self.event_handler.register_settings_update_listener(self.update_settings)
        self.event_handler.register_settings_update_listener(self.music_manager.handle_settings_update)
        self.event_handler.register_settings_update_listener(self.sound_manager.handle_settings_update)

        self.quit = False
        self.states = {
            'main_menu' : main_menu.MainMenu
        }

        SpellBook.load_spell_book(directories.MAGIC_PATH)

        # self.league = build_league()
        # self.battle = Battle(self.league[0], self.league[1])

    def __game_loop(self):
        clock = pygame.time.Clock()
        time  = pygame.time.get_ticks()
        pygame.mouse.set_visible(False)

        self.set_state('main_menu')

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
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption(self.settings['title'])

    def set_state(self, state_code):
        self.state_code = state_code
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

    def quit(self, event):
        with open(directories.SETTINGS_PATH, "w") as f:
            json.dump(
                self.settings,
                f,
                indent = 4,
                ensure_ascii=False
            )

        while self.sound_manager.still_playing():
            continue

        self.quit = True
