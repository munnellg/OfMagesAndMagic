import pygame
from app.view.animations import Delay, FadeIn, FadeOut, ChooseRandom, FrameAnimate, MovePosition, DelayCallBack, MoveValue, SequenceAnimation, ParallelAnimation, Timeout
from app.resources.event_handler import SET_GAME_STATE
from app.resources import text_renderer, colours
from app.resources.music import MusicManager
from app.resources.images import ImageManager
from app.conway.game_of_life import GameOfLife
from app.resources.event_handler import SOUND_EFFECT

class StateWinnersView:
    def __init__(self, parent):
        self.root     = parent.parent
        self.parent   = parent
        self.winners  = self.root.winners
        self.firework_size = 8
        self.fireworks = GameOfLife(self.parent.resolution[0]//self.firework_size + 50,self.parent.resolution[1]//self.firework_size + 50)

        self.root.event_handler.register_key_listener(self.handle_event)
        self.congratulations_text = text_renderer.render_title("Champions", colours.COLOUR_WHITE)
        self.team1_text = text_renderer.render_huge_text(self.winners[0].get_short_name(), colours.COLOUR_WHITE)

        self.see_you = text_renderer.render_huge_text("Good Luck in the Finals!", colours.COLOUR_WHITE)

        self.spawn_burst(self.fireworks.get_width()-65, 10)
        self.spawn_burst(self.fireworks.get_width()-65, (self.fireworks.get_height()-65)//2-5)
        self.spawn_burst(self.fireworks.get_width()-65, (self.fireworks.get_height()-65)//2+15)
        self.spawn_burst(self.fireworks.get_width()-65, self.fireworks.get_height()-65)

        self.spawn_burst(10, 10)
        self.spawn_burst(10, (self.fireworks.get_height()-65)//2-5)
        self.spawn_burst(10, (self.fireworks.get_height()-65)//2+15)
        self.spawn_burst(10, self.fireworks.get_height()-65)

        self.spawn_burst((self.fireworks.get_width()-65)//2 - 10, 10)
        self.spawn_burst((self.fireworks.get_width()-65)//2 + 20, 10)

        self.spawn_burst((self.fireworks.get_width()-65)//2 - 10, self.fireworks.get_height()-65)
        self.spawn_burst((self.fireworks.get_width()-65)//2 + 20, self.fireworks.get_height()-65)

        self.firework_animation = Timeout(self.update_fireworks, time=150)

        self.animations = SequenceAnimation()
        self.animations.add_animation(FadeIn(self.set_alpha, time=3000))
        self.animations.add_animation(Delay( time=5000 ))
        self.animations.add_animation(FadeOut(self.set_alpha, time=3000))

        self.alpha  = 0
        self.frame  = 0

    def update_fireworks(self):
        self.fireworks.update()

    def set_alpha(self, alpha):
        self.alpha = alpha

    def spawn_burst(self, x, y):
        self.fireworks.set_cell(  x, y,1)
        self.fireworks.set_cell(x+1, y,1)
        self.fireworks.set_cell(x+2, y,1)

        self.fireworks.set_cell(x+1, y+2,1)

        self.fireworks.set_cell( x, y+4,1)
        self.fireworks.set_cell(x+1,y+4,1)
        self.fireworks.set_cell(x+2,y+4,1)

    def render(self):
        surface = pygame.Surface(self.parent.resolution)
        for y in range(self.fireworks.get_height()):
            for x in range(self.fireworks.get_width()):
                node = self.fireworks.get_cell(x,y)
                if node > 0:
                    pygame.draw.rect(surface, colours.COLOUR_YELLOW, (x*self.firework_size, y*self.firework_size, self.firework_size, self.firework_size))


        surface.blit(self.congratulations_text,
            ((surface.get_width()-self.congratulations_text.get_width())/2,
            surface.get_height()/2 - 150)
        )

        surface.blit(
            self.team1_text,
            ((surface.get_width()-self.team1_text.get_width())/2,
            (surface.get_height()-self.team1_text.get_height())/2)
        )

        mask = pygame.Surface(self.parent.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.alpha))
        surface.blit(mask, (0,0))

        return surface

    def update(self, delta_t):
        if self.animations.finished():
            self.parent.trigger_exit_to_main()

        self.animations.animate(delta_t)
        self.firework_animation.animate(delta_t)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE]:
                self.parent.trigger_exit_to_main()

    def exit_state(self):
        self.parent.parent.event_handler.unregister_key_listener(self.handle_event)

class AnnounceWinners:
    def __init__(self, parent, state_seed='default'):
        self.parent = parent
        self.event_handler = parent.event_handler
        self.resolution = self.parent.resolution

        self.states = {
            'default'    : StateWinnersView
        }

        self.cur_state = state_seed
        self.state     = self.states[self.cur_state](self)

        music_manager = MusicManager()
        music_manager.restore_music_volume()
        music_manager.play_song("champions", loops=-1)

    def set_state(self, state):
        self.state.exit_state()
        self.state_code = state
        self.state = self.states[state](self)

    def render(self):
        return self.state.render()

    def update(self, delta_t):
        self.state.update(delta_t)

    def handle_event(self, event):
        self.state.handle_event(event)

    def trigger_exit_to_main(self):
        self.state.exit_state()
        event = pygame.event.Event(SET_GAME_STATE, state="main_menu", seed='intro')
        pygame.event.post(event)
