"""The match screen: you (left of the top bar) against the CPU (right), with the ref in the ring.

So far: walking and running (step 2), the HUD (3), striking (4), tie-ups (5), running attacks,
running collisions, ground moves, pins, the Boston crab and winning the match (6), the ropes,
the floor outside, the count-out and the top rope (7), the specials and finishers (8), and the intro,
the bell, sound and music (9).

Test keys (until the real menus exist):
Tab   your wrestler      C   CPU's wrestler (no mirror matches)      1 2 4   arena
K     CPU brain: FIGHT / WANDER / STILL      L   difficulty EASY / MEDIUM / HARD      J   match 1 / 2 / NEMESIS
- =   your energy down/up      9 0   CPU energy down/up      N   announcer says something
Enter or A during the intro: skip to the bell      Enter after a match: start again
"""
import math
import random

import pygame

from . import game_text, hud, ring, settings, ui
from .assets import Arena, Pairs, hex_rgb
from .cpu import DIFFICULTIES, Brain
from .effects import Effects
from .grapple import LIFTS, SLAMS, Move, Pin, Submission, TieUp
from .specials import is_finisher, resolve
from .referee import Referee
from .settings import BOT_Y, FULL_NAME, HUD_COL, SCREEN_W, SHORT_NAME, TOWN, WRESTLERS
from .sound import Silent
from .wrestler import HITTABLE, LOW, RUN_ATTACKS, STATS, TRAVEL, Wrestler

REF_SPOT = (92, 16)
CHATTER = ("strike", "stun", "tieup", "slam", "taunt", "pin", "kickout", "outside", "low_energy", "dont_give_up")
SCORE = {"hit": 100, "slam": 300, "taunt": 300, "finisher": 2000, "win": 5000, "quick_60": 3000,
         "quick_120": 1500}
WALKED_AWAY = 24            # gap that resets the 3-hit stun count
COMBO_TIMEOUT = 120         # ...and so does 2 seconds without a hit
GROUNDED = ("down", "getup", "out")
TIEABLE = ("stand", "walk", "block", "hit", "stunned")
RUNNING = ("run", "whipped", "runatk")
TIE_COOL = 40               # frames after a tie-up or move before the next lock-up
FPS = 60
COUNT_OUT = 20              # the ref counts to 20, one a second
DIVE_HIT = 12               # a dive lands on him if he's this close to where you come down
DING_FRAMES = 70            # the big DING! on screen
JINGLE_AFTER = 80           # frames after the final bell before the win / lose jingle
BIG_SLAM = 0.12             # slams this big (and every finisher) get a crowd cheer
START_SPOTS = ((30, 74, "up-right"), (74, 30, "down-left"))       # opposite corners for the intro
REF_INTRO = (52, 52)        # the ref waits in the middle until he calls for the bell
INTRO_HOLD = 45             # frames each intro line stays up once it's typed
PAUSE_MENU = ("CONTINUE", "MOVES LIST", "PASSWORD", "QUIT MATCH")
# the crooked ref against your nemesis (1 player only): slower when you pin him, way slower when he's outside
NORMAL_PIN_COUNT = 50       # frames between counts
NEMESIS_PIN_COUNT = 75
NEMESIS_OUT_COUNT = 105     # frames per count-out number (normally 60)


class Match:
    def __init__(self, font, sheets, arenas, p1="mike", p2="jim", arena=1, sound=None, match_no=1,
                 difficulty="MEDIUM"):
        self.font = font
        self.sound = sound or Silent()
        self.match_no = match_no            # 1, 2, or 3 = the nemesis
        self.difficulty = difficulty
        self.sheets = sheets
        self.arenas = arenas
        self.arena_no = arena
        self.announcer = hud.Announcer(font)
        self.effects = Effects()
        self.pairs = Pairs()
        self.paused = False
        self.pause_choice, self.pause_view, self.pause_page = 0, None, 0
        self.password = None        # shown in the pause menu (1-player runs)
        self.on_end = None          # the game takes over when the match is over and you press START
        self.on_quit = None         # QUIT MATCH
        self.slow_ref = False       # the nemesis match in a 1-player run
        self.tick = 0
        self.brain_mode = "FIGHT"
        self.phase = "intro"
        self.setup(p1, p2)
        self.intro()

    def setup(self, p1, p2, keep=None):
        """(re)place both wrestlers; keep = old (player, cpu) whose positions and energy carry over."""
        if keep:
            a, b = keep
            self.player = Wrestler(p1, a.x, a.y, a.facing)
            self.cpu = Wrestler(p2, b.x, b.y, b.facing)
            self.player.energy, self.cpu.energy = a.energy, b.energy
        else:
            (x1, y1, f1), (x2, y2, f2) = START_SPOTS
            self.player = Wrestler(p1, x1, y1, f1)
            self.cpu = Wrestler(p2, x2, y2, f2)
        self.player.opponent, self.cpu.opponent = self.cpu, self.player
        self.arena = self.pick_arena(self.arena_no)
        self.brain = Brain(self.cpu, self.player, self.brain_mode, self.match_no, self.difficulty)
        self.ref = Referee(*(REF_INTRO if self.phase == "intro" else REF_SPOT))
        self.low_said = set()
        self.grapple = None         # a TieUp, Move, Pin or Submission while one is happening
        self.tie_cool = 0
        self.match_time = 0
        self.over = None            # (winner, how) once someone has won
        self.over_t = 0
        self.shown_count = 0        # the big number on screen during a pin
        self.count_t = 0
        self.count_big = True
        self.countout = None        # frames toward the next count while someone is outside (None = nobody out)
        self.count_n = 0            # the count-out so far
        self.ding_t = 0
        self.last_ref_count = 0
        self.pads = {}

    def pick_arena(self, number):
        """the arena with this matchup's crowd signs (both names), when there are any."""
        if hasattr(self.arenas, "for_match"):
            return self.arenas.for_match(number, self.player.who, self.cpu.who)
        return self.arenas[number]

    def restart(self):
        self.sound.stop_music()
        self.setup(self.player.who, self.cpu.who)
        self.ring_bell()

    def names(self, w, move=""):
        other = w.opponent
        return {"name": FULL_NAME[w.who], "opp": FULL_NAME[other.who], "town": TOWN.get(w.who, ""),
                "move": move.upper()}

    def intro(self):
        a = self.announcer
        a.queue.clear()
        a.say("intro")
        for w in (self.cpu, self.player):
            a.say("intro_from", **self.names(w))
            a.say("intro_name", **self.names(w))

    # ------------------------------------------------------------------ the bell
    def ring_bell(self):
        """the match starts: DING!, the ref calls for it, and the match music kicks in."""
        self.phase = "fight"
        self.ding_t = DING_FRAMES
        self.sound.play("bell")
        self.sound.music("nemesis" if self.match_no == 3 else "match")
        self.ref.call_for_bell()
        self.announcer.queue.clear()
        self.announcer.say_now("bell")

    def update_intro(self, c):
        """the announcer introduces both men; nobody moves until the bell. Enter or A skips ahead."""
        self.tick += 1
        for w in (self.player, self.cpu):
            w.anim_tick += 1
            w.face_opponent()
        self.ref.t += 1
        self.ref.face_toward(self.cpu.x, self.cpu.y)
        if self.announcer.update() and self.tick % 2 == 0:
            self.sound.play("blip")
        a = self.announcer
        if not a.typing and a.wait > INTRO_HOLD:
            a.wait = INTRO_HOLD             # keep the intro moving
        if c.was_pressed("start") or c.was_pressed("a") or (a.done and self.tick > 30):
            self.ring_bell()

    # ------------------------------------------------------------------ input
    def handle_key(self, key):
        """test keys, only while debug is on (F3)."""
        if not settings.DEBUG:
            return
        p, c = self.player, self.cpu
        if key == pygame.K_TAB:
            self.setup(self.next_who(p.who, skip=c.who), c.who, keep=(p, c))
        elif key == pygame.K_c:
            self.setup(p.who, self.next_who(c.who, skip=p.who), keep=(p, c))
        elif key == pygame.K_k:
            modes = Brain.MODES
            self.brain_mode = modes[(modes.index(self.brain_mode) + 1) % len(modes)]
            self.brain.mode = self.brain_mode
            self.announcer.say_text(f"CPU: {self.brain_mode}")
        elif key in (pygame.K_l, pygame.K_j):
            if key == pygame.K_l:
                self.difficulty = DIFFICULTIES[(DIFFICULTIES.index(self.difficulty) + 1) % len(DIFFICULTIES)]
            else:
                self.match_no = self.match_no % 3 + 1
            self.brain.set_level(self.match_no, self.difficulty)
            self.announcer.say_text("CPU: " + self.brain.level_name)
        elif key in (pygame.K_1, pygame.K_2, pygame.K_4):
            self.arena_no = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_4: 4}[key]
            self.arena = self.pick_arena(self.arena_no)
        elif key in (pygame.K_MINUS, pygame.K_EQUALS):
            p.energy = min(1.0, max(0.0, p.energy + (0.1 if key == pygame.K_EQUALS else -0.1)))
        elif key in (pygame.K_9, pygame.K_0):
            c.energy = min(1.0, max(0.0, c.energy + (0.1 if key == pygame.K_0 else -0.1)))
        elif key == pygame.K_n:
            w = random.choice((p, c))
            self.announcer.say_now(random.choice(CHATTER), **self.names(w))

    @staticmethod
    def next_who(who, skip):
        i = WRESTLERS.index(who)
        for k in range(1, len(WRESTLERS) + 1):
            nxt = WRESTLERS[(i + k) % len(WRESTLERS)]
            if nxt != skip:
                return nxt

    # ------------------------------------------------------------------ update
    def update(self, c):
        if self.over:
            self.update_over(c)
            return
        if self.phase == "intro":
            self.update_intro(c)
            return
        if self.paused:
            self.update_pause(c)
            return
        if c.was_pressed("start"):
            self.paused = True
            self.pause_choice, self.pause_view, self.pause_page = 0, None, 0
            self.sound.play("select")
            return
        self.tick += 1
        self.match_time += 1
        p, cpu = self.player, self.cpu
        self.brain.countout = self.count_n if self.countout is not None else 0
        pad_c = self.brain.think()
        self.pads = {p: c, cpu: pad_c}
        p.control(c)
        cpu.control(pad_c)
        for w in (p, cpu):
            w.update()
        for w in (p, cpu):
            if w.state == "landed" and not self.grapple:
                self.land_dive(w, w.opponent)
        if self.grapple:
            self.update_grapple()
        else:
            for att in (p, cpu):
                if att.strike:
                    self.resolve_strike(att, att.opponent, att.strike)
                if att.state == "runatk" and not self.grapple:
                    self.check_run_attack(att, att.opponent)
            for w in (p, cpu):
                if w.request and not self.grapple:
                    self.start_request(w)
                w.request = None
        for w in (p, cpu):
            if w.gap_to(w.opponent) > WALKED_AWAY or w.since_hit > COMBO_TIMEOUT:
                w.hits_taken = 0 if w.state != "stunned" else w.hits_taken
            self.handle_events(w)
            self.check_low(w)
        if not self.grapple and self.same_level(p, cpu):
            if p.state in RUNNING and cpu.state in RUNNING and p.gap_to(cpu) <= 0.5:
                self.collide(p, cpu)
            self.keep_apart(p, cpu)
            self.check_tieup()
        else:
            p.blocked = cpu.blocked = False
        self.update_countout()
        if self.over:
            return
        self.ref.update((p, cpu))
        if not self.ref.job:
            for w in (p, cpu):      # bump the ref out of the way
                if not w.outside and w.state not in GROUNDED + ("grapple", "top") and w.state not in TRAVEL:
                    blocked = w.blocked
                    self.keep_apart(w, self.ref, stop_runs=False, b_yields=True)   # he gives way, always
                    w.blocked = blocked
        self.tie_cool = max(0, self.tie_cool - 1)
        self.count_t = max(0, self.count_t - 1)
        self.ding_t = max(0, self.ding_t - 1)
        self.effects.update()
        if self.announcer.update() and self.tick % 2 == 0:
            self.sound.play("blip")
        self.mash_blips(c)

    def mash_blips(self, c):
        """a little blip for every press while you're mashing on a meter."""
        g = self.grapple
        mashing = isinstance(g, (TieUp, Submission)) or (isinstance(g, Pin) and g.vic is self.player) \
            or self.player.mashing
        if mashing and any(c.was_pressed(b) for b in ("a", "s", "d")):
            self.sound.play("blip_mash")

    @staticmethod
    def same_level(a, b):
        """both in the ring or both on the floor, and neither up top or on the way somewhere."""
        busy = TRAVEL | {"top"}
        return a.outside == b.outside and a.state not in busy and b.state not in busy

    def land_dive(self, w, vic):
        """a dive comes down: on him (unless he blocks), or on nothing but mat."""
        close = math.hypot(vic.x - w.x, vic.y - w.y) <= DIVE_HIT + vic.radius
        if not vic.outside and close and (vic.state in HITTABLE or vic.state == "down"):
            if vic.state == "block":
                w.crash()
                self.sound.play("block")
                return
            self.start_move(w.dive_kind, w, vic)
            return
        w.crash()
        self.sound.play("slam")
        self.sound.grunt(w.who)
        if self.announcer.idle:
            self.announcer.say_text("HE MISSED! HE HIT", "NOTHING BUT MAT!")

    # ------------------------------------------------------------------ the count-out
    def update_countout(self):
        """anyone outside: the ref counts to 20. Everyone back in resets it (count-breaking is allowed)."""
        outs = [w for w in (self.player, self.cpu) if w.outside or (w.state == "ropes" and not w.cross_out)]
        if not outs:
            if self.countout is not None:
                self.countout = None
                self.ref.stop()
            return
        if self.countout is None:
            self.countout = 0
            self.count_n = 0
            if not self.ref.job or self.ref.job[0] == "countout":
                self.ref.count_out(outs[0])
        if self.ref.job and self.ref.job[0] == "countout" and self.ref.job[1] not in outs:
            self.ref.count_out(outs[0])
        self.countout += 1
        crooked = self.slow_ref and self.cpu in outs          # way slower when your nemesis is outside
        if self.countout >= (NEMESIS_OUT_COUNT if crooked else FPS):
            self.countout = 0
            self.count_n += 1
            self.ref.flip()
            self.show_count(self.count_n, big=False)
            self.sound.play("blip")
        n = self.count_n
        if n >= COUNT_OUT:
            if len(outs) == 2:
                self.win(None, "double")
            else:
                self.win(outs[0].opponent, "countout")

    def check_tieup(self):
        """walking into each other locks you up (no grapple button)."""
        p, cpu = self.player, self.cpu
        if self.tie_cool or not p.blocked:
            return
        if p.state in TIEABLE and cpu.state in TIEABLE and "walk" in (p.state, cpu.state):
            self.grapple = TieUp(p, cpu)
            self.grapple_events()
            if self.announcer.idle:
                self.announcer.say("tieup", **self.names(p))

    def start_request(self, w):
        name, vic = w.request, w.opponent
        if name == "pin":
            crooked = self.slow_ref and vic is self.cpu
            self.ref.count_every = NEMESIS_PIN_COUNT if crooked else NORMAL_PIN_COUNT
            self.grapple = Pin(w, vic, self.ref)
            self.last_ref_count = 0
            self.announcer.say_now("pin", **self.names(w))
        elif name == "boston crab":
            self.grapple = Submission(w, vic, self.ref)
            self.announcer.say_now("submission", **self.names(w))
        else:
            self.start_move(resolve(w, vic, name), w, vic)

    def start_move(self, name, att, vic):
        """every two-person move starts here: finishers get the flash and the call."""
        if name == "sleeper hold":
            self.grapple = Submission(att, vic, self.ref, "sleeper hold")
        else:
            self.grapple = Move(name, att, vic)
        if name in LIFTS:
            self.sound.grunt(att.who)
        if is_finisher(name):
            att.score += SCORE["finisher"]
            self.effects.finisher()
            self.sound.play("select")
            self.announcer.say_now("finisher", **self.names(att, name))

    def check_run_attack(self, att, vic):
        """a clothesline or dropkick in flight: does it reach him?"""
        if vic.state not in HITTABLE or not att.facing_toward(vic, 0.7) or vic.outside:
            return
        if vic.state in ("climb", "top"):
            if att.gap_to(vic) <= RUN_ATTACKS[att.run_kind]["reach"] + 4:
                vic.knock_off()             # run in and knock him off
                att.set_state("stumble")
                self.sound.play("hit")
            return
        if att.gap_to(vic) > RUN_ATTACKS[att.run_kind]["reach"]:
            return
        if vic.state == "block":            # block stops running attacks too
            att.push_back_from(vic)
            self.sound.play("block")
            return
        self.start_move(att.run_kind, att, vic)

    def collide(self, a, b):
        """two runners meet: both bump, unless one is heavier, then the lighter one goes down."""
        wa, wb = STATS[a.who]["weight"], STATS[b.who]["weight"]
        for w, other, mine, theirs in ((a, b, wa, wb), (b, a, wb, wa)):
            if mine < theirs:
                w.knock_down()
                w.energy = max(0.0, w.energy - 0.05)
                w.since_hit = 0
                self.announcer.say_now("knockdown", **self.names(other))
                self.sound.play("slam")
                self.sound.grunt(w.who)
            else:
                w.push_back_from(other)
                self.sound.play("block")
        self.spark_between(a, b, 20)

    def update_grapple(self):
        g = self.grapple
        if isinstance(g, TieUp):
            result = g.update(self.pads[g.a], self.pads[g.b])
            self.grapple_events()
            if not result:
                return
            if result[0] == "break":
                g.break_apart()
                self.end_grapple()
                return
            _, win, lose, move = result
            self.start_move(move, win, lose)
            return
        if isinstance(g, Pin):
            result = g.update(self.pads[g.att], self.pads[g.vic])
            self.show_count(self.ref.count)
            if self.ref.count != self.last_ref_count:
                self.last_ref_count = self.ref.count
                if self.ref.count:
                    self.sound.play("ref_slap")
            if result == "kickout":
                g.kick_out()
                self.last_ref_count = 0
                self.announcer.say_now("kickout", **self.names(g.vic))
                self.sound.play("crowd")
                self.end_grapple()
            elif result == "three":
                self.win(g.att, "pin")
            return
        if isinstance(g, Submission):
            result = g.update(self.pads[g.att], self.pads[g.vic])
            if result == "escape":
                g.release()
                self.announcer.say_now("escape", **self.names(g.vic))
                self.sound.play("crowd")
                self.end_grapple()
            elif result == "tapout":
                self.win(g.att, "sub")
            return
        if g.update():
            self.end_grapple()
            att = g.att
            if g.name in SLAMS:
                att.score += SCORE["slam"]
                self.effects.slam()
                if not is_finisher(g.name):
                    self.announcer.say_now("slam", **self.names(att))
                if is_finisher(g.name) or g.spec["damage"] >= BIG_SLAM:
                    self.sound.play("crowd")
            elif g.name != "rope whip":
                att.score += SCORE["hit"]
        elif g.t == g.hit_at and g.spec["damage"]:
            if g.name in SLAMS:
                self.sound.play("slam")
                self.sound.grunt(g.vic.who)
            else:
                self.spark_between(g.att, g.vic, 10 if g.name in ("stomp",) or "drop" in g.name else 18)
                self.sound.play("hit")

    def end_grapple(self):
        self.grapple = None
        self.tie_cool = TIE_COOL

    def grapple_events(self):
        g = self.grapple
        for kind, w in g.events:
            self.announcer.say_now(kind, **self.names(w))
        g.events.clear()

    def show_count(self, n, big=True):
        if n != self.shown_count:
            self.shown_count = n
            self.count_t = 40
            self.count_big = big

    # ------------------------------------------------------------------ winning
    def win(self, winner, how):
        """winner None = double count-out: nobody wins, and that's a loss for the player."""
        self.over = (winner, how)
        self.over_t = 0
        self.grapple = None
        self.sound.stop_music()
        self.sound.play("bell")
        if winner is None:
            for w in (self.player, self.cpu):
                if w.state not in GROUNDED:
                    w.set_state("stand")
            self.ref.stop()
            self.ref.set_state("call for bell")
            self.announcer.say_text("DOUBLE COUNT-OUT!", "NOBODY WINS THIS ONE!")
            return
        self.sound.play("crowd")
        loser = winner.opponent
        winner.score += SCORE["win"]
        secs = self.match_time / FPS
        if secs < 60:
            winner.score += SCORE["quick_60"]
        elif secs < 120:
            winner.score += SCORE["quick_120"]
        winner.set_state("victory")
        winner.face_toward(ring.RING * 2, ring.RING * 2)       # toward the camera
        if how == "countout":
            if loser.state not in GROUNDED:
                loser.set_state("stand")
        else:
            loser.set_state("out")
        if winner.outside:
            self.ref.stop()
            self.ref.set_state("call for bell")
        else:
            self.ref.raise_hand(winner)
        self.announcer.say_now({"pin": "win_pin", "sub": "win_sub", "countout": "win_countout"}[how],
                               **self.names(winner))

    def update_over(self, c):
        self.tick += 1
        self.over_t += 1
        for w in (self.player, self.cpu):
            w.t += 1
            w.anim_tick += 1
        if self.ref.job:
            self.ref.update((self.player, self.cpu))
        else:
            self.ref.t += 1
        self.effects.update()
        if self.announcer.update() and self.tick % 2 == 0:
            self.sound.play("blip")
        if self.over_t == JINGLE_AFTER:
            self.sound.music("win" if self.over[0] is self.player else "lose", loop=False)
        if self.over_t > 120 and (c.was_pressed("start") or c.was_pressed("a")):
            if self.on_end:
                self.on_end(self)
            else:
                self.restart()

    # ------------------------------------------------------------------ the pause menu
    def update_pause(self, c):
        """CONTINUE / MOVES LIST / PASSWORD / QUIT MATCH. The moves list shows only your wrestler,
        one page per situation (Left/Right turns the page)."""
        snd = self.sound
        ok = c.was_pressed("a") or c.was_pressed("start")
        if self.pause_view == "moves":
            n = len(game_text.moves_list(self.player.who))
            if c.was_pressed("right") or c.was_pressed("left"):
                self.pause_page = (self.pause_page + (1 if c.was_pressed("right") else -1)) % n
                snd.play("blip")
            elif ok or c.was_pressed("s"):
                self.pause_view = None
            return
        if self.pause_view == "password":
            if ok or c.was_pressed("s"):
                self.pause_view = None
            return
        if c.was_pressed("up") or c.was_pressed("down"):
            self.pause_choice = (self.pause_choice + (1 if c.was_pressed("down") else -1)) % len(PAUSE_MENU)
            snd.play("blip")
        if c.was_pressed("s") or (c.was_pressed("start") and self.pause_choice == 0):
            self.paused = False
            return
        if c.was_pressed("a") or c.was_pressed("start"):
            snd.play("select")
            pick = PAUSE_MENU[self.pause_choice]
            if pick == "CONTINUE":
                self.paused = False
            elif pick == "MOVES LIST":
                self.pause_view, self.pause_page = "moves", 0
            elif pick == "PASSWORD":
                self.pause_view = "password"
            else:
                self.sound.stop_music()
                if self.on_quit:
                    self.on_quit()
                else:
                    self.paused = False

    # ------------------------------------------------------------------ strikes
    def resolve_strike(self, att, vic, kind):
        """att's punch or kick reaches its impact frame: does it connect?"""
        if vic.state not in HITTABLE or vic.outside != att.outside:
            self.sound.play("whiff")
            return          # whiff over a downed opponent, or he's on the other side of the ropes
        if att.gap_to(vic) > att.reach[kind] or not att.facing_toward(vic):
            self.sound.play("whiff")
            return
        result = vic.take_strike(att, kind)
        if result == "blocked":
            self.sound.play("block")
            return
        self.sound.play("hit" if kind == "punch" else "kick")
        if result in ("stun", "knockdown", "knockoff"):
            self.sound.grunt(vic.who)
        if result == "knockdown":
            self.sound.play("slam")
        att.score += SCORE["hit"]
        self.spark_between(att, vic, 22 if kind == "punch" else 16)
        if result == "stun":
            self.announcer.say_now("stun", **self.names(att))
        elif result == "knockdown":
            self.announcer.say_now("knockdown", **self.names(att))
        elif result == "knockoff":
            self.announcer.say_text("HE'S BEEN KNOCKED", "OFF THE TOP!")
        elif self.announcer.idle and random.random() < 0.25:
            self.announcer.say("strike", **self.names(att))

    def spark_between(self, att, vic, height):
        vx, vy = ring.to_screen(vic.x, vic.y)
        ax, _ = ring.to_screen(att.x, att.y)
        self.effects.spark(vx + (ax - vx) * 0.3, vy - height)

    def handle_events(self, w):
        for e in w.events:
            if e == "taunt":
                w.score += SCORE["taunt"]
                self.announcer.say_now("taunt", **self.names(w))
                self.sound.play("crowd")            # the crowd pops for a finished taunt
                if w is self.player:
                    self.brain.bait()               # ...and it annoys him: he'll charge at you
            elif e == "went_out" and self.announcer.idle:
                self.announcer.say("outside", **self.names(w))
            elif e == "bounce":
                self.sound.play("block")
            elif e == "climb":
                self.sound.play("blip")
            elif e == "got_up" and w.energy < LOW:
                self.sound.grunt(w.who)
            elif e == "fell":
                self.sound.play("slam")
                self.sound.grunt(w.who)
        w.events.clear()

    def check_low(self, w):
        if w.energy >= LOW:
            self.low_said.discard(w.who)
        elif w.who not in self.low_said and self.announcer.idle:
            self.low_said.add(w.who)
            self.announcer.say("low_energy", **self.names(w))

    @staticmethod
    def keep_apart(a, b, stop_runs=True, b_yields=False):
        """bodies can't overlap. Running into someone stops you (but not into the ref, who always gives way).
        Someone lying down doesn't get shoved; whoever is standing steps off him."""
        a.blocked = b.blocked = False
        dx, dy = b.x - a.x, b.y - a.y
        d = math.hypot(dx, dy)
        gap = a.radius + b.radius
        if d >= gap:
            return
        if d < 0.01:
            dx, dy, d = 1.0, 0.0, 1.0
        ga, gb = a.state in GROUNDED, b.state in GROUNDED
        share_a = 0.5 if ga == gb else (0.0 if ga else 1.0)
        if b_yields:
            share_a = 0.0
        nx, ny = dx / d, dy / d
        pa, pb = (gap - d) * share_a, (gap - d) * (1 - share_a)
        a.x, a.y = ring.clamp(a.x - nx * pa, a.y - ny * pa, getattr(a, "outside", False))
        b.x, b.y = ring.clamp(b.x + nx * pb, b.y + ny * pb, getattr(b, "outside", False))
        a.blocked = b.blocked = True
        for w in (a, b):
            if stop_runs and w.state in ("run", "whipped"):
                w.set_state("stand")

    # ------------------------------------------------------------------ draw
    def draw_wrestler(self, surf, w):
        z = getattr(w, "z", 0.0)
        floor = ring.FLOOR_Z if getattr(w, "outside", False) or z < 0 else 0.0
        sx, sy = ring.to_screen(w.x, w.y, floor)
        pygame.draw.ellipse(surf, hex_rgb("#A4A4A4" if floor == 0 else "#000058"),
                            (round(sx) - 7, round(sy) - 2, 15, 5))
        fx, fy = ring.to_screen(w.x, w.y, z)
        self.sheets[w.who].draw(surf, w.move, w.facing, w.frame, (fx, fy))

    @staticmethod
    def in_front(w):
        """drawn after the front ropes: on the floor outside, or up on (or falling off) a turnbuckle."""
        return w.outside or w.z < 0 or w.z > 2

    def draw(self, surf):
        crowd_frame = (self.tick // 11) % Arena.FRAMES
        src = (0, -ring.ARENA_SHIFT, SCREEN_W, BOT_Y)
        ox, oy = self.effects.offset
        if ox or oy:                    # slam shake: draw the arena shifted, then put it back
            whole = surf
            surf = pygame.Surface(whole.get_size())
        surf.blit(self.arena.back[crowd_frame], (0, 0), src)
        g = self.grapple
        back = [(ring.depth(self.ref.x, self.ref.y), lambda: self.draw_wrestler(surf, self.ref))]
        front = []
        busy = (g.a, g.b) if isinstance(g, TieUp) else (g.att, g.vic) if g else ()
        if g:
            anchor = busy[0]
            layer = front if anchor.outside else back
            layer.append((ring.depth(anchor.x, anchor.y) + 6, lambda: self.draw_pair(surf, g, anchor)))
        for w in (self.player, self.cpu):
            if w not in busy:
                layer = front if self.in_front(w) else back
                layer.append((ring.depth(w.x, w.y), lambda w=w: self.draw_wrestler(surf, w)))
        for _, draw in sorted(back, key=lambda layer: layer[0]):
            draw()
        surf.blit(self.arena.front[crowd_frame], (0, 0), src)
        for _, draw in sorted(front, key=lambda layer: layer[0]):
            draw()
        self.effects.draw(surf)
        if ox or oy:
            whole.fill((0, 0, 0))
            whole.blit(surf, (ox, oy))
            surf = whole
        self.effects.draw_flash(surf, 0, BOT_Y)
        hud.top_bar(surf, self.font, self.player, self.cpu, self.tick)
        self.draw_meter(surf, g)
        self.draw_count(surf)
        if self.ding_t and (self.ding_t // 6) % 2 == 0:
            t = "DING!"
            self.font.draw_big(surf, (SCREEN_W - self.font.width(t) * 3) // 2, 70, t, "#F8D878", 3)
        self.announcer.draw(surf)
        if self.over and self.over_t > 120 and (self.tick // 20) % 2 == 0:
            t = "PUSH ENTER"
            self.font.draw(surf, (SCREEN_W - self.font.width(t)) // 2, 180, t, "#FCFCFC", shadow="#000000")
        if self.paused:
            self.draw_pause(surf)

    def draw_pause(self, surf):
        font = self.font
        ui.dim(surf, 24, BOT_Y)
        if self.pause_view == "moves":
            self.draw_moves(surf)
            return
        if self.pause_view == "password":
            ui.box(surf, 40, 90, 216, 140)
            ui.center(surf, font, 100, "YOUR PASSWORD", ui.GREY)
            ui.center(surf, font, 118, self.password or "NONE IN VS MODE", ui.YELLOW)
            return
        ui.box(surf, 64, 70, 192, 164)
        ui.center(surf, font, 80, "PAUSE", ui.YELLOW)
        for i, t in enumerate(PAUSE_MENU):
            font.draw(surf, 92, 96 + i * 14, t)
        ui.arrow(surf, 80, 97 + self.pause_choice * 14)

    def draw_moves(self, surf):
        font, who = self.font, self.player.who
        pages = game_text.moves_list(who)
        title, rows = pages[self.pause_page]
        ui.box(surf, 12, 28, 244, 204)
        font.draw(surf, 24, 38, SHORT_NAME[who] + "'S MOVES", HUD_COL[who])
        pg = f"{self.pause_page + 1}/{len(pages)}"
        font.draw(surf, 232 - font.width(pg), 38, pg, ui.GREY)
        ui.center(surf, font, 54, title, ui.YELLOW)
        y = 70
        for keys, move, kind in rows:
            col = "#FCFCFC"
            if kind == "special":
                col = HUD_COL[who]
            if kind == "finisher":
                col = "#F8D878" if (self.tick // 9) % 2 == 0 else "#FCA044"
                move = "*" + move
            if keys:
                font.draw(surf, 24, y, keys, ui.GREY)
                font.draw(surf, 100, y, move, col)
            else:
                ui.center(surf, font, y, move, col)
            y += 12 if title != "FINISHER" else 18
        if title != "FINISHER":
            font.draw(surf, 24, 172, "*FINISHER: UNDER 30%", ui.GREY)
        ui.center(surf, font, 190, "<  >  PAGE    ENTER  BACK", ui.GREY)

    def draw_meter(self, surf, g):
        p = self.player
        if isinstance(g, TieUp) and g.meter is not None:
            hud.mash_meter(surf, self.font, p.who, self.cpu.who, g.meter, self.tick)
        elif isinstance(g, Submission):
            hud.mash_meter(surf, self.font, p.who, self.cpu.who, g.lead(p), self.tick)
        elif isinstance(g, Pin) and g.vic is p:
            hud.one_meter(surf, self.font, p.who, g.progress, "KICK OUT!", self.tick)
        elif p.mashing:
            prog, label = p.mashing
            hud.one_meter(surf, self.font, p.who, prog, label, self.tick)

    def draw_count(self, surf):
        """the ref's count, big, in the middle of the ring."""
        if self.count_t <= 0 or not self.shown_count:
            return
        t = str(self.shown_count)
        if self.count_big:
            self.font.draw_big(surf, (SCREEN_W - self.font.width(t) * 3) // 2, 60, t, "#F8D878", 3)
        else:                       # the count-out: big, but up out of the way under the top bar
            self.font.draw_big(surf, (SCREEN_W - self.font.width(t) * 2) // 2, 30, t, "#FCFCFC", 2)

    def draw_pair(self, surf, g, anchor):
        fx, fy = ring.to_screen(anchor.x, anchor.y, anchor.z)
        pygame.draw.ellipse(surf, hex_rgb("#A4A4A4" if not anchor.outside else "#000058"),
                            (round(fx) - 11, round(fy) - 2, 23, 5))
        g.draw(surf, self.pairs, self.tick)
