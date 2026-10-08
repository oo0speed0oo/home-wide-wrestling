"""The whole game, screen to screen (design doc: Title screen, Game structure).

Title -> PUSH START -> menu:
  1 PLAYER     difficulty -> select -> [VS screen -> both entrances -> match -> win or lose] x 3 matches,
               your nemesis last, arenas 1, 2 and 4. Win the third: the champion ending, then the credits.
               Lose: GAME OVER and your password. Either way, a top-5 score goes in the Hall of Fame.
  VS MODE      pick both wrestlers, the arena and the CPU level -> VS screen -> entrances -> match -> NEW MATCH
  PASSWORD     8 letters; a good one picks up the run at that match (score back to 0). Secret codes:
               HVGE-HEDS big heads until you quit, THNK-YALL the ending and credits, BELT-TYME straight to
               the nemesis title match with the first wrestler on the select screen.
  HOW TO PLAY
Music: the menu theme on the menus; the match handles its own music and jingles.
"""
from . import game_text, screens
from .assets import set_big_heads
from .hall_of_fame import HallOfFame
from .match import Match
from .profiles import ARENA_FOR_MATCH, ORDER, RUN


class Run:
    """one 1-player run. The score carries from match to match; continuing from a password starts it at 0."""

    def __init__(self, who, difficulty, match_no):
        self.who, self.difficulty, self.match_no = who, difficulty, match_no
        self.score = 0

    @property
    def opponent(self):
        return RUN[self.who][self.match_no - 1]

    @property
    def password(self):
        return game_text.PASSWORDS[self.who, self.match_no]


class Game:
    def __init__(self, font, sheets, arenas, sound, hall=None):
        self.sound = sound
        self.art = screens.Art(font, sheets, arenas)
        self.hall = hall or HallOfFame()
        self.secrets = set()            # secret codes typed in since the game was started
        self.run = None
        self.scene = None
        self.go(screens.Title(self))

    def go(self, scene):
        self.scene = scene
        music = getattr(scene, "music", None)
        if music:
            self.sound.music(music)
        elif isinstance(scene, (screens.Entrance, screens.VSScreen)):
            self.sound.stop_music()

    def title(self):
        self.go(screens.Title(self))

    def update(self, c):
        self.scene.update(c)

    def draw(self, surf):
        self.scene.draw(surf)

    def handle_key(self, key):
        if hasattr(self.scene, "handle_key"):
            self.scene.handle_key(key)

    # ------------------------------------------------------------------ the 1-player run
    def start_run(self, who, difficulty, match_no):
        self.run = Run(who, difficulty, match_no)
        self.next_match()

    def next_match(self):
        r = self.run
        header = "MATCH 3: NEMESIS!" if r.match_no == 3 else f"MATCH {r.match_no} OF 3"
        self.go(screens.VSScreen(self, r.who, r.opponent, header, lambda: self.entrances(
            r.who, r.opponent, lambda: self.play(r.who, r.opponent, ARENA_FOR_MATCH[r.match_no], r.match_no,
                                                 r.difficulty, password=r.password, on_end=self.run_match_over,
                                                 nemesis=r.match_no == 3))))

    def run_match_over(self, m):
        r = self.run
        winner, how = m.over
        r.score += m.player.score
        if winner is m.player:
            last = r.match_no == 3
            line = ("champion", None) if last else ("next", RUN[r.who][r.match_no])
            self.go(screens.Win(self, r.who, how, m.match_time, line, then=self.after_win, score=r.score))
        else:
            self.go(screens.Lose(self, winner.who if winner else None, how, r.password, then=self.finish_run))

    def after_win(self):
        r = self.run
        if r.match_no == 3:
            self.go(screens.Champion(self, r.who, lambda: self.go(screens.Credits(self, self.finish_run))))
            return
        r.match_no += 1
        self.next_match()

    def finish_run(self):
        """the run is over (won or lost): a top-5 score gets a name in the Hall of Fame."""
        r, self.run = self.run, None
        if not r or not self.hall.qualifies(r.score):
            self.title()
            return

        def named(name):
            rank = self.hall.add(name, r.who, r.score)
            self.go(screens.HallOfFameScreen(self, self.title, new_rank=rank))
        self.go(screens.NameEntry(self, r.score, named))

    # ------------------------------------------------------------------ secret codes
    def use_secret(self, code):
        self.secrets.add(code)
        if code == "HVGE-HEDS":
            set_big_heads(True, self.art.sheets)
            self.go(screens.Title(self, start_at_menu=True))
        elif code == "THNK-YALL":
            self.go(screens.Champion(self, ORDER[0], lambda: self.go(screens.Credits(self, self.title))))
        elif code == "BELT-TYME":
            self.go(screens.DifficultyPick(self, lambda lvl: self.start_run(ORDER[0], lvl, 3)))

    # ------------------------------------------------------------------ VS mode
    def start_vs(self, setup):
        level = screens.LEVELS[setup.level]
        self.run = None
        self.go(screens.VSScreen(self, setup.you, setup.cpu, "VS MODE", lambda: self.entrances(
            setup.you, setup.cpu, lambda: self.play(setup.you, setup.cpu, setup.arena, 2, level,
                                                    on_end=lambda m: self.vs_over(m, setup)))))

    def vs_over(self, m, setup):
        winner, how = m.over
        back = lambda: self.go(screens.VSSetup(self, setup.you, setup.cpu, setup.arena, setup.level))
        if winner is None:
            self.go(screens.Lose(self, None, how, None, then=back))
        else:
            self.go(screens.Win(self, winner.who, how, m.match_time, ("new", None), then=back))

    # ------------------------------------------------------------------ shared
    def entrances(self, you, cpu, then):
        """the CPU comes out first, then you."""
        self.go(screens.Entrance(self, cpu, lambda: self.go(screens.Entrance(self, you, then))))

    def play(self, you, cpu, arena, match_no, difficulty, password=None, on_end=None, nemesis=False):
        a = self.art
        m = Match(a.font, a.sheets, a.arenas, you, cpu, arena, sound=self.sound, match_no=match_no,
                  difficulty=difficulty)
        m.password = password
        m.on_end = on_end
        m.on_quit = self.quit_match
        m.slow_ref = nemesis            # the ref is crooked against your nemesis (1 player only)
        self.go(m)

    def quit_match(self):
        self.run = None
        self.title()
