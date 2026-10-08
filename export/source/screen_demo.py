"""Full 256x240 match screen mock: grapple with the mash meter, then a pin with the ref's count, then the win."""
from PIL import Image, ImageDraw
import arenas
import chars3d as c3
import pairs
import hud
import font

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
W, H = 256, 216


def mv(who, name, i=0):
    return pairs.mv(who, name, i)


def shadow(img, P, X, Y, w=7):
    x, y = P(X, Y)
    ImageDraw.Draw(img).ellipse((x - w, y - 2, x + w, y + 2), fill=c3.hx("#A4A4A4"))


def solo(who, pose, face, X, Y):
    def f(img, P):
        shadow(img, P, X, Y)
        c3.render(who, pose, face, P(X, Y), W, H, img)
    return (X + Y, f)


def pair(att, dfn, frame, face, X, Y):
    def f(img, P):
        shadow(img, P, X, Y, 10)
        pairs.render_pair(att, dfn, frame, face, P(X, Y), W, H, img)
    return (X + Y, f)


def actors(*items):
    def draw(img, P):
        for _, f in sorted(items, key=lambda a: a[0]):
            f(img, P)
    return draw


REF_STAND = mv("ref", "stand")
frames = []


def shot(arena_fn, top, bottom, overlay=None, n=1):
    for _ in range(n):
        k = len(frames)
        a = arenas.scene(1, k % 8, arena_fn)
        scr = hud.compose(a, lambda s: top(s, k), lambda s: bottom(s, k))
        if overlay:
            overlay(scr, k)
        frames.append(scr)


clock = [83.0]


def top(st1, st2):
    def f(s, k):
        clock[0] -= 0.18
        hud.top_bar(s, "mike", "jim", st1, st2, clock[0], k)
    return f


def say(l1, l2, start):
    return lambda s, k: hud.announcer_bar(s, l1, l2, chars=(k - start) * 4, frame=k)


# ---- 1. test of strength: the mash meter swings to Mike
L1, L2 = "A TEST OF STRENGTH IN THE", "MIDDLE OF THE RING!"
start = len(frames)
for i, pos in enumerate([0, 0.1, -0.05, -0.2, -0.15, -0.35, -0.3, -0.5, -0.45, -0.65, -0.6, -0.85, -1.0, -1.0]):
    fr = pairs.SHARED[2][1][i % 2]
    act = actors(pair("mike", "jim", fr, "down-right", 36, 50), solo("ref", REF_STAND, "down-left", 66, 26))
    shot(act, top(0.72, 0.30), say(L1, L2, start),
         overlay=lambda s, k, p=pos: hud.mash_meter(s, "mike", "jim", p, k))

# ---- 2. the throw
start = len(frames)
thr = pairs.SHARED[4][1]
for i in range(6):
    act = actors(pair("mike", "jim", thr[0 if i < 3 else 1], "down-right", 36, 50),
                 solo("ref", REF_STAND, "down-left", 66, 26))
    shot(act, top(0.72, 0.30 if i < 3 else 0.18), say("WHAT A THROW!", "JIM IS DOWN!", start))

# ---- 3. the pin and the count
start = len(frames)
pin = pairs.SHARED[6][1]
count = mv("ref", "pin count", 0), mv("ref", "pin count", 1)
beats = [0] * 3 + [0, 1, 1] + [0, 0, 1, 1] + [0, 0, 1, 1, 1, 1, 1]
num = 0
for i, b in enumerate(beats):
    if i >= 3 and b == 1 and beats[i - 1] == 0:
        num += 1
    act = actors(pair("mike", "jim", pin[i % 2], "down-right", 40, 46), solo("ref", count[b], "down-left", 52, 28))
    txt = "ONE... TWO... THREE!"[:[0, 6, 13, 20][num]] if num else ""

    def big(s, k, n=num):
        if n:
            t = str(n)
            font.draw_text(s, 128 - 8, 40, t, "#F8D878", shadow="#000000", scale=2)
    shot(act, top(0.70, 0.18), lambda s, k, t=txt: hud.announcer_bar(s, "THE COVER!", t, frame=k), overlay=big)

# ---- 4. the win
start = len(frames)
for i in range(12):
    vic = mv("mike", "victory", (i // 2) % 2)
    act = actors(solo("mike", vic, "down-right", 44, 50), solo("ref", mv("ref", "raise hand", (i // 2) % 2), "down-right", 40, 62),
                 solo("jim", pairs.DOWN, "down-left", 70, 44))

    def bell(s, k, i=i):
        if i < 4:
            font.draw_text(s, 128 - 36, 40, "DING!", "#FCFCFC", shadow="#000000", scale=2) if i % 2 == 0 else None
    shot(act, top(0.70, 0.18), say("THE WINNER...", "MIGHTY MIKE!", start), overlay=bell)

big = [f.convert("RGB").resize((768, 720), Image.NEAREST) for f in frames]
big[0].save(OUT + "screen_demo.gif", save_all=True, append_images=big[1:], duration=180, loop=0, disposal=1)
for i, k in enumerate((10, 30, len(big) - 6)):
    big[k].save(OUT + f"screen_still{i + 1}.png")
print(len(frames))
