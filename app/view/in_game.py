import pygame
import random
import operator
from app.resources.event_handler import SET_GAME_STATE
from app.models.league import League
from app.view.animations import Delay, FadeIn, FadeOut, ChooseRandom, FrameAnimate, MovePosition, DelayCallBack, MoveValue, SequenceAnimation, ParallelAnimation
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

class RoundCounter:
    def __init__(self, battle):
        self.battle = battle
        self.round_number = battle.get_round_number()

        self.width  = 50
        self.height = 50
        self.pos = (0,0)
        self.background = pygame.Surface((self.width, self.height))
        fill_gradient(self.background, (0x00,0x4e,0x92), (0x00,0x04,0x28))
        # pygame.draw.rect(self.background, colours.COLOUR_WHITE, (10, 10, self.width-20, self.height-20), 2)

        self.digit = text_renderer.render_text("{}".format(self.round_number), colours.COLOUR_WHITE)

    def render(self):
        surface = self.background.copy()
        surface.blit(self.digit,
            (
                (self.width - self.digit.get_width())/2,
                (self.height - self.digit.get_height())/2
            )
        )
        return surface

    def get_pos(self):
        return self.pos

    def update(self, delta_t):
        rn = self.battle.get_round_number()
        if rn != self.round_number:
            self.round_number = rn
            self.digit = text_renderer.render_text("{}".format(self.round_number), colours.COLOUR_WHITE)

class MessageBar:
    def __init__(self, parent):
        self.width  = 650
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

    def animate_show(self):
        return MovePosition(self.hide_pos, self.show_pos, self.set_pos)

    def animate_hide(self):
        return MovePosition(self.show_pos, self.hide_pos, self.set_pos)

    def animate_set_message_show(self, message):
        sequence = SequenceAnimation()
        update_message = DelayCallBack(self.set_message, [message], time=0)
        show = self.animate_show()

        sequence.add_animation(update_message)
        sequence.add_animation(show)

        return sequence

    def animate_hide_set_message_show(self, message):
        sequence = SequenceAnimation()
        hide = self.animate_hide()
        update_message = DelayCallBack(self.set_message, [message], time=0)
        show = self.animate_show()

        sequence.add_animation(hide)
        sequence.add_animation(update_message)
        sequence.add_animation(show)

        return sequence

class MageSprite:
    def __init__(self, mage, direction, start, combat_zone):
        self.mage = mage
        self.direction = direction

        self.start = start
        self.combat_zone = combat_zone
        self.evasion_zone = (self.start[0] + 60*(direction + direction-1), self.start[1])
        self.pos = self.start

        self.sprite_sheet = self.mage.element.name.lower()+"_mage"

        self.hiding = False

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
        self.set_direction(1-self.direction)

    def set_direction(self, direction):
        self.direction = direction

    def set_pos(self, pos):
        self.pos = pos

    def update(self, delta_t):
        for animation in self.animations[self.state]:
            animation.animate(delta_t)

    def hide(self):
        self.hiding = True

    def show(self):
        self.hiding = False

    def render(self):
        if not self.hiding:
            return self.image_manager.get_tile(self.sprite_sheet, self.frame, self.direction)
        return pygame.Surface((0,0))

    def animate_move_start_to_combat(self):
        walk = DelayCallBack(self.set_state, ['walking'], time=0)
        move = MovePosition(self.start, self.combat_zone, self.set_pos, time=1000)
        stop = DelayCallBack(self.set_state, ['idle'], time=0)

        return SequenceAnimation([walk, move, stop])

    def animate_turn_around(self):
        return DelayCallBack(self.flip, time=0)

    def animate_move_combat_to_start(self):
        sequence = SequenceAnimation()
        walk = DelayCallBack(self.set_state, ['walking'], time=0)
        move = MovePosition(self.combat_zone, self.start, self.set_pos, time=1000)
        stop = DelayCallBack(self.set_state, ['idle'], time=0)

        sequence.add_animation(walk)
        sequence.add_animation(move)
        sequence.add_animation(stop)

        return sequence

    def animate_cast_spell(self):
        return DelayCallBack(self.set_state, ['cast_spell'], time=0)

    def animate_evade(self):
        walk = DelayCallBack(self.set_state, ['walking'], time=0)
        dodge_back = MovePosition(self.start, self.evasion_zone, self.set_pos, time=100)
        dodge_forward = MovePosition(self.evasion_zone, self.start, self.set_pos, time=100)
        idle = DelayCallBack(self.set_state, ['idle'], time=0)
        return SequenceAnimation([walk, dodge_back, dodge_forward,idle])

    def animate_faint(self):
        return DelayCallBack(self.set_state, ['dead'], time=0)

    def animate_take_damage(self, critical = False):
        sequence = SequenceAnimation()
        duration = 75
        cycles   = 8

        if critical:
            duration/=2
            cycles*=2

        for i in range(cycles):
            hide = DelayCallBack(self.hide, time=duration)
            show = DelayCallBack(self.show, time=duration)
            sequence.add_animation(hide)
            sequence.add_animation(show)

        return sequence

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

    def animate_update_health(self, mage):
        return MoveValue(self.set_mage_health, self.display_data[mage]['hp'], mage.cur_hp, [mage], time=1000  )

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

    def restore_positions(self):
        for mage in self.battle.team1:
            sprite = self.team1_sprites[mage]['sprite']
            sprite.set_pos(sprite.start)
            sprite.set_direction(0)
            sprite.show()

        for mage in self.battle.team2:
            sprite = self.team2_sprites[mage]['sprite']
            sprite.set_pos(sprite.start)
            sprite.set_direction(1)
            sprite.show()

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

    def sync(self):
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

        self.height = self.team1_name.get_height() + self.team2_name.get_height() + self.vs_text.get_height() + 20
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

        self.animations = SequenceAnimation()
        self.animations.add_animation(FadeIn(self.set_alpha, time=3000))

        next_table = SequenceAnimation()
        next_table.add_animation(Delay( time=3000 ))
        next_table.add_animation(FadeOut(self.set_alpha, time=500))
        next_table.add_animation(DelayCallBack(self.next_window, time=0))
        next_table.add_animation(FadeIn(self.set_alpha, time=500))
        self.animations.add_animation(next_table)

        close = SequenceAnimation()
        close.add_animation(Delay( time=3000 ))
        close.add_animation(FadeOut(self.set_alpha, time=500))
        self.animations.add_animation(close)

        self.alpha = 0

        self.parent.parent.event_handler.register_key_listener(self.handle_event)

        self.head_height = 145
        self.table = 0

    def set_alpha(self, alpha):
        self.alpha = alpha

    def next_window(self):
        if self.league.finished():
            if self.league.winners_chosen():
                self.parent.trigger_exit_to_announce_winners()
        if not self.league.finished():
            self.table += 1

    def render(self):
        surface = pygame.Surface(self.parent.resolution)
        table = self.tables[self.table].render()
        x = (surface.get_width()-table.get_width())//2
        y = self.head_height
        surface.blit(table, (x,y))

        mask = pygame.Surface(self.parent.resolution, pygame.SRCALPHA)
        mask.fill((0,0,0, 255-self.alpha))
        surface.blit(mask, (0,0))

        return surface

    def update(self, delta_t):
        if not self.animations.finished():
            self.animations.animate(delta_t)
        else:
            self.parent.set_state('battle_view')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.animations.skip_current()
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
        self.round_counter = self.parent.round_counter
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
            round_count = self.round_counter.render()
            window.blit(round_count, self.round_counter.get_pos())
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
        self.round_counter = self.parent.round_counter
        self.animations = SequenceAnimation()

        self.paused_text = text_renderer.render_large_text("PAUSED", colours.COLOUR_WHITE)

        self.skip_turn = False
        self.skip_game = False
        self.paused    = False

    def render(self):
        window  = self.battle_window.render()
        message = self.message_bar.render()
        status  = self.mage_status.render()
        window.blit(message, self.message_bar.get_pos())
        window.blit(status, (0, window.get_height()-200))
        round_count = self.round_counter.render()
        window.blit(round_count, self.round_counter.get_pos())
        if self.paused:
            window.blit(self.paused_text, (
                (
                    (window.get_width()-self.paused_text.get_width())/2,
                    (window.get_height()-self.paused_text.get_height())/2 - self.paused_text.get_height()
                )
            ))

        return window

    def play_all_move_animations(self):
        self.animations.skip()

    def toggle_pause(self):
        self.paused = not self.paused

    def skip_animations(self):
        self.animations.cur_animation = len(self.animations.animations)
        self.battle_window.restore_positions()
        self.battle_window.sync()
        self.mage_status.sync()

    def play_whole_game(self):
        result = self.parent.battle.play_next_move()
        while not result['finished']:
            result = self.parent.battle.play_next_move()
        self.battle_window.sync()
        self.mage_status.sync()
        self.match_over = True

    def update(self, delta_t):
        if self.paused:
            return

        if self.animations.finished():
            result = self.parent.battle.play_next_move()
            if result['finished']:
                self.parent.league.record_result(self.parent.battle)
                self.parent.set_state('outro')
            else:
                self.process_move_result(result)
        else:
            if self.skip_turn or self.skip_game:
                self.skip_animations()
                self.skip_turn = False

                if self.skip_game:
                    self.play_whole_game()
                    self.skip_game = False
            else:
                self.animations.animate(delta_t)

        self.battle_window.update(delta_t)
        self.round_counter.update(delta_t)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.root.trigger_exit_to_main()
            elif event.key == pygame.K_p:
                self.toggle_pause()
            elif not self.paused:
                if event.key == pygame.K_SPACE:
                    self.skip_turn = True
                elif event.key == pygame.K_RETURN:
                    self.skip_game = True
                elif event.key in [pygame.K_LEFT, pygame.K_1]:
                    self.parent.battle.award_victory(1)
                    self.skip_game = True
                elif event.key in [pygame.K_RIGHT, pygame.K_2]:
                    self.parent.battle.award_victory(2)
                    self.skip_game = True

    def exit_state(self):
        self.root.parent.event_handler.unregister_key_listener(self.handle_event)

    def animate_unknown_spell(self, move_result):
        update_message_bar = self.message_bar.animate_hide_set_message_show (
            "{} tries to cast {}".format(move_result['caster'].get_short_name(), move_result['spell'].name)
        )
        self.animations.add_animation(update_message_bar)
        self.animations.add_animation(Delay(time=1000))

        if move_result['reason'] == "unknown spell":
            update_message_bar = self.message_bar.animate_hide_set_message_show (
                "but {} does not know that spell".format(move_result['caster'].get_short_name())
            )
        elif move_result['reason'] == "cannot cast":
            update_message_bar = self.message_bar.animate_hide_set_message_show (
                "but {} is not master of {}".format(move_result['caster'].get_short_name(), move_result['spell'].element.name)
            )
        else:
            update_message_bar = self.message_bar.animate_hide_set_message_show (
                "but {} is not a spell".format(move_result['spell'].name)
            )
        self.animations.add_animation(update_message_bar)

    def gen_do_nothing_string(self, mage):
        text = random.choice([
            "{} is distracted by a squirrel",
            "{}'s spellbook is still at home",
            "{} wants everyone to get along",
            "The sun is in {}'s eyes",
            "{} contemplates life",
        ])

        return text.format(mage)

    def animate_does_nothing(self, move_result):
        update_message_bar = self.message_bar.animate_hide_set_message_show (
            self.gen_do_nothing_string(move_result['caster'].get_short_name())
        )
        self.animations.add_animation(update_message_bar)
        self.animations.add_animation(Delay(time=1000))

    def process_move_failed(self, move_result):
        if move_result['reason'] in ["unknown spell", "bad spell", "cannot cast"]:
            self.animate_unknown_spell(move_result)
        else:
            self.animate_does_nothing(move_result)

    def process_move_succeed(self, move_result):
        caster_sprite = self.battle_window.get_mage(move_result['caster'])['sprite']

        parallel = ParallelAnimation()

        hide_message_bar = self.message_bar.animate_hide()
        show_message = self.message_bar.animate_set_message_show(
            "{} casts {} ".format(move_result['caster'].get_short_name(), move_result['spell'].name)
        )
        cast = caster_sprite.animate_cast_spell()

        self.animations.add_animation(hide_message_bar)
        parallel.add_animation(cast)
        parallel.add_animation(show_message)
        self.animations.add_animation(parallel)
        self.animations.add_animation(Delay(time=1000))

        for result in move_result['result']:
            self.process_spell_cast(result, move_result['caster'])

    def process_spell_cast(self, cast, caster):
        if cast['type'] in ['attack', "rebound", "leech"]:
            self.process_attack_spell(cast, caster)
        elif cast['type'] == "healing":
            self.process_healing_spell(cast, caster)
        elif cast['type'] == 'stat_reduce':
            self.process_stat_reduce_spell(cast, caster)
        elif cast['type'] == 'stat_boost':
            self.process_stat_boost_spell(cast, caster)

    def process_attack_spell(self, cast, caster):
        target_sprite = self.battle_window.get_mage(cast['target'])['sprite']
        caster_sprite = self.battle_window.get_mage(caster)['sprite']

        if cast['sustained'] == 0 and cast['target'].cur_hp == 0:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{} is already unconscious".format(cast['target'].get_short_name())
            )
            self.animations.add_animation(show_message)
            self.animations.add_animation(Delay(time=1000))
        elif cast['evades']:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{} evades the attack".format(cast['target'].get_short_name())
            )
            dodge = target_sprite.animate_evade()

            self.animations.add_animation(show_message)
            self.animations.add_animation(dodge)
            self.animations.add_animation(Delay(time=800))
        else:
            show_message = self.message_bar.animate_hide_set_message_show(
                "Hits {} ".format(cast['target'].get_short_name())
            )
            update_stats = self.mage_status.animate_update_health(cast['target'])
            take_damage = target_sprite.animate_take_damage(cast['critical'])
            self.animations.add_animation(show_message)
            self.animations.add_animation(take_damage)
            self.animations.add_animation(update_stats)

            if cast['critical']:
                show_message = self.message_bar.animate_hide_set_message_show(
                    "Critical Hit"
                )
                self.animations.add_animation(show_message)
                self.animations.add_animation(Delay(time=1000))
            if cast['super_effective']:
                show_message = self.message_bar.animate_hide_set_message_show(
                    "It's super effective"
                )
                self.animations.add_animation(show_message)
                self.animations.add_animation(Delay(time=1000))
            if cast['not_very_effective']:
                show_message = self.message_bar.animate_hide_set_message_show(
                    "It's not very effective"
                )
                self.animations.add_animation(show_message)
                self.animations.add_animation(Delay(time=1000))

            if cast['sustained'] > 0 and cast['target'].cur_hp == 0:
                show_message = self.message_bar.animate_hide_set_message_show(
                    "{} fainted".format(cast['target'].get_short_name())
                )
                faint = target_sprite.animate_faint()

                self.animations.add_animation(show_message)
                self.animations.add_animation(faint)

            if cast['type'] == "leech":
                show_message = self.message_bar.animate_hide_set_message_show(
                    "{} absorbs {} HP".format(caster.get_short_name(), cast['leech'])
                )

                update_stats = self.mage_status.animate_update_health(caster)
                self.animations.add_animation(show_message)
                self.animations.add_animation(update_stats)

            if cast['type'] == "rebound":
                take_damage = caster_sprite.animate_take_damage()
                show_message = self.message_bar.animate_hide_set_message_show(
                    "{} is hit with the rebound".format(caster.get_short_name(), cast['rebound'])
                )
                update_stats = self.mage_status.animate_update_health(caster)
                self.animations.add_animation(take_damage)
                self.animations.add_animation(show_message)
                self.animations.add_animation(update_stats)

    def process_stat_boost_spell(self, cast, caster):
        target_sprite = self.battle_window.get_mage(cast['target'])['sprite']
        caster_sprite = self.battle_window.get_mage(caster)['sprite']

        if cast['effect'] < 0:
            show_message = self.message_bar.animate_hide_set_message_show(
                "Spell has no effect on {}".format(cast['target'].get_short_name())
            )
            self.animations.add_animation(show_message)
            self.animations.add_animation(Delay(time=1000))
        elif cast['effect']==0:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{}'s {} won't go any higher".format(cast['target'].get_short_name(), cast['stat'])
            )
            self.animations.add_animation(show_message)
        else:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{}'s {} rose".format(cast['target'].get_short_name(), cast['stat'])
            )
            self.animations.add_animation(show_message)

    def process_stat_reduce_spell(self, cast, caster):
        target_sprite = self.battle_window.get_mage(cast['target'])['sprite']
        caster_sprite = self.battle_window.get_mage(caster)['sprite']

        if cast['effect'] < 0:
            show_message = self.message_bar.animate_hide_set_message_show(
                "Spell has no effect on {}".format(cast['target'].get_short_name())
            )
            self.animations.add_animation(show_message)
            self.animations.add_animation(Delay(time=1000))
        elif cast['effect']==0:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{}'s {} won't go any lower".format(cast['target'].get_short_name(), cast['stat'])
            )
            self.animations.add_animation(show_message)
        else:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{}'s {} fell".format(cast['target'].get_short_name(), cast['stat'])
            )
            self.animations.add_animation(show_message)

    def process_healing_spell(self, cast, caster):
        target_sprite = self.battle_window.get_mage(cast['target'])['sprite']
        caster_sprite = self.battle_window.get_mage(caster)['sprite']

        if cast['target'].cur_hp == 0:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{} cannot be restored".format(cast['target'].get_short_name())
            )
            self.animations.add_animation(show_message)
            self.animations.add_animation(Delay(time=1000))
        else:
            show_message = self.message_bar.animate_hide_set_message_show(
                "{} regained {} HP".format(cast['target'].get_short_name(), cast['effect'])
            )
            update_stats = self.mage_status.animate_update_health(cast['target'])
            self.animations.add_animation(show_message)
            self.animations.add_animation(update_stats)

    def process_move_result(self, move_result):
        self.animations = SequenceAnimation()

        caster_sprite = self.battle_window.get_mage(move_result['caster'])['sprite']

        show_planning = self.message_bar.animate_set_message_show (
            "{} is planning a move".format(move_result['caster'].get_short_name()
        ))
        move_combat = caster_sprite.animate_move_start_to_combat()

        self.animations.add_animation(show_planning)
        self.animations.add_animation(move_combat)

        if not move_result['success']:
            self.process_move_failed(move_result)
        else:
            self.process_move_succeed(move_result)

        face_team = caster_sprite.animate_turn_around()
        move_home = caster_sprite.animate_move_combat_to_start()
        face_enemies = caster_sprite.animate_turn_around()

        self.animations.add_animation(face_team)
        self.animations.add_animation(move_home)
        self.animations.add_animation(face_enemies)

        hide_message_bar = self.message_bar.animate_hide()
        self.animations.add_animation(hide_message_bar)

        self.animations.add_animation(DelayCallBack(self.battle_window.sync, time=0))
        self.animations.add_animation(DelayCallBack(self.mage_status.sync, time=0))

class StateBattleEnd:
    def __init__(self, parent, root):
        self.root   = root
        self.parent = parent
        self.battle_window = self.parent.battle_window
        self.root.parent.event_handler.register_key_listener(self.handle_event)
        self.mage_status = self.parent.mage_status
        self.round_counter = self.parent.round_counter

        self.battle = self.parent.battle

        self.winner = self.battle.get_winner()

        self.winner_text = text_renderer.render_huge_text(self.winner, colours.COLOUR_WHITE)
        self.victory_text = text_renderer.render_huge_text("Victory", colours.COLOUR_WHITE)

        self.animations = SequenceAnimation()
        self.animations.add_animation( Delay( time=1000 ) )
        self.animations.add_animation( FadeOut(self.set_game_alpha, time=1500) )
        self.animations.add_animation( Delay( time=1500 ) )
        self.animations.add_animation( FadeOut(self.set_overlay_alpha, time=500))
        self.animations.add_animation( Delay( time=1000 ) )

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
        round_count = self.round_counter.render()
        window.blit(round_count, self.round_counter.get_pos())

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
        self.animations.animate(delta_t)
        if self.animations.finished():
            self.root.set_state('league_view')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.root.trigger_exit_to_main()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.animations.skip()

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
        self.round_counter = RoundCounter(self.battle)
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
        self.league = League(self.parent.teams, 2)

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

    def trigger_exit_to_announce_winners(self):
        self.parent.winners = self.league.get_winners()
        self.state.exit_state()
        event = pygame.event.Event(SET_GAME_STATE, state="announce_winners", seed='default')
        pygame.event.post(event)

    def trigger_exit_to_main(self):
        self.state.exit_state()
        event = pygame.event.Event(SET_GAME_STATE, state="main_menu", seed='intro')
        pygame.event.post(event)
