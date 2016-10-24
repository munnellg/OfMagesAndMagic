import pygame
import json
import sys
from app.resources import directories
from app.view import main_menu
from app.models.magic import SpellBook
from app.models.league import build_league
from app.models.battle import Battle
from app.resources.event_handler import EventHandler

class Walton:
    def __init__(self):

        SpellBook.load_spell_book(directories.MAGIC_PATH)
        self.event_handler = EventHandler()
        self.event_handler.register_quit_listener(self.quit)

        # Load settings from JSON file
        json_data=open(directories.SETTINGS_PATH).read()
        self.settings = json.loads(json_data)
        self.resolution = (self.settings['screen']['width'], self.settings['screen']['height'])
        self.title = self.settings['title']
        self.quit = False
        self.states = {
            'menu' : main_menu.MainMenu
        }

        # self.league = build_league()
        # self.battle = Battle(self.league[0], self.league[1])

    def __game_loop(self):
        clock = pygame.time.Clock()
        time  = pygame.time.get_ticks()
        pygame.mouse.set_visible(False)
        
        self.set_state('menu')

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
        if self.settings['screen']['fullscreen']:
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption(self.settings['title'])

    def set_state(self, state_code):
        self.state_code = state_code
        self.state = self.states[self.state_code](self)

    def run(self):
        self.__initialize_display()
        self.__game_loop()

    def quit(self, event):
        self.quit = True
