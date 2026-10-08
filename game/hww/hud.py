"""The match screen's black bars (layout from export/source/hud.py).

Top bar: both names in their colours, 24 energy pips each (the right bar mirrors the left),
         pips flash white under 30%. No clock (decided Oct 1).
Announcer bar: 24x24 portrait whose mouth flaps while 2 lines of up to 27 letters type out;
         a yellow arrow blinks when the line is finished.
"""
import os
import random

import pygame

from . import game_text
from .assets import hex_rgb
from .settings import BOT_Y, FULL_NAME, HUD_COL, SCREEN_H, SCREEN_W, SHORT_NAME, SPRITES_DIR, TOP_H

PIPS = 24
LOW = 0.3
GREY = hex_rgb("#3C3C3C")


def top_bar(surf, font, left, right, tick):
    """left/right: wrestlers (who, energy 0..1)."""
    pygame.draw.rect(surf, (0, 0, 0), (0, 0, SCREEN_W, TOP_H))
    pygame.draw.line(surf, GREY, (0, TOP_H - 1), (SCREEN_W - 1, TOP_H - 1))
    blink = (tick // 8) % 2 == 0
    for w, side in ((left, 0), (right, 1)):
        name = FULL_NAME[w.who] if font.width(FULL_NAME[w.who]) <= 112 else SHORT_NAME[w.who]
        x = 4 if side == 0 else SCREEN_W - 4 - font.width(name)
        font.draw(surf, x, 3, name, HUD_COL[w.who])
        bar_x = 4 if side == 0 else SCREEN_W - 4 - PIPS * 4 + 1
        energy_pips(surf, bar_x, 14, w.energy, HUD_COL[w.who], mirror=side == 1, blink=blink)


def energy_pips(surf, x, y, frac, col, mirror=False, blink=False):
    on = max(0, min(PIPS, round(frac * PIPS)))
    for i in range(PIPS):
        k = PIPS - 1 - i if mirror else i
        if i < on:
            c = hex_rgb("#FCFCFC") if (frac < LOW and blink) else hex_rgb(col)
        else:
            c = GREY
        pygame.draw.rect(surf, c, (x + k * 4, y, 3, 6))


def mash_meter(surf, font, left, right, pos, tick, y=30):
    """tug-of-war bar under the top bar, split in the two colours. pos -1..1: +1 = the left wrestler wins
    (his colour has pushed all the way across)."""
    w, h = 112, 8
    x0 = (SCREEN_W - w) // 2
    pygame.draw.rect(surf, (0, 0, 0), (x0 - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(surf, hex_rgb("#FCFCFC"), (x0 - 1, y - 1, w + 2, h + 2), 1)
    mid = x0 + w // 2 + round(pos * (w // 2 - 2))
    pygame.draw.rect(surf, hex_rgb(HUD_COL[left]), (x0, y, mid - x0, h))
    pygame.draw.rect(surf, hex_rgb(HUD_COL[right]), (mid, y, x0 + w - mid, h))
    pygame.draw.rect(surf, hex_rgb("#FCFCFC"), (mid - 1, y - 3, 2, h + 6))
    if (tick // 8) % 2 == 0:
        t = "MASH!"
        font.draw(surf, (SCREEN_W - font.width(t)) // 2, y + h + 4, t, "#FCFCFC", shadow="#000000")


def one_meter(surf, font, who, prog, label, tick, y=30):
    """one-sided meter (getting up, shaking off a stun, later pins): only you mash, fill to the white line."""
    w, h = 112, 8
    x0 = (SCREEN_W - w) // 2
    pygame.draw.rect(surf, (0, 0, 0), (x0 - 2, y - 2, w + 4, h + 4))
    pygame.draw.rect(surf, hex_rgb("#7C7C7C"), (x0 - 1, y - 1, w + 2, h + 2), 1)
    fill = round(max(0.0, min(1.0, prog)) * (w - 1))
    if fill:
        pygame.draw.rect(surf, hex_rgb(HUD_COL[who]), (x0, y, fill, h))
    pygame.draw.rect(surf, hex_rgb("#FCFCFC"), (x0 + w - 2, y - 3, 2, h + 6))
    if (tick // 8) % 2 == 0:
        font.draw(surf, (SCREEN_W - font.width(label)) // 2, y + h + 4, label, "#FCFCFC", shadow="#000000")


class Announcer:
    """Types out queued lines in the bottom bar, one at a time."""
    TYPE_TICKS = 2          # frames per letter
    HOLD = 110              # frames a finished line stays before the next queued one

    def __init__(self, font):
        self.font = font
        strip = pygame.image.load(os.path.join(SPRITES_DIR, "announcer_24x24_2frames.png")).convert_alpha()
        self.faces = [strip.subsurface((i * 24, 0, 24, 24)) for i in range(2)]
        self.queue = []
        self.line = ("", "")
        self.chars = 0
        self.wait = 0
        self.tick = 0

    def say(self, key, **names):
        """queue a random line for this moment, e.g. say("slam", name="MIGHTY MIKE", opp="JIM THE GOAT")."""
        l1, l2 = random.choice(game_text.ANNOUNCER[key])
        self.queue.append((l1.format(**names)[:27], l2.format(**names)[:27]))

    def say_now(self, key, **names):
        """drop whatever is waiting and say this straight away (big moments)."""
        self.queue.clear()
        self.say(key, **names)
        self.line = self.queue.pop(0)
        self.chars = 0
        self.wait = self.HOLD

    def say_text(self, l1, l2=""):
        """say exact words straight away (test messages)."""
        self.queue.clear()
        self.line = (l1[:27], l2[:27])
        self.chars = 0
        self.wait = self.HOLD

    @property
    def idle(self):
        """nothing typing or waiting, and the last line has been up a while."""
        return not self.typing and not self.queue and self.wait < self.HOLD // 2

    @property
    def total(self):
        return len(self.line[0]) + len(self.line[1])

    @property
    def typing(self):
        return self.chars < self.total

    def update(self):
        """returns True on a frame a letter appears (the match blips)."""
        self.tick += 1
        if self.typing:
            if self.tick % self.TYPE_TICKS == 0:
                self.chars += 1
                while self.typing and self.text_at(self.chars - 1) == " ":
                    self.chars += 1
                return True
            return False
        if self.wait > 0:
            self.wait -= 1
        if self.wait <= 0 and self.queue:
            self.line = self.queue.pop(0)
            self.chars = 0
            self.wait = self.HOLD
        return False

    @property
    def done(self):
        """everything queued has been said."""
        return not self.typing and not self.queue and self.wait <= 0

    def text_at(self, i):
        l1, l2 = self.line
        return (l1 + l2)[i] if 0 <= i < self.total else ""

    def draw(self, surf):
        pygame.draw.rect(surf, (0, 0, 0), (0, BOT_Y, SCREEN_W, SCREEN_H - BOT_Y))
        pygame.draw.line(surf, GREY, (0, BOT_Y), (SCREEN_W - 1, BOT_Y))
        talking = self.typing and (self.tick // 4) % 2 == 0
        surf.blit(self.faces[1 if talking else 0], (4, BOT_Y + 5))
        l1, l2 = self.line
        self.font.draw(surf, 34, BOT_Y + 7, l1[:self.chars])
        self.font.draw(surf, 34, BOT_Y + 19, l2[:max(0, self.chars - len(l1))])
        if self.total and not self.typing and (self.tick // 16) % 2 == 0:
            x, y = SCREEN_W - 10, SCREEN_H - 7
            pygame.draw.polygon(surf, hex_rgb("#F8D878"), [(x, y), (x + 5, y), (x + 2, y + 3)])
