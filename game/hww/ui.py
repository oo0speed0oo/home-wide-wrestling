"""Drawing helpers shared by the menu screens (the same look as export/source/screens.py)."""
import random

import pygame

from .assets import hex_rgb
from .settings import SCREEN_H, SCREEN_W

YELLOW, WHITE, GREY, DARK = "#F8D878", "#FCFCFC", "#7C7C7C", "#3C3C3C"
_dims = {}


def center(surf, font, y, text, color=WHITE, shadow=None, scale=1):
    if scale == 1:
        font.draw(surf, (SCREEN_W - font.width(text)) // 2, y, text, color, shadow)
    else:
        font.draw_big(surf, (SCREEN_W - font.width(text) * scale) // 2, y, text, color, scale, shadow or "#000000")


def box(surf, x0, y0, x1, y1, fill="#000000", edge=WHITE):
    """NES menu window: filled, white double border."""
    pygame.draw.rect(surf, hex_rgb(fill), (x0, y0, x1 - x0 + 1, y1 - y0 + 1))
    pygame.draw.rect(surf, hex_rgb(edge), (x0 + 1, y0 + 1, x1 - x0 - 1, y1 - y0 - 1), 1)
    pygame.draw.rect(surf, hex_rgb(edge), (x0 + 3, y0 + 3, x1 - x0 - 5, y1 - y0 - 5), 1)


def arrow(surf, x, y, color=YELLOW):
    pygame.draw.polygon(surf, hex_rgb(color), [(x, y), (x, y + 6), (x + 4, y + 3)])


def dim(surf, top=0, bottom=SCREEN_H):
    """NES-style dimming: black on every other pixel."""
    key = (surf.get_width(), bottom - top)
    if key not in _dims:
        d = pygame.Surface(key, pygame.SRCALPHA)
        for y in range(key[1]):
            for x in range((y + top) % 2, key[0], 2):
                d.set_at((x, y), (0, 0, 0, 255))
        _dims[key] = d
    surf.blit(_dims[key], (0, top))


def stars(surf, frame, seed=3, n=40, top=0, bottom=SCREEN_H):
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(SCREEN_W), rnd.randrange(top, bottom)
        if (frame + i) % 6 < 4:
            surf.set_at((x, y), hex_rgb(WHITE if i % 3 else YELLOW))


def blink(tick, period=18):
    """True for half of every period (PUSH START and friends)."""
    return (tick // period) % 2 == 0


class Strip:
    """frames of 256x240 laid out in a grid 10 across (the build tools' output)."""

    def __init__(self, path, count=None):
        sheet = pygame.image.load(path).convert()
        cols = sheet.get_width() // SCREEN_W
        rows = sheet.get_height() // SCREEN_H
        n = count or cols * rows
        self.frames = [sheet.subsurface(((i % cols) * SCREEN_W, (i // cols) * SCREEN_H, SCREEN_W, SCREEN_H))
                       for i in range(n)]

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, i):
        return self.frames[i]
