import pygame
from collections import defaultdict

class EventHandler:
    def __init__(self):
        self.callbacks = {
            pygame.KEYDOWN           : self.key_state_change,
            pygame.KEYUP             : self.key_state_change,
            pygame.MOUSEMOTION       : self.mouse_motion,
            pygame.MOUSEBUTTONUP     : self.mouse_button_state_change,
            pygame.MOUSEBUTTONDOWN   : self.mouse_button_state_change,
            pygame.QUIT              : self.quit
        }

        self.key_states = defaultdict(int)
        self.mouse_button_states = defaultdict(int)

        self.key_listeners  = []
        self.mouse_button_listeners = []
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

    def key_state_change(self, event):
        self.key_states[event.key] = pygame.time.get_ticks()
        for listener in self.key_listeners:
            listener(event)

    def mouse_motion(self, event):
        #print(event)
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
