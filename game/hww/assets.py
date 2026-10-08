"""Loads the exported art: sprite sheets (with their JSON row names), the font and the arena layers."""
import json
import os

import pygame

from .settings import ARENA_DIR, FACINGS, GAME_DIR, SPRITES_DIR

SCREEN_ART = os.path.join(GAME_DIR, "assets", "screens")


def hex_rgb(c):
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


BIGHEAD_DIR = os.path.join(GAME_DIR, "assets", "bighead")
STYLE = {"dir": SPRITES_DIR}        # the HVGE-HEDS secret code points this at BIGHEAD_DIR


class SoloSheet:
    """One wrestler's (or the ref's) solo sheet: rows = moves, columns = 4 facings x 2 frames."""

    def __init__(self, who, folder=None):
        folder = folder or STYLE["dir"]
        meta = json.load(open(os.path.join(folder, f"{who}_sheets.json")))["solo"]
        self.who = who
        self.cw, self.ch = meta["cell"]
        self.feet = tuple(meta["feet"])
        self.rows = meta["rows"]
        sheet = pygame.image.load(os.path.join(folder, f"{who}_solo.png")).convert_alpha()
        self.cells = {}
        for r, move in enumerate(self.rows):
            for f, face in enumerate(FACINGS):
                for k in range(2):
                    rect = pygame.Rect((f * 2 + k) * self.cw, r * self.ch, self.cw, self.ch)
                    self.cells[move, face, k] = sheet.subsurface(rect)

    def draw(self, surf, move, face, frame, feet_xy):
        """draw so the sprite's feet land on feet_xy (screen pixels)."""
        img = self.cells[move, face, frame % 2]
        surf.blit(img, (round(feet_xy[0]) - self.feet[0], round(feet_xy[1]) - self.feet[1]))


class PairSheet:
    """Two-person moves for one attacker on one victim: rows = moves, columns = 4 facings x 2 frames (96x96 cells).
    The attacker's feet sit at (48, 70) in every cell."""

    def __init__(self, att, vic, folder=None):
        folder = folder or STYLE["dir"]
        meta = json.load(open(os.path.join(folder, f"{att}_sheets.json")))["pairs"]
        self.cw, self.ch = meta["cell"]
        self.feet = tuple(meta["attacker_feet"])
        self.rows = meta["rows"]
        self.sheet = pygame.image.load(os.path.join(folder, f"{att}_vs_{vic}_pairs.png")).convert_alpha()

    def draw(self, surf, move, face, frame, feet_xy):
        r = self.rows.index(move)
        f = FACINGS.index(face)
        src = pygame.Rect((f * 2 + frame % 2) * self.cw, r * self.ch, self.cw, self.ch)
        surf.blit(self.sheet, (round(feet_xy[0]) - self.feet[0], round(feet_xy[1]) - self.feet[1]), src)


class Pairs:
    """Loads each attacker-vs-victim sheet the first time it's needed."""

    def __init__(self):
        self.cache = {}

    def get(self, att, vic):
        key = (STYLE["dir"], att, vic)
        if key not in self.cache:
            self.cache[key] = PairSheet(att, vic)
        return self.cache[key]


def set_big_heads(on, sheets):
    """switch every sprite to the big-head sheets (or back); `sheets` is the shared who -> SoloSheet dict."""
    STYLE["dir"] = BIGHEAD_DIR if on else SPRITES_DIR
    for who in list(sheets):
        sheets[who] = SoloSheet(who)


class Arena:
    """An arena as two 8-frame strips: the back (crowd, mats, ring) and the front ropes.
    With fighters=(player, cpu), the crowd's signs show that matchup (tools/build_arena_layers.py)."""
    FRAMES = 8

    def __init__(self, number, fighters=None):
        self.number = number
        name = f"arena{number}_back.png"
        if fighters:
            matchup = f"arena{number}_{fighters[0]}_vs_{fighters[1]}_back.png"
            if os.path.exists(os.path.join(ARENA_DIR, matchup)):
                name = matchup
        back = pygame.image.load(os.path.join(ARENA_DIR, name)).convert()
        front = pygame.image.load(os.path.join(ARENA_DIR, f"arena{number}_front.png")).convert_alpha()
        w, h = back.get_width() // self.FRAMES, back.get_height()
        self.back = [back.subsurface((i * w, 0, w, h)) for i in range(self.FRAMES)]
        self.front = [front.subsurface((i * w, 0, w, h)) for i in range(self.FRAMES)]


class Arenas(dict):
    """the three arenas (number -> Arena, plain crowd), plus each matchup's crowd loaded when first needed."""

    def __init__(self, numbers=(1, 2, 4)):
        super().__init__({n: Arena(n) for n in numbers})
        self.matchups = {}

    def for_match(self, number, p1, p2):
        key = (number, p1, p2)
        if key not in self.matchups:
            self.matchups[key] = Arena(number, (p1, p2))
        return self.matchups[key]


class Font:
    """The 8x8 NES font (white on transparent), tinted to any colour on demand."""

    def __init__(self):
        # the game's full sheet (tools/build_screen_assets.py) has a few more symbols than the exported one
        full = os.path.join(SCREEN_ART, "font_8x8_full")
        base = full if os.path.exists(full + ".json") else os.path.join(SPRITES_DIR, "font_8x8")
        meta = json.load(open(base + ".json"))
        self.cw, self.ch = meta["cell"]
        self.cols = meta["columns"]
        self.order = meta["order"]
        self.white = pygame.image.load(base + ".png").convert_alpha()
        self.tinted = {}

    def _sheet(self, color):
        if color not in self.tinted:
            s = self.white.copy()
            s.fill(hex_rgb(color) + (255,), special_flags=pygame.BLEND_RGBA_MULT)
            self.tinted[color] = s
        return self.tinted[color]

    def width(self, text):
        return len(text) * self.cw

    def draw_big(self, surf, x, y, text, color="#FCFCFC", scale=2, shadow="#000000"):
        """text at a whole-number scale, with a shadow (pin counts, DING!, VS)."""
        small = pygame.Surface((self.width(text) + 1, self.ch + 1), pygame.SRCALPHA)
        self.draw(small, 0, 0, text, color, shadow=shadow)
        surf.blit(pygame.transform.scale(small, (small.get_width() * scale, small.get_height() * scale)), (x, y))

    def draw(self, surf, x, y, text, color="#FCFCFC", shadow=None):
        if shadow:
            self.draw(surf, x + 1, y + 1, text, shadow)
        sheet = self._sheet(color)
        for i, ch in enumerate(text.upper()):
            k = self.order.find(ch)
            if k < 0:
                k = self.order.find("?")
            if ch == " ":
                continue
            src = pygame.Rect((k % self.cols) * self.cw, (k // self.cols) * self.ch, self.cw, self.ch)
            surf.blit(sheet, (x + i * self.cw, y), src)
