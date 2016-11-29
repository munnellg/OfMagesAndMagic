import pygame
from app.resources import text_renderer
from app.resources import colours
from app.resources.sounds import SoundManager
from app.resources.music import MusicManager
from app.resources.images import ImageManager
from app.resources.event_handler import SOUND_EFFECT, SETTINGS_UPDATED

class MenuItem(object):
    def __init__(self, label, height=-1, width=-1):
        self.label = label
        self.surface_label = text_renderer.render_menu_item(label, colours.COLOUR_WHITE)
        self.focused = False
        self.height = height
        self.width  = width

    def set_height(self, height):
        self.height = height

    def get_height(self):
        return self.height

    def set_width(self, width):
        self.width = width

    def get_width(self):
        return self.width

    def set_focused(self, focus):
        self.focused = focus

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        return surface

    def click(self):
        return

class ChoiceMenuItem(MenuItem):
    def __init__(self, label1, label2, callback, height=-1, width=-1):
        super(ChoiceMenuItem, self).__init__(label1, height, width)
        self.label2 = label2
        self.surface_label2 = text_renderer.render_menu_item(label2, colours.COLOUR_WHITE)
        self.padding = 80
        self.selected = 0
        self.bottom_margin = 0
        self.callback = callback

        if self.width < 0:
            self.width = max(self.surface_label2.get_width(), self.surface_label.get_width())*2+self.padding

        if self.height < 0:
            self.width = max(self.surface_label2.get_height(), self.surface_label.get_height())

    def get_value(self):
        return self.selected

    def set_value(self, value):
        self.selected = value

    def draw_focused(self, surface):
        if self.selected == 0:
            x1 = self.width//2 - 9 - self.surface_label.get_width() - self.padding//2
            x2 = x1  - 5
        else:
            x1 = self.width//2 + 9 + self.surface_label2.get_width() + self.padding//2
            x2 = x1  + 5

        y1 = self.height//2

        y2 = y1 + 5

        x3 = x2
        y3 = y1 - 5

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        surface.blit(self.surface_label,
                    (
                        (self.width-self.padding)//2-self.surface_label.get_width(),
                        (self.height-self.surface_label.get_height())//2
                    )
                )
        surface.blit(self.surface_label2,
                    (
                        (self.width + self.padding)//2,
                        (self.height-self.surface_label2.get_height())//2
                    )
                )
        if self.focused:
            self.draw_focused(surface)
        return surface

    def click(self, direction):
        if abs(direction) == 1:
            event = pygame.event.Event(SOUND_EFFECT, message="menu_scroll")
            pygame.event.post(event)
            self.selected += direction
            self.selected %= 2
        elif direction == 2:
            event = pygame.event.Event(SOUND_EFFECT, message="menu_click")
            pygame.event.post(event)
            self.callback()

class BooleanMenuItem(MenuItem):
    def __init__(self, label, value=False, height=-1, width=-1):
        super(BooleanMenuItem, self).__init__(label, height, width)
        self.value = value
        self.label = label
        self.padding = 30
        self.bottom_margin = 0
        self.surface_values = [
            text_renderer.render_menu_item("Disabled", colours.COLOUR_WHITE),
            text_renderer.render_menu_item("Enabled", colours.COLOUR_WHITE),
        ]

        if self.width < 0:
            self.width = max(self.surface_values[0].get_width(), self.surface_label.get_width())*2+self.padding

        if self.height < 0:
            self.height = max(
                max(
                    self.surface_label.get_height(),
                    self.surface_values[0].get_height()
                ), self.surface_values[1].get_height()
            )

    def get_value(self):
        return self.value

    def click(self, direction):
        event = pygame.event.Event(SOUND_EFFECT, message="menu_scroll")
        pygame.event.post(event)
        self.value = not self.value

    def draw_focused(self, surface):
        x1 = self.width//2 + 2
        y1 = self.height//2

        x2 = x1  + 5
        y2 = y1 + 5

        x3 = x2
        y3 = y1 - 5

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])
        value_surface = self.surface_values[int(self.value)]

        x1 = (self.width + self.padding)//2 + value_surface.get_width() + self.padding//2 + 7
        x2 = x1  - 5
        x3 = x2

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        value_surface = self.surface_values[int(self.value)]

        surface.blit(self.surface_label,
                    (
                        (self.width-self.padding)//2-self.surface_label.get_width(),
                        (self.height-self.surface_label.get_height())//2
                    )
                )
        surface.blit(value_surface,
                    (
                        (self.width + self.padding)//2,
                        (self.height-value_surface.get_height())//2
                    )
                )

        if self.focused:
            self.draw_focused(surface)

        return surface

class MultiOptionMenuItem(MenuItem):
    def __init__(self, label, options, selected=0, height=-1, width=-1):
        super(MultiOptionMenuItem, self).__init__(label, height, width)
        self.options  = options
        self.selected = selected
        self.padding  = 30
        self.bottom_margin = 0
        self.label    = label

        max_item_width = 0
        max_item_height = 0
        self.surface_values = []
        for item in options:
            rendered = text_renderer.render_menu_item(item, colours.COLOUR_WHITE)
            self.surface_values.append( rendered )

            if rendered.get_width() > max_item_width:
                max_item_width = rendered.get_width()
            if rendered.get_height() > max_item_height:
                max_item_height = rendered.get_height()

        self.width = max(max_item_width, self.surface_label.get_width())*2 + self.padding
        self.height = max(max_item_height, self.surface_label.get_height())

    def get_value(self):
        return self.selected

    def click(self, direction):
        event = pygame.event.Event(SOUND_EFFECT, message="menu_scroll")
        pygame.event.post(event)
        self.selected += direction//abs(direction)
        self.selected %= len(self.options)

    def draw_focused(self, surface):
        x1 = self.width//2 + 2
        y1 = self.height//2

        x2 = x1  + 5
        y2 = y1 + 5

        x3 = x2
        y3 = y1 - 5

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])
        value_surface = self.surface_values[self.selected]

        x1 = (self.width + self.padding)//2 + value_surface.get_width() + self.padding//2 + 7
        x2 = x1  - 5
        x3 = x2

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        value_surface = self.surface_values[self.selected]

        surface.blit(self.surface_label,
                    (
                        (self.width-self.padding)//2-self.surface_label.get_width(),
                        (self.height-self.surface_label.get_height())//2
                    )
                )
        surface.blit(value_surface,
                    (
                        (self.width + self.padding)//2,
                        (self.height-value_surface.get_height())//2
                    )
                )

        if self.focused:
            self.draw_focused(surface)

        return surface

class SliderMenuItem(MenuItem):
    def __init__(self, label, min_val, max_val, value, callback = None, height=-1, width=-1):
        super(SliderMenuItem, self).__init__(label, height, width)
        self.min_val = min_val
        self.max_val = max_val
        self.value   = value
        self.padding = 30
        self.bottom_margin = 0
        self.slider_width = 200
        self.width = max(self.slider_width, self.surface_label.get_width())*2 + self.padding
        self.slider_marker = pygame.Rect(0, 0, 10, 30)

        self.callback = callback

        self.increment = (max_val-min_val)//10

    def get_value(self):
        return self.value

    def click(self, direction):
        event = pygame.event.Event(SOUND_EFFECT, message="menu_scroll")
        pygame.event.post(event)

        self.value += (self.increment*(direction//abs(direction)))

        if self.value > self.max_val:
            self.value = self.max_val
        elif self.value < self.min_val:
            self.value = self.min_val

        if self.callback != None:
            self.callback(self.value)

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        self.slider_marker.top = (self.height-self.slider_marker.height)//2

        self.slider_marker.centerx  = (self.slider_width - self.slider_marker.width)
        self.slider_marker.centerx *= (float(self.value)/(self.max_val-self.min_val))
        self.slider_marker.centerx += self.width//2 + self.padding//2 + self.slider_marker.width//2

        colour = colours.COLOUR_GREY if self.focused else colours.COLOUR_WHITE
        surface.blit(self.surface_label,
                    (
                        (self.width-self.padding)//2-self.surface_label.get_width(),
                        (self.height-self.surface_label.get_height())//2
                    )
                )
        pygame.draw.line(
                            surface,
                            colours.COLOUR_WHITE,
                            (
                                (self.width+self.padding)//2,
                                self.height//2
                            ),
                            (
                                (self.width+self.padding)//2 + self.slider_width,
                                self.height//2
                            ),
                            5
                )
        pygame.draw.rect(
            surface,
            colour,
            self.slider_marker
        )
        return surface

class ButtonMenuItem:
    def __init__(self, text, callback, height=-1, width=-1):
        self.text = text
        self.callback = callback
        self.bottom_margin = 0
        self.surface = text_renderer.render_menu_item(text, colours.COLOUR_WHITE)

    def render(self):
        return self.surface

class TeamViewer:
    def __init__(self, region, teams=[]):
        self.width = region[0]
        self.height = region[1]
        self.callback = None
        self.teams = teams
        self.selected = 0

        self.header_top    = 0
        self.header_bottom = 45

        self.banners = []
        self.banner_width  = 0
        self.banner_height = 0
        self.team_member_height = 100
        self.team_member_width  = 760
        self.team_member_spacing = 10

        self.move_list_offset =  (self.width - self.team_member_width)//2 + 450
        self.hth_surface = text_renderer.render_text("HTH:", colours.COLOUR_WHITE)
        self.atk_surface = text_renderer.render_text("ATK:", colours.COLOUR_WHITE)
        self.def_surface = text_renderer.render_text("DEF:", colours.COLOUR_WHITE)
        self.spd_surface = text_renderer.render_text("SPD:", colours.COLOUR_WHITE)

        for team in teams:
            self.banners.append(text_renderer.render_menu_item(team.get_short_name(), colours.COLOUR_WHITE))
            if self.banners[-1].get_width() > self.banner_width:
                self.banner_width = self.banners[-1].get_width()
            if self.banners[-1].get_height() > self.banner_height:
                self.banner_height = self.banners[-1].get_height()

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        if len(self.teams) == 0:
            counter = text_renderer.render_menu_item("0/0", colours.COLOUR_WHITE)
            surface.blit(counter, (self.width-counter.get_width()-30, (self.header_bottom-counter.get_height())//2))
            return surface

        counter = text_renderer.render_menu_item("{}/{}".format(self.selected+1, len(self.teams)), colours.COLOUR_WHITE)
        surface.blit(counter, ((self.width+self.team_member_width)//2 - counter.get_width(), (self.header_bottom-counter.get_height())//2))

        banner = self.banners[self.selected]
        surface.blit(banner, ((self.width-banner.get_width())//2, (self.header_bottom-counter.get_height())//2))

        x1 = (self.width-self.banner_width)//2 - 15
        y1 = self.header_bottom//2

        x2 = x1  + 5
        y2 = y1 + 5

        x3 = x2
        y3 = y1 - 5

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])

        x1 = (self.width+self.banner_width)//2 + 15
        x2 = x1  - 5
        x3 = x2

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])

        for i in range(len(self.teams[self.selected])):
            self.render_team_member(surface, self.teams[self.selected][i], i*(self.team_member_height+self.team_member_spacing) + self.header_bottom)

        return surface

    def render_team_member(self, surface, team_member, v_offset):
        images = ImageManager()

        h_offset = (self.width-self.team_member_width)//2
        name = text_renderer.render_text(team_member.get_short_name(), colours.COLOUR_WHITE)
        surface.blit(name, (h_offset + self.team_member_height + 10, v_offset))
        surface.blit(self.hth_surface, (h_offset + self.team_member_height + 10, v_offset+self.team_member_height-60))

        surface.blit(self.hth_surface, (h_offset + self.team_member_height + 10, v_offset+self.team_member_height-60))
        stat_val = text_renderer.render_text(str(team_member.cur_hp), colours.COLOUR_WHITE)
        surface.blit(stat_val, (h_offset + self.team_member_height + 80, v_offset+self.team_member_height-60))

        surface.blit(self.atk_surface, (h_offset + self.team_member_height + 160, v_offset+self.team_member_height-60))
        stat_val = text_renderer.render_text(str(team_member.get_stat("attack")), colours.COLOUR_WHITE)
        surface.blit(stat_val, (h_offset + self.team_member_height + 230, v_offset+self.team_member_height-60))

        surface.blit(self.def_surface, (h_offset + self.team_member_height + 10, v_offset+self.team_member_height-30))
        stat_val = text_renderer.render_text(str(team_member.get_stat("defense")), colours.COLOUR_WHITE)
        surface.blit(stat_val, (h_offset + self.team_member_height + 80, v_offset+self.team_member_height-30))

        surface.blit(self.spd_surface, (h_offset + self.team_member_height + 160, v_offset+self.team_member_height-30))
        stat_val = text_renderer.render_text(str(team_member.get_stat("speed")), colours.COLOUR_WHITE)
        surface.blit(stat_val, (h_offset + self.team_member_height + 230, v_offset+self.team_member_height-30))

        icon = images.get_tile("{}_mage".format(team_member.element.name.lower()), 0, 0)
        surface.blit(icon, (h_offset, v_offset))
        for i in range(len(team_member.spells)):
            spell_val = text_renderer.render_text("{}. {}".format(i+1, team_member.spells[i]), colours.COLOUR_WHITE)
            surface.blit(spell_val, (self.move_list_offset, v_offset+i*23))

        pygame.draw.line(surface, colours.COLOUR_WHITE, (self.move_list_offset-10, v_offset), (self.move_list_offset-10, v_offset+self.team_member_height))
        pygame.draw.line(surface, colours.COLOUR_WHITE, (h_offset+ self.team_member_height, v_offset), (h_offset + self.team_member_height, v_offset+self.team_member_height))
        pygame.draw.rect(surface, colours.COLOUR_WHITE, ((self.width-self.team_member_width)//2, v_offset, self.team_member_width+1, self.team_member_height+1), 1)
        return

    def move_selection(self, distance):
        if distance == 3:
            event = pygame.event.Event(SOUND_EFFECT, message="menu_click")
            pygame.event.post(event)
            self.quit()
        else:
            event = pygame.event.Event(SOUND_EFFECT, message="menu_move")
            pygame.event.post(event)
            if len(self.teams) == 0:
                return
            self.selected += distance
            self.selected %= len(self.teams)

    def register_finished_callback(self, callback):
        self.callback = callback

    def quit(self):
        if self.callback != None:
            self.callback()

class SettingsMenu:
    def __init__(self, settings):
        self.settings = settings
        self.selected = 0
        self.valid_resolutions = ["{} x {}".format(item['width'], item['height']) for item in settings['valid_resolutions'] ]
        self.spacing_margin = 25
        self.padding = 10

        self.sound_enabled = BooleanMenuItem("Sound", self.settings['sound']['sound_enabled'])
        self.sound_volume = SliderMenuItem("Sound Volume", 0, 100, self.settings['sound']['sound_volume']*100, self.preview_sound_change)
        self.sound_volume.bottom_margin = self.spacing_margin

        self.music_enabled = BooleanMenuItem("Music", self.settings['sound']['music_enabled'])
        self.music_volume = SliderMenuItem("Music Volume", 0, 100, self.settings['sound']['music_volume']*100, self.preview_music_change)
        self.music_volume.bottom_margin = self.spacing_margin

        self.fullscreen = BooleanMenuItem("Fullscreen", self.settings['screen']['fullscreen'])
        self.resolution = MultiOptionMenuItem("Resolution", self.valid_resolutions, self.settings['screen']['resolution'])
        self.resolution.bottom_margin = self.spacing_margin

        self.finished_choice = ChoiceMenuItem("Apply", "Cancel", self.finished)

        self.sound_manager = SoundManager()
        self.music_manager = MusicManager()
        self.items = [
            self.sound_enabled,
            self.sound_volume,
            self.music_enabled,
            self.music_volume,
            self.fullscreen,
            self.resolution,
            self.finished_choice
        ]

        self.callback = None
        self.done = False

        max_height = 0
        self.width = 0
        for item in self.items:
            if item.get_height() > max_height:
                max_height = item.get_height()
            if item.get_width() > self.width:
                self.width = item.get_width()

        self.height = (max_height+self.padding)*(len(self.items)) - self.padding
        for item in self.items:
            self.height += item.bottom_margin
            item.set_height(max_height)
            item.set_width(self.width)

        self.items[self.selected].set_focused(True)

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        offset = 0
        for i in range(len(self.items)):
            item_surface = self.items[i].render()
            surface.blit(item_surface, (
                0,
                offset
            ))
            offset += self.items[i].get_height()+self.padding+self.items[i].bottom_margin

        return surface

    def preview_sound_change(self, volume):
        self.sound_manager.set_volume(volume/100.0)

    def preview_music_change(self, volume):
        self.music_manager.set_music_volume(volume/100.0)

    def move_selection(self, distance):
        event = pygame.event.Event(SOUND_EFFECT, message="menu_move")
        pygame.event.post(event)
        self.items[self.selected].set_focused(False)
        self.selected += distance//abs(distance)
        self.selected %= len(self.items)
        self.items[self.selected].set_focused(True)

    def click_selected(self, direction):
        if direction == 3:
            self.quit()
        else:
            self.items[self.selected].click(direction)

    def register_finished_callback(self, callback):
        self.callback = callback

    def quit(self):
        self.finished_choice.set_value(1)
        self.finished_choice.click(2)

    def finished(self):
        if self.finished_choice.get_value() == 0:
            self.settings['sound']['sound_enabled'] = self.sound_enabled.get_value()
            self.settings['sound']['sound_volume'] = self.sound_volume.get_value()/100.0
            self.settings['sound']['music_enabled'] = self.music_enabled.get_value()
            self.settings['sound']['music_volume'] = self.music_volume.get_value()/100.0
            self.settings['screen']['fullscreen'] = self.fullscreen.get_value()
            self.settings['screen']['resolution'] = self.resolution.get_value()
            
        event = pygame.event.Event(SETTINGS_UPDATED)
        pygame.event.post(event)

        if self.callback != None:
            self.callback()

class Menu:
    def __init__(self, items):
        self.items = items
        self.selected = 0

        self.item_height = 0
        self.item_width  = 0

        self.padding_bottom = 17

        for item in items:
            if item.surface.get_height() > self.item_height:
                self.item_height = item.surface.get_height()
            if item.surface.get_width() > self.item_width:
                self.item_width = item.surface.get_width()
        self.total_height = self.item_height + self.padding_bottom

        self.surface = pygame.Surface((self.item_width + 15, self.total_height*len(items)))

        for i in range(len(items)):
            y = i*self.total_height
            x = (self.item_width - items[i].surface.get_width())
            self.surface.blit(items[i].surface, (x,y))

    def move_selection(self, distance):
        event = pygame.event.Event(SOUND_EFFECT, message="menu_move")
        pygame.event.post(event)
        self.selected += distance
        self.selected %= len(self.items)

    def get_menu_surface(self):
        return self.surface

    def render(self):
        surface = self.surface.copy()

        y1 = self.selected * self.total_height + (self.total_height-12)/2
        x1 = self.surface.get_width() - 7
        x2 = x1 + 5
        y2 = y1 - 5
        x3 = x1 + 5
        y3 = y1 + 5

        pygame.draw.polygon(surface, colours.COLOUR_WHITE,[(x1,y1), (x2,y2), (x3,y3)])
        return surface

    def click_selected(self):
        event = pygame.event.Event(SOUND_EFFECT, message="menu_click")
        pygame.event.post(event)
        self.items[self.selected].callback()
