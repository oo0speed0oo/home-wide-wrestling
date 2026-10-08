"""In-match effects (from export/source/screens2.py): hit sparks, the finisher flash and the slam shake."""
import math

import pygame

from .assets import hex_rgb

WHITE, YELLOW = hex_rgb("#FCFCFC"), hex_rgb("#F8D878")


def _spark_points(k):
    """k = 0: a white star with a yellow core. k = 1: a smaller white ring."""
    pts = []
    if k == 0:
        for r in range(1, 9):
            for w in (-1, 0, 1) if r < 5 else (0,):
                pts += [(r, w, WHITE), (-r, w, WHITE), (w, r, WHITE), (w, -r, WHITE)]
        for r in range(1, 6):
            pts += [(r, r, YELLOW), (-r, r, YELLOW), (r, -r, YELLOW), (-r, -r, YELLOW)]
        pts += [(dx, dy, YELLOW) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    else:
        for a in range(12):
            ang = a * math.pi / 6
            for rr in (8, 9):
                pts.append((round(math.cos(ang) * rr), round(math.sin(ang) * rr), WHITE))
    return pts


SPARK = [_spark_points(0), _spark_points(1)]
SPARK_FRAMES = 10           # star for the first half, ring for the second


SHAKE = [(3, 2), (-3, -2), (2, 1), (-2, -1), (1, 0), (0, 0)]     # the ring shakes on a slam
FLASH_FRAMES = 16


class Effects:
    def __init__(self):
        self.sparks = []        # [x, y, age]
        self.shake_i = len(SHAKE) * 2     # not shaking
        self.flash_t = 0
        self.dither = None

    def slam(self):
        self.shake_i = 0

    def finisher(self):
        self.flash_t = FLASH_FRAMES

    @property
    def offset(self):
        """how far to shift the arena this frame."""
        return SHAKE[self.shake_i // 2] if self.shake_i < len(SHAKE) * 2 else (0, 0)

    def spark(self, x, y):
        self.sparks.append([round(x), round(y), 0])

    def update(self):
        self.shake_i += 1
        self.flash_t = max(0, self.flash_t - 1)
        for s in self.sparks:
            s[2] += 1
        self.sparks = [s for s in self.sparks if s[2] < SPARK_FRAMES]

    def draw_flash(self, surf, top, bottom):
        """the finisher flash: the arena goes white, then flickers out as a dither."""
        if not self.flash_t:
            return
        k = self.flash_t
        if k > FLASH_FRAMES - 4:
            surf.fill(WHITE, (0, top, surf.get_width(), bottom - top))
            return
        if k % 4 < 2:
            if self.dither is None or self.dither.get_height() != bottom - top:
                self.dither = pygame.Surface((surf.get_width(), bottom - top), pygame.SRCALPHA)
                for y in range(bottom - top):
                    for x in range(y % 2, surf.get_width(), 2):
                        self.dither.set_at((x, y), WHITE + (255,))
            surf.blit(self.dither, (0, top))

    def draw(self, surf):
        for x, y, age in self.sparks:
            for dx, dy, c in SPARK[0 if age < SPARK_FRAMES // 2 else 1]:
                surf.set_at((x + dx, y + dy), c)
