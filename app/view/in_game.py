import pygame
import operator
from app.resources.event_handler import SET_GAME_STATE
from app.models.league import League
from app.view.animations import Delay, FadeIn, FadeOut, ChooseRandom, FrameAnimate, MovePosition, DelayCallBack, MoveValue
from app.resources import text_renderer, colours
from app.resources.images import ImageManager

def filled_rounded_rect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = pygame.Rect(rect)
    color        = pygame.Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)

    circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
    pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

def fill_gradient(surface, color, gradient, rect=None, vertical=True, forward=True):
    """fill a surface with a gradient pattern
    Parameters:
    color -> starting color
    gradient -> final color
    rect -> area to fill; default is surface's rect
    vertical -> True=vertical; False=horizontal
    forward -> True=forward; False=reverse

    Pygame recipe: http://www.pygame.org/wiki/GradientCode
    """
    if rect is None: rect = surface.get_rect()
    x1,x2 = rect.left, rect.right
    y1,y2 = rect.top, rect.bottom
    if vertical: h = y2-y1
    else:        h = x2-x1
    if forward: a, b = color, gradient
    else:       b, a = color, gradient
    rate = (
        float(b[0]-a[0])/h,
        float(b[1]-a[1])/h,
        float(b[2]-a[2])/h
    )
    fn_line = pygame.draw.line
    if vertical:
        for line in range(y1,y2):
            color = (
                min(max(a[0]+(rate[0]*(line-y1)),0),255),
                min(max(a[1]+(rate[1]*(line-y1)),0),255),
                min(max(a[2]+(rate[2]*(line-y1)),0),255)
            )
            fn_line(surface, color, (x1,line), (x2,line))
    else:
        for col in range(x1,x2):
            color = (
                min(max(a[0]+(rate[0]*(col-x1)),0),255),
                min(max(a[1]+(rate[1]*(col-x1)),0),255),
                min(max(a[2]+(rate[2]*(col-x1)),0),255)
            )
            fn_line(surface, color, (col,y1), (col,y2))

class MessageBar:
    def __init__(self, parent):
        self.width  = 600
        self.height = 64
        self.parent = parent
        self.show_pos = (self.parent.parent.resolution[0]//2 - self.width//2, -10)
        self.hide_pos = (self.parent.parent.resolution[0]//2 - self.width//2, -self.height)

        self.background = pygame.Surface((self.width, self.height))
        fill_gradient(self.background, (0x00,0x4e,0x92), (0x00,0x04,0x28))
        pygame.draw.rect(self.background, colours.COLOUR_WHITE, (10, 0, self.width-20, self.height-10), 2)

        self.pos = self.hide_pos
        self.message = ""
        self.message_rendered = pygame.Surface((0,0))

    def set_message(self, message):
        self.message = message
        self.message_rendered = text_renderer.render_text(self.message, colours.COLOUR_WHITE)

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def render(self):
        surface = self.background.copy()

        surface.blit(self.message_rendered, (
            ((surface.get_width()-self.message_rendered.get_width())//2,
            (surface.get_height()-self.message_rendered.get_height())-20)
        ))
        return surface

class MageSprite:
    def __init__(self, mage, direction, start, combat_zone):
        self.mage = mage
        self.direction = direction

        self.start = start
        self.combat_zone = combat_zone
        self.evasion_zone = (self.start[0] + 60*(direction + direction-1), self.start[1])
        self.pos = self.start

        self.sprite_sheet = self.mage.element.name.lower()+"_mage"

        self.animations = {
            "idle"       : [ FrameAnimate(self.set_frame, [
                                (0, 6000, 15000, [(1, 0.75), (2, 0.25)]),
                                (1,  250, 0, [(0,1)]),
                                (2, 1000, 0, [(0,1)]),
                            ]
                        )],
            "walking"    : [FrameAnimate(self.set_frame, [
                                (0, 100, 0, [(1, 1)]),
                                (3, 100, 0, [(0, 1)]),
                            ]
                        )],
            "cast_spell" : [FrameAnimate(self.set_frame, [
                                (0, 300, 0, [(1, 1)]),
                                (4, 150, 0, [(1, 1)]),
                            ]
                        )],
            "dead"       :
                        [FrameAnimate(self.set_frame, [
                                (0, 150,  0, [(1, 1)]),
                                (5, 150,  0, [(2, 1)]),
                                (6, 1000, 0, [(2, 1)]),
                            ]
                        )]
        }

        self.image_manager = ImageManager()
        self.state = "idle" if self.mage.cur_hp > 0 else "dead"
        self.frame = 0

    def set_frame(self, frame):
        self.frame = frame

    def set_state(self, state):
        if state != self.state:
            self.state = state
            for animation in self.animations[self.state]:
                animation.reset()

    def get_pos(self):
        return self.pos

    def sync(self):
        self.set_state("idle" if self.mage.cur_hp > 0 else "dead")

    def flip(self):
        self.direction = 1-self.direction

    def set_pos(self, pos):
        self.pos = pos

    def update(self, delta_t):
        for animation in self.animations[self.state]:
            animation.animate(delta_t)
    def render(self):
        return self.image_manager.get_tile(self.sprite_sheet, self.frame, self.direction)

class MageStatusWindow:
    def __init__(self, team1, team2, width, height):
        self.width = width
        self.height = height
        self.team1 = team1
        self.team2 = team2

        self.display_data = {}
        self.max_bar_width = self.width/2 - 40 - 250
        self.background = pygame.Surface((self.width, self.height))
        fill_gradient(self.background, (0x00,0x4e,0x92), (0x00,0x04,0x28))
        pygame.draw.rect(self.background, colours.COLOUR_WHITE, (
            10, 10, self.width/2 - 20, self.height - 20),
            5
        )
        pygame.draw.rect(self.background, colours.COLOUR_WHITE, (
            self.width/2 + 10, 10, self.width/2 - 20, self.height - 20
            ),
            5
        )

        for mage in team1:
            self.display_data[mage] = {}
            self.display_data[mage]['name'] = text_renderer.render_text(mage.get_short_name(), colours.COLOUR_WHITE)
            self.display_data[mage]['hp'] = mage.cur_hp
            self.display_data[mage]['max_hp'] = mage.max_hp

        for mage in team2:
            self.display_data[mage] = {}
            self.display_data[mage]['name'] = text_renderer.render_text(mage.get_short_name(), colours.COLOUR_WHITE)
            self.display_data[mage]['hp'] = mage.cur_hp
            self.display_data[mage]['max_hp'] = mage.max_hp

    def update(self, delta_t):
        return

    def set_mage_health(self, health, mage):
        self.display_data[mage]['hp'] = health

    def get_mage_health(self, mage):
        return self.display_data[mage]['hp']

    def sync(self):
        for mage in self.team1:
            self.display_data[mage]['hp'] = mage.cur_hp
            self.display_data[mage]['max_hp'] = mage.max_hp

        for mage in self.team2:
            self.display_data[mage]['hp'] = mage.cur_hp
            self.display_data[mage]['max_hp'] = mage.max_hp

    def render(self):
        surface = self.background.copy()

        y_offset = 0
        for mage in self.team1:
            y = 20+33*y_offset
            surf_name = self.display_data[mage]['name']
            surface.blit(surf_name, (20, y))
            filled_rounded_rect(surface, (
                268, y+1,
                self.max_bar_width+3, 29
            ), colours.COLOUR_BLACK)

            filled_rounded_rect(surface, (
                270, y+3,
                max(1,self.max_bar_width*(float(self.display_data[mage]['hp'])/max(1,mage.max_hp))), 25
            ), colours.COLOUR_RED)

            health_text = text_renderer.render_small_text(
                "{}/{}".format( int(self.display_data[mage]['hp']), mage.max_hp), colours.COLOUR_WHITE
            )
            surface.blit(health_text, (( self.max_bar_width + 540 - health_text.get_width())/2, y + (30 - health_text.get_height())/2))
            y_offset += 1

        y_offset = 0
        for mage in self.team2:
            y = 20+33*y_offset
            surf_name = self.display_data[mage]['name']
            surface.blit(surf_name, (self.width/2 + 20, y))
            filled_rounded_rect(surface, (
                self.width/2 + 268, y+1,
                self.max_bar_width+3, 29
            ), colours.COLOUR_BLACK)

            filled_rounded_rect(surface, (
                self.width/2 + 270, y+3,
                max(1,self.max_bar_width*(float(self.display_data[mage]['hp'])/max(1,mage.max_hp))), 25
            ), colours.COLOUR_RED)

            health_text = text_renderer.render_small_text(
                "{}/{}".format(int(self.display_data[mage]['hp']), mage.max_hp), colours.COLOUR_WHITE
            )

            surface.blit(health_text, ((self.width + self.max_bar_width + 540 - health_text.get_width())/2, y + (30 - health_text.get_height())/2 ))

            y_offset += 1

        return surface

class BattleWindow:
    def __init__(self, battle, resolution):
        self.battle = battle
        self.resolution = resolution

        self.battle_area = pygame.Rect(
            ((self.resolution[0]-600)/2),
            ((self.resolution[1]-600)),
            600,
            5*65
        )

        self.sprites = []
        i = 0
        self.team1_sprites = { }
        for mage in self.battle.team1:
            self.team1_sprites[mage] = {
                "sprite" : MageSprite(mage, 0, (self.battle_area.x-i*15, self.battle_area.y + i*65),
                ( self.battle_area.x+ self.battle_area.w/2 - 50, self.battle_area.y+ self.battle_area.h/2 - 50))
            }
            self.sprites.append(self.team1_sprites[mage]["sprite"])
            i += 1

        i = 0
        self.team2_sprites = { }
        for mage in self.battle.team2:
            self.team2_sprites[mage] = {
                "sprite" : MageSprite(mage, 1, (self.battle_area.x+self.battle_area.w+i*15-100, self.battle_area.y + i*65 ),
                ( self.battle_area.x+ self.battle_area.w/2 - 50, self.battle_area.y+ self.battle_area.h/2 - 50))
            }
            self.sprites.append(self.team2_sprites[mage]["sprite"])
            i += 1

        self.image_manager = ImageManager()
        self.stage = self.image_manager.get_image('battle_stage')

    def sync(self):
        for mage in self.sprites:
            mage.sync()

    def get_mage(self, mage):
        if mage in self.team1_sprites:
            return self.team1_sprites[mage]
        if mage in self.team2_sprites:
            return self.team2_sprites[mage]
        return None

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

    def sync_mages(self):
        for mage in self.sprites:
            if mage.mage.cur_hp == 0:
                mage.set_state('dead')
            else:
                mage.set_state('idle')

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
        scores = sorted(scores, key=lambda item: -item[1])

        #pygame.draw.rect(surface, colours.COLOUR_WHITE, (0,0,self.width, self.cell_height), 1)
        #pygame.draw.rect(surface, colours.COLOUR_WHITE, (0,0,self.width*self.team_name_weight, self.cell_height), 1)
        r = self.team_name_head.get_rect()
        pygame.draw.line(surface, colours.COLOUR_WHITE, (self.margin, (self.cell_height - self.team_name_head.get_height())//2+r.h), (self.margin+r.w, (self.cell_height - self.team_name_head.get_height())//2+r.h))
        surface.blit(self.team_name_head, (
            self.margin,
            (self.cell_height - self.team_name_head.get_height())//2
        ))

        r = self.team_score_head.get_rect()
        pygame.draw.line(surface, colours.COLOUR_WHITE,
            (self.width - self.margin, (self.cell_height - self.team_score_head.get_height())//2+r.h),
            (self.width - self.margin - r.w, (self.cell_height - self.team_score_head.get_height())//2+r.h)
        )
        surface.blit(self.team_score_head, (
            self.width - self.margin - self.team_score_head.get_width(),
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

        self.match_head = text_renderer.render_large_text("Matches", colours.COLOUR_WHITE)
        self.vs_text = text_renderer.render_menu_item("Vs.", colours.COLOUR_WHITE)
        self.margin = 10
        self.cell_height = 64
        self.team_name_weight = 0.75

        self.width = 600
        self.height = self.cell_height * (len(matches) + 1)

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        r = self.match_head.get_rect()
        pygame.draw.line(surface, colours.COLOUR_WHITE,
            ((self.width - self.match_head.get_width())//2, r.y+r.h), ((self.width - self.match_head.get_width())//2+r.w, r.y+r.h)
        )

        # pygame.draw.rect(surface, colours.COLOUR_WHITE, (0,0,self.width, self.cell_height), 1)

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
                0,
                (self.cell_height - team_name.get_height())//2 + self.cell_height*counter
            ))

            team_name  = text_renderer.render_menu_item(match[1].get_short_name(), colours.COLOUR_WHITE)
            surface.blit(team_name, (
                self.width - team_name.get_width(),
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
            FadeIn(self.set_alpha, time=3000),
            Delay( time=3000 ),
            FadeOut(self.set_alpha, time=500),
            FadeIn(self.set_alpha,  time=500),
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
        self.mage_status = self.parent.mage_status
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
            window  = self.battle_window.render()
            status  = self.mage_status.render()
            window.blit(status, (0, window.get_height()-200))
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
        self.mage_status = self.parent.mage_status
        self.animations = []
        self.skip_turn = False
        self.skip_game = False

    def render(self):
        window  = self.battle_window.render()
        message = self.message_bar.render()
        status  = self.mage_status.render()
        window.blit(message, self.message_bar.get_pos())
        window.blit(status, (0, window.get_height()-200))
        return window

    def play_all_move_animations(self):
        while len(self.animations) > 0:
            for animation in self.animations[0]:
                animation.skip()
            self.animations = self.animations[1:]

    def play_whole_game(self):
        result = self.parent.battle.play_next_move()
        while not result['finished']:
            result = self.parent.battle.play_next_move()
        self.battle_window.sync_mages()
        self.match_over = True

    def advance_move_animation(self, delta_t):
        for animation in self.animations[0]:
            animation.animate(delta_t)
        self.animations[0] = [animation for animation in self.animations[0] if not animation.finished()]
        if len(self.animations[0]) == 0:
            self.animations = self.animations[1:]

    def update(self, delta_t):

        if len(self.animations) == 0:
            result = self.parent.battle.play_next_move()
            if result['finished']:
                self.parent.league.record_result(self.parent.battle)
                self.parent.set_state('outro')
            else:
                self.process_move_result(result)
        else:
            if self.skip_turn or self.skip_game:
                self.play_all_move_animations()
                self.skip_turn = False

                if self.skip_game:
                    self.play_whole_game()
                    self.skip_game = False
            else:
                self.advance_move_animation(delta_t)

        self.battle_window.update(delta_t)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.root.trigger_exit_to_main()
            if event.key == pygame.K_SPACE:
                self.skip_turn = True
            if event.key == pygame.K_RETURN:
                self.skip_game = True

    def exit_state(self):
        self.root.parent.event_handler.unregister_key_listener(self.handle_event)

    def animate_does_nothing(self, move_result):
        self.animations += [
            [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
            [DelayCallBack(self.message_bar.set_message,
                ["{} gets distracted and does nothing".format(move_result['caster'].get_short_name())],
                  time=0)],
            [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
            [Delay(time=2000)],
        ]

    def process_move_failed(self, move_result):
        if move_result['reason'] == "invalid target" or move_result['reason'] == "does nothing":
            self.animate_does_nothing(move_result)

    def process_move_succeed(self, move_result):
        caster_sprite = self.battle_window.get_mage(move_result['caster'])

        self.animations += [
            [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
            [DelayCallBack(self.message_bar.set_message,
                ["{} casts {} ".format(move_result['caster'].get_short_name(), move_result['spell'].name)],
                  time=0)],
            [DelayCallBack(caster_sprite['sprite'].set_state, ['cast_spell'], time=0)],
            [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
            [Delay(time=1000)]
        ]

        for result in move_result['result']:
            self.process_spell_cast(result)

    def process_spell_cast(self, cast):
        if cast['type'] == 'attack':
            self.process_attack_spell(cast)

    def process_attack_spell(self, cast):
        target_sprite = self.battle_window.get_mage(cast['target'])

        if cast['sustained'] == 0 and cast['target'].cur_hp == 0:
            self.animations += [
                [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                [DelayCallBack(self.message_bar.set_message,
                    ["{} is already unconscious".format(cast['target'].get_short_name())],
                      time=0)],
                [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                [Delay(time=1000)]
            ]
        elif cast['evades']:
            self.animations += [
                [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                [DelayCallBack(self.message_bar.set_message,
                    ["{} evades the attack".format(cast['target'].get_short_name())],
                      time=0)],
                [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                [DelayCallBack(target_sprite['sprite'].set_state, ['walking'], time=0)],
                [MovePosition(target_sprite['sprite'].start, target_sprite['sprite'].evasion_zone, target_sprite['sprite'].set_pos, time=100)],
                [MovePosition(target_sprite['sprite'].evasion_zone, target_sprite['sprite'].start, target_sprite['sprite'].set_pos, time=100)],
                [DelayCallBack(target_sprite['sprite'].set_state, ['idle'], time=0)],
                [Delay(time=800)]
            ]
        else:
            self.animations += [
                [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                [DelayCallBack(self.message_bar.set_message,
                    ["Hits {} ".format(cast['target'].get_short_name())],
                      time=0)],
                [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                [Delay(time=200)],
                [MoveValue(self.mage_status.set_mage_health, self.mage_status.get_mage_health(cast['target']), cast['target'].cur_hp, [cast['target']], time=1000  )]
            ]
            if cast['critical']:
                self.animations += [
                    [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                    [DelayCallBack(self.message_bar.set_message,
                        ["Critical Hit".format(cast['target'].get_short_name())],
                          time=0)],
                    [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                    [Delay(time=1000)]
                ]
            if cast['super_effective']:
                self.animations += [
                    [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                    [DelayCallBack(self.message_bar.set_message,
                        ["It's super effective".format(cast['target'].get_short_name())],
                          time=0)],
                    [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                    [Delay(time=1000)]
                ]
            if cast['not_very_effective']:
                self.animations += [
                    [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                    [DelayCallBack(self.message_bar.set_message,
                        ["It's not very effective".format(cast['target'].get_short_name())],
                          time=0)],
                    [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                    [Delay(time=1000)]
                ]

            if cast['sustained'] > 0 and cast['target'].cur_hp == 0:
                self.animations += [
                    [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
                    [DelayCallBack(self.message_bar.set_message,
                        ["{} fainted".format(cast['target'].get_short_name())],
                          time=0)],
                    [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
                    [DelayCallBack(target_sprite['sprite'].set_state, ['dead'], time=0)],
                ]

    def process_move_result(self, move_result):

        caster_sprite = self.battle_window.get_mage(move_result['caster'])

        self.message_bar.set_message(
            "{} is planning a move".format(move_result['caster'].get_short_name())
        )
        self.animations += [
            [MovePosition(self.message_bar.hide_pos, self.message_bar.show_pos, self.message_bar.set_pos)],
            [DelayCallBack(caster_sprite['sprite'].set_state, ['walking'], time=0)],
            [MovePosition(caster_sprite['sprite'].start, caster_sprite['sprite'].combat_zone, caster_sprite['sprite'].set_pos, time=1000)],
            [DelayCallBack(caster_sprite['sprite'].set_state, ['idle'], time=0)],
        ]

        if not move_result['success']:
            self.process_move_failed(move_result)
        else:
            self.process_move_succeed(move_result)

        self.animations += [
            [DelayCallBack(caster_sprite['sprite'].flip, time=0)],
            [DelayCallBack(caster_sprite['sprite'].set_state, ['walking'], time=0)],
            [MovePosition(caster_sprite['sprite'].combat_zone, caster_sprite['sprite'].start, caster_sprite['sprite'].set_pos, time=1000)],
            [DelayCallBack(caster_sprite['sprite'].flip, time=0)],
            [DelayCallBack(caster_sprite['sprite'].set_state, ['idle'], time=0)],
            [MovePosition(self.message_bar.show_pos, self.message_bar.hide_pos, self.message_bar.set_pos)],
            [DelayCallBack(self.battle_window.sync, time=0)],
            [DelayCallBack(self.mage_status.sync, time=0)],
        ]

class StateBattleEnd:
    def __init__(self, parent, root):
        self.root   = root
        self.parent = parent
        self.battle_window = self.parent.battle_window
        self.root.parent.event_handler.register_key_listener(self.handle_event)
        self.mage_status = self.parent.mage_status
        self.battle = self.parent.battle

        self.winner = self.battle.get_winner()

        self.winner_text = text_renderer.render_huge_text(self.winner, colours.COLOUR_WHITE)
        self.victory_text = text_renderer.render_huge_text("Victory", colours.COLOUR_WHITE)

        self.animations = [
            FadeOut(self.set_game_alpha, time=1500),
            Delay( time=1500 ),
            FadeOut(self.set_overlay_alpha, time=500)
        ]
        self.cur_animation = 0

        self.game_alpha    = 255
        self.overlay_alpha = 255

    def set_game_alpha(self, value):
        self.game_alpha = value

    def set_overlay_alpha(self, value):
        self.overlay_alpha = value

    def render(self):
        window  = self.battle_window.render()
        status  = self.mage_status.render()
        window.blit(status, (0, window.get_height()-200))

        mask = pygame.Surface(self.root.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.game_alpha))
        window.blit(mask, (0,0))

        window.blit( self.victory_text,
            (
                (window.get_width()-self.victory_text.get_width())/2,
                window.get_height()/2-self.victory_text.get_height()*2
            )
        )

        window.blit( self.winner_text,
            (
                (window.get_width()-self.winner_text.get_width())/2,
                window.get_height()/2 - self.winner_text.get_height()
            )
        )

        mask = pygame.Surface(self.root.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.overlay_alpha))
        window.blit(mask, (0,0))

        return window

    def update(self, delta_t):
        self.battle_window.update(delta_t)

        if self.cur_animation < len(self.animations):
            self.animations[self.cur_animation].animate(delta_t)
            if self.animations[self.cur_animation].finished():
                self.cur_animation += 1
        else:
            self.root.set_state('league_view')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.root.trigger_exit_to_main()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                for animation in self.animations:
                    animation.skip()

    def exit_state(self):
        self.root.parent.event_handler.unregister_key_listener(self.handle_event)

class StateBattleView:
    def __init__(self, parent, state_seed='intro'):
        self.parent = parent
        self.league = self.parent.league
        self.battle = self.league.get_next_battle()

        self.message_bar = MessageBar(self)
        self.battle_window = BattleWindow(self.battle, self.parent.resolution)
        self.mage_status = MageStatusWindow( self.battle.team1, self.battle.team2, self.parent.resolution[0], 200 )

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
