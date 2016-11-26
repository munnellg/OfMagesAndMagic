import pygame
from app.view.animations import Delay, FadeIn, FadeOut, ChooseRandom, FrameAnimate, MovePosition, DelayCallBack, MoveValue, SequenceAnimation, ParallelAnimation
from app.resources.event_handler import SET_GAME_STATE
from app.resources import text_renderer, colours

class StateWinnersView:
    def __init__(self, parent):
        self.root     = parent.parent
        self.parent   = parent
        self.winners  = self.root.winners

        self.root.event_handler.register_key_listener(self.handle_event)
        self.congratulations_text = text_renderer.render_title("Congratulations", colours.COLOUR_WHITE)
        self.team1_text = text_renderer.render_huge_text(self.winners[0].get_short_name(), colours.COLOUR_WHITE)
        self.and_text = text_renderer.render_menu_item("AND", colours.COLOUR_WHITE)
        self.team2_text = text_renderer.render_huge_text(self.winners[1].get_short_name(), colours.COLOUR_WHITE)

        self.see_you = text_renderer.render_huge_text("Good Luck in the Finals!", colours.COLOUR_WHITE)

        self.animations = SequenceAnimation()
        #self.animations.add_animation(Delay( time=5000 ))
        self.animations.add_animation(FadeIn(self.set_alpha, time=3000))

        next_table = SequenceAnimation()
        next_table.add_animation(Delay( time=5000 ))
        next_table.add_animation(FadeOut(self.set_alpha, time=500))
        next_table.add_animation(DelayCallBack(self.next_window, time=0))
        next_table.add_animation(FadeIn(self.set_alpha, time=500))
        self.animations.add_animation(next_table)

        self.alpha  = 0
        self.frame  = 0
        self.frames = []

        self.frames.append(pygame.Surface(self.parent.resolution))
        self.frames[0].blit(
            self.congratulations_text,
            ((self.frames[0].get_width()-self.congratulations_text.get_width())/2,
            self.frames[0].get_height()/2 - 250)
        )

        self.frames[0].blit(
            self.team1_text,
            ((self.frames[0].get_width()-self.team2_text.get_width())/2,
            self.frames[0].get_height()/2 - 125)
        )

        self.frames[0].blit(
            self.and_text,
            ((self.frames[0].get_width()-self.and_text.get_width())/2,
            (self.frames[0].get_height()-self.and_text.get_height())/2)
        )

        self.frames[0].blit(
            self.team2_text,
            ((self.frames[0].get_width()-self.team2_text.get_width())/2,
            self.frames[0].get_height()/2 + 50)
        )

        self.frames.append(pygame.Surface(self.parent.resolution))
        self.frames[1].blit(
            self.see_you,
            ((self.frames[1].get_width()-self.see_you.get_width())/2,
            (self.frames[1].get_height()-self.see_you.get_height())/2)
        )

    def next_window(self):
        self.frame = 1

    def set_alpha(self, alpha):
        self.alpha = alpha

    def render(self):
        surface = self.frames[self.frame].copy()
        mask = pygame.Surface(self.parent.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.alpha))
        surface.blit(mask, (0,0))
        return surface

    def update(self, delta_t):
        if not self.animations.finished():
            self.animations.animate(delta_t)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                self.parent.trigger_exit_to_main()

    def exit_state(self):
        self.parent.parent.event_handler.unregister_key_listener(self.handle_event)

class AnnounceWinners:
    def __init__(self, parent, state_seed='default'):
        self.parent = parent
        self.event_handler = parent.event_handler
        self.resolution = self.parent.resolution

        self.states = {
            'default' : StateWinnersView,
        }

        self.cur_state = state_seed
        self.state     = self.states[self.cur_state](self)

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
        event = pygame.event.Event(SET_GAME_STATE, state="main_menu", seed='default')
        pygame.event.post(event)
