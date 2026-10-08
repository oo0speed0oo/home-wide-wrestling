"""The screens around the matches (layouts from export/source/screens.py, screens2.py, select_screen.py).

Each screen has update(c) and draw(surf). The Game (game.py) decides what comes next.
Buttons on every screen: arrows move, A or Enter picks, S goes back.
"""
import math
import os
import random

import pygame

from . import game_text, ui
from .assets import hex_rgb
from .profiles import NAME2, ORDER, QUOTE, STATS, TAPE, TITLE, wrap
from .settings import GAME_DIR, HUD_COL, SCREEN_H, SCREEN_W, SHORT_NAME, SPRITES_DIR
from .ui import GREY, WHITE, YELLOW, arrow, blink, box, center

SCREEN_ART = os.path.join(GAME_DIR, "assets", "screens")
STEP = 9                    # game frames per "frame" of the art's animations (they were drawn at ~150 ms)
LEVELS = ("EASY", "MEDIUM", "HARD")
MENU = ("1 PLAYER", "VS MODE", "PASSWORD", "HOW TO PLAY")


class Art:
    """everything the screens draw with, loaded once."""

    def __init__(self, font, sheets, arenas):
        self.font, self.sheets, self.arenas = font, sheets, arenas
        self.logo = pygame.image.load(os.path.join(SCREEN_ART, "logo.png")).convert_alpha()
        self.title_bg = ui.Strip(os.path.join(SCREEN_ART, "title_bg.png"), 30)
        strip = pygame.image.load(os.path.join(SPRITES_DIR, "portraits_80x72.png")).convert_alpha()
        self.portrait = {who: strip.subsurface((i * 80, 0, 80, 72)) for i, who in enumerate(ORDER)}
        self.mini = {who: pygame.transform.scale(p, (40, 36)) for who, p in self.portrait.items()}
        self.thumb = {n: pygame.transform.scale(a.back[0].subsurface((0, 0, 256, 216)), (96, 81))
                      for n, a in arenas.items()}
        self._entrances = {}

    def entrance(self, who):
        if who not in self._entrances:
            self._entrances[who] = ui.Strip(os.path.join(SCREEN_ART, f"entrance_{who}.png"), 70)
        return self._entrances[who]


def pressed_ok(c):
    return c.was_pressed("a") or c.was_pressed("start")


def menu_move(c, choice, n):
    if c.was_pressed("up"):
        return (choice - 1) % n, True
    if c.was_pressed("down"):
        return (choice + 1) % n, True
    return choice, False


# ---------------------------------------------------------------------------------------------- title
class Title:
    """logo, searchlights, the four stars on a stage. PUSH START, then the menu, then (1 PLAYER) difficulty."""
    music = "menu"

    def __init__(self, game, start_at_menu=False):
        self.g = game
        self.tick = 0
        self.stage = "menu" if start_at_menu else "press"
        self.choice = 0
        self.level = 1

    def update(self, c):
        self.tick += 1
        snd = self.g.sound
        if self.stage == "press":
            if c.was_pressed("start") or c.was_pressed("a"):
                snd.play("select")
                self.stage = "menu"
            return
        if self.stage == "menu":
            self.choice, moved = menu_move(c, self.choice, len(MENU))
            if moved:
                snd.play("blip")
            if c.was_pressed("s"):
                self.stage = "press"
            elif pressed_ok(c):
                snd.play("select")
                pick = MENU[self.choice]
                if pick == "1 PLAYER":
                    self.stage = "difficulty"
                elif pick == "VS MODE":
                    self.g.go(VSSetup(self.g))
                elif pick == "PASSWORD":
                    self.g.go(Password(self.g))
                else:
                    self.g.go(HowToPlay(self.g))
            return
        # difficulty
        self.level, moved = menu_move(c, self.level, len(LEVELS))
        if moved:
            snd.play("blip")
        if c.was_pressed("s"):
            self.stage = "menu"
        elif pressed_ok(c):
            snd.play("select")
            self.g.go(Select(self.g, lambda who: self.g.start_run(who, LEVELS[self.level], 1)))

    def draw(self, surf):
        f = self.tick // STEP
        font = self.g.art.font
        surf.blit(self.g.art.title_bg[f % 30], (0, 0))
        logo = self.g.art.logo
        surf.blit(logo, ((SCREEN_W - logo.get_width()) // 2, 12))
        banner(surf, font, 12 + logo.get_height() + 2)
        pygame.draw.rect(surf, hex_rgb("#3C3C3C"), (24, 146, 209, 4))          # the stage
        for i, (who, face) in enumerate((("mike", "down-right"), ("stew", "down-right"), ("jim", "down-left"),
                                         ("niko", "down-left"))):
            self.g.art.sheets[who].draw(surf, "victory", face, f // 3 + i, (56 + i * 48, 146))
        if self.stage == "press":
            if (f // 3) % 2 == 0:
                center(surf, font, 162, "PUSH START")
        else:
            for i, t in enumerate(MENU):
                font.draw(surf, 92, 155 + i * 10, t)
            arrow(surf, 80, 156 + self.choice * 10)
        for i, t in enumerate(("TM AND @ 1990", "BEST FRIEND GAMES LTD.", "LICENSED BY", "FRIENDS OF JAPAN INC.")):
            center(surf, font, 198 + i * 9, t, "#BCBCBC" if i < 2 else GREY)
        if self.stage == "difficulty":
            ui.dim(surf)
            box(surf, 64, 92, 192, 168)
            center(surf, font, 102, "DIFFICULTY", YELLOW)
            for i, t in enumerate(LEVELS):
                font.draw(surf, 100, 120 + i * 14, t)
            arrow(surf, 88, 121 + self.level * 14)


def banner(surf, font, y, text="HOME WIDE WRESTLING"):
    w = font.width(text) + 24
    x0 = (SCREEN_W - w) // 2
    pygame.draw.rect(surf, hex_rgb("#A81000"), (x0, y, w + 1, 14))
    pygame.draw.line(surf, hex_rgb("#F87858"), (x0, y), (x0 + w, y))
    pygame.draw.line(surf, (0, 0, 0), (x0, y + 13), (x0 + w, y + 13))
    center(surf, font, y + 3, text, WHITE, "#000000")


class DifficultyPick:
    """the difficulty box on its own (after a password)."""
    music = "menu"

    def __init__(self, game, then):
        self.g, self.then = game, then
        self.title = Title(game, start_at_menu=True)
        self.title.stage = "difficulty"

    def update(self, c):
        self.title.tick += 1
        t = self.title
        t.level, moved = menu_move(c, t.level, len(LEVELS))
        if moved:
            self.g.sound.play("blip")
        if c.was_pressed("s"):
            self.g.go(Title(self.g, start_at_menu=True))
        elif pressed_ok(c):
            self.g.sound.play("select")
            self.then(LEVELS[t.level])

    def draw(self, surf):
        self.title.draw(surf)


# ---------------------------------------------------------------------------------------------- select
SLOTS = {"mike": (24, 18), "stew": (152, 18), "jim": (24, 120), "niko": (152, 120)}


class Select:
    """2x2 portraits with a blinking frame. A picks, S shows his profile card (S again to go back)."""
    music = "menu"

    def __init__(self, game, then, back=None):
        self.g, self.then, self.back = game, then, back
        self.tick = 0
        self.sel = 0
        self.profile = None         # frames since the profile card opened

    def update(self, c):
        self.tick += 1
        snd = self.g.sound
        if self.profile is not None:
            self.profile += 1
            if c.was_pressed("s") or c.was_pressed("start") or c.was_pressed("a"):
                self.profile = None
            return
        col, row = self.sel % 2, self.sel // 2
        if c.was_pressed("left") or c.was_pressed("right"):
            col = 1 - col
        if c.was_pressed("up") or c.was_pressed("down"):
            row = 1 - row
        if col + row * 2 != self.sel:
            self.sel = col + row * 2
            snd.play("blip")
        if pressed_ok(c):
            snd.play("select")
            self.then(ORDER[self.sel])
        elif c.was_pressed("s"):
            self.profile = 0
        elif c.was_pressed("d"):
            self.g.go(self.back() if self.back else Title(self.g, start_at_menu=True))

    def draw(self, surf):
        font = self.g.art.font
        surf.fill((0, 0, 0))
        who_sel = ORDER[self.sel]
        if self.profile is not None:
            draw_profile(surf, self.g.art, who_sel, 1 + self.profile // 6)
            return
        center(surf, font, 5, "SELECT YOUR WRESTLER", YELLOW)
        for k in ORDER:
            x, y = SLOTS[k]
            surf.blit(self.g.art.portrait[k], (x, y))
            col = HUD_COL[k] if k == who_sel else WHITE
            for i, line in enumerate(NAME2[k]):
                font.draw(surf, x + 40 - font.width(line) // 2, y + 76 + i * 9, line, col)
            if k == who_sel and blink(self.tick, 9):
                pygame.draw.rect(surf, hex_rgb(WHITE), (x - 6, y - 3, 92, 100), 2)
        center(surf, font, 226, "A:PICK  S:PROFILE", GREY)


def draw_profile(surf, art, k, rows_shown):
    font = art.font
    surf.blit(art.portrait[k], ((SCREEN_W - 80) // 2, 6))
    center(surf, font, 84, TITLE[k], HUD_COL[k])
    y = 102
    for i, (lab, val) in enumerate(STATS[k]):
        if i >= rows_shown:
            break
        lines = wrap(val, 15)
        font.draw(surf, 104 - font.width(lab), y, lab)
        font.draw(surf, 108, y, ":")
        for j, ln in enumerate(lines):
            font.draw(surf, 124, y + j * 10, ln)
        y += 10 * len(lines) + 3
    if rows_shown > len(STATS[k]):
        qy = max(y + 8, 204 if "|" in QUOTE[k] else 212)
        for j, ln in enumerate(QUOTE[k].split("|")):
            center(surf, font, qy + j * 10, ln, YELLOW)


# ---------------------------------------------------------------------------------------------- VS mode setup
class VSSetup:
    """YOU / CPU / ARENA / LEVEL / START. Left and right change a row. (VS PLAYER is hidden in v1.)"""
    music = "menu"
    ARENAS = (1, 2, 4)

    def __init__(self, game, you="mike", cpu="jim", arena=1, level=1):
        self.g = game
        self.you, self.cpu, self.arena, self.level = you, cpu, arena, level
        self.row = 0
        self.tick = 0

    def cycle(self, who, step, skip):
        i = ORDER.index(who)
        while True:
            i = (i + step) % len(ORDER)
            if ORDER[i] != skip:         # no mirror matches
                return ORDER[i]

    def update(self, c):
        self.tick += 1
        snd = self.g.sound
        self.row, moved = menu_move(c, self.row, 5)
        step = (1 if c.was_pressed("right") else 0) - (1 if c.was_pressed("left") else 0)
        if step:
            if self.row == 0:
                self.you = self.cycle(self.you, step, self.cpu)
            elif self.row == 1:
                self.cpu = self.cycle(self.cpu, step, self.you)
            elif self.row == 2:
                a = self.ARENAS
                self.arena = a[(a.index(self.arena) + step) % len(a)]
            elif self.row == 3:
                self.level = (self.level + step) % len(LEVELS)
        if moved or step:
            snd.play("blip")
        if c.was_pressed("s"):
            self.g.go(Title(self.g, start_at_menu=True))
        elif pressed_ok(c) and self.row == 4:
            snd.play("select")
            self.g.start_vs(self)

    def draw(self, surf):
        font, art = self.g.art.font, self.g.art
        surf.fill((0, 0, 0))
        center(surf, font, 6, "VS MODE", YELLOW)
        surf.blit(art.mini[self.you], (36, 22))
        surf.blit(art.mini[self.cpu], (180, 22))
        font.draw(surf, 56 - font.width(SHORT_NAME[self.you]) // 2, 62, SHORT_NAME[self.you], HUD_COL[self.you])
        font.draw(surf, 200 - font.width(SHORT_NAME[self.cpu]) // 2, 62, SHORT_NAME[self.cpu], HUD_COL[self.cpu])
        center(surf, font, 34, "VS", "#F83800", scale=2)
        rows = [("YOU", SHORT_NAME[self.you]), ("CPU", SHORT_NAME[self.cpu]), ("ARENA", str(self.arena)),
                ("LEVEL", LEVELS[self.level]), ("START", None)]
        for i, (lab, val) in enumerate(rows):
            y = 80 + i * 12
            font.draw(surf, 48, y, lab, YELLOW if i == self.row else WHITE)
            if val is not None:
                font.draw(surf, 112, y, "<", GREY)
                font.draw(surf, 124, y, val)
                font.draw(surf, 124 + font.width(val) + 4, y, ">", GREY)
        arrow(surf, 36, 81 + self.row * 12)
        pygame.draw.rect(surf, hex_rgb(WHITE), (78, 146, 100, 85), 1)
        surf.blit(art.thumb[self.arena], (80, 148))


# ---------------------------------------------------------------------------------------------- VS screen
class VSScreen:
    """split backdrop in both colours, portraits slide in, a flashing VS, the tale of the tape, FIGHT!"""
    music = "menu"
    LENGTH = 22 * STEP

    def __init__(self, game, p1, p2, header, then):
        self.g, self.p1, self.p2, self.header, self.then = game, p1, p2, header, then
        self.tick = 0

    def update(self, c):
        self.tick += 1
        if self.tick == 6 * STEP:
            self.g.sound.play("slam")
        if self.tick >= self.LENGTH or (self.tick > 20 and pressed_ok(c)):
            self.then()

    def draw(self, surf):
        font, art = self.g.art.font, self.g.art
        f = self.tick // STEP
        p1, p2 = self.p1, self.p2
        surf.fill((0, 0, 0))
        pygame.draw.polygon(surf, shade(HUD_COL[p1], 0.35), [(0, 0), (140, 0), (116, 150), (0, 150)])
        pygame.draw.polygon(surf, shade(HUD_COL[p2], 0.35), [(140, 0), (SCREEN_W, 0), (SCREEN_W, 150), (116, 150)])
        pygame.draw.line(surf, hex_rgb(WHITE), (140, 0), (116, 150), 2)
        center(surf, font, 6, self.header, YELLOW, "#000000")
        slide = max(0, 6 - f) * 16
        surf.blit(art.portrait[p1], (8 - slide, 26))
        surf.blit(pygame.transform.flip(art.portrait[p2], True, False), (SCREEN_W - 88 + slide, 26))
        for i, t in enumerate(NAME2[p1]):
            font.draw(surf, 48 - font.width(t) // 2, 102 + i * 9, t, HUD_COL[p1], "#000000")
        for i, t in enumerate(NAME2[p2]):
            font.draw(surf, SCREEN_W - 48 - font.width(t) // 2, 102 + i * 9, t, HUD_COL[p2], "#000000")
        if f >= 6:
            center(surf, font, 54, "VS", YELLOW if f % 2 else "#F83800", scale=3)
        y = 158
        for lab in ("HEIGHT", "WEIGHT", "RECORD"):
            center(surf, font, y, lab, GREY)
            a, b = TAPE[p1][lab], TAPE[p2][lab]
            font.draw(surf, 12, y, a)
            font.draw(surf, SCREEN_W - 12 - font.width(b), y, b)
            y += 12
        if f >= 8 and f % 4 < 3:
            center(surf, font, 204, "FIGHT!", "#F83800", shadow=YELLOW, scale=2)


def shade(col, k):
    r, g, b = hex_rgb(col)
    return int(r * k), int(g * k), int(b * k)


# ---------------------------------------------------------------------------------------------- entrance
class Entrance:
    """a wrestler's ramp entrance: big screen, pyro, victory pose at the top, down to the ring. A skips."""
    music = None
    TICKS = 7                       # the reels run at about 110 ms a frame

    def __init__(self, game, who, then):
        self.g, self.who, self.then = game, who, then
        self.strip = game.art.entrance(who)
        self.tick = 0

    def update(self, c):
        if self.tick == 0:
            self.g.sound.play("crowd")
        self.tick += 1
        if self.tick == 30 * self.TICKS:
            self.g.sound.play("crowd")      # the pop when he hits his pose
        if self.tick >= len(self.strip) * self.TICKS or (self.tick > 10 and pressed_ok(c)):
            self.then()

    def draw(self, surf):
        surf.blit(self.strip[min(len(self.strip) - 1, self.tick // self.TICKS)], (0, 0))


# ---------------------------------------------------------------------------------------------- results
HOW = {"pin": "PINFALL", "sub": "SUBMISSION", "countout": "COUNT-OUT", "double": "DOUBLE COUNT-OUT"}


def clock(frames):
    s = frames // 60
    return f"{s // 60}:{s % 60:02d}"


class Win:
    """the winner under a spotlight with confetti, his catchphrase, how he won and the time,
    then NEXT OPPONENT (or HOME WIDE CHAMPION! after the last match, or NEW MATCH in VS mode)."""
    music = None

    def __init__(self, game, who, how, frames, next_line, then, score=None):
        self.g, self.who, self.how, self.time, self.next_line, self.then = game, who, how, clock(frames), \
            next_line, then
        self.score = score
        self.tick = 0
        self.spot = pygame.Surface((SCREEN_W, 110), pygame.SRCALPHA)
        for y in range(110):
            for x in range(SCREEN_W):
                if (x + y) % 4 == 0 and abs(x - 128) <= 8 + y * 0.35:
                    self.spot.set_at((x, y), hex_rgb(YELLOW) + (255,))

    def update(self, c):
        self.tick += 1
        if self.tick > 40 and pressed_ok(c):
            self.g.sound.play("select")
            self.then()

    def draw(self, surf):
        font, art = self.g.art.font, self.g.art
        f = self.tick // STEP
        surf.fill((0, 0, 0))
        surf.blit(self.spot, (0, 0))
        rnd = random.Random(7)
        cols = ("#F83800", "#3CBCFC", "#58D854", "#F8D878", "#FCFCFC")
        for i in range(60):                                         # confetti falling
            x = rnd.randrange(SCREEN_W)
            y = (rnd.randrange(SCREEN_H) + self.tick // 3 * (2 + i % 3)) % 150
            surf.set_at((x, y), hex_rgb(cols[i % 5]))
        center(surf, font, 6, f"{TITLE[self.who]} WINS!", HUD_COL[self.who], "#000000")
        surf.blit(art.portrait[self.who], ((SCREEN_W - 80) // 2, 22))
        pygame.draw.rect(surf, hex_rgb("#3C3C3C"), (0, 94, SCREEN_W, 2))
        for j, ln in enumerate(QUOTE[self.who].split("|")):
            center(surf, font, 102 + j * 10, ln, YELLOW)
        rows = [("WIN BY", HOW[self.how]), ("TIME", self.time)]
        if self.score is not None:
            rows.append(("SCORE", f"{self.score:,}"))
        box(surf, 40, 126, 216, 140 + 14 * len(rows))
        for i, (lab, val) in enumerate(rows):
            font.draw(surf, 52, 135 + i * 14, lab, GREY)
            font.draw(surf, 116, 135 + i * 14, val)
        kind, who = self.next_line
        y = 150 + 14 * len(rows)
        if kind == "next":
            center(surf, font, y, "NEXT OPPONENT", GREY)
            center(surf, font, y + 12, TITLE[who], HUD_COL[who])
        elif kind == "champion":
            center(surf, font, y + 4, "HOME WIDE CHAMPION!", YELLOW if f % 2 else WHITE, "#A81000")
        else:
            center(surf, font, y + 4, "NEW MATCH", WHITE)
        if self.tick > 40 and (f // 3) % 2 == 0:
            center(surf, font, 220, "PUSH START")


class Lose:
    """gloomy rain, the winner's portrait and catchphrase, how you lost, GAME OVER and your password."""
    music = None

    def __init__(self, game, winner, how, password, then):
        self.g, self.winner, self.how, self.password, self.then = game, winner, how, password, then
        self.tick = 0

    def update(self, c):
        self.tick += 1
        if self.tick > 60 and pressed_ok(c):
            self.g.sound.play("select")
            self.then()

    def draw(self, surf):
        font, art = self.g.art.font, self.g.art
        f = self.tick // STEP
        surf.fill((0, 0, 0))
        rain = random.Random(11)
        for i in range(50):
            x = rain.randrange(SCREEN_W)
            y = (rain.randrange(SCREEN_H) + self.tick // 3 * 6) % 120
            for k in range(3):
                if 0 <= y + k < 120:
                    surf.set_at(((x - k) % SCREEN_W, y + k), hex_rgb("#24188C"))
        if self.winner:
            center(surf, font, 6, "YOU LOSE...", "#F83800", "#000000")
            surf.blit(art.portrait[self.winner], ((SCREEN_W - 80) // 2, 22))
            for j, ln in enumerate(QUOTE[self.winner].split("|")):
                center(surf, font, 100 + j * 10, ln, HUD_COL[self.winner])
        else:
            center(surf, font, 6, "NOBODY WINS...", "#F83800", "#000000")
        center(surf, font, 126, f"BY {HOW[self.how]}", GREY)
        if f >= 6:
            center(surf, font, 146, "GAME OVER", WHITE if f % 4 < 3 else GREY, "#A81000", scale=2)
        if self.password:
            box(surf, 40, 172, 216, 214)
            center(surf, font, 181, "YOUR PASSWORD", GREY)
            center(surf, font, 196, self.password, YELLOW)


# ---------------------------------------------------------------------------------------------- password
KEYS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"       # no I, O, 0, 1: easy to copy off the TV
DEL, END = len(KEYS), len(KEYS) + 1


class Password:
    """8 characters shown as XXXX-XXXX, a letter grid, DEL and END. A picks, S deletes."""
    music = "menu"

    def __init__(self, game):
        self.g = game
        self.entered = ""
        self.cur = 0
        self.tick = 0
        self.status = None
        self.status_t = 0
        self.after = None

    def move(self, c):
        cur = self.cur
        if cur >= DEL:                              # the bottom row: DEL, END
            if c.was_pressed("left") or c.was_pressed("right"):
                return END if cur == DEL else DEL
            if c.was_pressed("up"):
                return 24 + (2 if cur == DEL else 5)
            return cur
        col, row = cur % 8, cur // 8
        if c.was_pressed("left"):
            col = (col - 1) % 8
        if c.was_pressed("right"):
            col = (col + 1) % 8
        if c.was_pressed("up"):
            row = (row - 1) % 4
        if c.was_pressed("down"):
            if row == 3:
                return DEL if col < 4 else END
            row += 1
        return row * 8 + col

    def update(self, c):
        self.tick += 1
        snd = self.g.sound
        if self.status_t:
            self.status_t -= 1
            if self.status_t == 0 and self.after:
                self.after()
            return
        new = self.move(c)
        if new != self.cur:
            self.cur = new
            snd.play("blip")
        if c.was_pressed("s") or (pressed_ok(c) and self.cur == DEL):
            self.entered = self.entered[:-1]
            snd.play("blip")
        elif c.was_pressed("d"):
            self.g.go(Title(self.g, start_at_menu=True))
        elif pressed_ok(c) and self.cur == END:
            self.check()
        elif pressed_ok(c) and len(self.entered) < 8:
            self.entered += KEYS[self.cur]
            snd.play("blip")
            if len(self.entered) == 8:
                self.cur = END

    def check(self):
        code = self.entered[:4] + "-" + self.entered[4:]
        found = [k for k, v in game_text.PASSWORDS.items() if v == code]
        snd = self.g.sound
        if found:
            who, match_no = found[0]
            self.status = f"PASSWORD OK! MATCH {match_no}"
            snd.play("select")
            self.after = lambda: self.g.go(DifficultyPick(self.g, lambda lvl: self.g.start_run(who, lvl, match_no)))
            self.status_t = 90
        elif code in game_text.SECRETS:
            self.status = "SECRET CODE!"
            snd.play("select")
            snd.play("crowd")
            self.after = lambda: self.g.use_secret(code)
            self.status_t = 90
        else:
            self.status = "WRONG PASSWORD"
            snd.play("blip_error")
            self.after = None
            self.status_t = 60

    def draw(self, surf):
        font = self.g.art.font
        surf.fill((0, 0, 0))
        center(surf, font, 14, "ENTER PASSWORD", YELLOW)
        for i in range(8):
            x = 52 + i * 18 + (8 if i >= 4 else 0)
            pygame.draw.line(surf, hex_rgb(GREY), (x, 52), (x + 9, 52))
            if i < len(self.entered):
                font.draw(surf, x + 1, 42, self.entered[i])
            elif i == len(self.entered) and blink(self.tick, 9):
                pygame.draw.rect(surf, hex_rgb(WHITE), (x, 42, 9, 9))
        font.draw(surf, 124, 42, "-", GREY)
        box(surf, 20, 70, 236, 166)
        for k, ch in enumerate(KEYS):
            cx, cy = 40 + (k % 8) * 24, 84 + (k // 8) * 18
            font.draw(surf, cx, cy, ch, YELLOW if k == self.cur else WHITE)
            if k == self.cur:
                pygame.draw.rect(surf, hex_rgb(YELLOW), (cx - 3, cy - 3, 13, 14), 1)
        for i, t in enumerate(("DEL", "END")):
            font.draw(surf, 72 + i * 88, 178, t, YELLOW if self.cur == DEL + i else WHITE)
        if self.cur >= DEL:
            arrow(surf, 62 + (self.cur - DEL) * 88, 179)
        if self.status:
            ok = "OK" in self.status or "SECRET" in self.status
            center(surf, font, 204, self.status, "#58D854" if ok else "#F83800")
            if not self.status_t:
                self.status = None
        else:
            center(surf, font, 204, "A:PICK  S:DEL", GREY)


# ---------------------------------------------------------------------------------------------- the ending
class Champion:
    """the new champion holds the title belt over his head, fireworks over a packed house, the announcer's call.
    Pre-rendered from export/source/screens2.py (tools/build_screen_assets.py champions)."""
    music = None
    TICKS = 8
    LOOP_FROM = 36

    def __init__(self, game, who, then):
        self.g, self.who, self.then = game, who, then
        self.strip = ui.Strip(os.path.join(SCREEN_ART, f"champion_{who}.png"), 72)
        self.tick = 0

    def update(self, c):
        if self.tick == 0:
            self.g.sound.music("win", loop=False)
            self.g.sound.play("crowd")
        self.tick += 1
        if self.tick % 150 == 0:
            self.g.sound.play("crowd")
        if self.tick > 12 * 60 or (self.tick > 3 * 60 and pressed_ok(c)):
            self.then()

    def draw(self, surf):
        i = self.tick // self.TICKS
        n = len(self.strip)
        if i >= n:
            i = self.LOOP_FROM + (i - n) % (n - self.LOOP_FROM)
        surf.blit(self.strip[i], (0, 0))


CREDITS = [
    ("LOGO", None), ("", None),
    ("STARRING", YELLOW),
    ("MIGHTY MIKE", "#F83800"), ("BIG BEEFY STEW", "#3CBCFC"), ("JIM \"THE GOAT\"", "#58D854"),
    ("NIMBLE NIKO", "#9878F8"), ("", None),
    ("GAME DESIGN", YELLOW), ("MIGHTY MIKE", WHITE), ("", None),
    ("ART, CODE AND MUSIC", YELLOW), ("CLAUDE", WHITE), ("", None),
    ("REFEREE", YELLOW), ("THE REF", WHITE), ("", None),
    ("ANNOUNCER", YELLOW), ("THE VOICE OF HWW", WHITE), ("", None),
    ("SPECIAL THANKS", YELLOW), ("THE FANS", WHITE), ("EVERYONE WHO", WHITE),
    ("NEVER GAVE UP", WHITE), ("", None), ("", None),
    ("TM AND @ 1990", "#BCBCBC"), ("BEST FRIEND GAMES LTD.", "#BCBCBC"), ("LICENSED BY", GREY),
    ("FRIENDS OF JAPAN INC.", GREY), ("", None), ("", None), ("", None),
    ("THANK YOU FOR PLAYING!", YELLOW),
]
LINE = 14


class Credits:
    """scrolling up over twinkling stars, ending on THANK YOU FOR PLAYING! A speeds it up."""
    music = "menu"
    SPEED = 0.45                # pixels a frame

    def __init__(self, game, then):
        self.g, self.then = game, then
        self.scroll = 0.0
        self.tick = 0
        logo_h = game.art.logo.get_height()
        self.length = logo_h + 4 + (len(CREDITS) - 1) * LINE
        self.stop_at = self.length + SCREEN_H // 2 - LINE      # the last line rests in the middle
        self.rest = 0

    def update(self, c):
        self.tick += 1
        if self.scroll < self.stop_at:
            self.scroll = min(self.stop_at, self.scroll + self.SPEED * (4 if c.held["a"] else 1))
            return
        self.rest += 1
        if self.rest > 60 and pressed_ok(c) or self.rest > 6 * 60:
            self.then()

    def draw(self, surf):
        font, logo = self.g.art.font, self.g.art.logo
        surf.fill((0, 0, 0))
        ui.stars(surf, self.tick // STEP, seed=21, n=60)
        y = SCREEN_H - int(self.scroll)
        for text, col in CREDITS:
            if text == "LOGO":
                if -logo.get_height() < y < SCREEN_H:
                    surf.blit(logo, ((SCREEN_W - logo.get_width()) // 2, y))
                y += logo.get_height() + 4
                continue
            if text and -8 < y < SCREEN_H:
                center(surf, font, y, text, col)
            y += LINE


# ---------------------------------------------------------------------------------------------- hall of fame
RANKS = ("1ST", "2ND", "3RD", "4TH", "5TH")
NAME_KEYS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ.-"
SPACE, NDEL, NEND = len(NAME_KEYS), len(NAME_KEYS) + 1, len(NAME_KEYS) + 2


class NameEntry:
    """NEW HIGH SCORE! Up to 10 letters on a letter grid, with SPACE, DEL and END. A picks, S deletes."""
    music = "menu"

    def __init__(self, game, score, then):
        self.g, self.score, self.then = game, score, then
        self.name = ""
        self.cur = 0
        self.tick = 0

    def move(self, c):
        cur = self.cur
        if cur >= SPACE:                             # bottom row: SPACE, DEL, END
            k = cur - SPACE
            if c.was_pressed("left"):
                k = (k - 1) % 3
            if c.was_pressed("right"):
                k = (k + 1) % 3
            if c.was_pressed("up"):
                return 20 + k * 3
            return SPACE + k
        col, row = cur % 10, cur // 10
        if c.was_pressed("left"):
            col = (col - 1) % 10
        if c.was_pressed("right"):
            col = (col + 1) % 10
        if c.was_pressed("up"):
            row = (row - 1) % 3
        if c.was_pressed("down"):
            row += 1
        new = row * 10 + col
        if row >= 3 or new >= len(NAME_KEYS):
            return SPACE + min(2, col // 4)
        return new

    def update(self, c):
        self.tick += 1
        snd = self.g.sound
        new = self.move(c)
        if new != self.cur:
            self.cur = new
            snd.play("blip")
        if c.was_pressed("s") or (pressed_ok(c) and self.cur == NDEL):
            self.name = self.name[:-1]
            snd.play("blip")
        elif pressed_ok(c) and self.cur == NEND:
            snd.play("select")
            self.then(self.name.strip())
        elif pressed_ok(c) and len(self.name) < 10:
            self.name += " " if self.cur == SPACE else NAME_KEYS[self.cur]
            snd.play("blip")
            if len(self.name) == 10:
                self.cur = NEND

    def draw(self, surf):
        font = self.g.art.font
        f = self.tick // STEP
        surf.fill((0, 0, 0))
        center(surf, font, 12, "NEW HIGH SCORE!", YELLOW if f % 2 else WHITE, "#A81000")
        center(surf, font, 28, f"{self.score:,}")
        center(surf, font, 46, "ENTER YOUR NAME", GREY)
        for i in range(10):
            x = 48 + i * 16
            pygame.draw.line(surf, hex_rgb(GREY), (x, 74), (x + 8, 74))
            if i < len(self.name):
                font.draw(surf, x, 64, self.name[i])
            elif i == len(self.name) and blink(self.tick, 9):
                pygame.draw.rect(surf, hex_rgb(WHITE), (x, 64, 8, 8))
        box(surf, 12, 88, 244, 190)
        for k, ch in enumerate(NAME_KEYS):
            cx, cy = 28 + (k % 10) * 21, 102 + (k // 10) * 18
            font.draw(surf, cx, cy, ch, YELLOW if k == self.cur else WHITE)
            if k == self.cur:
                pygame.draw.rect(surf, hex_rgb(YELLOW), (cx - 3, cy - 3, 13, 14), 1)
        for i, t in enumerate(("SPACE", "DEL", "END")):
            font.draw(surf, 40 + i * 70, 168, t, YELLOW if self.cur == SPACE + i else WHITE)
        if self.cur >= SPACE:
            arrow(surf, 30 + (self.cur - SPACE) * 70, 169)
        center(surf, font, 212, "A:PICK  S:DEL", GREY)


class HallOfFameScreen:
    """the top 5 with full names, in each wrestler's colour; a new entry blinks."""
    music = "menu"

    def __init__(self, game, then, new_rank=None):
        self.g, self.then, self.new_rank = game, then, new_rank
        self.tick = 0
        logo = game.art.logo
        self.logo = pygame.transform.scale(logo, (logo.get_width() * 2 // 3, logo.get_height() * 2 // 3))

    def update(self, c):
        self.tick += 1
        if self.tick > 30 and (pressed_ok(c) or c.was_pressed("s")):
            self.then()

    def draw(self, surf):
        font = self.g.art.font
        f = self.tick // STEP
        surf.fill((0, 0, 0))
        ui.stars(surf, f, seed=9, n=40)
        surf.blit(self.logo, ((SCREEN_W - self.logo.get_width()) // 2, 8))
        center(surf, font, 58, "HALL OF FAME", YELLOW, "#A81000")
        font.draw(surf, 24, 80, "RANK", GREY)
        font.draw(surf, 72, 80, "NAME", GREY)
        font.draw(surf, 184, 80, "SCORE", GREY)
        for i, (nm, who, score) in enumerate(self.g.hall.entries):
            y = 98 + i * 18
            col = HUD_COL.get(who, WHITE)
            if self.new_rank == i and f % 2:
                col = WHITE
            font.draw(surf, 32, y, RANKS[i])
            font.draw(surf, 72, y, nm, col)
            s = f"{score:,}"
            font.draw(surf, 232 - font.width(s), y, s)
        if (f // 3) % 2 == 0:
            center(surf, font, 212, "PUSH START")


# ---------------------------------------------------------------------------------------------- how to play
class HowToPlay:
    music = "menu"

    def __init__(self, game):
        self.g = game

    def update(self, c):
        if pressed_ok(c) or c.was_pressed("s"):
            self.g.go(Title(self.g, start_at_menu=True))

    def draw(self, surf):
        font = self.g.art.font
        surf.fill((0, 0, 0))
        center(surf, font, 10, "HOW TO PLAY", YELLOW)
        box(surf, 12, 26, 244, 160)
        for i, (k, v) in enumerate(game_text.HOW_TO_PLAY):
            y = 38 + i * 14
            font.draw(surf, 24, y, k, YELLOW)
            font.draw(surf, 100, y, v)
        lines = ["WIN BY PINFALL, SUBMISSION", "OR COUNT-OUT.", "", "FINISHERS WORK WHEN HE'S", "UNDER 30% ENERGY.",
                 "PAUSE TO SEE YOUR MOVES."]
        for i, t in enumerate(lines):
            center(surf, font, 170 + i * 10, t, "#BCBCBC")
