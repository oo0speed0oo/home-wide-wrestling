"""Balance check: the CPU against itself, every matchup, both at the same level.

Prints, per wrestler: win rate, how the matches ended, how long they took, and how often each side used
its finisher. Run after changing damage or timing numbers:

    python game/tools/balance_sim.py [matches per pairing] [match: 1, 2 or 3] [nohabits]

"nohabits" turns off every CPU's habit (Mike's tie-ups, Niko's top rope...) to measure the wrestlers alone.

It runs without a window (and without sound). Nothing is saved.
"""
import collections
import os
import random
import sys
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((256, 240))

from hww import cpu as C  # noqa: E402
from hww.assets import Arena, Font, SoloSheet  # noqa: E402
from hww.controls import Controls  # noqa: E402
from hww.grapple import Move, Submission  # noqa: E402
from hww.match import Match  # noqa: E402
from hww.specials import is_finisher  # noqa: E402

WHO = ("mike", "stew", "jim", "niko")
MAX_SECONDS = 300


def play(sheets, arenas, font, a, b, match_no, seed, habits=True):
    random.seed(seed)
    m = Match(font, sheets, arenas, a, b, arena=1, match_no=match_no)
    m.ring_bell()
    bot = C.Brain(m.player, m.cpu, "FIGHT", match_no, "MEDIUM")
    if not habits:                  # measure the wrestlers themselves, not their CPU habits
        bot.habit = m.brain.habit = None
    c = Controls()
    fin = collections.Counter()
    last = None
    while not m.over and m.match_time < MAX_SECONDS * 60:
        bot.countout = m.count_n if m.countout is not None else 0
        pad = bot.think()
        c.begin_frame()
        for k in c.held:
            c.held[k] = pad.held[k]
        c.pressed = set(pad.pressed)
        m.update(c)
        g = m.grapple
        if isinstance(g, (Move, Submission)) and g is not last and is_finisher(g.name):
            fin[g.att.who] += 1
        last = g
    return m, fin


def main():
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    match_no = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    habits = "nohabits" not in sys.argv
    font = Font()
    sheets = {w: SoloSheet(w) for w in WHO + ("ref",)}
    arenas = {n: Arena(n) for n in (1, 2, 4)}
    wins, games, how, length = collections.Counter(), collections.Counter(), collections.Counter(), []
    finishers, vs = collections.Counter(), collections.Counter()
    t0 = time.time()
    seed = 0
    for a in WHO:
        for b in WHO:
            if a == b:
                continue
            for _ in range(per):
                seed += 1
                m, fin = play(sheets, arenas, font, a, b, match_no, seed, habits)
                games[a] += 1
                games[b] += 1
                finishers.update(fin)
                if m.over and m.over[0]:
                    w = m.over[0].who
                    wins[w] += 1
                    vs[w, b if w == a else a] += 1
                    how[m.over[1]] += 1
                else:
                    how["double" if m.over else "time limit"] += 1
                length.append(m.match_time / 60)
    n = len(length)
    print(f"{n} matches at match-{match_no} level in {time.time() - t0:.0f} s")
    print(f"length: average {sum(length) / n / 60:.1f} min, shortest {min(length):.0f} s, longest {max(length):.0f} s")
    print("ended by:", ", ".join(f"{k} {v / n:.0%}" for k, v in how.most_common()))
    print("wins (and finishers per match):")
    for w in WHO:
        print(f"  {w:5s} {wins[w] / games[w]:4.0%}   finishers {finishers[w] / games[w]:.1f}")
    print("head to head (row beat column, out of", 2 * per, "):")
    print("        " + "".join(f"{b:>6s}" for b in WHO))
    for a in WHO:
        print(f"  {a:5s} " + "".join(f"{vs[a, b] if a != b else '-':>6}" for b in WHO))


if __name__ == "__main__":
    main()
