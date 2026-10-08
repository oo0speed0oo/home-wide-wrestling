"""The referee (generic for now). Stays out of the way, walks over to count pins, checks on
submissions, counts out anyone on the floor (from inside, at the ropes), and raises the winner's hand.
The nemesis slow count comes later.

Sheet rows: stand, walk, pin count, count out, ask submit, raise hand, call for bell.
"""
import math

from . import ring
from .wrestler import EDGE, FACING_DIR

SPEED = 1.1                 # mat units per frame: he hustles
COUNT_EVERY = 50            # frames between "ONE", "TWO", "THREE"
SLAP = 10                   # frames his hand is on the mat
ROOM = 22                   # he keeps about this far from the wrestlers when nothing's happening


class Referee:
    who = "ref"
    radius = 5

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vert, self.horiz = "down", "left"
        self.state = "stand"
        self.t = 0
        self.job = None             # None, ("pin", victim), ("submission", victim), ("raise", winner)
        self.count = 0              # pin count so far
        self.count_t = 0
        self.blocked = False
        self.axis = None            # the line the two wrestlers are on; he counts from the side of it
        self.flips = 0              # count-out arm swings
        self.z = 0.0
        self.outside = False
        self.bell_t = 0             # frames left calling for the bell
        self.count_every = COUNT_EVERY      # slower when you pin your nemesis (the match sets it)

    @property
    def facing(self):
        return f"{self.vert}-{self.horiz}"

    @property
    def move(self):
        return self.state

    @property
    def frame(self):
        if self.state == "walk":
            return (self.t // 10) % 2
        if self.state == "pin count":
            return 1 if 0 < self.count_t <= SLAP else 0
        if self.state == "count out":
            return self.flips % 2
        if self.state in ("ask submit", "raise hand", "call for bell"):
            return (self.t // 20) % 2
        return (self.t // 24) % 2

    def face_toward(self, x, y):
        dx, dy = x - self.x, y - self.y
        if dx or dy:
            d = max(FACING_DIR.values(), key=lambda v: v[0] * dx + v[1] * dy)
            for face, fd in FACING_DIR.items():
                if fd == d:
                    self.vert, self.horiz = face.split("-")

    def set_state(self, s):
        if s != self.state:
            self.state = s
            self.t = 0

    # ------------------------------------------------------------------ jobs
    def count_pin(self, victim, axis=None):
        self.job = ("pin", victim)
        self.axis = axis
        self.count = 0
        self.count_t = 0

    def watch_submission(self, victim, axis=None):
        self.job = ("submission", victim)
        self.axis = axis

    def count_out(self, w):
        self.job = ("countout", w)
        self.axis = None
        self.flips = 0

    def flip(self):
        self.flips += 1

    def raise_hand(self, winner):
        self.job = ("raise", winner)
        self.axis = None

    def stop(self):
        self.job = None
        self.count = 0
        self.set_state("stand")

    @property
    def counting(self):
        return self.state == "pin count"

    # ------------------------------------------------------------------ every frame
    def call_for_bell(self, frames=45):
        self.bell_t = frames
        self.set_state("call for bell")

    def update(self, wrestlers):
        self.t += 1
        if self.bell_t > 0:
            self.bell_t -= 1
            return
        if self.job:
            kind, w = self.job
            if kind == "countout":
                spot = self.rope_spot(w)
            else:
                spot = self.spot_beside(w, 22 if kind == "pin" else 24)
            if self.walk_to(*spot):
                self.face_toward(w.x, w.y)
                if kind == "pin":
                    if self.state != "pin count":
                        self.set_state("pin count")
                        self.count_t = 0
                    self.count_t += 1
                    if self.count_t >= self.count_every and self.count < 3:
                        self.count += 1
                        self.count_t = 1
                else:
                    self.set_state({"submission": "ask submit", "countout": "count out"}.get(kind, "raise hand"))
            return
        # nothing to do: keep out of the way
        near = [w for w in wrestlers if math.hypot(w.x - self.x, w.y - self.y) < ROOM]
        if near:
            closest = min(near, key=lambda w: math.hypot(w.x - self.x, w.y - self.y))
            dx, dy = self.x - closest.x, self.y - closest.y          # step away from whoever's nearest
            if self.x <= EDGE + 1 or self.x >= ring.RING - EDGE - 1 or self.y <= EDGE + 1 or \
                    self.y >= ring.RING - EDGE - 1:
                dx, dy = -dy, dx                                    # pinned on the ropes: slide along them
            d = math.hypot(dx, dy) or 1
            tx, ty = self.x + dx / d * 10, self.y + dy / d * 10
            if not self.walk_to(*self.clamp(tx, ty), stop_state=None):
                return
        self.set_state("stand")
        self.face_toward(*self.watch_point(wrestlers))

    def spot_beside(self, w, dist):
        """a spot next to wrestler w, on whichever side has more room."""
        best = None
        sides = FACING_DIR.values()
        if self.axis:               # off to the side of the pair, so he isn't hidden behind them
            sides = [d for d in sides if d[0] * self.axis[0] + d[1] * self.axis[1] == 0]
        for d in sides:
            x, y = w.x + d[0] * dist, w.y + d[1] * dist
            room = min(x - EDGE, ring.RING - EDGE - x, y - EDGE, ring.RING - EDGE - y)
            score = room - 0.3 * math.hypot(x - self.x, y - self.y)
            if best is None or score > best[0]:
                best = (score, x, y)
        return self.clamp(best[1], best[2])

    def rope_spot(self, w):
        """inside, at the ropes nearest to whoever's on the floor."""
        lo, hi = EDGE, ring.RING - EDGE
        if w.x > ring.RING:
            return hi - 2, min(hi, max(lo, w.y))
        if w.y > ring.RING:
            return min(hi, max(lo, w.x)), hi - 2
        return self.clamp(w.x, w.y)

    @staticmethod
    def clamp(x, y):
        lo, hi = EDGE, ring.RING - EDGE
        return min(hi, max(lo, x)), min(hi, max(lo, y))

    @staticmethod
    def watch_point(wrestlers):
        return (sum(w.x for w in wrestlers) / len(wrestlers), sum(w.y for w in wrestlers) / len(wrestlers))

    def walk_to(self, x, y, stop_state="stand"):
        """step toward (x, y); True once he's there."""
        dx, dy = x - self.x, y - self.y
        d = math.hypot(dx, dy)
        if d <= SPEED:
            self.x, self.y = x, y
            return True
        self.x += dx / d * SPEED
        self.y += dy / d * SPEED
        self.face_toward(x, y)
        self.set_state("walk")
        return False
