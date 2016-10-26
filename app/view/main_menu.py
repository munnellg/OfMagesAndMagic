import pygame
from collections import defaultdict
from app.resources import colours
from app.resources import text_renderer
from app.view import animations
from app.view.menu import Menu, MenuItem, SettingsMenu, ButtonMenuItem

class TitleBanner:
    def __init__(self, text):
        words = text.split()
        word_surfaces = []
        max_height = 0
        max_width  = 0

        for word in words:
            ws = text_renderer.render_title(word, colours.COLOUR_WHITE)
            if ws.get_height() > max_height:
                max_height = ws.get_height()
            if ws.get_width() > max_width:
                max_width = ws.get_width()
            word_surfaces.append(ws)

        self.surface = pygame.Surface((max_width, max_height*len(words)))

        for i in range(len(word_surfaces)):
            y = i*max_height
            x = (max_width - word_surfaces[i].get_width())//2
            self.surface.blit(word_surfaces[i], (x,y))

    def render(self):
        return self.surface

class State:
    def render(self):
        return
    def update(self, delta_t):
        return
    def handle_event(self, event):
        return
    def exit_state(self):
        return

class StateSettings(State):
    def __init__(self, main_menu):
        self.parent     = main_menu.parent
        self.main_menu  = main_menu
        self.settings   = self.parent.settings
        self.resolution = self.main_menu.resolution

        self.parent.event_handler.register_key_listener(self.handle_keypress)
        self.title = text_renderer.render_title("Options", colours.COLOUR_WHITE)

        self.title_position = (
            (self.resolution[0] - self.title.get_width())// 2,
            15
        )

        self.directions = {
            pygame.K_UP     : [-1,  0],
            pygame.K_DOWN   : [ 1,  0],
            pygame.K_RIGHT  : [ 0,  1],
            pygame.K_LEFT   : [ 0, -1],
            pygame.K_SPACE  : [ 0,  2],
            pygame.K_RETURN : [ 0,  2]
        }
        self.animation = None
        self.menu = SettingsMenu(self.settings)

    def render(self):
        surface = pygame.Surface(self.resolution)
        surface.blit(self.title, self.title_position)
        m_surface = self.menu.render()
        surface.blit(m_surface, (
                (self.resolution[0]-m_surface.get_width())//2,
                (self.resolution[1]-m_surface.get_height())//2
            )
        )
        return surface

    def handle_keypress(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.directions:
                magnitude = self.directions[event.key]
                if magnitude[0] != 0:
                    self.animation = animations.Timeout(
                        self.menu.move_selection,
                        [magnitude[0]]
                    )
                elif magnitude[1] != 0:
                    self.animation = animations.Timeout(
                        self.menu.click_selected,
                        [magnitude[1]]
                    )
        else:
            if event.key in self.directions:
                self.animation = None

    def update(self, delta_t):
        if self.animation != None:
            self.animation.animate(delta_t)

    def exit_state(self):
        self.parent.event_handler.unregister_key_listener(self.handle_keypress)

class StateAnimatedIntro(State):
    def __init__(self, main_menu):
        self.parent     = main_menu.parent
        self.main_menu  = main_menu
        self.resolution = main_menu.resolution
        self.title_banner = main_menu.title_banner
        self.alpha = 0

        self.animation  = 0

        self.animations = [
            animations.FadeIn(self),
        ]

        self.parent.event_handler.register_key_listener(self.handle_keypress)

    def set_alpha(self, alpha):
        self.alpha = alpha

    def render(self):
        surface = pygame.Surface(self.resolution)
        surface.blit(self.title_banner.render(), self.main_menu.banner_position)
        surface.blit(self.main_menu.menu.get_menu_surface(), self.main_menu.menu_position)

        mask = pygame.Surface(self.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.alpha))
        surface.blit(mask, (0,0))

        return surface

    def update(self, delta_t):
        if self.animations[self.animation].finished():
            self.animation += 1

        if self.animation == len(self.animations):
            self.main_menu.set_state('default')
        else:
            self.animations[self.animation].animate(delta_t)

    def skip(self):
        for animation in range(self.animation, len(self.animations)):
            self.animations[animation].skip()

    def handle_keypress(self, event):
        if event.type == pygame.KEYDOWN:
            self.main_menu.set_state('default')

    def exit_state(self):
        self.skip()
        self.parent.event_handler.unregister_key_listener(self.handle_keypress)

class StateDefault(State):
    def __init__(self, main_menu):
        self.parent     = main_menu.parent
        self.main_menu  = main_menu
        self.resolution = main_menu.resolution
        self.title_banner = main_menu.title_banner
        self.parent.event_handler.register_key_listener(self.handle_keypress)
        self.animation = None
        self.directions = {
            pygame.K_UP   : -1,
            pygame.K_DOWN : 1
        }

    def render(self):
        surface = pygame.Surface(self.resolution)
        surface.blit(self.title_banner.render(), self.main_menu.banner_position)
        surface.blit(self.main_menu.menu.render(), self.main_menu.menu_position)
        return surface

    def handle_keypress(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key in self.directions:
                self.animation = animations.Timeout(
                    self.main_menu.menu.move_selection,
                    [self.directions[event.key]]
                )
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.main_menu.menu.click_selected()
        else:
            if event.key in self.directions:
                self.animation = None

    def update(self, delta_t):
        if self.animation != None:
            self.animation.animate(delta_t)

    def exit_state(self):
        self.parent.event_handler.unregister_key_listener(self.handle_keypress)

class MainMenu:
    def __init__(self, parent):
        self.parent = parent
        self.resolution = parent.resolution
        self.event_handler = parent.event_handler
        self.title_banner = TitleBanner(self.parent.title)
        self.banner_position = (self.resolution[0]//10, self.resolution[1]//10)

        self.menu = Menu([
            ButtonMenuItem("Start", None),
            ButtonMenuItem("View Teams", None),
            ButtonMenuItem("Options", self.show_settings),
            ButtonMenuItem("Exit", self.trigger_exit)]
        )

        self.menu_position = (
            self.resolution[0]-self.resolution[0]//10-self.menu.surface.get_width(),
            self.resolution[1]-self.resolution[1]//5-self.menu.surface.get_height()
        )

        self.states = {
            "intro"    : StateAnimatedIntro,
            "settings" : StateSettings,
            "default"  : StateDefault
        }

        self.state_code = "intro"
        self.state = self.states[self.state_code](self)

    def set_state(self, state):
        self.state.exit_state()
        self.state_code = state
        self.state = self.states[state](self)

    def render(self):
        return self.state.render()

    def update(self, delta_t):
        return self.state.update(delta_t)

    def handle_event(self, event):
        return self.state.handle_event()

    def show_settings(self):
        self.set_state('settings')

    def trigger_exit(self):
        event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(event)
