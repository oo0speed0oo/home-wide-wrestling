"""Home Wide Wrestling - wrestlers for the angled ring view.

Each wrestler is a small 3D figure (capsules and balls on a skeleton). It's
projected with the same angle as the ring, sorted back-to-front, and painted
pixel by pixel in the Tag Team look: 3 colours per wrestler, no outlines,
big NES heads. One model gives every facing direction.
"""
import math
from PIL import Image

HS = 1.6          # big NES heads
K = 0.72          # pixels per unit (matches the ring mockup)
Q = 1 / math.sqrt(2)

PAL = {
    "black": "#000000", "red": "#F83800", "blue": "#0058F8", "navy": "#0000BC",
    "green": "#00A800", "blond": "#F8B800", "white": "#FCFCFC", "ref": "#F0B888",
    "mike": "#C68642", "stew": "#F4C0A0", "niko": "#F2D0A8", "jim": "#F8D0B8",
}


def hx(c):
    c = PAL.get(c, c)
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


# ---------------------------------------------------------------- vectors
def v_add(*vs):
    return tuple(sum(c) for c in zip(*vs))


def v_mul(v, k):
    return tuple(c * k for c in v)


def v_norm(v):
    L = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / L for c in v)


def proj(p):
    """ring-world (X, Y, Z-up) -> screen offset in pixels, same angle as the ring."""
    X, Y, Z = p
    return ((X - Y) * K * Q, (X + Y) * K * Q / 2 - Z * K)


def depth(p):
    return (p[0] + p[1]) * Q + p[2] * 0.002     # bigger = closer to the camera


# ---------------------------------------------------------------- 2D primitives after projection
class Ball:
    def __init__(self, c, r, mat, clip=False, bias=0.0):
        self.c3, self.r, self.mat, self.clip = c, r, mat, clip
        self.d = depth(c) + bias

    def prep(self, o):
        x, y = proj(self.c3)
        self.c = (o[0] + x, o[1] + y)
        self.rr = self.r * K

    def bbox(self):
        return self.c[0] - self.rr, self.c[1] - self.rr, self.c[0] + self.rr, self.c[1] + self.rr

    def hit(self, x, y):
        return (x - self.c[0]) ** 2 + (y - self.c[1]) ** 2 <= self.rr ** 2


class Rod:
    def __init__(self, a, b, r, mat, bias=0.0):
        self.a3, self.b3, self.r, self.mat, self.clip = a, b, r, mat, False
        self.d = depth(v_mul(v_add(a, b), 0.5)) + bias

    def prep(self, o):
        ax, ay = proj(self.a3)
        bx, by = proj(self.b3)
        self.a, self.b, self.rr = (o[0] + ax, o[1] + ay), (o[0] + bx, o[1] + by), self.r * K

    def bbox(self):
        return (min(self.a[0], self.b[0]) - self.rr, min(self.a[1], self.b[1]) - self.rr,
                max(self.a[0], self.b[0]) + self.rr, max(self.a[1], self.b[1]) + self.rr)

    def hit(self, x, y):
        (ax, ay), (bx, by) = self.a, self.b
        vx, vy = bx - ax, by - ay
        L2 = vx * vx + vy * vy
        t = 0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2))
        px, py = ax + t * vx - x, ay + t * vy - y
        return px * px + py * py <= self.rr * self.rr


class Dot:   # a face pixel, only drawn when that side of the head faces the camera
    def __init__(self, p, mat, show):
        self.p3, self.mat, self.show, self.clip = p, mat, show, False
        self.d = 1e9

    def prep(self, o):
        x, y = proj(self.p3)
        self.p = (o[0] + x, o[1] + y)


# ---------------------------------------------------------------- the wrestlers
CH = {
    # lengths in units; colours are the wrestler's 3 NES colours
    "mike": dict(Lt=14.0, rt=5.6, sw=6.6, hw=3.6, Lth=8.6, Lsh=8.0, rth=2.9, rsh=2.5, Lu=6.2, Lf=6.0,
                 ra=2.5, Rh=4.4, belly=(2.2, 5.6), skin="mike", c2="red", c3="black"),
    "stew": dict(Lt=17.0, rt=7.6, sw=9.0, hw=5.4, Lth=10.4, Lsh=9.6, rth=4.2, rsh=3.4, Lu=7.4, Lf=7.0,
                 ra=2.9, Rh=4.6, belly=(4.8, 10.4), skin="stew", c2="blue", c3="black",
                 guard=((0.25, 0.6, -1.0), (1.0, 0.15, 0.2))),
    "jim": dict(Lt=17.0, rt=6.6, sw=7.8, hw=4.6, Lth=11.0, Lsh=10.2, rth=3.6, rsh=3.0, Lu=7.2, Lf=6.8,
                ra=2.6, Rh=4.3, belly=(4.2, 8.6), skin="jim", c2="green", c3="blond",
                guard=((0.2, 0.85, -0.8), (1.0, 0.4, 0.3))),
    "niko": dict(Lt=18.0, rt=4.4, sw=5.6, hw=3.0, Lth=12.6, Lsh=11.8, rth=2.5, rsh=2.1, Lu=7.8, Lf=7.4,
                 ra=1.8, Rh=4.2, belly=None, skin="niko", c2="navy", c3="black"),
    # the generic referee: striped shirt, black trousers, bow tie
    "ref": dict(Lt=15.0, rt=5.2, sw=6.2, hw=3.3, Lth=9.4, Lsh=8.8, rth=2.6, rsh=2.3, Lu=6.4, Lf=6.2,
                ra=2.0, Rh=4.2, belly=None, skin="ref", c2="white", c3="black"),
}

# facing directions on screen -> angle in the ring plane
FACE = {"down-right": 0, "down-left": 90, "up-left": 180, "up-right": 270}

GUARD = ((0.35, 0.35, -1.0), (1.0, -0.15, 0.7))


def pose(lean=4, legs=((6, 0, 0), (-6, 0, 0)), arms=None, pitch=0, roll=0, lift=0, air=False, fx=None,
         yell=False):
    """legs: per leg (thigh pitch, shin pitch, spread) in degrees, + = forward/outward.
    arms: {"R": (upper, fore), "L": (upper, fore)} as (forward, outward, up) vectors.
    pitch: whole body tips forward (+) or backward (-) about the hips. lift: height off the mat."""
    arms = arms or {}
    return dict(lean=lean, legs=legs, arms={"R": arms.get("R", GUARD), "L": arms.get("L", GUARD)},
                pitch=pitch, roll=roll, lift=lift, air=air, fx=fx, yell=yell)


def both(up, fore):
    return {"R": (up, fore), "L": (up, fore)}


FLEX = both((0, 1, 0.15), (0, 0.15, 1))
UP = both((0.2, 0.35, 0.9), (0.1, -0.2, 1))
LOCKED = both((0, 0.25, 1), (0, 0, 1))
DANGLE = both((0.1, 0.3, -1), (0.1, 0, -1))
SPREAD = both((0, 1, 0.3), (0, 0.6, 0.8))
FLAIL = {"R": ((0.3, 0.8, 0.6), (0, 0.4, 1)), "L": ((-0.3, 0.8, -0.4), (0.3, 0.6, -0.6))}

# Mike's full move list (2 frames each where it moves). Order = rows of the move sheet.
MOVES = [
    ("stand", [pose()]),
    ("walk", [pose(6, ((24, 8, 0), (-20, -32, 0))), pose(6, ((-20, -32, 0), (24, 8, 0)))]),
    ("run", [pose(20, ((45, 10, 0), (-35, -75, 0)), {"R": ((0.8, 0.3, -0.5), (0.5, 0, 1)), "L": ((-0.7, 0.3, -0.7), (0.3, 0, 1))}),
             pose(20, ((-35, -75, 0), (45, 10, 0)), {"L": ((0.8, 0.3, -0.5), (0.5, 0, 1)), "R": ((-0.7, 0.3, -0.7), (0.3, 0, 1))})]),
    ("punch", [pose(0, arms={"R": ((-0.5, 0.45, -0.6), (0.7, 0, 0.8))}),
               pose(12, ((10, 0, 0), (-18, -8, 0)), {"R": ((1, 0.08, 0.05), (1, 0, 0.05))})]),
    ("kick", [pose(-4, ((70, -15, 0), (-4, 0, 0))), pose(-14, ((88, 85, 0), (-8, 0, 0)))]),
    ("block", [pose(2, arms=both((0.7, 0.25, 0.15), (0.15, -0.8, 0.8)))]),
    ("taunt", [pose(0, arms={"R": ((0.1, 0.5, 0.9), (0, 0.1, 1)), "L": ((-0.2, 0.8, -0.6), (-0.2, -0.8, 0.3))}),
               pose(0, ((6, 0, 8), (-6, 0, 8)), FLEX)]),
    ("hit", [pose(-18, ((-4, 0, 0), (12, 0, 0)), both((0.2, 0.7, -0.5), (0.3, 0.4, -0.8)))]),
    ("stunned", [pose(8, arms=DANGLE, roll=9, fx="stars"), pose(8, arms=DANGLE, roll=-9, fx="stars")]),
    ("knocked down", [pose(0, ((10, 0, 0), (30, 0, 0)), FLAIL, pitch=-50, lift=6, air=True),
                      pose(0, ((8, 10, 10), (4, 14, 10)), SPREAD, pitch=-90)]),
    ("get up", [pose(12, ((88, 95, 10), (82, 92, 10)), both((-0.5, 0.4, -0.8), (-0.2, 0, -1))),
                pose(18, ((70, -10, 0), (-10, -95, 0)), {"R": ((0.5, 0.3, -0.7), (0.4, 0, -0.8))})]),
    ("tie-up", [pose(22, ((12, 0, 0), (-26, -10, 0)), both((0.9, 0.2, 0.2), (0.8, -0.3, 0.4))),
                pose(28, ((16, 0, 0), (-30, -12, 0)), both((0.95, 0.15, 0.15), (0.8, -0.35, 0.3)))]),
    ("lift", [pose(-6, ((8, 0, 10), (-8, 0, 10)), UP), pose(-12, ((8, 0, 12), (-10, 0, 12)), LOCKED)]),
    ("throw", [pose(-10, ((8, 0, 10), (-8, 0, 10)), LOCKED),
               pose(26, ((25, 0, 6), (-25, -10, 6)), both((1, 0.2, -0.2), (1, 0, -0.35)))]),
    ("being lifted", [pose(0, ((10, 5, 0), (-5, 0, 0)), FLAIL, pitch=-90, lift=30, air=True),
                      pose(0, ((-5, 0, 0), (10, 5, 0)), SPREAD, pitch=-85, lift=31, air=True)]),
    ("being thrown", [pose(0, ((20, 0, 0), (-10, 0, 0)), FLAIL, pitch=-45, lift=18, air=True),
                      pose(0, ((30, 20, 0), (10, 10, 0)), SPREAD, pitch=-120, lift=8, air=True)]),
    ("pin", [pose(0, ((0, 20, 12), (0, 20, 12)), both((0.9, 0.3, -0.4), (0.3, 0, -1)), pitch=80, lift=6, air=True),
             pose(0, ((0, 20, 12), (0, 20, 12)), both((0.9, 0.35, -0.5), (0.4, 0, -1)), pitch=85, lift=5, air=True)]),
    ("stomp", [pose(6, ((75, 0, 0), (-4, 0, 0))), pose(12, ((30, 10, 0), (-8, 0, 0)))]),
    ("dive", [pose(0, ((-20, -10, 0), (-30, -20, 0)), both((1, 0.35, 0.2), (1, 0, 0.1)), pitch=60, lift=24, air=True),
              pose(0, ((-10, 0, 0), (-15, 0, 0)), both((1, 0.3, 0), (1, 0, 0)), pitch=88, lift=12, air=True)]),
    ("boston crab", [pose(-10, ((14, 0, 16), (-14, 0, 16)), both((0.6, 0.3, -0.5), (0.8, -0.45, 0.1))),
                     pose(-20, ((16, 0, 18), (-16, 0, 18)), both((0.5, 0.3, -0.6), (0.8, -0.5, 0.25)))]),
    ("sit up", [pose(0, ((10, 10, 10), (6, 12, 10)), both((0.2, 0.5, -0.8), (0, 0, -1)), pitch=-55),
                pose(12, ((88, 95, 10), (82, 92, 10)), both((-0.5, 0.4, -0.8), (-0.2, 0, -1)))]),
    # ---- added Oct 5: the rest of the Tecmo move set, plus the top rope
    ("headlock", [pose(14, ((14, 0, 12), (-14, -6, 12)), {"R": ((0.4, 0.9, 0.0), (0.7, -0.8, -0.3)),
                                                          "L": ((0.7, 0.4, -0.3), (0.6, -0.7, 0.0))}),
                  pose(22, ((16, 0, 14), (-16, -8, 14)), {"R": ((0.4, 0.9, -0.1), (0.6, -0.9, -0.4)),
                                                          "L": ((0.7, 0.4, -0.4), (0.6, -0.8, -0.1))})]),
    ("knee lift", [pose(18, ((12, 0, 0), (-26, -10, 0)), both((0.9, 0.2, 0.2), (0.8, -0.3, 0.4))),
                   pose(-6, ((88, 5, 0), (-4, 0, 0)), both((0.9, 0.2, 0.1), (0.8, -0.3, 0.3)))]),
    ("clothesline", [pose(20, ((45, 10, 0), (-35, -75, 0)), {"R": ((0.1, 1, 0.15), (0.2, 1, 0.1)),
                                                              "L": ((-0.7, 0.3, -0.7), (0.3, 0, 1))}),
                     pose(26, ((20, 0, 0), (-30, -40, 0)), {"R": ((0.6, 0.8, 0.15), (0.9, 0.4, 0.1)),
                                                            "L": ((-0.7, 0.3, -0.7), (0.3, 0, 1))})]),
    ("dropkick", [pose(0, ((60, 40, 0), (50, 30, 0)), both((0.2, 0.8, 0.4), (0, 0.4, 1)), pitch=-30, lift=16, air=True),
                  pose(0, ((85, 85, 0), (80, 80, 0)), both((0.1, 0.8, 0.5), (0, 0.3, 1)), pitch=-55, lift=10, air=True)]),
    ("knee drop", [pose(-6, ((95, 0, 4), (0, -100, 4)), both((0.2, 0.6, 0.8), (0, 0.3, 1)), lift=16, air=True),
                   pose(12, ((0, -90, 6), (85, 0, 6)), both((0.3, 0.6, -0.6), (0.3, 0, -1)))]),
    ("elbow drop", [pose(0, ((10, 20, 8), (10, 20, 8)), {"R": ((0.2, 0.5, -1), (0.9, 0.1, 0.2)),
                                                         "L": ((0.2, 0.5, 0.8), (0, 0.3, 1))}, pitch=70, lift=18, air=True),
                    pose(0, ((10, 20, 10), (10, 20, 10)), {"R": ((0.2, 0.5, -1), (0.9, 0.1, 0.2)),
                                                           "L": ((0.1, 0.8, 0.0), (0.2, 0.5, -0.4))}, pitch=86, lift=5, air=True)]),
    ("back drop", [pose(6, ((10, 10, 10), (-10, -10, 10)), both((0.9, 0.5, -0.2), (0.3, -0.9, 0.1))),
                   pose(0, ((10, 40, 12), (10, 40, 12)), both((0.1, 0.5, 1), (0, 0.3, 1)), pitch=-75, lift=2, air=True)]),
    ("pile driver", [pose(-10, ((8, 0, 10), (-8, 0, 10)), LOCKED),
                     pose(0, ((85, 90, 14), (80, 88, 14)), both((0.5, 0.4, 0.6), (0.6, -0.4, 0.5)))]),
    ("rope whip", [pose(10, ((16, 0, 6), (-20, -10, 6)), both((0.9, 0.3, -0.1), (1, 0, -0.1))),
                   pose(26, ((25, 0, 6), (-25, -10, 6)), {"R": ((1, 0.2, -0.2), (1, 0, -0.35)), "L": GUARD})]),
    ("shoulder throw", [pose(40, ((20, 10, 10), (-10, -10, 10)), both((0.7, 0.3, -0.6), (0.6, 0, -0.7))),
                        pose(-10, ((8, 0, 10), (-8, 0, 10)), UP)]),
    ("climb", [pose(4, ((80, 10, 6), (-6, 0, 6)), both((0.5, 0.4, 0.8), (0.3, 0, 1))),
               pose(4, ((-6, 0, 6), (80, 10, 6)), {"R": ((0.5, 0.4, 0.6), (0.4, 0, 1)), "L": ((0.4, 0.4, 0.9), (0.2, 0, 1))})]),
    ("on top rope", [pose(16, ((45, -30, 22), (45, -30, 22)), SPREAD),
                     pose(4, ((20, -10, 18), (20, -10, 18)), both((0.1, 0.6, 0.8), (0, 0.3, 1)))]),
]

OWN = {
    "mike": [
        ("victory", [pose(0, ((6, 0, 8), (-6, 0, 8)), FLEX),
                 pose(0, ((6, 0, 8), (-6, 0, 8)), {"R": ((0.1, 0.4, 0.9), (0, 0, 1)), "L": ((0.1, 0.4, 0.9), (0, 0, 1))})]),
        ("powerbomb", [pose(-8, ((10, 0, 12), (-10, 0, 12)), UP),
                   pose(30, ((50, -30, 10), (40, -35, 10)), both((0.8, 0.3, -0.3), (0.8, 0, -0.6)))]),
        ("military press", [pose(-4, ((8, 0, 10), (-8, 0, 10)), UP), pose(-8, ((8, 0, 12), (-8, 0, 12)), LOCKED)]),
        ("bear hug", [pose(10, ((10, 0, 8), (-14, 0, 8)), both((0.8, 0.7, 0), (0.2, -1, 0))),
                  pose(-10, ((10, 0, 10), (-14, 0, 10)), both((0.8, 0.6, 0.2), (0.2, -1, 0.1)))]),
    ],
    "stew": [
        ("victory", [pose(0, ((6, 0, 10), (-6, 0, 10)), {"R": ((0.1, 1.0, 0.45), (0.0, 0.35, 1)),
                                                          "L": ((0.1, 0.55, -0.9), (0.7, 0.1, 0.1))}, yell=True),
                     pose(4, ((6, 0, 10), (-6, 0, 10)), {"R": ((0.1, 1.0, 0.55), (0.0, 0.3, 1)),
                                                          "L": ((0.2, 0.55, -0.9), (0.7, 0.1, 0.2))}, yell=True)]),
        ("running lariat", [pose(20, ((45, 10, 0), (-35, -75, 0)), {"R": ((0.2, 1, 0.1), (0.2, 1, 0.1)),
                                                                  "L": ((-0.7, 0.3, -0.7), (0.3, 0, 1))}, yell=True),
                            pose(30, ((20, 0, 0), (-30, -40, 0)), {"R": ((0.7, 0.8, 0.1), (0.8, 0.5, 0.1)),
                                                                  "L": ((-0.7, 0.3, -0.7), (0.3, 0, 1))}, yell=True)]),
        ("headbutt", [pose(-20, ((10, 0, 0), (-20, -8, 0)), both((0.9, 0.2, 0.2), (0.8, -0.3, 0.4))),
                      pose(32, ((16, 0, 0), (-30, -12, 0)), both((0.9, 0.25, 0.1), (0.8, -0.35, 0.3)))]),
        ("seated butt drop", [pose(0, ((85, 90, 12), (80, 88, 12)), both((0.1, 0.8, 0.5), (0, 0.4, 1)), lift=16, air=True),
                              pose(10, ((88, 95, 12), (84, 92, 12)), both((0.2, 0.8, 0.1), (0.1, 0.6, 0.4)))]),
    ],
    "jim": [
        ("victory", [pose(0, ((6, 0, 10), (-6, 0, 10)), both((0.1, 0.75, 0.75), (0, 0.35, 1))),
                     pose(0, ((6, 0, 10), (-6, 0, 10)), {"R": ((0.5, 0.6, 0.5), (1, 0.2, 0.2)),
                                                          "L": ((0.1, 0.6, -0.8), (0.3, -0.6, 0.4))})]),
        ("sleeper hold", [pose(8, ((10, 0, 8), (-14, 0, 8)), {"R": ((0.9, 0.3, 0.35), (0.25, -1, 0.15)),
                                                             "L": ((0.8, 0.5, 0.3), (0.4, -0.6, 0.6))}),
                          pose(-6, ((12, 0, 10), (-16, 0, 10)), {"R": ((0.85, 0.3, 0.3), (0.2, -1, 0.1)),
                                                              "L": ((0.8, 0.5, 0.25), (0.45, -0.6, 0.55))})]),
        ("vertical suplex", [pose(-14, ((8, 0, 10), (-8, 0, 10)), LOCKED),
                             pose(0, ((20, 10, 8), (10, 10, 8)), both((0.2, 0.6, 0.9), (0, 0.3, 1)), pitch=-50,
                                  lift=4, air=True)]),
        ("hip toss", [pose(12, ((20, 0, 8), (-20, -10, 8)), {"R": ((0.4, 0.8, 0.1), (0.6, -0.6, 0.1)),
                                                            "L": ((0.8, 0.3, 0.1), (0.8, -0.3, 0.3))}),
                      pose(30, ((30, 0, 8), (-30, -20, 8)), {"R": ((0.8, 0.6, -0.3), (0.9, 0.2, -0.5)),
                                                            "L": ((0.9, 0.2, 0.2), (0.9, 0, -0.2))})]),
    ],
    "niko": [
        ("victory", [pose(0, ((6, 0, 8), (-6, 0, 8)), both((0.1, 0.9, 0.6), (0, 0.5, 1))),
                     pose(0, ((6, 0, 8), (-6, 0, 8)), {"R": ((0.3, 0.5, 0.8), (0.2, 0, 1)),
                                                        "L": ((0.1, 0.6, -0.8), (0.3, -0.5, 0.3))})]),
        ("ddt", [pose(18, ((12, 0, 8), (-20, -10, 8)), {"R": ((0.9, 0.2, 0.2), (0.5, -1, 0.1)),
                                                        "L": ((0.6, 0.6, -0.3), (0.6, -0.3, 0.2))}),
                 pose(0, ((60, 60, 10), (40, 50, 10)), {"R": ((0.8, 0.2, -0.4), (0.4, -1, -0.2)),
                                                        "L": ((0.2, 0.8, -0.2), (0, 0.6, -0.8))}, pitch=-60)]),
        ("flying crossbody", [pose(0, ((-6, -6, 6), (-4, -4, 6)), both((0.6, 0.8, 0.1), (0.5, 0.4, 0.1)), pitch=78,
                                   lift=22, air=True),
                              pose(0, ((-4, -4, 6), (-2, -2, 6)), both((0.7, 0.7, 0), (0.6, 0.3, -0.1)), pitch=88,
                                   lift=10, air=True)]),
        ("missile dropkick", [pose(0, ((70, 60, 0), (60, 50, 0)), both((0.2, 0.8, 0.4), (0, 0.4, 1)), pitch=-40,
                                   lift=22, air=True),
                              pose(0, ((88, 88, 0), (80, 82, 0)), both((0.1, 0.8, 0.5), (0, 0.3, 1)), pitch=-60,
                                   lift=14, air=True)]),
    ],
}


KNEEL = ((88, 0, 8), (0, -90, 8))           # one foot planted, other knee on the mat
REF_MOVES = [
    ("stand", [pose(2, arms=both((0.1, 0.35, -1), (0.2, 0.1, -1)))]),
    ("walk", [pose(6, ((24, 8, 0), (-20, -32, 0)), {"R": ((0.4, 0.3, -1), (0.4, 0, -1)), "L": ((-0.4, 0.3, -1), (-0.1, 0, -1))}),
              pose(6, ((-20, -32, 0), (24, 8, 0)), {"L": ((0.4, 0.3, -1), (0.4, 0, -1)), "R": ((-0.4, 0.3, -1), (-0.1, 0, -1))})]),
    ("pin count", [pose(40, KNEEL, {"R": ((0.2, 0.4, 1), (0.1, 0.1, 1)), "L": ((0.6, 0.4, -0.7), (0.5, 0, -0.8))}),
                   pose(62, KNEEL, {"R": ((1, 0.3, -0.5), (0.5, 0, -1)), "L": ((0.6, 0.4, -0.7), (0.5, 0, -0.8))})]),
    ("count out", [pose(2, arms={"R": ((0.7, 0.4, 0.6), (0.3, 0, 1)), "L": ((0.1, 0.35, -1), (0.2, 0.1, -1))}),
                   pose(2, arms={"R": ((0.8, 0.4, 0.3), (0.8, 0, 0.6)), "L": ((0.1, 0.35, -1), (0.2, 0.1, -1))})]),
    ("ask submit", [pose(45, ((20, 10, 10), (-10, -10, 10)), {"R": ((0.7, 0.3, -0.6), (0.9, -0.2, 0.1)), "L": ((0.5, 0.5, -0.8), (0.2, 0, -1))}),
                    pose(50, ((20, 10, 10), (-10, -10, 10)), {"R": ((0.7, 0.3, -0.5), (0.9, -0.1, 0.4)), "L": ((0.5, 0.5, -0.8), (0.2, 0, -1))})]),
    ("raise hand", [pose(0, ((6, 0, 6), (-6, 0, 6)), {"R": ((0.1, 0.5, 1), (0.05, 0.2, 1)), "L": ((0.1, 0.35, -1), (0.2, 0.1, -1))}),
                    pose(-4, ((6, 0, 8), (-6, 0, 8)), {"R": ((0.1, 0.4, 1), (0.05, 0.1, 1)), "L": ((0.1, 0.35, -1), (0.2, 0.1, -1))})]),
    ("call for bell", [pose(0, ((6, 0, 8), (-6, 0, 8)), both((0.2, 0.2, 1), (0.1, -0.6, 0.8))),
                       pose(0, ((6, 0, 8), (-6, 0, 8)), both((0.1, 1, 0.5), (0, 0.7, 0.7)))]),
]


def moves_for(name):
    if name == "ref":
        return REF_MOVES
    return MOVES + OWN.get(name, [])


POSES = {"stand": MOVES[0][1][0], "walkA": MOVES[1][1][0], "walkB": MOVES[1][1][1]}


def _rot_pc(p, pz, pitch, roll):
    """tip a local point about the hips: pitch around the side axis, roll around the forward axis."""
    a, b, c = p
    dc = c - pz
    if roll:
        r = math.radians(roll)
        b, dc = b * math.cos(r) + dc * math.sin(r), -b * math.sin(r) + dc * math.cos(r)
    if pitch:
        q = math.radians(pitch)
        a, dc = a * math.cos(q) + dc * math.sin(q), -a * math.sin(q) + dc * math.cos(q)
    return (a, b, pz + dc)


def build(name, pz_pose, facing):
    """pz_pose: a pose dict (or a name in POSES). Built in local space (forward, side, up),
    tipped/lifted as a whole, grounded, then turned to face `facing`."""
    c = CH[name]
    P = POSES[pz_pose] if isinstance(pz_pose, str) else pz_pose
    th = math.radians(FACE[facing] if isinstance(facing, str) else facing)
    f = (math.cos(th), math.sin(th), 0.0)
    s = (-math.sin(th), math.cos(th), 0.0)
    skin, c2, c3 = c["skin"], c["c2"], c["c3"]
    specs = []            # (kind, points, radius, material, bias, clip)

    def rod(a, b, r, m, bias=0.0):
        specs.append(("rod", [a, b], r, m, bias, False))

    def ball(p, r, m, bias=0.0, clip=False):
        specs.append(("ball", [p], r, m, bias, clip))

    def add(p, v):
        return (p[0] + v[0], p[1] + v[1], p[2] + v[2])

    def mul(v, k):
        return (v[0] * k, v[1] * k, v[2] * k)

    def unit(v):
        L_ = math.sqrt(sum(x * x for x in v)) or 1.0
        return (v[0] / L_, v[1] / L_, v[2] / L_)

    leg_len = c["Lth"] + c["Lsh"] + 1.2
    H0 = (0.0, 0.0, leg_len)
    lean = math.radians(P["lean"])
    S0 = add(H0, (math.sin(lean) * c["Lt"], 0, math.cos(lean) * c["Lt"]))
    up = (math.sin(lean), 0, math.cos(lean))

    # legs
    for sd, (a_th, a_sh, spread) in zip((1, -1), P["legs"]):
        hip = add(H0, (0, sd * c["hw"], 0))
        ta, sa, sp_ = math.radians(a_th), math.radians(a_sh), math.radians(spread)
        knee = add(hip, mul((math.sin(ta), sd * math.sin(sp_), -math.cos(ta) * math.cos(sp_)), c["Lth"]))
        ank = add(knee, mul((math.sin(sa), sd * math.sin(sp_) * 0.5, -math.cos(sa)), c["Lsh"]))
        toe = add(ank, (2.8 * math.cos(sa), 0, 2.8 * math.sin(sa) - 0.3))
        legmat = c2 if name == "niko" else (c3 if name == "ref" else skin)
        rod(hip, knee, c["rth"], legmat)
        rod(knee, ank, c["rsh"], legmat)
        boot = c3 if name in ("stew", "ref") else c2
        rod(add(ank, mul((-math.sin(sa), 0, math.cos(sa)), 3.0)), ank, c["rsh"] + 0.3, boot)
        rod(ank, toe, 1.7, boot)
        rod(hip, add(hip, mul((math.sin(ta), 0, -math.cos(ta)), 2.6)), c["rth"] + 0.3, c3 if name == "ref" else c2, 0.5)

    # torso, hips, shoulders, belly
    body = skin if name in ("mike", "niko") else c2
    # a singlet stops below the neck; bare-chested wrestlers are skin all the way up
    top = S0 if body == skin else add(S0, mul(up, -(c["rt"] - 2.0)))
    rod(H0, top, c["rt"], body)
    rod(add(H0, (0, -c["hw"], 1.0)), add(H0, (0, c["hw"], 1.0)), c["rt"] * (0.62 if name == "ref" else 0.9), c3 if name == "ref" else c2, 0.5)
    rod(add(S0, mul(up, -1.2)), add(S0, mul(up, -1.2)), 0, body)
    rod(add(add(S0, (0, -c["sw"], 0)), mul(up, -1.2)), add(add(S0, (0, c["sw"], 0)), mul(up, -1.2)), 2.8,
        c2 if name == "ref" else skin)
    if name == "ref":       # black stripes round the shirt, and a bow tie
        fw0 = (math.cos(lean), 0, -math.sin(lean))
        for dv in (fw0, mul(fw0, -1), (0, 1, 0), (0, -1, 0)):
            off = mul(dv, c["rt"] * 0.82)
            rod(add(add(H0, mul(up, 2.5)), off), add(add(S0, mul(up, -1.5)), off), 0.95, c3, 0.35)
        ball(add(add(S0, mul(up, -0.2)), mul(fw0, c["rt"] * 0.55)), 1.3, c3, 0.8)
    if name == "stew":      # singlet straps over both shoulders
        for sd in (1, -1):
            rod(add(add(S0, (0, sd * c["sw"] * 0.55, 0)), mul(up, -0.6)),
                add(add(S0, (0, sd * c["sw"] * 0.45, 0)), mul(up, -(c["rt"] - 1.0))), 1.4, body, 0.3)
    if name == "jim":       # one strap over the left shoulder
        rod(add(add(S0, (0, -c["sw"] * 0.55, 0)), mul(up, -0.6)),
            add(add(S0, (0, -c["sw"] * 0.3, 0)), mul(up, -(c["rt"] - 1.0))), 1.5, body, 0.3)
    if c["belly"]:
        bf, br = c["belly"]
        bc = add(add(H0, mul(up, c["Lt"] * 0.38)), (bf * math.cos(lean), 0, -bf * math.sin(lean)))
        if name == "stew":
            bz = add(H0, mul(up, c["Lt"] * 0.38))
            rod(add(bz, mul(up, -2.4)), add(bz, mul(up, 2.4)), c["rt"] + 0.3, c3, 0.5)
            ball(bc, br, c2, 0.6)                           # blue belly
            fw_ = (br * 0.35 * math.cos(lean), 0, -br * 0.35 * math.sin(lean))
            rod(add(add(bc, fw_), (0, -br * 0.82, 0)), add(add(bc, fw_), (0, br * 0.82, 0)), 2.9, c3, 0.65)  # black band
        else:
            ball(bc, br, body, 0.6)
    if name == "stew":
        ball(add(add(S0, mul(up, -1.6)), (c["rt"] * 0.55, 0, 0)), 3.0, skin, 0.7)

    # arms, each on its own
    for sd, key in ((1, "R"), (-1, "L")):
        sh = add(add(S0, (0, sd * c["sw"], 0)), mul(up, -1.0))
        arm = P["arms"][key]
        if arm is GUARD and c.get("guard"):
            arm = c["guard"]
        (ua, ub, uc), (fa_, fb, fc) = arm
        el = add(sh, mul(unit((ua, sd * ub, uc)), c["Lu"]))
        fv = unit((fa_, sd * fb, fc))
        wr = add(el, mul(fv, c["Lf"]))
        rod(sh, el, c["ra"], skin, 0.4)
        if name == "ref":   # short white sleeves
            rod(sh, add(sh, mul(unit((ua, sd * ub, uc)), c["Lu"] * 0.5)), c["ra"] + 0.6, c2, 0.42)
        rod(el, wr, c["ra"] * 0.95, skin, 0.45)
        ball(wr, c["ra"] + 0.8, skin, 0.5)
        if name in ("mike", "niko"):
            rod(add(wr, mul(fv, -2.6)), add(wr, mul(fv, -1.4)), c["ra"] + 0.3, c2 if name == "mike" else c3, 0.46)

    # head
    R = c["Rh"] * HS
    hc = add(S0, add(mul(up, 1.0 + R * 0.9), (0.6, 0, 0)))
    fwd = (math.cos(lean), 0, -math.sin(lean))        # face direction before tipping
    hu = up

    def hl(a, b, cc):      # head-local offset (forward, side, up) in units of R
        return add(hc, add(add(mul(fwd, a * R), (0, b * R, 0)), mul(hu, cc * R)))

    ball(hc, R, skin)
    hair = c3
    if name == "mike":
        ball(hl(-0.35, 0, -0.1), R * 1.28, hair, -0.6)
        for k in range(8):
            a_ = math.radians(k * 45)
            ball(hl(-0.45, math.cos(a_) * 1.05, math.sin(a_) * 1.05 - 0.2), R * 0.42, hair, -0.7)
        ball(hl(-0.05, 0, 0.55), R * 0.72, hair, 0.05)
        ball(hl(0.55, 0, -0.62), R * 0.46, c3, 0.07)                      # beard
    elif name == "niko":
        ball(hl(-0.05, 0, 0.12), R * 1.06, hair, 1.0)
    elif name == "jim":
        ball(hl(-0.2, 0, 0.32), R * 0.98, hair, 0.05)                      # short blond hair
        ball(hl(0.62, 0, -0.74), R * 0.2, c3, 0.07)                       # small goatee on the chin
    elif name == "ref":
        ball(hl(-0.2, 0, 0.36), R * 0.98, hair, 0.05)                      # short neat hair
        ball(hl(0.35, 0, 0.72), R * 0.4, hair, 0.06)                       # combed front
        ball(hl(-0.45, 0, 0.05), R * 0.82, hair, 0.04)                     # back of the head
    elif name == "stew":
        ball(hl(-0.2, 0, 0.32), R * 0.98, hair, 0.05)
        ball(hl(0.45, 0, 0.72), R * 0.36, hair, 0.06)
    if name == "niko":      # bowl of shaggy hair: bangs down to the eyes, only the lower face shows
        ball(hl(0.66, 0, -0.3), R * 0.52, skin, 1.1)
    else:
        ball(hl(0.63, 0, -0.05), R * 0.62, skin, 0.08)                     # face over the fringe
    eyes = [hl(0.88, sd * 0.36, -0.12 if name == "niko" else 0.1) for sd in (1, -1)]
    if P.get("yell"):
        eyes += [hl(0.9, 0, -0.38), hl(0.9, 0.12, -0.45)]
    star_c = hl(0, 0, 1.5)

    # tip / lift / ground the whole figure, then face it the right way
    pzv = leg_len
    tf = lambda p: _rot_pc(p, pzv, P["pitch"], P["roll"])
    specs = [(k, [tf(q) for q in pts], r, m, bi, cl) for k, pts, r, m, bi, cl in specs]
    eyes = [tf(e) for e in eyes]
    star_c = tf(star_c)
    face_dir = unit(_rot_pc(add((0, 0, pzv), fwd), pzv, P["pitch"], P["roll"])[:2] + (0,))
    face_dir = (face_dir[0], face_dir[1], 0)
    low = min(min(q[2] for q in pts) - r for k, pts, r, *_ in specs)
    dz = (P["lift"] if P["air"] else 0) - low
    W_ = lambda p: v_add(v_mul(f, p[0]), v_mul(s, p[1]), (0.0, 0.0, p[2] + dz))
    out = []
    for k, pts, r, m, bi, cl in specs:
        if k == "rod":
            if r > 0:
                out.append(Rod(W_(pts[0]), W_(pts[1]), r, m, bi))
        else:
            out.append(Ball(W_(pts[0]), r, m, cl, bi))
    fw = v_add(v_mul(f, face_dir[0]), v_mul(s, face_dir[1]))
    show = fw[0] * Q + fw[1] * Q > 0.3 and abs(P["pitch"]) < 60
    for e in eyes:
        out.append(Dot(W_(e), c2 if name == "jim" else "black", show))
    if P.get("fx") == "stars":
        out.append(Stars(W_(star_c)))
    return out


class Stars:     # dizzy stars circling above the head (effect, drawn in white/yellow)
    def __init__(self, p):
        self.p3, self.d, self.clip = p, 1e9, False

    def prep(self, o):
        x, y = proj(self.p3)
        self.p = (o[0] + x, o[1] + y)


def render(name, pose, facing, feet, W, H, img=None):
    """Paint one wrestler with its feet at screen point `feet`."""
    return render_prims(build(name, pose, facing), feet, W, H, img)


def shift(prims, dX, dY, dZ=0.0):
    """move a built wrestler around the ring (world units), keeping its depth right for sorting."""
    for p in prims:
        for a in ("a3", "b3", "c3", "p3"):
            if hasattr(p, a):
                q = getattr(p, a)
                setattr(p, a, (q[0] + dX, q[1] + dY, q[2] + dZ))
        if p.d < 1e8:
            p.d += (dX + dY) * Q + dZ * 0.002
    return prims


def render_prims(prims, feet, W, H, img=None):
    img = img or Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    for p in prims:
        p.prep(feet)
    solid = [p for p in prims if not isinstance(p, (Dot, Stars))]
    solid.sort(key=lambda p: p.d)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lp = layer.load()
    for p in solid:
        col = hx(p.mat)
        x0, y0, x1, y1 = p.bbox()
        for y in range(max(0, int(y0) - 1), min(H, int(y1) + 2)):
            for x in range(max(0, int(x0) - 1), min(W, int(x1) + 2)):
                if p.hit(x + 0.5, y + 0.5):
                    if p.clip and not lp[x, y][3]:
                        continue
                    lp[x, y] = col
    for p in prims:
        if isinstance(p, Dot) and p.show:
            x, y = int(p.p[0]), int(p.p[1])
            if 0 <= x < W and 0 <= y < H and lp[x, y][3]:
                lp[x, y] = hx(p.mat)
    for p in prims:
        if isinstance(p, Stars):
            for k, col in ((0, "#FCFCFC"), (1, "#F8D878"), (2, "#FCFCFC")):
                x = int(p.p[0] + (k - 1) * 5)
                y = int(p.p[1] + (0 if k == 1 else 2))
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= x + dx < W and 0 <= y + dy < H:
                        lp[x + dx, y + dy] = hx(col)
    img.alpha_composite(layer)
    return img


def sheet(name, out_path):
    """4 facings x (stand, walk A, walk B), on a mat-grey background, 6x."""
    cw, chh = 44, 60
    img = Image.new("RGBA", (cw * 4, chh * 3), hx("#BCBCBC"))
    for i, fc in enumerate(["down-right", "down-left", "up-right", "up-left"]):
        for j, pose in enumerate(["stand", "walkA", "walkB"]):
            cell = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
            render(name, pose, fc, (cw / 2, chh - 4), cw, chh, cell)
            img.alpha_composite(cell, (i * cw, j * chh))
    img.convert("RGB").resize((img.width * 6, img.height * 6), Image.NEAREST).save(out_path)


if __name__ == "__main__":
    import sys
    who = sys.argv[1] if len(sys.argv) > 1 else "mike"
    sheet(who, f"/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/{who}_3d_sheet.png")
    print("ok")
