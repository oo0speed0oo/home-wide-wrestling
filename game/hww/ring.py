"""The angled ring. Game logic is a flat square mat; this only turns mat positions into screen pixels.

Mat coordinates: X and Y run 0..RING along the ring's two edges, Z is height above the mat.
Same projection as export/source/arenas.py, moved onto the 256x240 screen.

Outside: the floor is FLOOR_Z below the mat. Only the two front sides of the floor can be seen
(the ring hides the back), so wrestlers go out over the front ropes: the X = RING side (down-right on
screen) and the Y = RING side (down-left).
"""
import math

from .settings import ARENA_SHIFT

CX, CY = 128, 80             # where mat (0, 0) sits in the arena art
RING = 104                   # the mat is RING x RING
EDGE = 9                     # how close to the ropes your feet can get inside
FLOOR_Z = -18                # the floor outside, below the mat
OUT_NEAR = RING + 12         # outside: closest you can stand to the apron...
OUT_FAR = RING + 34          # ...and farthest out
OUT_LOW = 6                  # the floor strips run along the side from here...
MAX_SUM = 226                # ...and x + y can't go past this (the bottom of the screen)
CORNERS = {"back": (0, 0), "right": (RING, 0), "front": (RING, RING), "left": (0, RING)}


def to_screen(x, y, z=0.0):
    """mat (x, y, z) -> screen pixel (sx, sy)."""
    return CX + (x - y), CY + (x + y) / 2 - z + ARENA_SHIFT


def depth(x, y):
    """bigger = closer to the camera = drawn later."""
    return x + y


def clamp_in(x, y):
    return min(RING - EDGE, max(EDGE, x)), min(RING - EDGE, max(EDGE, y))


def clamp_out(x, y):
    """keep a point on the visible floor outside: the strip along the X side or the Y side."""
    x = min(OUT_FAR, max(OUT_LOW, x))
    y = min(OUT_FAR, max(OUT_LOW, y))
    if x < OUT_NEAR and y < OUT_NEAR:          # inside the ring's footprint: step out to the nearer strip
        if OUT_NEAR - x <= OUT_NEAR - y:
            x = OUT_NEAR
        else:
            y = OUT_NEAR
    if x + y > MAX_SUM:
        extra = (x + y - MAX_SUM) / 2
        x, y = x - extra, y - extra
        if x < OUT_NEAR and y < OUT_NEAR:
            if x >= y:
                x = OUT_NEAR
                y = MAX_SUM - x
            else:
                y = OUT_NEAR
                x = MAX_SUM - y
    return x, y


def clamp(x, y, outside):
    return clamp_out(x, y) if outside else clamp_in(x, y)


def nearest_corner(x, y):
    name = min(CORNERS, key=lambda n: math.hypot(x - CORNERS[n][0], y - CORNERS[n][1]))
    return name, CORNERS[name]
