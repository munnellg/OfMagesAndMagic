import pygame
import os
from app.resources.directories import FONT_ALEX_BRUSH
from app.resources import colours

pygame.font.init()
title_font = pygame.font.Font(FONT_ALEX_BRUSH, 84)
menu_item_font = pygame.font.SysFont('serif', 32)
huge_font = pygame.font.SysFont('serif', 64)
large_font = pygame.font.SysFont('serif', 48)
regular_font = pygame.font.SysFont('serif', 24)


def render_title(text, colour = colours.COLOUR_AMLSERVINYOUR):
    return title_font.render(text, 1, colour)

def render_menu_item(text, colour = colours.COLOUR_AMLSERVINYOUR):
    return menu_item_font.render(text, 1, colour)

def render_huge_text(text, colour = colours.COLOUR_AMLSERVINYOUR):
    return huge_font.render(text, 1, colour)

def render_large_text(text, colour = colours.COLOUR_AMLSERVINYOUR):
    return large_font.render(text, 1, colour)

def render_text(text, colour = colours.COLOUR_AMLSERVINYOUR ):
    return regular_font.render(text, 1, colour)

def render_text_wrapped(surface, text, rect, color = colours.COLOUR_AMLSERVINYOUR, aa=True):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = regular_font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while self.regular_font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        image = regular_font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return y
