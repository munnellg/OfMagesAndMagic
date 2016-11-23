import pygame
import operator
from app.resources.event_handler import SET_GAME_STATE
from app.models.league import League
from app.view.animations import Delay, FadeIn, FadeOut, ChooseRandom, FrameAnimate
from app.resources import text_renderer, colours
from app.resources.images import ImageManager

class MessageBar:
    def __init__(self, parent):
        self.width  = 600
        self.height = 64
        self.parent = parent
        self.pos = (0, -self.height)
        self.animations = []
        self.message = ""

    def update(self, delta_t):
        if len(self.animations) > 0:
            self.animations[0].animate(delta_t)
            if self.animation.finished():
                self.animations = self.animations[1:]

    def set_message(self, message):
        self.animations.append()
        self.message_bar.set_message(message)
        self.animations.append()
        self.animations.append()

    def show(self):
        return

    def get_pos(self):
        return self.pos

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        text_renderer.render_text_wrapped(surface, self.message, (10, 10, 580, 44), color = colours.COLOUR_WHITE)
        return surface

    def hide(self):
        return

class MoveAnimation:
    def __init__(self, parent, move):
        self.parent = parent
        self.move = move
        self.current_animation = None

        self.states = {
            "show_planning" : None,
            "plan_failure"  : None,
            "plan_success"  : None,
            "move_finished" : None
        }

    def skip(self):
        return

    def finished(self):
        return False

    def animate(self, delta_t):
        return

    def planning(self):
        self.parent.show_message("{} is planning a move".format(self.move['caster'].get_short_name()))

    def show_move_result(self):
        print(self.move['success'])

class MageSprite:
    def __init__(self, mage, direction, start, combat_zone):
        self.mage = mage
        self.direction = direction
        self.start = start
        self.combat_zone = combat_zone

        self.pos = self.start

        self.sprite_sheet = self.mage.element.name.lower()+"_mage"

        self.state_arguments = {
            "idle"       : [0, 1, 2],
            "walking"    : [0, 3],
            "cast_spell" : [0, 4],
            "dead"       : [6]
        }

        self.animations = {
            "idle"       : [ FrameAnimate(self.set_frame, [
                                (0, 6000, 15000, [(1, 0.75), (2, 0.25)]),
                                (1,  250, 0, [(0,1)]),
                                (2, 1000, 0, [(0,1)]),
                            ]
                        )],
            "walking"    : [FrameAnimate(self.set_frame, [
                                (0, 300, 0, [(1, 1)]),
                                (3, 300, 0, [(0, 1)]),
                            ]
                        )],
            "cast_spell" : [FrameAnimate(self.set_frame, [
                                (0, 300, 0, [(1, 1)]),
                                (4, 150, 0, [(0, 1)]),
                            ]
                        )],
            "dead"       :
                        [FrameAnimate(self.set_frame, [
                                (0, 1000,  0,  [(1, 1)]),
                                (5, 150, 0, [(2, 1)]),
                                (6, 1000, 0, [(2, 1)]),
                            ]
                        )]
        }

        self.image_manager = ImageManager()
        self.state = "idle"
        self.frame = 0

    def set_frame(self, frame):
        if frame == -1:
            self.set_state('idle')
        self.frame = frame

    def get_pos(self):
        return self.pos

    def update(self, delta_t):
        for animation in self.animations[self.state]:
            animation.animate(delta_t)

    def render(self):
        return self.image_manager.get_tile(self.sprite_sheet, self.frame, self.direction)

class MageStatusView:
    def __init__(self, team1, team2, width, height):
        self.width = width
        self.height = height

    def update(self, delta_t):
        return

    def render(self):
        return

class BattleWindow:
    def __init__(self, battle, resolution):
        self.battle = battle
        self.resolution = resolution

        self.battle_area = pygame.Rect(
            ((self.resolution[0]-600)/2),
            ((self.resolution[1]-600)),
            600,
            650
        )

        self.sprites = []
        i = 0
        self.team1_sprites = { }
        for mage in self.battle.team1:
            self.team1_sprites[mage] = {
                "sprite" : MageSprite(mage, 0, (self.battle_area.x-i*10, self.battle_area.y + i*65), ( (self.resolution[0]-50)/2, (self.resolution[1]-50)/2))
            }
            self.sprites.append(self.team1_sprites[mage]["sprite"])
            i += 1

        i = 0
        self.team2_sprites = { }
        for mage in self.battle.team2:
            self.team2_sprites[mage] = {
                "sprite" : MageSprite(mage, 1, ((self.battle_area.x+self.battle_area.w-100)+i*10, self.battle_area.y + i*65), ( (self.resolution[0]-50)/2, (self.resolution[1]-50)/2))
            }
            self.sprites.append(self.team2_sprites[mage]["sprite"])
            i += 1

        self.image_manager = ImageManager()
        self.stage = self.image_manager.get_image('battle_stage')

    def render(self):
        surface  = pygame.Surface(self.resolution)
        surface.blit(self.stage,
            ((surface.get_width()-self.stage.get_width())/2,
            (surface.get_height()-200 - self.stage.get_height()))
        )
        for mage in self.sprites:
            image = mage.render()
            surface.blit(image, mage.get_pos())

        return surface

    def update(self, delta_t):
        for mage in self.sprites:
            mage.update(delta_t)

class VersusBanner:
    def __init__(self, team1, team2):
        self.team1_name = text_renderer.render_huge_text(team1, colours.COLOUR_WHITE)
        self.team2_name = text_renderer.render_huge_text(team2, colours.COLOUR_WHITE)
        self.vs_text = text_renderer.render_large_text("Vs", colours.COLOUR_WHITE)

        self.height = max(self.team1_name.get_height(), self.team2_name.get_height()) * 3
        self.width  = max(self.team1_name.get_width(), self.team2_name.get_width())

    def render(self):
        surface = pygame.Surface((self.width, self.height))

        surface.blit(self.team1_name,
            (
                (surface.get_width()-self.team1_name.get_width())/2,
                0
            )
        )

        surface.blit(self.vs_text,
            (
                (surface.get_width()-self.vs_text.get_width())/2,
                (surface.get_height()-self.vs_text.get_height())/2
            )
        )

        surface.blit(self.team2_name,
            (
                (surface.get_width()-self.team2_name.get_width())/2,
                (surface.get_height()-self.team2_name.get_height())
            )
        )

        return surface

class StatsWindow:
    def __init__(self):
        return

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
    def __init__(self, parent, root):
        self.root   = root
        self.parent = parent
        self.root.parent.event_handler.register_key_listener(self.handle_event)

        self.battle_window = self.parent.battle_window
        self.versus_banner = VersusBanner(
            self.parent.battle.team1.get_short_name(),
            self.parent.battle.team2.get_short_name()
        )

        self.animations = [
            FadeIn(self.set_alpha, time=1500),
            Delay( time=1500 ),
            FadeOut(self.set_alpha, time=1500),
            FadeIn(self.set_alpha, time=1500),
        ]
        self.alpha = 0

        self.cur_animation = 0

    def set_alpha(self, alpha):
        self.alpha = alpha

    def render(self):
        surface = pygame.Surface(self.root.resolution)
        if self.cur_animation < 3:
            banner = self.versus_banner.render()
            surface.blit(banner,
                (
                    (surface.get_width()-banner.get_width())//2,
                    (surface.get_height()-banner.get_height())//2
                )
            )
        else:
            window = self.battle_window.render()
            surface.blit(window, (0,0))

        mask = pygame.Surface(self.root.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.alpha))
        surface.blit(mask, (0,0))

        return surface

    def update(self, delta_t):
        self.battle_window.update(delta_t)

        if self.cur_animation < len(self.animations):
            self.animations[self.cur_animation].animate(delta_t)
            if self.animations[self.cur_animation].finished():
                self.cur_animation += 1
        else:
            self.parent.set_state('in_battle')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                for animation in self.animations:
                    animation.skip()
            elif event.key == pygame.K_ESCAPE:
                self.root.trigger_exit_to_main()

    def exit_state(self):
        self.root.parent.event_handler.unregister_key_listener(self.handle_event)

class StateInBattle:
    def __init__(self, parent, root):
        self.root   = root
        self.parent = parent
        self.message_bar = self.parent.message_bar
        self.root.parent.event_handler.register_key_listener(self.handle_event)
        self.battle_window = self.parent.battle_window
        result = self.parent.battle.play_next_move()
        self.move_animate = MoveAnimation(self, result)

    def render(self):
        window  = self.battle_window.render()
        message = self.message_bar.render()
        window.blit(message, self.message_bar.get_pos())
        return window

    def update(self, delta_t):
        if self.move_animate.finished():
            result = self.parent.battle.play_next_move()
            self.move_animate = MoveAnimation(self, result)

        self.move_animate.animate(delta_t)
        self.battle_window.update(delta_t)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.root.trigger_exit_to_main()

    def exit_state(self):
        self.root.parent.event_handler.unregister_key_listener(self.handle_event)

class StateBattleEnd:
    def __init__(self, parent, root):
        self.root   = root
        self.parent = parent

    def render(self):
        return pygame.Surface(self.parent.resolution)

    def update(self, delta_t):
        return

    def handle_event(self, event):
        return

class StateBattleView:
    def __init__(self, parent, state_seed='intro'):
        self.parent = parent
        self.league = self.parent.league
        self.battle = self.league.get_next_battle()

        self.message_bar = MessageBar(self)
        self.battle_window = BattleWindow(self.battle, self.parent.resolution)

        self.states = {
            'intro'     : StateBattleStart,
            'in_battle' : StateInBattle,
            'outro'     : StateBattleEnd
        }
        self.cur_state = state_seed
        self.state     = self.states[self.cur_state](self, self.parent)

    def render(self):
        return self.state.render()

    def update(self, delta_t):
        self.state.update(delta_t)

    def handle_event(self, event):
        self.state.handle_event(event)

    def set_state(self, state):
        self.state.exit_state()
        self.state_code = state
        self.state = self.states[state](self, self.parent)

    def exit_state(self):
        self.state.exit_state()

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
