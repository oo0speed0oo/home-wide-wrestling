"""The CPU opponent (design doc: CPU and balancing).

It presses the same buttons a player would and plays by the same rules: the same energy weighting,
the same get-up numbers, "Don't give up yet!" too. It never cheats: no hidden damage and no mashing
faster than a person could (always under the 10-a-second cap).

It gets a little better at a few simple things each match:
                         match 1   match 2   nemesis
  mash speed (presses/s)    4        5.5        7
  reaction delay           0.5 s    0.35 s     0.25 s
  blocks your strikes      20%      40%        60%
  big move too early       30%      15%        5%      (a mistake you can punish)
Easy / Medium / Hard shifts the whole ladder one step (decided Oct 5): Medium is the table above,
Easy is one step softer, Hard one step tougher.

Every wrestler has a habit you can learn and beat:
  Mighty Mike     always goes for tie-ups. Stay out of reach with strikes: his reach is short.
  Nimble Niko     climbs the top rope a lot. Run in and knock him off.
  Jim "The Goat"  goes for holds when you're down, and takes his time. Get up fast and he's left open.
  Big Beefy Stew  charges at you constantly. Block, and he's wide open after the push-back.
Taunting from far away annoys him (the taunt's bait): for a few seconds he charges at you, which
sets up a counter.

Test brains: WANDER just walks around, STILL stands there (a punching bag).
"""
import math
import random

from . import ring
from .grapple import HEAVY, TIEUP_MOVES
from .specials import FINISH_UNDER, resolve
from .wrestler import ARROW_DIR, CATCH, DIVE_RANGE, EDGE, FACING_DIR, GROUND_REACH, RUN_ATTACKS, STRIKES

BUTTONS = ("up", "down", "left", "right", "a", "s", "d", "start")
FPS = 60

# the ladder: index 1..3 is the design doc's table, 0 and 4 are the steps past each end for Easy and Hard
LADDER = [
    {"mash": 3.0, "react": 0.65, "block": 0.10, "early": 0.45},
    {"mash": 4.0, "react": 0.50, "block": 0.20, "early": 0.30},    # match 1
    {"mash": 5.5, "react": 0.35, "block": 0.40, "early": 0.15},    # match 2
    {"mash": 7.0, "react": 0.25, "block": 0.60, "early": 0.05},    # nemesis
    {"mash": 8.5, "react": 0.18, "block": 0.70, "early": 0.02},
]
DIFFICULTIES = ("EASY", "MEDIUM", "HARD")
SHIFT = {"EASY": -1, "MEDIUM": 0, "HARD": 1}
MATCH_NAMES = {1: "MATCH 1", 2: "MATCH 2", 3: "NEMESIS"}

HABIT = {"mike": "tie-ups", "niko": "top rope", "jim": "holds", "stew": "charges"}
FINISHER_INPUT = {"mike": (["down"], "s"), "niko": (["up"], "s"), "jim": ([], "a")}   # tie-up finishers
TIEUP_INPUTS = [([], "s"), (["up"], "s"), (["left"], "s"), (["down"], "s"),
                ([], "a"), (["up"], "a"), ([], "d"), (["up"], "d")]
BAIT_FRAMES = 300           # annoyed by a taunt for 5 seconds
OPEN_AFTER = 70             # Stew after being blocked, Jim after you get up on him: frames standing there


def skill_for(match, difficulty):
    """match 1..3 (3 = the nemesis), difficulty EASY/MEDIUM/HARD -> the CPU's numbers."""
    return LADDER[max(0, min(len(LADDER) - 1, match + SHIFT[difficulty]))]


class PadState:
    """looks like Controls to a Wrestler: held buttons plus buttons pressed this frame."""

    def __init__(self):
        self.held = {b: False for b in BUTTONS}
        self.pressed = set()

    def was_pressed(self, button):
        return button in self.pressed

    def set(self, held):
        self.pressed = {b for b in held if not self.held[b]}
        for b in self.held:
            self.held[b] = b in held


def arrows_toward(dx, dy):
    """the arrows that walk closest to mat direction (dx, dy)."""
    (sx, sy), _ = max(ARROW_DIR.items(), key=lambda kv: (kv[1][0] * dx + kv[1][1] * dy) / math.hypot(*kv[1]))
    held = []
    if sx:
        held.append("right" if sx > 0 else "left")
    if sy:
        held.append("down" if sy > 0 else "up")
    return held


class Brain:
    MODES = ("FIGHT", "WANDER", "STILL")

    def __init__(self, me, opponent, mode="FIGHT", match=1, difficulty="MEDIUM"):
        self.me, self.opp = me, opponent
        me.can_run = False          # only runs on purpose, never by a stray double-tap
        self.mode = mode
        self.set_level(match, difficulty)
        self.habit = HABIT.get(me.who)
        self.pad = PadState()
        self.mash_acc = 0.0
        self.react = 0              # frames before he can act on what just changed
        self.last_seen = None
        self.open_t = 0             # standing there, open (his habit's weak spot)
        self.annoyed = 0            # taunted: charging at you
        self.target = None
        self.rest = 60
        self.cooldown = 30
        self.will_block = None      # decided once per incoming attack
        self.block_for = 0
        self.plan = None            # tie-up: (arrows, button) to mash
        self.grab = False           # walking in for a tie-up instead of striking
        self.will_catch = None
        self.seq = []               # button presses queued up (a double-tap to run)
        self.run_with = None        # clothesline or dropkick planned for this run
        self.ground_cool = 0
        self.countout = 0           # seconds counted so far (the match tells us)
        self.follow = None          # go out after him? decided once per trip
        self.go_top = None          # climb for a dive? decided once per knockdown
        self.climb_up = False       # Niko heading up the turnbuckle while you're standing
        self.backoff = 0            # stepping away to get room for a charge
        self.top_wait = 0

    def set_level(self, match, difficulty):
        self.match, self.difficulty = match, difficulty
        self.skill = skill_for(match, difficulty)

    @property
    def level_name(self):
        return f"{MATCH_NAMES[self.match]} {self.difficulty}"

    def bait(self):
        """the player finished a taunt."""
        self.annoyed = BAIT_FRAMES

    # ------------------------------------------------------------------ every frame
    def mash(self):
        """True on the frames he presses, at his mash speed."""
        self.mash_acc += self.skill["mash"] / FPS
        if self.mash_acc >= 1.0 and not self.pad.pressed:
            self.mash_acc -= 1.0
            return True
        return False

    def watch(self):
        """he reacts to changes a moment late (the reaction delay)."""
        seen = (self.opp.state, self.opp.outside, self.me.state in ("stand", "walk"))
        if seen != self.last_seen:
            self.last_seen = seen
            self.react = round(self.skill["react"] * FPS)
        elif self.react > 0:
            self.react -= 1

    def think(self):
        me = self.me
        self.watch()
        self.annoyed = max(0, self.annoyed - 1)
        if me.state == "recoil" and self.habit == "charges":
            self.open_t = OPEN_AFTER            # pushed back: Stew just stands there for a moment
        if me.state in ("down", "stunned"):
            self.pad.set(("a",) if self.mode != "STILL" and self.mash() else ())
            return self.pad
        if me.state == "grapple":
            self.grab = False
            self.pad.set(self.mash_tieup() if self.mode != "STILL" else [])
            return self.pad
        self.plan = None
        if self.seq:
            me.can_run = True
            self.pad.set(self.seq.pop(0))
            return self.pad
        me.can_run = False
        if self.mode == "STILL":
            self.pad.set(())
            return self.pad
        if me.state == "top":
            self.pad.set(self.on_top())
            return self.pad
        if me.outside and (self.countout >= 12 or not self.opp.outside):
            self.pad.set(self.climb_back_in())
            return self.pad
        if self.open_t > 0 and me.state in ("stand", "walk"):
            self.open_t -= 1
            self.pad.set(())
            return self.pad
        self.pad.set(self.fight() if self.mode == "FIGHT" else self.wander())
        return self.pad

    # ------------------------------------------------------------------ wander
    def pick_target(self):
        lo, hi = EDGE + 6, ring.RING - EDGE - 6
        for _ in range(20):
            x, y = random.uniform(lo, hi), random.uniform(lo, hi)
            if math.hypot(x - self.opp.x, y - self.opp.y) > 24:
                return x, y
        return random.uniform(lo, hi), random.uniform(lo, hi)

    def wander(self):
        me = self.me
        if self.rest > 0:
            self.rest -= 1
            return []
        if self.target is None:
            self.target = self.pick_target()
        dx, dy = self.target[0] - me.x, self.target[1] - me.y
        if math.hypot(dx, dy) < 3 or me.blocked:
            self.target = None
            self.rest = random.randint(30, 110)
            return []
        return arrows_toward(dx, dy)

    # ------------------------------------------------------------------ tie-up
    def mash_tieup(self):
        """hold a direction and mash a button. Big moves only once you're worn down, except for the
        occasional too-early mistake."""
        me, opp = self.me, self.opp
        if self.plan is None and opp.energy < FINISH_UNDER and me.who in FINISHER_INPUT:
            self.plan = FINISHER_INPUT[me.who]          # he's hurt: go for the finisher
        if self.plan is None:
            early_ok = opp.energy < 0.7 or random.random() < self.skill["early"]
            options = []
            for arrows, button in TIEUP_INPUTS:
                move = "rope whip" if button == "d" else TIEUP_MOVES[button, "side" if arrows == ["left"] else
                                                                  (arrows[0] if arrows else None)]
                move = resolve(me, opp, move)
                if move in HEAVY and not early_ok:
                    continue
                weight = 3 if (self.habit == "holds" and button == "a" and not arrows) else 1
                options += [(arrows, button)] * weight
            self.plan = random.choice(options)
        arrows, button = self.plan
        return arrows + ([button] if self.mash() else [])

    # ------------------------------------------------------------------ fight
    def fight(self):
        me, opp = self.me, self.opp
        gap = me.gap_to(opp)
        self.cooldown -= 1
        # incoming punch, kick or running attack: block it sometimes (decided once per attack)
        incoming = (opp.state in STRIKES and gap <= opp.reach["kick"] + 4) or \
                   (opp.state == "runatk" and gap <= 30 and opp.facing_toward(me, 0.7))
        if incoming and me.state in ("stand", "walk", "block"):
            if self.will_block is None:
                self.will_block = random.random() < self.skill["block"]
            if self.will_block:
                self.block_for = 20
        elif not incoming:
            self.will_block = None
        if self.block_for > 0:
            self.block_for -= 1
            return ["d"]
        if me.state in ("run", "runatk"):
            return self.running(gap)
        if opp.outside != me.outside:
            return self.opp_outside()
        self.follow = None
        self.ground_cool -= 1
        if opp.state == "down" and opp.t >= 10:
            if self.go_top is None:
                chance = 0.8 if self.habit == "top rope" else 0.15
                self.go_top = not me.outside and random.random() < chance
            if self.go_top:
                return self.to_corner()
            return self.on_ground(gap)
        if opp.state == "getup" and self.habit == "holds" and gap <= GROUND_REACH:
            self.open_t = OPEN_AFTER            # Jim was still setting up his hold: left open
            return []
        self.go_top = None
        if opp.state in ("getup", "out"):
            return []
        if opp.state in ("whipped", "run") and gap <= CATCH + 6:
            if self.will_catch is None:
                self.will_catch = random.random() < 0.4 + self.skill["block"] / 2
            if self.will_catch and me.can_catch():
                return ["a"]
            return []
        self.will_catch = None
        toward = arrows_toward(opp.x - me.x, opp.y - me.y)
        if self.react > 0:
            return toward if gap > me.reach["kick"] + 4 else []        # still catching up with what happened
        if self.grab:
            if gap > me.reach["kick"] + 20:
                self.grab = False
            return toward
        # Niko's habit: up the turnbuckle even when you're standing
        if self.habit == "top rope" and gap > 16 and not me.outside and random.random() < 0.006:
            self.climb_up = True
        if self.climb_up:
            return self.to_corner()
        if self.habit == "charges" or self.annoyed or self.backoff:
            charge = self.maybe_charge(gap)     # charging comes first for Stew and anyone you've taunted
            if charge is not None:
                return charge
        if gap <= me.reach["punch"]:
            grab_chance = 0.08 if self.habit == "tie-ups" else 0.02
            if self.cooldown <= 0 and random.random() < grab_chance:
                self.grab = True            # walk in and lock up
                return toward
            if self.cooldown <= 0 and random.random() < (0.03 if self.habit == "tie-ups" else 0.08):
                self.cooldown = random.randint(20, 50)
                return [random.choice("aas")]
            return []
        if self.habit == "tie-ups" and gap <= 30:
            self.grab = True                # Mike: straight in for the lock-up
            return toward
        if gap <= me.reach["kick"] and self.cooldown <= 0 and random.random() < 0.05:
            self.cooldown = random.randint(20, 50)
            return ["s"]
        if gap > 40 and random.random() < 0.004:
            return ["d"]                    # show off from far away
        charge = self.maybe_charge(gap)
        return toward if charge is None else charge

    def maybe_charge(self, gap):
        """run at him: Stew all the time, anyone who's been taunted, and Stew to finish.
        Too close to get going? Back off first to make room."""
        me, opp = self.me, self.opp
        eager = self.habit == "charges" or self.annoyed
        away = arrows_toward(me.x - opp.x, me.y - opp.y)
        if self.backoff > 0:
            self.backoff -= 1
            if gap < 34 and self.backoff:
                return away
            self.backoff = 0
        if opp.state not in ("stand", "walk", "taunt", "block"):
            return None
        if gap <= 24:
            if eager and random.random() < 0.05:
                self.backoff = 50
                return away
            return None
        if gap >= 75:
            return None
        finishing = opp.energy < FINISH_UNDER and me.who == "stew"
        chance = 0.006
        if self.habit == "charges":
            chance = 0.05
        if self.annoyed:
            chance = max(chance, 0.05)
        if random.random() >= chance:
            return None
        arrows = self.axis_arrows()
        if not arrows:
            if self.habit == "charges" or self.annoyed:
                return self.line_up()
            return None
        self.run_with = "clothesline" if finishing or self.habit == "charges" else \
            random.choice(("clothesline", "dropkick"))
        self.seq = [arrows, arrows, [], arrows, arrows]    # double-tap toward him
        return []

    # ------------------------------------------------------------------ running and the ground
    def axis_arrows(self):
        """the two arrows that run straight at the opponent, if he's lined up along one of the ropes' lines."""
        me, opp = self.me, self.opp
        dx, dy = opp.x - me.x, opp.y - me.y
        d = max(FACING_DIR.values(), key=lambda v: v[0] * dx + v[1] * dy)
        side = abs(dx * d[1] - dy * d[0])           # how far off the line he is
        if side > 6:
            return None
        for (sx, sy), md in ARROW_DIR.items():
            if md == d:
                return (["right"] if sx > 0 else ["left"]) + (["down"] if sy > 0 else ["up"])
        return None

    def line_up(self):
        """step sideways until he's straight down a rope line from me."""
        me, opp = self.me, self.opp
        dx, dy = opp.x - me.x, opp.y - me.y
        if abs(dx) > abs(dy):
            return arrows_toward(0, dy)
        return arrows_toward(dx, 0)

    def running(self, gap):
        me, opp = self.me, self.opp
        if me.state == "runatk":
            return []
        kind = "clothesline" if self.run_with == "clothesline" else "dropkick"
        reach = RUN_ATTACKS[resolve(me, opp, kind)]["reach"]
        if me.facing_toward(opp, 0.8) and gap <= reach + 6:
            return ["a" if kind == "clothesline" else "s"]
        if not me.facing_toward(opp, 0.3) and not me.bounce:
            return ["d"]                    # he's not in my path: stop
        return []

    def on_ground(self, gap):
        """opponent down: walk over, then pin him if he's low, otherwise stomp, drop or crab him.
        Jim takes his time setting up a hold."""
        me, opp = self.me, self.opp
        if gap > GROUND_REACH - 2:
            return arrows_toward(opp.x - me.x, opp.y - me.y)
        if self.ground_cool > 0 or self.react > 0:
            return []
        if self.habit == "holds":
            self.ground_cool = random.randint(40, 70)
            if opp.energy < 0.3 and random.random() < 0.5:
                return ["a"]                                    # pin
            return ["left", "a"] if random.random() < 0.7 else ["s"]   # the crab, mostly
        self.ground_cool = random.randint(20, 50)
        if opp.energy < 0.35 and random.random() < 0.6:
            return ["a"]                                        # pin
        return random.choice([["up", "a"], ["s"], ["left", "a"], ["up", "a"]])   # stomp, drop, crab

    # ------------------------------------------------------------------ ropes, floor and corners
    def climb_back_in(self):
        """walk to the apron and lean on it until he climbs through."""
        me = self.me
        R = ring.RING
        if me.y <= R - EDGE:
            return ["up", "left"]           # on the X-side floor: lean back in through those ropes
        if me.x <= R - EDGE:
            return ["up", "right"]          # on the Y-side floor
        return arrows_toward(-1, 0) if me.x - R < me.y - R else arrows_toward(0, -1)   # round the corner first

    def opp_outside(self):
        """he's on the floor and I'm in the ring: follow him out sometimes, otherwise wait at the ropes."""
        me, opp = self.me, self.opp
        if self.follow is None:
            self.follow = random.random() < 0.4
        R = ring.RING
        if opp.x > R:
            target = (R - EDGE, min(R - EDGE, max(EDGE, opp.y)))
            out_arrows = ["down", "right"]
        else:
            target = (min(R - EDGE, max(EDGE, opp.x)), R - EDGE)
            out_arrows = ["down", "left"]
        dx, dy = target[0] - me.x, target[1] - me.y
        if math.hypot(dx, dy) > 3:
            return arrows_toward(dx, dy)
        return out_arrows if self.follow and self.countout < 10 else []

    def to_corner(self):
        """walk into the nearest corner (leaning into it climbs)."""
        me = self.me
        name, (cx, cy) = ring.nearest_corner(me.x, me.y)
        if math.hypot(cx - me.x, cy - me.y) > (80 if self.habit == "top rope" else 45):
            self.go_top = False
            self.climb_up = False
            return []
        return arrows_toward(cx - me.x, cy - me.y)

    def on_top(self):
        """up on the turnbuckle: dive once he's in range, or soon anyway. Niko waits longer up there."""
        me, opp = self.me, self.opp
        self.top_wait += 1
        in_range = not opp.outside and math.hypot(opp.x - me.x, opp.y - me.y) <= DIVE_RANGE - 6
        patience = 180 if self.habit == "top rope" else 120
        if (in_range and self.top_wait > max(20, round(self.skill["react"] * FPS))) or self.top_wait > patience:
            self.top_wait = 0
            self.go_top = None
            self.climb_up = False
            return [random.choice("as")]
        return []
