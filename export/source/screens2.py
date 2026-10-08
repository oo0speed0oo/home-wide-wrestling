"""The rest of the screens (Oct 5): title menu + difficulty, VS mode setup, pause moves list, how to play,
high scores, name entry, the champion ending, and the in-match effects (sparks, flash, shake, one-sided meter)."""
import math
import random
from PIL import Image, ImageDraw
import arenas
import chars3d as c3
import crowd
import entrance as ent
import font
import game_text as gt
import hud
import pairs
import portraits as pt
import screens as sc
import select_screen as sel

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
SW, SH = 256, 240
hx = sc.hx
center = sc.center
LEVELS = ("EASY", "MEDIUM", "HARD")


def mini(who):
    p = pt.PORTRAITS[who]()
    return p.resize((40, 36), Image.NEAREST)


# ---------------------------------------------------------------- title menu + difficulty
def title_menu(frame, choice):
    return sc.title(frame, menu=choice)


def difficulty(frame, choice):
    img = sc.title(frame, menu=0)
    sc.dither(img, lambda x, y: True, "#000000", 2, (0, 0, SW, SH))
    sc.box(img, 64, 92, 192, 168)
    center(img, 102, "DIFFICULTY", "#F8D878")
    for i, t in enumerate(LEVELS):
        font.draw_text(img, 100, 120 + i * 14, t, "#FCFCFC")
    sc.arrow(img, 88, 121 + choice * 14)
    return img


# ---------------------------------------------------------------- VS mode setup
ARENA_THUMB = {a: arenas.scene(a, 0).resize((96, 81), Image.NEAREST) for a in (1, 2, 4)}


def vs_setup(you, cpu, arena, level, row, frame):
    img = sc.blank()
    center(img, 6, "VS MODE", "#F8D878")
    d = ImageDraw.Draw(img)
    img.alpha_composite(mini(you), (36, 22))
    img.alpha_composite(mini(cpu), (180, 22))
    font.draw_text(img, 56 - font.width(hud.SHORT[you]) // 2, 62, hud.SHORT[you], hud.HUD_COL[you])
    font.draw_text(img, 200 - font.width(hud.SHORT[cpu]) // 2, 62, hud.SHORT[cpu], hud.HUD_COL[cpu])
    center(img, 34, "VS", "#F83800", shadow="#000000", scale=2)
    rows = [("YOU", hud.SHORT[you]), ("CPU", hud.SHORT[cpu]), ("ARENA", str(arena)), ("LEVEL", LEVELS[level]),
            ("START", None)]
    for i, (lab, val) in enumerate(rows):
        y = 80 + i * 12
        font.draw_text(img, 48, y, lab, "#FCFCFC" if i != row else "#F8D878")
        if val is not None:
            font.draw_text(img, 112, y, "<", "#7C7C7C")
            font.draw_text(img, 124, y, val, "#FCFCFC")
            font.draw_text(img, 124 + font.width(val) + 4, y, ">", "#7C7C7C")
    sc.arrow(img, 36, 81 + row * 12)
    d.rectangle((78, 146, 177, 230), outline=hx("#FCFCFC"))
    img.alpha_composite(ARENA_THUMB[arena], (80, 148))
    return img


# ---------------------------------------------------------------- pause: moves list (your wrestler only)
def moves_page(match_frame, who, page, frame):
    pages = gt.moves_list(who)
    title, rows = pages[page]
    img = match_frame.copy()
    sc.dither(img, lambda x, y: True, "#000000", 2, (0, 24, SW, 208))
    sc.box(img, 12, 28, 244, 204)
    font.draw_text(img, 24, 38, hud.SHORT[who] + "'S MOVES", hud.HUD_COL[who])
    pg = f"{page + 1}/{len(pages)}"
    font.draw_text(img, 232 - font.width(pg), 38, pg, "#7C7C7C")
    center(img, 54, title, "#F8D878")
    y = 70
    for keys, move, kind in rows:
        col = "#FCFCFC"
        if kind == "special":
            col = hud.HUD_COL[who]
        if kind == "finisher":
            col = "#F8D878" if (frame // 2) % 2 == 0 else "#FCA044"
            move = "*" + move
        if keys:
            font.draw_text(img, 24, y, keys, "#7C7C7C")
            font.draw_text(img, 100, y, move, col)
        else:
            center(img, y, move, col)
        y += 12 if title != "FINISHER" else 18
    if title != "FINISHER":
        font.draw_text(img, 24, 172, "*FINISHER: UNDER 30%", "#7C7C7C")
    center(img, 190, "<  >  PAGE    ENTER  BACK", "#7C7C7C")
    return img


# ---------------------------------------------------------------- how to play
def how_to_play():
    img = sc.blank()
    center(img, 10, "HOW TO PLAY", "#F8D878")
    sc.box(img, 12, 26, 244, 160)
    for i, (k, v) in enumerate(gt.HOW_TO_PLAY):
        y = 38 + i * 14
        font.draw_text(img, 24, y, k, "#F8D878")
        font.draw_text(img, 100, y, v, "#FCFCFC")
    lines = ["WIN BY PINFALL, SUBMISSION", "OR COUNT-OUT.", "", "FINISHERS WORK WHEN HE'S", "UNDER 30% ENERGY.",
             "PAUSE TO SEE YOUR MOVES."]
    for i, t in enumerate(lines):
        center(img, 170 + i * 10, t, "#BCBCBC")
    return img


# ---------------------------------------------------------------- high scores + name entry
SCORES = [("MIKE", "mike", 48300), ("STEW", "stew", 41900), ("JIM", "jim", 37200), ("NIKO", "niko", 30100),
          ("BFG", "mike", 10000)]          # example entries until someone plays


def high_scores(frame, new_rank=None):
    img = sc.blank()
    sc.stars(img, frame, seed=9, n=40)
    img.alpha_composite(sc.LOGO.resize((sc.LOGO.width * 2 // 3, sc.LOGO.height * 2 // 3), Image.NEAREST),
                        ((SW - sc.LOGO.width * 2 // 3) // 2, 8))
    center(img, 58, "HALL OF FAME", "#F8D878", shadow="#A81000")
    font.draw_text(img, 24, 80, "RANK", "#7C7C7C")
    font.draw_text(img, 72, 80, "NAME", "#7C7C7C")
    font.draw_text(img, 184, 80, "SCORE", "#7C7C7C")
    for i, (nm, who, score) in enumerate(SCORES):
        y = 98 + i * 18
        col = hud.HUD_COL[who]
        if new_rank == i and (frame // 2) % 2:
            col = "#FCFCFC"
        font.draw_text(img, 32, y, ["1ST", "2ND", "3RD", "4TH", "5TH"][i], "#FCFCFC")
        font.draw_text(img, 72, y, nm, col)
        s = f"{score:,}"
        font.draw_text(img, 232 - font.width(s), y, s, "#FCFCFC")
    if (frame // 3) % 2 == 0:
        center(img, 212, "PUSH START", "#FCFCFC")
    return img


NAME_KEYS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ.-"


def name_entry(name, cur, frame, score=52700):
    img = sc.blank()
    center(img, 12, "NEW HIGH SCORE!", "#F8D878" if frame % 2 else "#FCFCFC", shadow="#A81000")
    center(img, 28, f"{score:,}", "#FCFCFC")
    center(img, 46, "ENTER YOUR NAME", "#7C7C7C")
    for i in range(10):
        x = 48 + i * 16
        ImageDraw.Draw(img).line((x, 74, x + 8, 74), fill=hx("#7C7C7C"))
        if i < len(name):
            font.draw_text(img, x, 64, name[i], "#FCFCFC")
        elif i == len(name) and (frame // 2) % 2 == 0:
            ImageDraw.Draw(img).rectangle((x, 64, x + 7, 71), fill=hx("#FCFCFC"))
    sc.box(img, 12, 88, 244, 190)
    for k, ch in enumerate(NAME_KEYS):
        cx, cy = 28 + (k % 10) * 21, 102 + (k // 10) * 18
        col = "#F8D878" if k == cur else "#FCFCFC"
        font.draw_text(img, cx, cy, ch, col)
        if k == cur:
            ImageDraw.Draw(img).rectangle((cx - 3, cy - 3, cx + 9, cy + 10), outline=hx("#F8D878"))
    for i, t in enumerate(("SPACE", "DEL", "END")):
        font.draw_text(img, 40 + i * 70, 168, t, "#FCFCFC")
    center(img, 212, "A:PICK  S:DEL", "#7C7C7C")
    return img


# ---------------------------------------------------------------- the belt and the champion ending
def belt(scale=1):
    im = Image.new("RGBA", (96, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gold, dark, light = hx("#F8B800"), hx("#AC7C00"), hx("#F8D878")
    d.rectangle((0, 11, 95, 21), fill=hx("#1C1C1C"))                      # leather strap
    d.line((0, 11, 95, 11), fill=hx("#545454"))
    d.line((0, 21, 95, 21), fill=hx("#000000"))
    for x in (12, 70):                                                    # side plates
        d.rounded_rectangle((x, 9, x + 13, 23), 3, fill=dark)
        d.rounded_rectangle((x + 1, 10, x + 12, 22), 3, fill=gold)
        d.point((x + 6, 15), fill=hx("#D82800"))
        d.point((x + 7, 16), fill=hx("#D82800"))
    d.ellipse((28, 0, 67, 31), fill=dark)                                 # main plate
    d.ellipse((29, 1, 66, 30), fill=gold)
    d.ellipse((33, 5, 62, 26), fill=light)
    d.ellipse((35, 7, 60, 24), fill=gold)
    crowd.put_text(im, 39, 11, "HWW", "#A81000")
    for x, y in ((47, 3), (47, 26), (31, 15), (63, 15)):                  # studs
        d.point((x, y), fill=hx("#FCFCFC"))
    if scale > 1:
        im = im.resize((96 * scale, 32 * scale), Image.NEAREST)
    return im


def champion(who, frame):
    img = sc.blank()
    top = Image.new("RGBA", (SW, 62), (0, 0, 0, 0))
    crowd.draw_crowd(top, frame, 4)
    px = top.load()
    for y in range(62):                                                   # dark house
        for x in range(SW):
            r, g, b, a = px[x, y]
            if (r, g, b) not in ((252, 252, 252), (248, 216, 120)):
                px[x, y] = (r * 6 // 10, g * 6 // 10, b * 6 // 10, a)
    img.alpha_composite(top, (0, 92))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 154, SW, 207), fill=hx("#BCBCBC"))                     # the ring, right up close
    d.line((0, 154, SW, 154), fill=hx("#FCFCFC"))
    for y, col in ((140, "#0058F8"), (146, "#FCFCFC"), (152, "#F83800")):
        d.line((0, y, SW, y), fill=hx(col))
    # fireworks in the sky
    sparks = []
    for start, (x0, y0) in ((0, (40, 70)), (3, (216, 60)), (7, (128, 50)), (11, (70, 40)), (15, (190, 44))):
        age = (frame - start) % 18
        rnd = random.Random(start)
        for i in range(24):
            a = 2 * math.pi * i / 24
            sp = rnd.uniform(2.5, 3.5)
            x = x0 + math.cos(a) * sp * age
            y = y0 + math.sin(a) * sp * age + 0.12 * age * age
            if age < 12 and 0 <= y < 92:
                sparks.append((x, y, [hud.HUD_COL[who], "#F8D878", "#FCFCFC"][i % 3], age < 2))
    ent.draw_sparks(img, sparks)
    # the champion, big, belt held over his head
    old = c3.K
    c3.K = 1.55
    vic = c3.moves_for(who)[-4][1][(frame // 3) % 2]
    UPB = c3.pose(0, ((6, 0, 10), (-6, 0, 10)), c3.both((0.05, 0.75, 0.9), (0.0, -0.45, 1)))
    pose = UPB if (frame // 6) % 2 == 0 else vic
    layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    c3.render(who, pose, "down-left", (128, 200), SW, SH, layer)
    c3.K = old
    bb = layer.getbbox()
    d.ellipse((96, 196, 160, 204), fill=hx("#7C7C7C"))
    img.alpha_composite(layer)
    if pose is UPB and bb:
        b = belt(1)
        img.alpha_composite(b, (128 - 48, bb[1] - 20))
    else:
        img.alpha_composite(belt(1), (128 - 48, 60))
    center(img, 8, "THE NEW", "#FCFCFC", shadow="#000000")
    center(img, 20, "HOME WIDE CHAMPION", "#F8D878" if frame % 2 else "#FCA044", shadow="#A81000")
    center(img, 34, sel.TITLE[who], hud.HUD_COL[who], shadow="#000000")
    l1, l2 = gt.ANNOUNCER["champion"][0]
    hud.announcer_bar(img, l1, l2.format(name=hud.SHORT[who]), chars=frame * 3, frame=frame)
    return img


# ---------------------------------------------------------------- in-match effects
def spark(img, x, y, k):
    """hit spark: a white star with a yellow core, then a smaller ring."""
    px = img.load()
    pts = []
    if k == 0:
        for r in range(1, 9):
            for w in (-1, 0, 1) if r < 5 else (0,):
                pts += [(r, w, "#FCFCFC"), (-r, w, "#FCFCFC"), (w, r, "#FCFCFC"), (w, -r, "#FCFCFC")]
        for r in range(1, 6):
            pts += [(r, r, "#F8D878"), (-r, r, "#F8D878"), (r, -r, "#F8D878"), (-r, -r, "#F8D878")]
        pts += [(dx, dy, "#F8D878") for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    else:
        for a in range(12):
            ang = a * math.pi / 6
            for rr in (8, 9):
                pts.append((round(math.cos(ang) * rr), round(math.sin(ang) * rr), "#FCFCFC"))
    for dx, dy, c in pts:
        X, Y = int(x + dx), int(y + dy)
        if 0 <= X < SW and 0 <= Y < SH:
            px[X, Y] = hx(c)


def flash(img, k):
    px = img.load()
    for y in range(24, 208):
        for x in range((y + k) % 2, SW, 2 if k else 1):
            px[x, y] = hx("#FCFCFC")


def effects_demo():
    """arena 1, Mike vs Jim: punch with sparks, a slam with screen shake, the powerbomb with the finisher flash,
    then the one-sided kick-out meter while the ref counts."""
    frames = []
    W, H = 256, 216

    def shot(actors, top, bottom, overlay=None, shake=(0, 0)):
        a = arenas.scene(1, len(frames) % 8, actors)
        if shake != (0, 0):
            moved = Image.new("RGBA", a.size, hx("#000000"))
            moved.alpha_composite(a, (shake[0], shake[1]) if shake[1] >= 0 else (shake[0], 0),
                                  (0, 0) if shake[1] >= 0 else (0, -shake[1]))
            a = moved
        scr = hud.compose(a, top, bottom)
        if overlay:
            overlay(scr)
        frames.append(scr)

    def pair_at(fr, X=40, Y=50, dfn="jim", att="mike"):
        def f(img, P):
            x, y = P(X, Y)
            ImageDraw.Draw(img).ellipse((x - 10, y - 2, x + 10, y + 2), fill=c3.hx("#A4A4A4"))
            pairs.render_pair(att, dfn, fr, "down-right", (x, y), W, H, img)
        return f

    ref = lambda pose, X=66, Y=28, face="down-left": (lambda img, P: c3.render("ref", pose, face, P(X, Y), W, H, img))

    def both(*fs):
        return lambda img, P: [f(img, P) for f in fs]

    def top(e1, e2):
        return lambda s: hud.top_bar(s, "mike", "jim", e1, e2, 0, len(frames))

    def say(l1, l2, start):
        return lambda s: hud.announcer_bar(s, l1, l2, chars=(len(frames) - start) * 4, frame=len(frames))

    REF = c3.REF_MOVES[0][1][0]
    punch = pairs.SHARED[0][1]
    st = len(frames)
    e2 = 0.62
    for i in range(10):
        hit = i % 2 == 1
        if hit:
            e2 -= 0.03
        x0, y0 = arenas.P(40, 50)
        ov = (lambda s, k=(i // 2) % 2: spark(s, x0 + 13, y0 - 8 - 20, k)) if hit else None
        shot(both(ref(REF), pair_at(punch[1 if hit else 0])), top(0.8, e2), say("WHAT A SHOT!", "", st), ov)
    # slam with shake
    st = len(frames)
    thr = pairs.SHARED[4][1]
    for i in range(10):
        fr = thr[0] if i < 4 else thr[1]
        sh = [(0, 0)] * 4 + [(3, 2), (-3, -2), (2, 1), (-2, -1), (1, 0), (0, 0)]
        shot(both(ref(REF), pair_at(fr)), top(0.8, 0.4 if i < 4 else 0.28), say("WHAT A SLAM!", "JIM IS DOWN!", st),
             shake=sh[i])
    # finisher: powerbomb with flash
    st = len(frames)
    pb = pairs.OWN["mike"][0][1]
    for i in range(14):
        fr = pb[0] if i < 6 else pb[1]
        ov = None
        if i in (6, 7):
            ov = lambda s, k=i - 6: flash(s, k)
        elif i >= 8:
            ov = lambda s, i=i: font.draw_text(s, (SW - font.width("POWERBOMB!", 2)) // 2, 44, "POWERBOMB!",
                                              "#F8D878" if i % 2 else "#FCA044", shadow="#A81000", scale=2)
        sh = (3, 2) if i == 6 else ((-3, -1) if i == 7 else (0, 0))
        shot(both(ref(REF), pair_at(fr)), top(0.8, 0.28 if i < 6 else 0.08),
             say("HERE IT COMES...", "THE POWERBOMB!!!", st), ov, shake=sh)
    # pin: one-sided kick-out meter for Jim while the ref counts
    st = len(frames)
    pin = pairs.SHARED[6][1]
    count = c3.REF_MOVES[2][1]
    for i in range(16):
        prog = min(0.85, i * 0.06)
        n = min(3, 1 + i // 5)

        def ov(s, i=i, prog=prog, n=n):
            hud.one_meter(s, "jim", prog, "KICK OUT!", i)
            font.draw_text(s, 128 - 8, 60, str(n), "#F8D878", shadow="#000000", scale=2)
        shot(both(ref(count[i % 2], 52, 28), pair_at(pin[i % 2], 40, 46)), top(0.8, 0.08),
             say("THE COVER!", "ONE... TWO...", st), ov)
    return frames


if __name__ == "__main__":
    shots = {
        "title_menu": title_menu(1, 1), "difficulty": difficulty(1, 1),
        "vs_setup": vs_setup("mike", "stew", 2, 1, 2, 0),
        "moves_tieup": None, "moves_finisher": None, "how_to_play": how_to_play(),
        "high_scores": high_scores(0, new_rank=1), "name_entry": name_entry("MIGHTY", 12, 0),
        "champion": champion("mike", 4),
    }
    m = arenas.scene(1, 0)
    live = hud.compose(m, lambda s: hud.top_bar(s, "mike", "jim", 0.62, 0.41, 0, 1),
                       lambda s: hud.announcer_bar(s, "PAUSED", "", frame=1))
    shots["moves_tieup"] = moves_page(live, "mike", 1, 0)
    shots["moves_finisher"] = moves_page(live, "mike", 6, 0)
    for k, im in shots.items():
        im.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST).save(OUT + f"s2_{k}.png")
    fx = effects_demo()
    big = [f.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST) for f in fx]
    big[0].save(OUT + "effects_demo.gif", save_all=True, append_images=big[1:], duration=140, loop=0, disposal=1)
    ch = [champion(w, f) for w in ("mike", "stew", "jim", "niko") for f in range(16)]
    big = [f.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST) for f in ch]
    big[0].save(OUT + "champion_demo.gif", save_all=True, append_images=big[1:], duration=130, loop=0, disposal=1)
    print("ok", len(fx), len(ch))
