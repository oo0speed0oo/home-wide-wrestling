"""Step 1: one wrestler standing in the ring. Checks the window, the keys and that every sheet loads.

Arrows   turn to face that way (up on the keys = up on the screen)
A / S    previous / next move on the sheet
D        pause / play the 2-frame animation
Tab      next wrestler (and the referee)
1 2 4    arena 1, 2 or 4
Enter    pause
"""
import pygame

from . import ring
from .assets import Arena, hex_rgb
from .settings import ANIM_TICKS, BOT_Y, FULL_NAME, HUD_COL, SCREEN_W, TOP_H, WRESTLERS

CAST = WRESTLERS + ("ref",)


class Viewer:
    def __init__(self, font, sheets, arenas):
        self.font = font
        self.sheets = sheets
        self.arenas = arenas
        self.arena = self.arenas[1]
        self.who = "mike"
        self.move_i = 0
        self.vert, self.horiz = "down", "right"     # facing = down-right
        self.animate = True
        self.paused = False
        self.tick = 0
        self.anim_tick = 0
        self.pos = (ring.RING / 2, ring.RING / 2)  # centre of the mat

    @property
    def sheet(self):
        return self.sheets[self.who]

    @property
    def move(self):
        return self.sheet.rows[self.move_i]

    @property
    def facing(self):
        return f"{self.vert}-{self.horiz}"

    def handle_key(self, key):
        """keys that are only for this test screen."""
        if key == pygame.K_TAB:
            self.who = CAST[(CAST.index(self.who) + 1) % len(CAST)]
            self.move_i = 0
        elif key in (pygame.K_1, pygame.K_2, pygame.K_4):
            self.arena = self.arenas[{pygame.K_1: 1, pygame.K_2: 2, pygame.K_4: 4}[key]]

    def update(self, c):
        if c.was_pressed("start"):
            self.paused = not self.paused
        if self.paused:
            return
        self.tick += 1
        # only the facing changes in step 1; walking comes in step 2
        if c.held["up"]:
            self.vert = "up"
        if c.held["down"]:
            self.vert = "down"
        if c.held["left"]:
            self.horiz = "left"
        if c.held["right"]:
            self.horiz = "right"
        n = len(self.sheet.rows)
        if c.was_pressed("a"):
            self.move_i = (self.move_i - 1) % n
        if c.was_pressed("s"):
            self.move_i = (self.move_i + 1) % n
        if c.was_pressed("d"):
            self.animate = not self.animate
        if self.animate:
            self.anim_tick += 1

    def draw(self, surf):
        crowd_frame = (self.tick // 11) % Arena.FRAMES
        surf.blit(self.arena.back[crowd_frame], (0, 0), (0, -ring.ARENA_SHIFT, SCREEN_W, BOT_Y))
        fx, fy = ring.to_screen(*self.pos)
        pygame.draw.ellipse(surf, hex_rgb("#A4A4A4"), (round(fx) - 7, round(fy) - 2, 15, 5))
        self.sheet.draw(surf, self.move, self.facing, self.anim_tick // ANIM_TICKS, (fx, fy))
        surf.blit(self.arena.front[crowd_frame], (0, 0), (0, -ring.ARENA_SHIFT, SCREEN_W, BOT_Y))
        self.draw_bars(surf)

    def draw_bars(self, surf):
        f = self.font
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, SCREEN_W, TOP_H))
        pygame.draw.line(surf, hex_rgb("#3C3C3C"), (0, TOP_H - 1), (SCREEN_W - 1, TOP_H - 1))
        f.draw(surf, 4, 3, FULL_NAME[self.who], HUD_COL[self.who])
        tag = f"ARENA {self.arena.number}"
        f.draw(surf, SCREEN_W - 4 - f.width(tag), 3, tag, "#BCBCBC")
        f.draw(surf, 4, 13, f"MOVE {self.move_i + 1}/{len(self.sheet.rows)}", "#7C7C7C")

        pygame.draw.rect(surf, (0, 0, 0), (0, BOT_Y, SCREEN_W, 240 - BOT_Y))
        pygame.draw.line(surf, hex_rgb("#3C3C3C"), (0, BOT_Y), (SCREEN_W - 1, BOT_Y))
        f.draw(surf, 4, BOT_Y + 4, self.move[:31], "#F8D878")
        f.draw(surf, 4, BOT_Y + 13, self.facing + ("" if self.animate else "  HOLD"), "#FCFCFC")
        f.draw(surf, 4, BOT_Y + 22, "A/S MOVE D ANIM TAB WHO 124", "#7C7C7C")
        if self.paused and (pygame.time.get_ticks() // 400) % 2 == 0:
            t = "PAUSE"
            f.draw(surf, (SCREEN_W - f.width(t)) // 2, 100, t, "#FCFCFC", shadow="#000000")
