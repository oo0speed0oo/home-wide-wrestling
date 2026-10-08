"""Tie-ups and the two-person moves that come out of them (design doc: Tie-ups, The two meters, Reversals).

- walking into each other starts a tie-up; there's no grapple button and it can't be blocked
- both mash on the tug-of-war meter; the direction + button you press picks your move
- each press is worth 0.5 + energy, so a fresh wrestler has the edge; presses over 10 a second don't count
- energy 30% or more apart: no meter, the fresher wrestler's first press does it
  ("Don't give up yet!": twice per wrestler per match the underdog gets the meter anyway, presses worth more)
- a tie-up lasts about 2 seconds; if nobody wins, they break apart
- big moves too early (opponent at 70% or more): the receiver barely has to mash
- a stunned wrestler can't fight the tie-up: one press does it

Also the running attacks and the ground: pins (the ref counts, only the pinned man mashes, using the
get-up numbers), stomps and drops, and the Boston crab (a tug of war that drains the victim; tap out or escape).
"""
from . import ring
from .specials import SPECIAL_NAMES, resolve
from .wrestler import ARROW_DIR, FACING_DIR, STATS

C3 = 0.509                 # art units (the 3D figures) -> mat units

# ---------------------------------------------------------------- tie-up moves (Controls: Full Tecmo move set)
# (button, direction) -> move. direction: None, "up", "down", "side" (left or right)
TIEUP_MOVES = {
    ("s", None): "knee lift", ("s", "up"): "brain buster", ("s", "side"): "back drop", ("s", "down"): "pile driver",
    ("a", None): "headlock", ("a", "up"): "body slam", ("a", "side"): "headlock", ("a", "down"): "headlock",
}
LIGHT = {"knee lift", "headlock", "body slam", "rope whip"}
HEAVY = {"back drop", "brain buster", "pile driver"} | SPECIAL_NAMES      # specials are big moves too
LIFTS = {"body slam", "brain buster", "pile driver", "military press", "powerbomb", "vertical suplex"}
HEAVY_SAFE = 0.7           # heavy moves are safe once the opponent is under 70%

# each move: frames as (sheet row, frame, ticks); damage; what happens to the victim; where he lands
#   land: (forward/behind, art units) measured from the attacker along his facing
MOVES = {
    "knee lift": {"frames": [("knee lift", 0, 10), ("knee lift", 1, 16)], "damage": 0.05, "end": "stagger"},
    "headlock": {"frames": [("headlock", 0, 16), ("headlock", 1, 16)] * 3, "damage": 0.07, "end": "release"},
    "body slam": {"frames": [("lift", 0, 12), ("lift", 1, 18), ("throw", 0, 10), ("throw", 1, 14)],
                  "damage": 0.10, "end": "down", "land": 22},
    "brain buster": {"frames": [("brain buster", 0, 30), ("brain buster", 1, 16)], "damage": 0.14, "end": "down",
                     "land": -16},
    "pile driver": {"frames": [("pile driver", 0, 30), ("pile driver", 1, 18)], "damage": 0.16, "end": "down",
                    "land": 6},
    "back drop": {"frames": [("back drop", 0, 14), ("back drop", 1, 16)], "damage": 0.13, "end": "down",
                  "land": -16},
    "rope whip": {"frames": [("rope whip", 0, 10), ("rope whip", 1, 8)], "damage": 0.0, "end": "whipped",
                  "land": 30},
    "post slam": {"frames": [("post slam", 0, 12), ("post slam", 1, 20)], "damage": 0.12, "end": "down",
                  "land": 10},
    # off the top rope: he lies `ground` art units in front of where you land
    "dive": {"frames": [("dive", 0, 6), ("dive", 1, 20)], "damage": 0.12, "end": "stay_down", "ground": 12,
             "att_end": "rise"},
    "flying knee drop": {"frames": [("flying knee drop", 0, 6), ("flying knee drop", 1, 20)], "damage": 0.11,
                         "end": "stay_down", "ground": 8, "att_end": "rise"},
    # ---- specials and finishers (step 8)
    "military press": {"frames": [("military press", 0, 12), ("military press", 1, 34), ("throw", 0, 8),
                                  ("throw", 1, 14)], "damage": 0.13, "end": "down", "land": 22},
    "bear hug": {"frames": [("bear hug", 0, 16), ("bear hug", 1, 16)] * 3, "damage": 0.10, "end": "release"},
    "powerbomb": {"frames": [("powerbomb", 0, 34), ("powerbomb", 1, 24)], "damage": 0.20, "end": "down",
                  "land": 18},
    "headbutt": {"frames": [("headbutt", 0, 12), ("headbutt", 1, 18)], "damage": 0.09, "end": "stun"},
    "running lariat": {"frames": [("running lariat", 0, 6), ("running lariat", 1, 22)], "damage": 0.20,
                       "end": "down", "land": 16},
    "vertical suplex": {"frames": [("vertical suplex", 0, 34), ("vertical suplex", 1, 18)], "damage": 0.14,
                        "end": "down", "land": -18},
    "hip toss": {"frames": [("hip toss", 0, 10), ("hip toss", 1, 18)], "damage": 0.08, "end": "down",
                 "land": 18},
    "ddt": {"frames": [("ddt", 0, 16), ("ddt", 1, 22)], "damage": 0.20, "end": "down", "land": 2},
    "flying crossbody": {"frames": [("flying crossbody", 0, 6), ("flying crossbody", 1, 18)], "damage": 0.11,
                         "end": "down", "land": 36, "att_end": "fall"},
    "missile dropkick": {"frames": [("missile dropkick", 0, 6), ("missile dropkick", 1, 18)], "damage": 0.14,
                         "end": "down", "land": 36, "att_end": "fall"},
    "shoulder throw": {"frames": [("shoulder throw", 0, 10), ("shoulder throw", 1, 16)], "damage": 0.10,
                       "end": "down", "land": -4},
    # running attacks
    "clothesline": {"frames": [("clothesline", 0, 6), ("clothesline", 1, 18)], "damage": 0.07, "end": "down",
                    "land": 16},
    "dropkick": {"frames": [("dropkick", 0, 6), ("dropkick", 1, 18)], "damage": 0.10, "end": "down",
                 "land": 30, "att_end": "fall"},
    # on a downed opponent: "ground" = how far in front of the attacker he lies (art units)
    "stomp": {"frames": [("stomp", 0, 10), ("stomp", 1, 12)] * 2, "damage": 0.04, "end": "stay_down",
              "ground": 14},
    "elbow drop": {"frames": [("elbow drop", 0, 14), ("elbow drop", 1, 20)], "damage": 0.07, "end": "stay_down",
                   "ground": 10, "att_end": "rise"},
    "knee drop": {"frames": [("knee drop", 0, 14), ("knee drop", 1, 20)], "damage": 0.07, "end": "stay_down",
                  "ground": 12, "att_end": "rise"},
    "seated butt drop": {"frames": [("seated butt drop", 0, 14), ("seated butt drop", 1, 20)], "damage": 0.08,
                         "end": "stay_down", "ground": 2, "att_end": "rise"},
}
SLAMS = {"body slam", "brain buster", "pile driver", "back drop", "shoulder throw", "clothesline", "dropkick",
         "post slam", "dive", "flying knee drop", "military press", "powerbomb", "running lariat",
         "vertical suplex", "hip toss", "ddt", "flying crossbody", "missile dropkick"}
GROUND_OFFSET = {"pin": 12, "boston crab": 10}
HOLDS = {"boston crab": {"offset": 10, "drain": 0.0004, "ground": True},       # about 2.4% a second
         "sleeper hold": {"offset": 9, "drain": 0.0008, "ground": False}}      # about 5% a second (a finisher)

# pins and submissions
KICKOUT_MIN = 3            # even a fresh wrestler has to press a few times
SUB_WIN = 6.0              # push lead that wins a submission (either way)
SUB_DRAIN = 0.0007         # energy per frame the hold takes (about 4% a second)
SUB_MAX = 360              # 6 seconds and he lets go
TAP_UNDER = 0.15           # nobody taps out until he's under 15% (balance pass); before that the hold drains him

TIE_FRAMES = 120           # about 2 seconds
WIN = 4.0                  # push lead that wins the tug of war
CLEAR_LEAD = 0.4           # at the 2-second mark, a lead this big still wins (balance pass)
PRESS_GAP = 6              # at most 10 counted presses a second
AUTO_GAP = 0.3             # energy gap with no meter
TOO_EARLY = 2.5            # receiver's presses count this much more against a big move too early
UNDERDOG = 1.5             # "Don't give up yet!" presses count this much more
LIFT_WEIGHT = {1: 1.0, 2: 1.0, 3: 1.25}   # heavy wrestlers are harder to lift
POWER_PUSH = {1: 0.97, 2: 1.0, 3: 1.05}   # Power: a small push bonus in tie-ups (balance pass: was .95 / 1.1)
THROWN = {1: 4, 2: 0, 3: -2}              # light wrestlers fly farther (mat units)
BREAK_PUSH = 4
DONT_GIVE_UP = 2           # per wrestler per match


def stick_dir(pad):
    if pad.held["up"]:
        return "up"
    if pad.held["down"]:
        return "down"
    if pad.held["left"] or pad.held["right"]:
        return "side"
    return None


def whip_dir(pad, facing):
    """D + an arrow: the rope to whip him into (the nearest of the four). No arrow = the way you face."""
    sx = pad.held["right"] - pad.held["left"]
    sy = pad.held["down"] - pad.held["up"]
    if not (sx or sy):
        return FACING_DIR[facing]
    dx, dy = ARROW_DIR[sx, sy]
    if dx and dy:          # one arrow points between two ropes: lean toward the one you face
        fx, fy = FACING_DIR[facing]
        return (dx, 0) if abs(fx) else (0, dy)
    return dx, dy


def stat(w, name):
    return STATS.get(w.who, {}).get(name, 2)


def place(w, x, y):
    w.x, w.y = ring.clamp(x, y, w.outside)


def face_axis(a, b):
    """turn a toward b along the nearest mat axis and stand b right in front of him, facing back."""
    a.face_toward(b.x, b.y)
    fx, fy = FACING_DIR[a.facing]
    d = a.radius + b.radius
    place(b, a.x + fx * d, a.y + fy * d)
    b.face_toward(a.x, a.y)


class TieUp:
    """Both wrestlers locked up, mashing. a = the player (left side of the meter), b = the CPU."""

    def __init__(self, a, b):
        self.a, self.b = a, b
        stunned = [w for w in (a, b) if w.state == "stunned"]
        face_axis(a, b)
        for w in (a, b):
            w.set_state("grapple")
        self.timer = 0
        self.push = {a: 0.0, b: 0.0}
        self.choice = {a: None, b: None}
        self.last_press = {a: -99, b: -99}
        self.boost = {a: 1.0, b: 1.0}
        self.events = []
        self.auto = None           # the only wrestler whose press counts (no meter)
        if stunned:
            self.auto = b if stunned[0] is a else a
        elif abs(a.energy - b.energy) >= AUTO_GAP:
            fresh, under = (a, b) if a.energy > b.energy else (b, a)
            if under.dont_give_up > 0:
                under.dont_give_up -= 1
                self.boost[under] = UNDERDOG
                self.events.append(("dont_give_up", under))
            else:
                self.auto = fresh

    @property
    def meter(self):
        """-1..1, positive = the player (left) is winning. None when there's no meter."""
        if self.auto:
            return None
        return max(-1.0, min(1.0, (self.push[self.a] - self.push[self.b]) / WIN))

    def press_value(self, w):
        opp = self.b if w is self.a else self.a
        v = (0.5 + w.energy) * POWER_PUSH[stat(w, "power")] * self.boost[w]
        theirs = self.choice[opp] and resolve(opp, w, self.choice[opp])
        if theirs in LIFTS:
            v *= LIFT_WEIGHT[stat(w, "weight")]
        if theirs in HEAVY and w.energy >= HEAVY_SAFE:
            v *= TOO_EARLY
        return v

    def read(self, w, pad):
        """a counted press this frame picks the move; returns True if it counted."""
        for button in ("a", "s", "d"):
            if pad.was_pressed(button):
                if self.timer - self.last_press[w] < PRESS_GAP:
                    return False
                self.last_press[w] = self.timer
                if button == "d" and not w.outside:
                    self.choice[w] = "rope whip"
                    w.whip_to = whip_dir(pad, w.facing)
                elif button == "a" and stick_dir(pad) == "side" and w.outside:
                    self.choice[w] = "post slam"
                else:
                    self.choice[w] = TIEUP_MOVES["a" if button == "d" else button, stick_dir(pad)]
                return True
        return False

    def update(self, pad_a, pad_b):
        """returns ("win", winner, loser, move), ("break",) or None while still struggling."""
        self.timer += 1
        for w, pad in ((self.a, pad_a), (self.b, pad_b)):
            if self.read(w, pad):
                if self.auto is w:
                    return "win", w, self.other(w), resolve(w, self.other(w), self.choice[w])
                if not self.auto:
                    self.push[w] += self.press_value(w)
        m = self.meter
        if m is not None and abs(m) >= 1:
            win = self.a if m > 0 else self.b
            lose = self.other(win)
            theirs = self.choice[lose] and resolve(lose, win, self.choice[lose])
            if theirs in HEAVY and win.energy >= HEAVY_SAFE:
                self.events.append(("reversal", lose))
            return "win", win, lose, resolve(win, lose, self.choice[win] or "headlock")
        if self.timer >= TIE_FRAMES:
            m = self.meter
            if m is not None and abs(m) >= CLEAR_LEAD:     # time's up: a clear leader still gets his move
                win = self.a if m > 0 else self.b
                return "win", win, self.other(win), resolve(win, self.other(win), self.choice[win] or "headlock")
            return ("break",)                               # too close to call: they break apart
        return None

    def other(self, w):
        return self.b if w is self.a else self.a

    def break_apart(self):
        a, b = self.a, self.b
        fx, fy = FACING_DIR[a.facing]
        place(a, a.x - fx * BREAK_PUSH, a.y - fy * BREAK_PUSH)
        place(b, b.x + fx * BREAK_PUSH, b.y + fy * BREAK_PUSH)
        for w in (a, b):
            w.set_state("stand")

    def draw(self, surf, pairs, tick):
        """the tie-up from the player's side; a little shove back and forth."""
        fx, fy = ring.to_screen(self.a.x, self.a.y, self.a.z)
        pairs.get(self.a.who, self.b.who).draw(surf, "tie-up", self.a.facing, (tick // 8) % 2, (fx, fy))


class Move:
    """One two-person move playing out: the attacker's pair sheet, frame by frame, then the result."""

    def __init__(self, name, att, vic):
        self.name, self.att, self.vic = name, att, vic
        self.spec = MOVES[name]
        self.frames = self.spec["frames"]
        self.i = 0
        self.t = 0
        if name == "rope whip":
            att.turn_to(att.whip_to)
        elif "ground" in self.spec:
            stand_over(att, vic, self.spec["ground"])
        else:
            att.face_toward(vic.x, vic.y)
        for w in (att, vic):
            w.set_state("grapple")
        self.length = sum(f[2] for f in self.frames)
        self.hit_at = self.length - self.frames[-1][2]     # the damage lands on the last frame

    @property
    def row(self):
        return self.frames[self.i][:2]

    def update(self):
        """returns True when the move is over."""
        self.t += 1
        elapsed = 0
        for k, f in enumerate(self.frames):
            elapsed += f[2]
            if self.t < elapsed:
                self.i = k
                break
        else:
            self.finish()
            return True
        if self.t == self.hit_at and self.spec["damage"]:
            self.vic.energy = max(0.0, self.vic.energy - self.spec["damage"])
            self.vic.since_hit = 0
        return False

    def finish(self):
        att, vic, spec = self.att, self.vic, self.spec
        fx, fy = FACING_DIR[att.facing]
        end = spec["end"]
        att.set_state("stand")
        vic.hits_taken = 0
        vic.stun_left = 0
        if spec.get("att_end") == "rise":
            att.set_state("getup")
        elif spec.get("att_end") == "fall":
            att.knock_down(auto=True)
            att.t = 10
        if end == "stay_down":
            vic.stay_down()
        elif end == "down":
            land = spec["land"] * C3
            clear = att.radius + vic.radius + 3
            land = (max(abs(land), clear) + THROWN[stat(vic, "weight")]) * (1 if land >= 0 else -1)
            place(vic, att.x + fx * land, att.y + fy * land)
            vic.face_toward(att.x, att.y)
            vic.knock_down()
            vic.t = 10                  # already lying flat
        elif end == "whipped":
            place(vic, att.x + fx * spec["land"] * C3, att.y + fy * spec["land"] * C3)
            vic.start_whipped((fx, fy))
        elif end == "stun":
            gap = att.radius + vic.radius + 2
            place(vic, att.x + fx * gap, att.y + fy * gap)
            vic.face_toward(att.x, att.y)
            vic.stun_left = 180
            vic.set_state("stunned")
        else:                           # knee lift staggers him back; a headlock lets go
            gap = att.radius + vic.radius + (6 if end == "stagger" else 2)
            place(vic, att.x + fx * gap, att.y + fy * gap)
            vic.face_toward(att.x, att.y)
            vic.set_state("hit")

    def draw(self, surf, pairs, tick):
        fx, fy = ring.to_screen(self.att.x, self.att.y, self.att.z)
        row, frame = self.row
        pairs.get(self.att.who, self.vic.who).draw(surf, row, self.att.facing, frame, (fx, fy))



def stand_over(att, vic, offset):
    """step the attacker up to a downed opponent so the pair sheet lines up: he lies `offset` art units ahead."""
    att.face_toward(vic.x, vic.y)
    fx, fy = FACING_DIR[att.facing]
    place(att, vic.x - fx * offset * C3, vic.y - fy * offset * C3)
    att.face_toward(vic.x, vic.y)


def kickout_presses(energy):
    """the get-up numbers: 20 presses at 0%, 8 at 30%, and on down to a few when you're fresh."""
    return max(KICKOUT_MIN, round(20 - energy * 40))


class Pin:
    """The cover. The ref walks over and counts; only the pinned man mashes (A, S or D) to kick out."""
    name = "pin"

    def __init__(self, att, vic, ref):
        self.att, self.vic, self.ref = att, vic, ref
        stand_over(att, vic, GROUND_OFFSET["pin"])
        for w in (att, vic):
            w.set_state("grapple")
        self.needed = kickout_presses(vic.energy)
        self.presses = 0
        self.last = -99
        self.timer = 0
        ref.count_pin(vic, FACING_DIR[att.facing])

    @property
    def progress(self):
        return self.presses / self.needed

    def update(self, pad_att, pad_vic):
        """returns "kickout", "three" or None."""
        self.timer += 1
        if any(pad_vic.was_pressed(b) for b in ("a", "s", "d")) and self.timer - self.last >= PRESS_GAP:
            self.last = self.timer
            self.presses += 1
        if self.presses >= self.needed:
            return "kickout"
        if self.ref.count >= 3:
            return "three"
        return None

    def kick_out(self):
        self.att.set_state("getup")
        self.vic.stay_down()
        self.ref.stop()

    def draw(self, surf, pairs, tick):
        fx, fy = ring.to_screen(self.att.x, self.att.y, self.att.z)
        pairs.get(self.att.who, self.vic.who).draw(surf, "pin", self.att.facing, (tick // 20) % 2, (fx, fy))


class Submission:
    """The Boston crab (or Jim's sleeper hold): both mash. The hold drains the victim; he escapes if he
    pushes the bar to his side, and taps out if it reaches the attacker's."""

    def __init__(self, att, vic, ref, name="boston crab"):
        self.att, self.vic, self.ref = att, vic, ref
        self.name = name
        self.hold = HOLDS[name]
        if self.hold["ground"]:
            stand_over(att, vic, self.hold["offset"])
        else:                       # from a tie-up: he's right in front, and they sit down together
            att.face_toward(vic.x, vic.y)
            fx, fy = FACING_DIR[att.facing]
            place(vic, att.x + fx * self.hold["offset"] * C3, att.y + fy * self.hold["offset"] * C3)
        for w in (att, vic):
            w.set_state("grapple")
        self.push = {att: 0.0, vic: 0.0}
        self.last = {att: -99, vic: -99}
        self.timer = 0
        ref.watch_submission(vic, FACING_DIR[att.facing])

    def lead(self, w):
        """-1..1 from w's side: +1 = w has won."""
        other = self.vic if w is self.att else self.att
        return max(-1.0, min(1.0, (self.push[w] - self.push[other]) / SUB_WIN))

    def update(self, pad_att, pad_vic):
        """returns "escape", "tapout" or None."""
        self.timer += 1
        self.vic.energy = max(0.0, self.vic.energy - self.hold["drain"])
        for w, pad in ((self.att, pad_att), (self.vic, pad_vic)):
            if any(pad.was_pressed(b) for b in ("a", "s", "d")) and self.timer - self.last[w] >= PRESS_GAP:
                self.last[w] = self.timer
                self.push[w] += 0.5 + w.energy
        if self.lead(self.vic) >= 1 or self.timer >= SUB_MAX:
            return "escape"
        if self.vic.energy >= TAP_UNDER:        # too fresh to give up: the bar stops short of his end
            self.push[self.att] = min(self.push[self.att], self.push[self.vic] + SUB_WIN * 0.95)
        elif self.lead(self.att) >= 1:
            return "tapout"
        return None

    def release(self):
        self.att.set_state("stand")
        self.vic.stay_down()
        self.ref.stop()

    def draw(self, surf, pairs, tick):
        fx, fy = ring.to_screen(self.att.x, self.att.y, self.att.z)
        pairs.get(self.att.who, self.vic.who).draw(surf, self.name, self.att.facing, (tick // 12) % 2, (fx, fy))
