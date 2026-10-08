"""Entrance mockup: WWE-style ramp with a big video screen, pyro, and the wrestler's victory pose at the top.

Screen 256x240: scene above, announcer bar at the bottom (y 208+).
"""
import math
import random
from PIL import Image, ImageDraw
import chars3d as c3
import font
import hud
import portraits as pt
import select_screen as sel

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
SW, SH = 256, 240
SCENE_H = 208

# stage geometry
SCR = (64, 6, 192, 70)            # big video screen
STAGE_Y = 92                      # top of the ramp / stage front edge
RAMP_TOP = (110, 146)             # ramp x-span at the stage
RAMP_BOT = (52, 204)              # ramp x-span at the bottom of the scene
PYRO = [(98, STAGE_Y - 2), (158, STAGE_Y - 2), (40, 150), (216, 150)]


def hx(c):
    return font._hx(c)


def dither(img, fn, col, n=2, box=(0, 0, SW, SCENE_H)):
    px = img.load()
    x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(SCENE_H, y1)):
        for x in range(max(0, x0), min(SW, x1)):
            if (x + y) % n == 0 and fn(x, y):
                px[x, y] = hx(col)


def ramp_x(y):
    t = (y - STAGE_Y) / (SCENE_H - STAGE_Y)
    return RAMP_TOP[0] + (RAMP_BOT[0] - RAMP_TOP[0]) * t, RAMP_TOP[1] + (RAMP_BOT[1] - RAMP_TOP[1]) * t


def crowd_sides(img, frame, col):
    """packed fans on both sides of the ramp, heads only, arms going up; their colour washes in the wrestler's light."""
    rnd = random.Random(5)
    d = ImageDraw.Draw(img)
    px = img.load()
    for row in range(14):
        y = 96 + row * 8
        for x in range(-4, SW + 4, 7):
            xx = x + (row % 2) * 3 + rnd.randrange(-1, 2)
            lo, hi = ramp_x(y)
            if lo - 6 < xx < hi + 6:
                continue
            shade = 0.28 + 0.035 * row
            body = hud.shade(random.Random(xx * 31 + row).choice(["#F83800", "#0058F8", "#00A800", "#F8B800", "#7C7C7C"]),
                             shade)
            skin = hud.shade(random.Random(xx + row * 7).choice(["#F4C0A0", "#C68642", "#F2D0A8", "#8D5524"]), shade + 0.1)
            d.rectangle((xx - 3, y + 2, xx + 3, y + 8), fill=body)
            d.ellipse((xx - 2, y - 2, xx + 2, y + 2), fill=skin)
            if (frame + xx + row) % 5 < 2:                       # arms up
                d.line((xx - 3, y + 2, xx - 4, y - 4), fill=skin)
                d.line((xx + 3, y + 2, xx + 4, y - 4), fill=skin)
    for i in range(4):                                             # camera flashes
        r = random.Random(frame * 13 + i)
        if r.random() < 0.45:
            x, y = r.randrange(SW), r.randrange(100, 200)
            lo, hi = ramp_x(y)
            if not (lo - 4 < x < hi + 4):
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= x + dx < SW and 0 <= y + dy < SCENE_H:
                        px[x + dx, y + dy] = hx("#FCFCFC")


def video_screen(img, who, frame, on):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = SCR
    d.rectangle((x0 - 4, y0 - 3, x1 + 4, y1 + 3), fill=hx("#3C3C3C"))       # truss frame
    for x in range(x0 - 4, x1 + 5, 6):
        d.line((x, y0 - 3, x + 3, y0), fill=hx("#7C7C7C"))
    d.rectangle((x0, y0, x1, y1), fill=hx("#000000"))
    if not on:
        rnd = random.Random(frame)
        px = img.load()
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if rnd.random() < 0.25:
                    px[x, y] = hx("#545454")
        return
    col = hud.HUD_COL[who]
    d.rectangle((x0, y0, x1, y1), fill=hud.shade(col, 0.3))
    for y in range(y0, y1, 4):                                            # rolling light bands
        if (y // 4 + frame) % 4 == 0:
            d.line((x0, y, x1, y), fill=hud.shade(col, 0.55))
    por = pt.PORTRAITS[who]()
    por = por.crop((2, 0, pt.PW - 2, 56))
    img.alpha_composite(por, (x0 + 4, y0 + 4))
    # name scrolling on the right of the screen, two lines
    nm = hud.SHORT[who]
    tx = x0 + 86 + (40 - font.width(nm)) // 2
    font.draw_text(img, tx, y0 + 20, nm, col, shadow="#000000")
    if (frame // 2) % 2 == 0:
        font.draw_text(img, x0 + 94, y0 + 38, "HWW", "#F8D878", shadow="#000000")
    px = img.load()                                                      # scanlines
    for y in range(y0, y1 + 1, 2):
        for x in range(x0, x1 + 1):
            r, g, b, a = px[x, y]
            px[x, y] = (r * 3 // 4, g * 3 // 4, b * 3 // 4, a)


def stage(img, who, frame, lit):
    d = ImageDraw.Draw(img)
    col = hud.HUD_COL[who]
    # stage deck under the screen with the curtain doorway
    d.rectangle((40, 74, 216, STAGE_Y), fill=hx("#1C1C1C"))
    d.rectangle((112, 74, 144, STAGE_Y), fill=hx("#000000"))           # entrance gap
    for x in (110, 146):                                              # LED pillars
        for y in range(74, STAGE_Y, 3):
            on = ((y // 3 + frame) % 3 == 0) if lit else False
            d.rectangle((x - 1, y, x, y + 1), fill=hx(col if on else "#3C3C3C"))
    # ramp
    L0, R0 = RAMP_TOP
    L1, R1 = RAMP_BOT
    d.polygon([(L0, STAGE_Y), (R0, STAGE_Y), (R1, SCENE_H), (L1, SCENE_H)], fill=hx("#545454"))
    for y in range(STAGE_Y + 6, SCENE_H, 10):                          # ramp panel seams
        lo, hi = ramp_x(y)
        d.line((lo + 2, y, hi - 2, y), fill=hx("#3C3C3C"))
    # chasing light bulbs down both ramp edges
    for k in range(18):
        t = k / 17
        y = STAGE_Y + (SCENE_H - STAGE_Y) * t
        lo, hi = ramp_x(y)
        on = lit and (k + frame) % 3 == 0
        c = col if on else "#3C3C3C"
        r = 1 + t
        d.ellipse((lo - r - 1, y - r, lo + r - 1, y + r), fill=hx(c))
        d.ellipse((hi - r + 1, y - r, hi + r + 1, y + r), fill=hx(c))
    # HWW across the stage front
    for x in (64, 168):
        font.draw_text(img, x, 80, "HWW", "#F8D878" if lit else "#545454")
    # pyro posts
    for x, y in PYRO:
        d.rectangle((x - 2, y - 4, x + 2, y + 2), fill=hx("#7C7C7C"))


class Spark:
    def __init__(self, x, y, vx, vy, col, life):
        self.x, self.y, self.vx, self.vy, self.col, self.life = x, y, vx, vy, col, life


def fireworks(frame, who, bursts):
    """returns live sparks for this frame. bursts = [(start_frame, post index)]."""
    col = hud.HUD_COL[who]
    sparks = []
    for start, p in bursts:
        age = frame - start
        if age < 0 or age > 14:
            continue
        x0, y0 = PYRO[p]
        rnd = random.Random(start * 7 + p)
        for i in range(26):
            ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05)
            sp = rnd.uniform(3.0, 6.5)
            vx, vy = math.cos(ang) * sp * 0.8, math.sin(ang) * sp
            x = x0 + vx * age
            y = y0 + vy * age + 0.45 * age * age                              # gravity
            c = [col, "#F8D878", "#FCFCFC"][i % 3]
            if age > 10 and (i + frame) % 2:
                continue
            sparks.append((x, y, c, age < 3))
    return sparks


def draw_sparks(img, sparks):
    px = img.load()
    for x, y, c, big in sparks:
        x, y = int(x), int(y)
        pts = ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)) if big else ((0, 0), (1, 0))
        for dx, dy in pts:
            if 0 <= x + dx < SW and 0 <= y + dy < SCENE_H:
                px[x + dx, y + dy] = hx(c)


def spotlights(img, frame, col, lit):
    for k, (tx, ph) in enumerate(((10, 0.0), (246, 1.7), (128, 3.1))):
        bx = 128 + 60 * math.sin(frame / 9 * 2 * math.pi + ph)
        by = 160
        c = "#FCFCFC" if (not lit or k == 2) else col
        dither(img, lambda x, y, t=tx, b=bx: 0 <= y <= by and abs(x - (t + (b - t) * y / by)) <= 1 + 22 * y / by,
               c, 4, (0, 0, SW, by))


def wrestler(img, who, frame_in_walk, pose, face, y):
    """draw the wrestler on the ramp at screen y; bigger as he comes toward us (fake NES-style depth)."""
    t = (y - STAGE_Y) / (SCENE_H - STAGE_Y)
    old = c3.K
    c3.K = 0.62 + 0.75 * t
    x = 128
    ImageDraw.Draw(img).ellipse((x - 6 - 4 * t, y - 1, x + 6 + 4 * t, y + 1 + t), fill=hx("#3C3C3C"))
    c3.render(who, pose, face, (x, y), SW, SCENE_H, img)
    c3.K = old


INTRO = {
    "mike": [("THE FOLLOWING CONTEST IS", "SCHEDULED FOR ONE FALL!"), ("FROM THE IRON DUNGEON,", "WEIGHING 244 POUNDS..."),
             ("MIGHTY", "MIKE!!!")],
    "stew": [("THE FOLLOWING CONTEST IS", "SCHEDULED FOR ONE FALL!"), ("FROM THE ALL-YOU-CAN-EAT", "BUFFET, 412 POUNDS..."),
             ("BIG BEEFY", "STEW!!!")],
    "jim": [("THE FOLLOWING CONTEST IS", "SCHEDULED FOR ONE FALL!"), ("FROM THE TOP OF THE", "MOUNTAIN, 318 POUNDS..."),
            ("JIM", "\"THE GOAT\"!!!")],
    "niko": [("THE FOLLOWING CONTEST IS", "SCHEDULED FOR ONE FALL!"), ("FROM HIGH ABOVE THE", "CLOUDS, 221 POUNDS..."),
             ("NIMBLE", "NIKO!!!")],
}


def entrance(who, n_frames=70):
    """the whole entrance as frames: dark, BOOM, screen on, pose at the top, walk down the ramp."""
    victory = c3.moves_for(who)[-4][1]
    walk = (c3.MOVES[1][1][0], c3.MOVES[1][1][1])
    BOOM = 10
    bursts = [(BOOM, 0), (BOOM, 1), (BOOM + 4, 2), (BOOM + 4, 3), (BOOM + 14, 0), (BOOM + 14, 1),
              (BOOM + 22, 2), (BOOM + 22, 3), (BOOM + 30, 0), (BOOM + 30, 1)]
    lines = INTRO[who]
    frames = []
    for f in range(n_frames):
        lit = f >= BOOM
        img = Image.new("RGBA", (SW, SH), hx("#000000"))
        spotlights(img, f, hud.HUD_COL[who], lit)
        video_screen(img, who, f, lit)
        stage(img, who, f, lit)
        crowd_sides(img, f if lit else 0, hud.HUD_COL[who])
        # the wrestler: steps out at BOOM+2, poses at the top, then walks down
        if f >= BOOM + 2:
            k = f - (BOOM + 2)
            if k < 20:
                wrestler(img, who, k, victory[(k // 3) % 2], "down-left", STAGE_Y + 2)
            else:
                w = k - 20
                y = min(SCENE_H - 6, STAGE_Y + 2 + w * 3.2)
                wrestler(img, who, w, walk[(w // 2) % 2], "down-right" if (w // 8) % 2 else "down-left", y)
        draw_sparks(img, fireworks(f, who, bursts))
        if f == BOOM or f == BOOM + 1:                                    # the pyro flash
            px = img.load()
            for y in range(0, SCENE_H, 1):
                for x in range((y + f) % 2, SW, 2):
                    px[x, y] = hx("#FCFCFC")
        # announcer
        li = 0 if f < BOOM else (1 if f < BOOM + 22 else 2)
        start = 0 if li == 0 else (BOOM if li == 1 else BOOM + 22)
        hud.announcer_bar(img, lines[li][0], lines[li][1], chars=(f - start) * 3, frame=f)
        if li == 2 and f >= BOOM + 30 and (f // 2) % 2 == 0:                  # name in lights over the ramp
            nm = sel.TITLE[who]
            font.draw_text(img, (SW - font.width(nm, 1)) // 2, 98, nm, hud.HUD_COL[who], shadow="#000000")
        frames.append(img)
    return frames


if __name__ == "__main__":
    import sys
    who_list = sys.argv[1:] or ["mike"]
    allf = []
    for who in who_list:
        fr = entrance(who)
        allf += fr
        big = [f.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST) for f in fr]
        big[0].save(OUT + f"entrance_{who}.gif", save_all=True, append_images=big[1:], duration=110, loop=0,
                    disposal=1)
        for name, k in (("dark", 5), ("boom", 12), ("pose", 20), ("walk", 52)):
            big[k].save(OUT + f"entrance_{who}_{name}.png")
    print(len(allf))
