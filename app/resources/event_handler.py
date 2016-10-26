import pygame
from collections import defaultdict

STATE_CHANGED    = pygame.USEREVENT + 1
SOUND_EFFECT     = pygame.USEREVENT + 2
SETTINGS_UPDATED = pygame.USEREVENT + 3

class EventHandler:
    def __init__(self):
        self.callbacks = {
            pygame.KEYDOWN           : self.key_state_change,
            pygame.KEYUP             : self.key_state_change,
            pygame.MOUSEMOTION       : self.mouse_motion,
            pygame.MOUSEBUTTONUP     : self.mouse_button_state_change,
            pygame.MOUSEBUTTONDOWN   : self.mouse_button_state_change,
            pygame.QUIT              : self.quit,
            STATE_CHANGED            : self.state_change,
            SOUND_EFFECT             : self.sound_effect,
            SETTINGS_UPDATED         : self.settings_updated
        }

        self.key_states = defaultdict(int)
        self.mouse_button_states = defaultdict(int)

        self.key_listeners  = []
        self.state_change_listeners = []
        self.sound_effect_listeners = []
        self.mouse_button_listeners = []
        self.settings_listeners     = []
        self.quit_listeners = []

    def handle_event(self, event):
        if event.type in self.callbacks:
            self.callbacks[event.type](event)

    def register_key_listener(self, listener):
        self.key_listeners.append(listener)

    def unregister_key_listener(self, listener):
        self.key_listeners.remove(listener)

    def register_quit_listener(self, listener):
        self.quit_listeners.append(listener)

    def unregister_quit_listener(self, listener):
        self.quit_listeners.remove(listener)

    def register_mouse_button_listener(self, listener):
        self.mouse_button_listeners.append(listener)

    def unregister_mouse_button_listener(self, listener):
        self.mouse_button_listeners.remove(listener)

    def register_state_change_listener(self, listener):
        self.state_change_listeners.append(listener)

    def unregister_state_change_listener(self, listener):
        self.state_change_listeners.remove(listener)

    def register_sound_effect_listener(self, listener):
        self.sound_effect_listeners.append(listener)

    def unregister_state_change_listener(self, listener):
        self.sound_effect_listeners.remove(listener)

    def register_settings_update_listener(self, listener):
        self.settings_listeners.append(listener)

    def unregister_settings_update_listener(self, listener):
        self.settings_listeners.remove(listener)

    def settings_updated(self, event):
        for listener in self.settings_listeners:
            listener(event)

    def key_state_change(self, event):
        self.key_states[event.key] = pygame.time.get_ticks()
        for listener in self.key_listeners:
            listener(event)

    def state_change(self, event):
        for listener in self.state_change_listeners:
            listener(event)

    def sound_effect(self, event):
        for listener in self.sound_effect_listeners:
            listener(event)

    def mouse_motion(self, event):
        return

    def mouse_button_state_change(self, event):
        self.mouse_button_states[event.button] = pygame.time.get_ticks()
        for listener in self.mouse_button_listeners:
            listener(event)

    def get_key_event_time(self, key):
        if key in self.key_states:
            return self.key_states[key]

    def quit(self, event):
        for listener in self.quit_listeners:
            listener(event)
