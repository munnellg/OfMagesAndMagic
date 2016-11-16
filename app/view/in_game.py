import pygame
import operator
from app.resources.event_handler import SET_GAME_STATE
from app.models.league import League
from app.view.animations import Delay, FadeIn, FadeOut
from app.resources import text_renderer, colours

class ScoreTable:
    def __init__(self, league):
        self.league = league

        scores = self.league.get_scores()

        self.team_name_head = text_renderer.render_menu_item("Team", colours.COLOUR_WHITE)
        self.team_score_head = text_renderer.render_menu_item("Score", colours.COLOUR_WHITE)

        self.margin = 10
        self.cell_height = 64
        self.team_name_weight = 0.75

        self.width = 600
        self.height = self.cell_height * (len(scores) + 1)

    def render(self):
        surface = pygame.Surface((self.width, self.height))

        scores = self.league.get_scores()
        scores = [( team, scores[team]) for team in scores]
        scores = sorted(scores, key=operator.itemgetter(1))

        pygame.draw.rect(surface, colours.COLOUR_WHITE, (0,0,self.width, self.cell_height), 1)
        pygame.draw.rect(surface, colours.COLOUR_WHITE, (0,0,self.width*self.team_name_weight, self.cell_height), 1)

        surface.blit(self.team_name_head, (
            self.margin,
            (self.cell_height - self.team_name_head.get_height())//2
        ))

        surface.blit(self.team_score_head, (
            self.width*self.team_name_weight + self.margin,
            (self.cell_height - self.team_score_head.get_height())//2
        ))

        counter = 1
        for score in scores:
            pygame.draw.line(surface, colours.COLOUR_WHITE, (0,self.cell_height*(counter+1)), (self.width, self.cell_height*(counter+1)))
            team_name  = text_renderer.render_menu_item(score[0], colours.COLOUR_WHITE)
            team_score = text_renderer.render_menu_item("{}".format(score[1]), colours.COLOUR_WHITE)
            surface.blit(team_name, (
                self.margin,
                (self.cell_height - team_name.get_height())//2 + self.cell_height*counter
            ))

            surface.blit(team_score, (
                self.width - self.margin - team_score.get_width(),
                (self.cell_height - team_score.get_height())//2 + self.cell_height*counter
            ))
            counter = counter+1

        return surface

class MatchTable:
    def __init__(self, league):
        self.league = league

        matches = self.league.get_matches_list()

        self.match_head = text_renderer.render_menu_item("Matches", colours.COLOUR_WHITE)
        self.vs_text = text_renderer.render_menu_item("Vs.", colours.COLOUR_WHITE)
        self.margin = 10
        self.cell_height = 64
        self.team_name_weight = 0.75

        self.width = 600
        self.height = self.cell_height * (len(matches) + 1)

    def render(self):
        surface = pygame.Surface((self.width, self.height))

        pygame.draw.rect(surface, colours.COLOUR_WHITE, (0,0,self.width, self.cell_height), 1)

        surface.blit(self.match_head, (
            (self.width - self.match_head.get_width())//2,
            (self.cell_height - self.match_head.get_height())//2
        ))

        counter = 1
        for match in self.league.get_matches_list():
            pygame.draw.line(surface, colours.COLOUR_WHITE, (0,self.cell_height*(counter+1)), (self.width, self.cell_height*(counter+1)))

            surface.blit(self.vs_text, (
                (self.width - self.vs_text.get_width())//2,
                (self.cell_height - self.vs_text.get_height())//2 + self.cell_height*counter
            ))

            team_name  = text_renderer.render_menu_item(match[0].get_short_name(), colours.COLOUR_WHITE)
            surface.blit(team_name, (
                (self.width - self.vs_text.get_width())//2 - self.margin - team_name.get_width(),
                (self.cell_height - team_name.get_height())//2 + self.cell_height*counter
            ))

            team_name  = text_renderer.render_menu_item(match[1].get_short_name(), colours.COLOUR_WHITE)
            surface.blit(team_name, (
                (self.width + self.vs_text.get_width())//2 + self.margin,
                (self.cell_height - team_name.get_height())//2 + self.cell_height*counter
            ))
            counter = counter+1

        return surface

class StateLeagueView:
    def __init__(self, parent):
        self.parent = parent
        self.league = self.parent.league

        self.tables = [
            ScoreTable(self.league),
            MatchTable(self.league)
        ]

        self.animations = [
            FadeIn(self.set_alpha, time=1500),
            Delay( time=3000 ),
            FadeOut(self.set_alpha, time=250),
            FadeIn(self.set_alpha,  time=250),
            Delay( time=3000 ),
            FadeOut(self.set_alpha, time=500)
        ]
        self.cur_animation = 0

        self.alpha = 0

        self.parent.parent.event_handler.register_key_listener(self.handle_event)

        self.elapsed = 0
        self.head_height = 145

    def set_alpha(self, alpha):
        self.alpha = alpha

    def render(self):
        surface = pygame.Surface(self.parent.resolution)
        table = self.tables[int(self.cur_animation > 2)].render()
        x = (surface.get_width()-table.get_width())//2
        y = self.head_height
        surface.blit(table, (x,y))

        mask = pygame.Surface(self.parent.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.alpha))
        surface.blit(mask, (0,0))

        return surface

    def show_next_table(self):
        if self.cur_table < len(self.tables) - 1:
            self.cur_table += 1

    def update(self, delta_t):
        if self.cur_animation < len(self.animations):
            self.animations[self.cur_animation].animate(delta_t)
            if self.animations[self.cur_animation].finished():
                self.cur_animation += 1
        else:
            self.parent.set_state('battle_view')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if self.cur_animation < len(self.animations):
                    self.animations[self.cur_animation].skip()
            elif event.key == pygame.K_ESCAPE:
                self.parent.trigger_exit_to_main()

    def exit_state(self):
        self.parent.parent.event_handler.unregister_key_listener(self.handle_event)

class StateBattleStart:
    def __init__(self, parent):
        self.parent = parent

    def render(self):
        return pygame.Surface(self.parent.resolution)

    def update(self, delta_t):
        return

    def handle_event(self, event):
        return

class StateInBattle:
    def __init__(self, parent):
        self.parent = parent

    def render(self):
        return pygame.Surface(self.parent.resolution)

    def update(self, delta_t):
        return

    def handle_event(self, event):
        return

class StateBattleEnd:
    def __init__(self, parent):
        self.parent = parent

    def render(self):
        return pygame.Surface(self.parent.resolution)

    def update(self, delta_t):
        return

    def handle_event(self, event):
        return

class StateBattleView:
    def __init__(self, parent):
        self.parent = parent
        self.league = self.parent.league
        self.battle = self.league.get_next_battle()
        self.parent.parent.event_handler.register_key_listener(self.handle_event)

    def render(self):
        return pygame.Surface(self.parent.resolution)

    def update(self, delta_t):
        return

    def handle_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.parent.trigger_exit_to_main()
        
    def exit_state(self):
        self.parent.parent.event_handler.unregister_key_listener(self.handle_event)

class Game:
    def __init__(self, parent, state_seed='league_view'):
        self.parent = parent
        self.resolution = self.parent.resolution
        self.league = League(self.parent.teams)

        self.states = {
            'league_view' : StateLeagueView,
            'battle_view' : StateBattleView
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
