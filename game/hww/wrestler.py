"""A wrestler in the ring: where he stands on the mat, which way he faces, and what he's doing.

Movement (design doc, Movement, ropes, and outside):
- free 8-direction walking; up on the arrow keys is up on the screen
- double-tap an arrow to run straight at the rope you're facing; bounce off all four ropes
  as long as you like; D stops the run
- the 4 facings are the screen diagonals, which are exactly the mat's two axes
- standing still or attacking, you turn to face the opponent by yourself (decided Oct 5)

Striking (design doc, Striking, stun, and knockdowns):
- A punch, S kick. D blocks when close, taunts when far
- hits don't freeze you: after a moment you can walk out of a hit
- 3 unblocked hits in a row stun for 5 seconds (mash A/S to shorten it); one more hit knocks you down
- block: no damage; can't be held more than about 3 seconds. 3 blocked hits in a row push the attacker back
- getting up: 30% energy or more = up on your own; under 30% = mash (get-up numbers), another try if you fail
- every 10 seconds without being hit, energy goes up 10%

Running and the ground (design doc: Controls, Win conditions):
- running: A clothesline, S dropkick (a missed dropkick lands you on your back), D stops
- two runners who collide both bump; if one is heavier, the lighter one goes down
- opponent down: A pin, Up/Down+A stomp, Left/Right+A Boston crab, S (with or without Left/Right)
  knee drop / elbow drop (Stew: seated butt drop)

Ropes, outside and the top rope (design doc: Movement, ropes, and outside; Top rope):
- lean on a front rope (keep walking into it) to climb out to the floor; outside, walk into the apron
  to climb back in. Same sprite both ways, just a different position
- walk into a corner (or press Up there) to climb to the top. A diving body attack, S; flying knee
  drop, A; walk away from the corner to climb down. Anyone who hits you up there knocks you off,
  to the floor outside near that turnbuckle
"""
import math

from . import ring, specials

# body stats, rated 1-3 (design doc: Body type affects gameplay)
STATS = {
    "mike": {"speed": 2, "power": 3, "weight": 2},
    "niko": {"speed": 3, "power": 1, "weight": 1},
    "jim": {"speed": 2, "power": 2, "weight": 2},
    "stew": {"speed": 1, "power": 2, "weight": 3},
}

BODY_RADIUS = {"mike": 6, "niko": 5, "jim": 6, "stew": 8, "ref": 5}   # on the mat; wrestlers can't overlap
# how far past the two bodies a punch / kick reaches. Mike is short, so he has to get close (balance note).
REACH = {"mike": (7, 9), "jim": (8, 11), "stew": (8, 11), "niko": (11, 15)}     # balance pass: Mike 6 -> 7,
#                                                                                   Niko 10/13 -> 11/15
CLOSE = 14                  # gap under which D blocks; farther away D taunts
CATCH = 10                  # gap for a shoulder throw on someone running at you
GROUND_REACH = 14           # gap to a downed opponent for ground moves
# running attacks: frames you keep flying forward looking for him, and how far ahead it reaches
RUN_ATTACKS = {"clothesline": {"length": 16, "reach": 4}, "dropkick": {"length": 18, "reach": 10},
               "running lariat": {"length": 16, "reach": 5}, "flying crossbody": {"length": 20, "reach": 14}}
STUMBLE_FRAMES = 18         # a missed clothesline
DROP = {"mike": "elbow drop", "jim": "knee drop", "niko": "knee drop", "stew": "seated butt drop"}

PUSH_THROUGH = 20           # frames leaning on the ropes (or into a corner) before you go through / up
CROSS_FRAMES = 30           # over the ropes, in or out
CLIMB_FRAMES = 30
TOP_Z = 24                  # standing on the top turnbuckle
CORNER_IN = 6               # where you stand on the corner, in from the post
DIVE_FRAMES = 26
DIVE_RANGE = 56             # how far a dive can reach
DIVE_DIST = 34              # where you land when there's nobody to aim at
FALL_FRAMES = 24
FALL_DAMAGE = 0.06          # knocked off the top to the floor
CRASH_DAMAGE = 0.05         # a dive that hits nothing but mat

WALK_SPEED = {1: 0.50, 2: 0.60, 3: 0.72}   # mat units per frame (the mat is 104 across)
RUN_SPEED = {1: 1.05, 2: 1.25, 3: 1.45}
EDGE = ring.EDGE            # how close to the ropes your feet can get
DOUBLE_TAP = 14             # frames between taps that count as a double-tap
BOUNCE_FRAMES = 5           # held against the rope for a moment before springing back

# strikes: total frames, the frame the blow lands, damage (share of full energy, before Power)
STRIKES = {"punch": {"length": 20, "impact": 8, "damage": 0.04},
           "kick": {"length": 28, "impact": 12, "damage": 0.06}}
POWER = {1: 0.9, 2: 1.0, 3: 1.2}           # strike damage by Power (balance pass: Niko's 0.85 -> 0.9)
HYPE = 1.5                  # a finished taunt makes your next hit this much bigger

HIT_FRAMES = 14             # getting hit (you can walk out of it after HIT_LOCK)
HIT_LOCK = 5
RECOIL_FRAMES = 24          # pushed back after 3 blocked hits
RECOIL_PUSH = 6
STUN_FRAMES = 300           # 5 seconds
STUN_MASH = 12              # each A/S press while stunned takes this many frames off
BLOCK_MAX = 180             # 3 seconds
TAUNT_FRAMES = 72
TAUNT_ENERGY = 0.03
DOWN_FRAMES = 40            # lying there before you can try to get up
AUTO_GETUP = 30             # then this long more if you have 30% or more
GETUP_WINDOW = 300          # 5 seconds to mash up
GETUP_FRAMES = 24
LOW = 0.3
RECOVER_EVERY = 600         # 10 seconds without being hit...
RECOVER = 0.10              # ...gives back 10%

# facing -> the mat direction it points along
FACING_DIR = {"down-right": (1, 0), "up-left": (-1, 0), "down-left": (0, 1), "up-right": (0, -1)}

# arrows (screen x, screen y) -> mat direction. Two arrows together walk along a rope, the same way
# the 4 facings point; one arrow walks straight up, down, left or right on the screen.
ARROW_DIR = {
    (1, 1): (1, 0), (-1, -1): (-1, 0), (-1, 1): (0, 1), (1, -1): (0, -1),
    (1, 0): (1, -1), (-1, 0): (-1, 1), (0, 1): (1, 1), (0, -1): (-1, -1),
}

# state -> sprite row
ROW = {"stand": "stand", "walk": "walk", "run": "run", "punch": "punch", "kick": "kick", "block": "block",
       "taunt": "victory", "hit": "hit", "recoil": "hit", "stunned": "stunned", "down": "knocked down",
       "getup": "get up", "grapple": "tie-up", "whipped": "run", "stumble": "clothesline",
       "victory": "victory", "out": "knocked down", "ropes": "climb", "climb": "climb", "descend": "climb",
       "top": "on top rope", "fall": "being thrown", "landed": "knocked down"}
LOOP = {"stand": 24, "walk": 10, "run": 6, "victory": 18, "ropes": 8, "climb": 8, "descend": 8, "top": 24, "whipped": 6, "grapple": 8, "block": 20, "taunt": 18, "stunned": 16}
# states where you're on your way somewhere and can't be controlled
TRAVEL = {"ropes", "climb", "descend", "fly", "fall", "landed"}
# states a punch or kick can land on
HITTABLE = {"stand", "walk", "run", "whipped", "runatk", "climb", "top", "punch", "kick", "block", "taunt", "hit", "recoil", "stunned"}


def getup_presses(energy):
    """get-up numbers: 0% = 20 presses, 10% = 16, 20% = 12, 30% = 8 (all within 5 seconds)."""
    return max(8, round(20 - energy * 40))


class Wrestler:
    def __init__(self, who, x, y, facing="down-right"):
        self.who = who
        self.x, self.y = x, y
        self.z = 0.0                # height above the mat (the floor outside is ring.FLOOR_Z)
        self.outside = False
        self.vert, self.horiz = facing.split("-")
        self.opponent = None
        self.state = "stand"
        self.t = 0                  # frames in this state
        self.anim_tick = 0
        self.run_dir = (0, 0)
        self.bounce = 0             # frames left pressed into the ropes
        self.last_tap = {}          # arrow -> frame it was last pressed
        self.clock = 0
        self.energy = 1.0           # 0..1, shown as 24 pips
        self.radius = BODY_RADIUS.get(who, 6)
        self.blocked = False        # bumped into the other wrestler this frame
        self.can_run = True
        stats = STATS.get(who, {"speed": 2, "power": 2, "weight": 2})
        self.walk_speed = WALK_SPEED[stats["speed"]]
        self.run_speed = RUN_SPEED[stats["speed"]]
        self.power = POWER[stats["power"]]
        self.reach = dict(zip(("punch", "kick"), REACH.get(who, (8, 11))))
        # fighting
        self.strike = None          # "punch"/"kick" on the frame the blow lands; the match checks if it connects
        self.hype = False
        self.score = 0
        self.hits_taken = 0         # unblocked hits in a row (3 = stunned)
        self.blocked_hits = 0       # my hits blocked in a row (3 = pushed back)
        self.block_locked = False   # held block too long: let go of D first
        self.stun_left = 0
        self.since_hit = 0
        self.mash_needed = 0        # get-up mashing (0 = getting up on your own)
        self.mashes = 0
        self.try_start = 0
        self.events = []            # things that just happened, for the announcer and score
        # grappling
        self.request = None         # a two-person move to start (the match starts it), e.g. shoulder throw
        self.whip_to = (1, 0)
        self.whip_bounces = 0
        self.dont_give_up = 2       # "Don't give up yet!" uses left this match
        self.run_kind = None        # clothesline / dropkick while flying at him
        self.force_auto = False     # down from your own missed dropkick: you just get up
        self.saved_down = None      # get-up progress while a ground move is being done to him
        # ropes, floor and corners
        self.push_t = 0             # frames leaning on the ropes / into a corner
        self.path = None            # (x0, y0, z0, x1, y1, z1, arc, frames) while travelling
        self.cross_out = False
        self.corner = None          # (x, y) of the post you're on
        self.dive_kind = None       # "dive" or "flying knee drop"

    # ------------------------------------------------------------------ looks
    @property
    def facing(self):
        return f"{self.vert}-{self.horiz}"

    @property
    def move(self):
        if self.state == "runatk":
            return self.run_kind
        if self.state == "fly":
            return {"dive": "dive", "missile dropkick": "missile dropkick"}.get(self.dive_kind, "knee drop")
        return ROW[self.state]

    @property
    def frame(self):
        s, t = self.state, self.t
        if s in LOOP:
            return self.anim_tick // LOOP[s]
        if s in STRIKES:
            return 0 if t < STRIKES[s]["impact"] else 1
        if s in ("hit", "recoil"):
            return 0 if t < 7 else 1
        if s == "down":
            return 0 if t < 10 else 1
        if s == "out":
            return 1
        if s == "runatk":
            return 0 if t < 6 else 1
        if s == "stumble":
            return 1
        if s in ("fly", "fall", "landed"):
            return 0 if s != "landed" else 1
        if s == "getup":
            return 0 if t < GETUP_FRAMES // 2 else 1
        return 0

    @property
    def mashing(self):
        """(progress 0..1, label) when this wrestler has a one-sided meter to fill, else None."""
        if self.state == "down" and self.mash_needed:
            return self.mashes / self.mash_needed, "GET UP!"
        if self.state == "stunned":
            return 1 - self.stun_left / STUN_FRAMES, "SHAKE IT OFF!"
        return None

    def set_state(self, s):
        if s == "grapple" and self.state != "grapple":
            # grabbed while lying there: remember how far along getting up he was
            self.saved_down = (self.t, self.mash_needed, self.mashes, self.try_start, self.force_auto) \
                if self.state == "down" else None
        if s != self.state:
            self.state = s
            self.t = 0
            self.anim_tick = 0

    # ------------------------------------------------------------------ geometry
    def gap_to(self, other):
        """distance between the edges of the two bodies."""
        return math.hypot(other.x - self.x, other.y - self.y) - self.radius - other.radius

    def facing_toward(self, other, cos_min=0.5):
        dx, dy = other.x - self.x, other.y - self.y
        d = math.hypot(dx, dy) or 1
        fx, fy = FACING_DIR[self.facing]
        return (fx * dx + fy * dy) / d >= cos_min

    def face_opponent(self):
        if self.opponent:
            self.face_toward(self.opponent.x, self.opponent.y)

    def face_toward(self, x, y):
        """turn to whichever of the 4 facings points closest to mat point (x, y)."""
        dx, dy = x - self.x, y - self.y
        if dx or dy:
            self.turn_to(max(FACING_DIR.values(), key=lambda d: d[0] * dx + d[1] * dy))

    def turn_to(self, d):
        for face, fd in FACING_DIR.items():
            if fd == d:
                self.vert, self.horiz = face.split("-")

    # ------------------------------------------------------------------ input (player or CPU pad)
    def control(self, c):
        self.clock += 1
        s = self.state
        if s == "down":
            if self.mash_needed and (c.was_pressed("a") or c.was_pressed("s")):
                self.mashes += 1
            return
        if s == "stunned":
            if c.was_pressed("a") or c.was_pressed("s"):
                self.stun_left -= STUN_MASH
            return
        if s in STRIKES or s in TRAVEL or s in ("taunt", "recoil", "getup", "grapple", "whipped", "runatk",
                                                "stumble", "victory", "out"):
            return
        if s == "top":
            self.control_top(c)
            return
        if not c.held["d"]:
            self.block_locked = False
        if s == "run":
            if c.was_pressed("d"):
                self.set_state("stand")
            elif not self.bounce:
                for button, kind in (("a", "clothesline"), ("s", "dropkick")):
                    if c.was_pressed(button):
                        self.run_kind = specials.resolve(self, self.opponent, kind) if self.opponent else kind
                        self.set_state("runatk")
            return
        if s == "block":
            if c.held["d"] and self.t < BLOCK_MAX:
                self.face_opponent()
                return
            if c.held["d"]:
                self.block_locked = True      # held too long: the block drops
            self.set_state("stand")
        if s == "hit" and self.t < HIT_LOCK:
            return
        # attacks: you turn to face the opponent first
        for button, kind in (("a", "punch"), ("s", "kick")):
            if c.was_pressed(button):
                if self.can_catch():
                    self.request = "shoulder throw"
                    return
                ground = self.ground_move(button, c)
                if ground:
                    self.request = ground
                    return
                self.face_opponent()
                self.set_state(kind)
                return
        if c.held["d"] and not self.block_locked and (c.was_pressed("d") or s != "hit"):
            near = self.opponent and self.gap_to(self.opponent) <= CLOSE
            if near:
                self.face_opponent()
                self.set_state("block")
                return
            if c.was_pressed("d"):
                self.face_opponent()
                self.set_state("taunt")
                return
        self.face_from_arrows(c)
        for arrow in ("up", "down", "left", "right"):
            if c.was_pressed(arrow):
                if self.can_run and self.clock - self.last_tap.get(arrow, -99) <= DOUBLE_TAP:
                    self.start_run()
                    self.last_tap.clear()
                    return
                self.last_tap[arrow] = self.clock
        sx = (c.held["right"] - c.held["left"])
        sy = (c.held["down"] - c.held["up"])
        if sx or sy:
            # same speed across the mat in every direction (the game logic is flat; only the drawing is angled)
            dx, dy = ARROW_DIR[sx, sy]
            k = self.walk_speed / math.hypot(dx, dy)
            self.walk(dx * k, dy * k)
            self.set_state("walk")
            self.lean(dx * k, dy * k, c)
        elif s != "hit":
            self.push_t = 0
            self.set_state("stand")
            self.face_opponent()

    def face_from_arrows(self, c):
        if c.held["up"]:
            self.vert = "up"
        if c.held["down"]:
            self.vert = "down"
        if c.held["left"]:
            self.horiz = "left"
        if c.held["right"]:
            self.horiz = "right"

    def ground_move(self, button, c):
        """the move for A or S next to a downed opponent (None if he isn't down and close)."""
        o = self.opponent
        if not o or o.state != "down" or o.t < 10 or self.gap_to(o) > GROUND_REACH or o.outside != self.outside:
            return None
        side = c.held["left"] or c.held["right"]
        if button == "s":
            return DROP.get(self.who, "knee drop")
        if c.held["up"] or c.held["down"]:
            return "stomp"
        if side:
            return "boston crab"
        return "stomp" if self.outside else "pin"      # pins only count in the ring

    # ------------------------------------------------------------------ ropes and corners
    def at_corner(self):
        if self.outside:
            return None
        name, (cx, cy) = ring.nearest_corner(self.x, self.y)
        if abs(self.x - cx) <= EDGE + 3 and abs(self.y - cy) <= EDGE + 3:
            return cx, cy
        return None

    def lean(self, dx, dy, c):
        """walking into the ropes or a corner: keep it up and you go through / up."""
        corner = self.at_corner()
        pushing = False
        if corner and c.was_pressed("up"):
            self.start_climb()          # Corner + Up
            return
        if corner:
            to_x, to_y = corner[0] - self.x, corner[1] - self.y
            d = math.hypot(to_x, to_y) or 1
            if (dx * to_x + dy * to_y) / (d * math.hypot(dx, dy)) > 0.85:
                pushing = True
                self.push_t += 1
                if self.push_t >= PUSH_THROUGH:
                    self.start_climb()
                return
        normal = self.rope_normal(dx, dy)
        if normal:
            pushing = True
            self.push_t += 1
            if self.push_t >= PUSH_THROUGH:
                self.start_cross(normal)
        if not pushing:
            self.push_t = 0

    def rope_normal(self, dx, dy):
        """the way out through the rope you're leaning on (front ropes only), or None."""
        sp = math.hypot(dx, dy) or 1
        R = ring.RING
        if not self.outside:
            if self.x >= R - EDGE - 0.01 and dx / sp > 0.5:
                return (1, 0)
            if self.y >= R - EDGE - 0.01 and dy / sp > 0.5:
                return (0, 1)
        else:
            if self.x <= ring.OUT_NEAR + 0.01 and dx / sp < -0.5 and EDGE <= self.y <= R - EDGE:
                return (-1, 0)
            if self.y <= ring.OUT_NEAR + 0.01 and dy / sp < -0.5 and EDGE <= self.x <= R - EDGE:
                return (0, -1)
        return None

    def go(self, state, x1, y1, z1, frames, arc=0.0):
        self.path = (self.x, self.y, self.z, x1, y1, z1, arc, frames)
        self.push_t = 0
        self.set_state(state)

    def start_cross(self, normal):
        R = ring.RING
        self.events.append("climb")
        if not self.outside:
            x1 = ring.OUT_NEAR if normal[0] else self.x
            y1 = ring.OUT_NEAR if normal[1] else self.y
            self.cross_out = True
            self.go("ropes", x1, y1, ring.FLOOR_Z, CROSS_FRAMES, arc=10)
        else:
            x1 = R - EDGE if normal[0] else self.x
            y1 = R - EDGE if normal[1] else self.y
            self.cross_out = False
            self.go("ropes", x1, y1, 0.0, CROSS_FRAMES, arc=12)

    def corner_spot(self, cx, cy, inset):
        mid = ring.RING / 2
        ix = 1 if cx < mid else -1
        iy = 1 if cy < mid else -1
        return cx + ix * inset, cy + iy * inset

    def start_climb(self):
        corner = self.at_corner()
        if not corner:
            return
        self.corner = corner
        x1, y1 = self.corner_spot(*corner, CORNER_IN)
        self.go("climb", x1, y1, TOP_Z, CLIMB_FRAMES)
        self.events.append("climb")

    def control_top(self, c):
        self.face_opponent()
        for button, kind in (("a", "flying knee drop"), ("s", "dive")):
            if c.was_pressed(button):
                self.start_dive(kind)
                return
        sx = c.held["right"] - c.held["left"]
        sy = c.held["down"] - c.held["up"]
        if sx or sy:
            dx, dy = ARROW_DIR[sx, sy]
            cx, cy = self.corner
            if dx * (cx - self.x) + dy * (cy - self.y) < 0:        # stepping away from the post
                x1, y1 = self.corner_spot(cx, cy, CORNER_IN + 8)
                self.go("descend", x1, y1, 0.0, 16)

    def start_dive(self, kind):
        self.dive_kind = specials.resolve(self, self.opponent, kind) if self.opponent else kind
        o = self.opponent
        tx, ty = None, None
        if o and not o.outside:
            dx, dy = o.x - self.x, o.y - self.y
            if math.hypot(dx, dy) <= DIVE_RANGE:
                tx, ty = o.x, o.y
        if tx is None:                  # nobody in range: fly at the middle of the ring
            mid = ring.RING / 2
            dx, dy = mid - self.x, mid - self.y
            d = math.hypot(dx, dy) or 1
            tx, ty = self.x + dx / d * DIVE_DIST, self.y + dy / d * DIVE_DIST
        tx, ty = ring.clamp_in(tx, ty)
        self.face_toward(tx, ty)
        self.go("fly", tx, ty, 0.0, DIVE_FRAMES, arc=12)

    def knock_off(self):
        """hit while climbing or up top: fall to the floor outside near that turnbuckle
        (from the back corner, where there's no floor to see, you land back in the ring)."""
        cx, cy = self.corner or (self.x, self.y)
        R = ring.RING
        if cx >= R - 1:
            x1, y1, out = ring.OUT_NEAR + 4, min(R - EDGE, max(EDGE, self.y)), True
        elif cy >= R - 1:
            x1, y1, out = min(R - EDGE, max(EDGE, self.x)), ring.OUT_NEAR + 4, True
        else:
            x1, y1 = self.corner_spot(cx, cy, CORNER_IN + 12)
            out = False
        self.cross_out = out
        self.go("fall", *ring.clamp(x1, y1, out), ring.FLOOR_Z if out else 0.0, FALL_FRAMES, arc=8)

    def can_catch(self):
        """the opponent is running at me off the ropes, close enough for a shoulder throw."""
        o = self.opponent
        if not o or o.state not in ("run", "whipped") or o.bounce:
            return False
        toward = o.run_dir[0] * (self.x - o.x) + o.run_dir[1] * (self.y - o.y) > 0
        return toward and self.gap_to(o) <= CATCH

    def start_whipped(self, d):
        """sent into the ropes: run there, bounce back, and only take control after the next rope."""
        self.run_dir = d
        self.turn_to(d)
        self.bounce = 0
        self.whip_bounces = 0
        self.set_state("whipped")

    def start_run(self):
        if self.outside:
            return                  # no room to run on the floor
        self.run_dir = FACING_DIR[self.facing]
        self.bounce = 0
        self.set_state("run")

    # ------------------------------------------------------------------ movement
    def walk(self, dx, dy):
        self.x, self.y = ring.clamp(self.x + dx, self.y + dy, self.outside)

    def travel(self):
        """move along the current path; True when it's done."""
        x0, y0, z0, x1, y1, z1, arc, frames = self.path
        k = min(1.0, self.t / frames)
        self.x = x0 + (x1 - x0) * k
        self.y = y0 + (y1 - y0) * k
        self.z = z0 + (z1 - z0) * k + arc * 4 * k * (1 - k)
        return k >= 1.0

    def arrive(self):
        s = self.state
        self.path = None
        if s == "ropes":
            self.outside = self.cross_out
            self.z = ring.FLOOR_Z if self.outside else 0.0
            self.set_state("stand")
            self.events.append("went_out" if self.outside else "came_in")
        elif s == "climb":
            self.set_state("top")
        elif s == "descend":
            self.corner = None
            self.set_state("stand")
        elif s == "fly":
            self.set_state("landed")     # the match decides: did it hit him?
        elif s == "fall":
            self.corner = None
            self.outside = self.cross_out
            self.z = ring.FLOOR_Z if self.outside else 0.0
            self.energy = max(0.0, self.energy - FALL_DAMAGE)
            self.since_hit = 0
            self.knock_down()
            self.t = 10
            self.events.append("fell")
            if self.outside:
                self.events.append("went_out")

    def crash(self):
        """a dive that hit nothing."""
        self.corner = None
        self.energy = max(0.0, self.energy - CRASH_DAMAGE)
        self.knock_down(auto=True)
        self.t = 10

    def run_step(self):
        if self.bounce:
            self.bounce -= 1
            if not self.bounce:     # spring off the ropes and run the other way
                self.run_dir = (-self.run_dir[0], -self.run_dir[1])
                self.turn_to(self.run_dir)
                if self.state == "whipped":
                    self.whip_bounces += 1
                    if self.whip_bounces >= 2:
                        self.state = "run"     # back in control
            return
        dx, dy = self.run_dir
        nx, ny = self.x + dx * self.run_speed, self.y + dy * self.run_speed
        lo, hi = EDGE, ring.RING - EDGE
        if not (lo <= nx <= hi and lo <= ny <= hi):
            self.x, self.y = min(hi, max(lo, nx)), min(hi, max(lo, ny))
            self.bounce = BOUNCE_FRAMES
            self.events.append("bounce")
            return
        self.x, self.y = nx, ny

    # ------------------------------------------------------------------ every frame
    def update(self):
        self.t += 1
        self.anim_tick += 1
        self.strike = None
        self.recover()
        s, t = self.state, self.t
        if s in TRAVEL and self.path:
            if self.travel():
                self.arrive()
        elif s == "landed" and t > 2:
            self.crash()                # nobody sorted out the landing: it missed
        elif s in ("run", "whipped"):
            self.run_step()
        elif s == "runatk":
            if not self.bounce:
                self.run_step()
            if self.bounce or t >= RUN_ATTACKS[self.run_kind]["length"]:
                self.bounce = 0
                if self.run_kind in ("dropkick", "flying crossbody"):
                    self.knock_down(auto=True)      # missed: you land on your back
                    self.t = 10
                else:
                    self.set_state("stumble")
        elif s == "stumble" and t >= STUMBLE_FRAMES:
            self.set_state("stand")
        elif s in STRIKES:
            if t == STRIKES[s]["impact"]:
                self.strike = s
            if t >= STRIKES[s]["length"]:
                self.set_state("stand")
        elif s == "hit" and t >= HIT_FRAMES:
            self.set_state("stand")
        elif s == "recoil" and t >= RECOIL_FRAMES:
            self.set_state("stand")
        elif s == "taunt" and t >= TAUNT_FRAMES:
            self.hype = True
            self.energy = min(1.0, self.energy + TAUNT_ENERGY)
            self.events.append("taunt")
            self.set_state("stand")
        elif s == "stunned":
            self.stun_left -= 1
            if self.stun_left <= 0:
                self.hits_taken = 0
                self.set_state("stand")
        elif s == "down":
            self.update_down()
        elif s == "getup" and t >= GETUP_FRAMES:
            self.hits_taken = 0
            self.set_state("stand")

    def update_down(self):
        t = self.t
        if t == DOWN_FRAMES:
            if self.energy >= LOW or self.force_auto:
                self.mash_needed = 0
            else:
                self.start_getup_try()
        if t < DOWN_FRAMES:
            return
        if not self.mash_needed:
            if t >= DOWN_FRAMES + AUTO_GETUP:
                self.set_state("getup")
                self.events.append("got_up")
        elif self.mashes >= self.mash_needed:
            self.mash_needed = 0
            self.set_state("getup")
            self.events.append("got_up")
        elif t - self.try_start >= GETUP_WINDOW:
            self.start_getup_try()          # failed: another 5-second try, still open to attack

    def start_getup_try(self):
        self.mash_needed = getup_presses(self.energy)
        self.mashes = 0
        self.try_start = self.t

    def recover(self):
        self.since_hit += 1
        if self.since_hit % RECOVER_EVERY == 0 and self.energy < 1.0:
            self.energy = min(1.0, self.energy + RECOVER)

    # ------------------------------------------------------------------ getting hit
    def take_strike(self, attacker, kind):
        """attacker's punch/kick connected. Returns what happened: blocked, hit, stun, knockdown or knockoff."""
        if self.state in ("climb", "top"):
            self.knock_off()
            return "knockoff"
        if self.state == "block":
            attacker.blocked_hits += 1
            if attacker.blocked_hits >= 3:
                attacker.blocked_hits = 0
                attacker.push_back_from(self)
            return "blocked"
        attacker.blocked_hits = 0
        dmg = STRIKES[kind]["damage"] * attacker.power
        if attacker.hype:
            dmg *= HYPE
            attacker.hype = False
        self.energy = max(0.0, self.energy - dmg)
        self.since_hit = 0
        if self.state == "stunned":
            self.hits_taken = 0
            self.knock_down()
            return "knockdown"
        self.hits_taken += 1
        if self.hits_taken >= 3:
            self.stun_left = STUN_FRAMES
            self.set_state("stunned")
            return "stun"
        self.set_state("hit")
        if self.state == "hit":
            self.t = 0
        return "hit"

    def knock_down(self, auto=False):
        self.mash_needed = 0
        self.force_auto = auto
        self.set_state("down")

    def stay_down(self):
        """put back on the mat after a ground move. If he was already down, his get-up clock just carries on
        where it was (a ground move pauses it, it doesn't restart it, so nobody can be stomped forever)."""
        saved = self.saved_down
        self.knock_down()
        if saved:
            self.t, self.mash_needed, self.mashes, self.try_start, self.force_auto = saved
            self.saved_down = None
        else:
            self.t = DOWN_FRAMES - 20

    def push_back_from(self, other):
        dx, dy = self.x - other.x, self.y - other.y
        d = math.hypot(dx, dy) or 1
        self.walk(dx / d * RECOIL_PUSH, dy / d * RECOIL_PUSH)
        self.set_state("recoil")
