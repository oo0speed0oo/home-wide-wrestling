"""Home Wide Wrestling menu screens, all 256x240: title, VS, win, lose (game over), password, pause, credits."""
import math
import random
from PIL import Image, ImageDraw, ImageOps
import font
import hud
import make_logo
import portraits as pt
import chars3d as c3
import select_screen as sel

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
SW, SH = 256, 240
PORT = sel.PORT


def hx(c):
    return font._hx(c)


def blank(col="#000000"):
    return Image.new("RGBA", (SW, SH), hx(col))


def center(img, y, text, col="#FCFCFC", shadow=None, scale=1):
    font.draw_text(img, (SW - font.width(text, scale)) // 2, y, text, col, shadow, scale)


def dither(img, fn, col, n=2, box=(0, 0, SW, SH)):
    px = img.load()
    x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(SH, y1)):
        for x in range(max(0, x0), min(SW, x1)):
            if (x + y) % n == 0 and fn(x, y):
                px[x, y] = hx(col)


def box(img, x0, y0, x1, y1, fill="#000000", edge="#FCFCFC"):
    """NES menu window: filled, white double border."""
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x1, y1), fill=hx(fill))
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline=hx(edge))
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), outline=hx(edge))


def arrow(img, x, y, col="#F8D878"):
    ImageDraw.Draw(img).polygon([(x, y), (x, y + 6), (x + 4, y + 3)], fill=hx(col))


# ---------------------------------------------------------------- the logo, NES size
def logo_big():
    big = make_logo.letters([make_logo.H_, make_logo.W_, make_logo.W_])
    big = big.crop(big.getbbox())
    big = big.resize((big.width * 3, big.height * 3), Image.NEAREST)
    pad = Image.new("RGBA", (big.width + 8, big.height + 8), (0, 0, 0, 0))
    pad.alpha_composite(big, (4, 4))
    big = make_logo.outline(pad, "#000000", 1)
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sp, bp = shadow.load(), big.load()
    for y in range(big.height):
        for x in range(big.width):
            if bp[x, y][3]:
                sp[x, y] = hx("#A81000")
    out = Image.new("RGBA", (big.width + 4, big.height + 4), (0, 0, 0, 0))
    out.alpha_composite(shadow, (4, 4))
    out.alpha_composite(big, (0, 0))
    return out


LOGO = logo_big()


def banner(img, y, text="HOME WIDE WRESTLING"):
    d = ImageDraw.Draw(img)
    w = font.width(text) + 24
    x0 = (SW - w) // 2
    d.rectangle((x0, y, x0 + w, y + 13), fill=hx("#A81000"))
    d.line((x0, y, x0 + w, y), fill=hx("#F87858"))
    d.line((x0, y + 13, x0 + w, y + 13), fill=hx("#000000"))
    center(img, y + 3, text, "#FCFCFC", shadow="#000000")


def stars(img, frame, seed=3, n=40, top=0, bottom=SH):
    rnd = random.Random(seed)
    px = img.load()
    for i in range(n):
        x, y = rnd.randrange(SW), rnd.randrange(top, bottom)
        if (frame + i) % 6 < 4:
            px[x, y] = hx("#FCFCFC" if i % 3 else "#F8D878")


# ---------------------------------------------------------------- 1. title
MENU = ("1 PLAYER", "VS MODE", "PASSWORD", "HOW TO PLAY")


def title(frame, menu=None):
    img = blank()
    stars(img, frame, n=50, bottom=150)
    for top_x, sway in ((20, 1), (236, -1)):               # sweeping searchlights behind the logo
        bx = 128 + sway * 40 * math.sin(frame / 10 * 2 * math.pi)
        dither(img, lambda x, y, t=top_x, b=bx: abs(x - (t + (b - t) * y / 150)) <= 2 + 26 * y / 150,
               "#24188C", 2, (0, 0, SW, 150))
    img.alpha_composite(LOGO, ((SW - LOGO.width) // 2, 12))
    banner(img, 12 + LOGO.height + 2)
    # the four stars of the show, victory poses on a little stage
    ImageDraw.Draw(img).rectangle((24, 146, 232, 149), fill=hx("#3C3C3C"))
    for i, (who, face) in enumerate((("mike", "down-right"), ("stew", "down-right"), ("jim", "down-left"),
                                     ("niko", "down-left"))):
        pose = c3.moves_for(who)[-4][1][(frame // 3 + i) % 2]            # each one's victory
        c3.render(who, pose, face, (56 + i * 48, 146), SW, SH, img)
    if menu is None:
        if (frame // 3) % 2 == 0:
            center(img, 162, "PUSH START", "#FCFCFC")
    else:
        for i, t in enumerate(MENU):
            font.draw_text(img, 92, 155 + i * 10, t, "#FCFCFC")
        arrow(img, 80, 156 + menu * 10)
    for i, t in enumerate(("TM AND @ 1990", "BEST FRIEND GAMES LTD.", "LICENSED BY", "FRIENDS OF JAPAN INC.")):
        center(img, 198 + i * 9, t, "#BCBCBC" if i < 2 else "#7C7C7C")
    return img


# ---------------------------------------------------------------- 2. VS
TAPE = {k: dict(sel.STATS[k]) for k in sel.ORDER}


def vs(p1, p2, match, frame):
    img = blank()
    d = ImageDraw.Draw(img)
    c1, c2 = hud.HUD_COL[p1], hud.HUD_COL[p2]
    d.polygon([(0, 0), (140, 0), (116, 150), (0, 150)], fill=hud.shade(c1, 0.35))      # split backdrop
    d.polygon([(140, 0), (SW, 0), (SW, 150), (116, 150)], fill=hud.shade(c2, 0.35))
    d.line((140, 0, 116, 150), fill=hx("#FCFCFC"), width=2)
    center(img, 6, f"MATCH {match} OF 3", "#F8D878", shadow="#000000")
    slide = max(0, 6 - frame) * 16                                                  # portraits slide in
    img.alpha_composite(PORT[p1], (8 - slide, 26))
    img.alpha_composite(ImageOps.mirror(PORT[p2]), (SW - 88 + slide, 26))
    for i, t in enumerate(sel.NAME2[p1]):
        font.draw_text(img, 48 - font.width(t) // 2, 102 + i * 9, t, c1, "#000000")
    for i, t in enumerate(sel.NAME2[p2]):
        font.draw_text(img, SW - 48 - font.width(t) // 2, 102 + i * 9, t, c2, "#000000")
    if frame >= 6:
        col = "#F8D878" if frame % 2 else "#F83800"
        center(img, 54, "VS", col, shadow="#000000", scale=3)
    # tale of the tape
    y = 158
    for lab in ("HEIGHT", "WEIGHT", "RECORD"):
        center(img, y, lab, "#7C7C7C")
        a, b = TAPE[p1][lab], TAPE[p2][lab]
        font.draw_text(img, 12, y, a, "#FCFCFC")
        font.draw_text(img, SW - 12 - font.width(b), y, b, "#FCFCFC")
        y += 12
    if frame >= 8 and frame % 4 < 3:
        center(img, 204, "FIGHT!", "#F83800", shadow="#F8D878", scale=2)
    return img


# ---------------------------------------------------------------- 3. win
def win(who, next_opp, frame, how="PINFALL", time="1:07"):
    img = blank()
    dither(img, lambda x, y: abs(x - 128) <= 8 + y * 0.35, "#F8D878", 4, (0, 0, SW, 110))   # spotlight
    rnd = random.Random(7)
    px = img.load()
    for i in range(60):                                                              # confetti falling
        x = rnd.randrange(SW)
        y = (rnd.randrange(SH) + frame * (2 + i % 3)) % 150
        px[x, y] = hx(("#F83800", "#3CBCFC", "#58D854", "#F8D878", "#FCFCFC")[i % 5])
    center(img, 6, f"{sel.TITLE[who]} WINS!", hud.HUD_COL[who], shadow="#000000")
    img.alpha_composite(PORT[who], ((SW - pt.PW) // 2, 22))
    ImageDraw.Draw(img).rectangle((0, 94, SW, 95), fill=hx("#3C3C3C"))
    for j, ln in enumerate(sel.QUOTE[who].split("|")):
        center(img, 102 + j * 10, ln, "#F8D878")
    box(img, 40, 128, 216, 168)
    font.draw_text(img, 52, 137, "WIN BY", "#7C7C7C")
    font.draw_text(img, 116, 137, how, "#FCFCFC")
    font.draw_text(img, 52, 151, "TIME", "#7C7C7C")
    font.draw_text(img, 116, 151, time, "#FCFCFC")
    if next_opp:
        center(img, 180, "NEXT OPPONENT", "#7C7C7C")
        center(img, 192, sel.TITLE[next_opp], hud.HUD_COL[next_opp])
    else:
        center(img, 184, "HOME WIDE CHAMPION!", "#F8D878" if frame % 2 else "#FCFCFC", shadow="#A81000")
    if (frame // 3) % 2 == 0:
        center(img, 220, "PUSH START", "#FCFCFC")
    return img


# ---------------------------------------------------------------- 4. lose / game over
import game_text
PASSWORD = game_text.PASSWORDS[("mike", 3)]


def lose(winner, frame, how="SUBMISSION"):
    img = blank()
    rain = random.Random(11)
    px = img.load()
    for i in range(50):                                                              # gloomy rain
        x = rain.randrange(SW)
        y = (rain.randrange(SH) + frame * 6) % 120
        for k in range(3):
            if 0 <= y + k < 120:
                px[(x - k) % SW, y + k] = hx("#24188C")
    center(img, 6, "YOU LOSE...", "#F83800", shadow="#000000")
    img.alpha_composite(PORT[winner], ((SW - pt.PW) // 2, 22))
    for j, ln in enumerate(sel.QUOTE[winner].split("|")):
        center(img, 100 + j * 10, ln, hud.HUD_COL[winner])
    center(img, 126, f"BY {how}", "#7C7C7C")
    if frame >= 6:
        center(img, 146, "GAME OVER", "#FCFCFC" if frame % 4 < 3 else "#7C7C7C", shadow="#A81000", scale=2)
    box(img, 40, 172, 216, 214)
    center(img, 181, "YOUR PASSWORD", "#7C7C7C")
    center(img, 196, PASSWORD, "#F8D878")
    return img


# ---------------------------------------------------------------- 5. password entry
KEYS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"       # no I, O, 0, 1: easy to copy off the TV


def password(entered, cur, frame, status=None):
    img = blank()
    center(img, 14, "ENTER PASSWORD", "#F8D878")
    # 8 slots, dash in the middle
    for i in range(8):
        x = 52 + i * 18 + (8 if i >= 4 else 0)
        ImageDraw.Draw(img).line((x, 52, x + 9, 52), fill=hx("#7C7C7C"))
        if i < len(entered):
            font.draw_text(img, x + 1, 42, entered[i], "#FCFCFC")
        elif i == len(entered) and (frame // 2) % 2 == 0:
            ImageDraw.Draw(img).rectangle((x, 42, x + 8, 50), fill=hx("#FCFCFC"))
    font.draw_text(img, 124, 42, "-", "#7C7C7C")
    box(img, 20, 70, 236, 166)
    for k, ch in enumerate(KEYS):
        cx, cy = 40 + (k % 8) * 24, 84 + (k // 8) * 18
        col = "#F8D878" if k == cur else "#FCFCFC"
        font.draw_text(img, cx, cy, ch, col)
        if k == cur:
            ImageDraw.Draw(img).rectangle((cx - 3, cy - 3, cx + 9, cy + 10), outline=hx("#F8D878"))
    for i, t in enumerate(("DEL", "END")):
        font.draw_text(img, 72 + i * 88, 178, t, "#FCFCFC")
    if cur == len(KEYS) + 1:
        arrow(img, 150, 179)
    if status:
        center(img, 204, status, "#58D854" if "OK" in status else "#F83800")
    else:
        center(img, 204, "A:PICK  S:DEL", "#7C7C7C")
    return img


# ---------------------------------------------------------------- 6. pause, over a live match frame
def pause(match_frame, choice, frame):
    img = match_frame.copy()
    dither(img, lambda x, y: True, "#000000", 2, (0, 24, SW, 208))                 # dim the match
    box(img, 64, 70, 192, 164)
    center(img, 80, "PAUSE", "#F8D878")
    for i, t in enumerate(("CONTINUE", "MOVES LIST", "PASSWORD", "QUIT MATCH")):
        font.draw_text(img, 92, 96 + i * 14, t, "#FCFCFC")
    if (frame // 2) % 2 == 0 or True:
        arrow(img, 80, 97 + choice * 14)
    return img


# ---------------------------------------------------------------- 7. credits (scrolling)
CREDITS = [
    ("LOGO", None), ("", None),
    ("STARRING", "#F8D878"),
    ("MIGHTY MIKE", "#F83800"), ("BIG BEEFY STEW", "#3CBCFC"), ("JIM \"THE GOAT\"", "#58D854"),
    ("NIMBLE NIKO", "#9878F8"), ("", None),
    ("GAME DESIGN", "#F8D878"), ("MIGHTY MIKE", "#FCFCFC"), ("", None),
    ("ART, CODE AND MUSIC", "#F8D878"), ("CLAUDE", "#FCFCFC"), ("", None),
    ("REFEREE", "#F8D878"), ("THE REF", "#FCFCFC"), ("", None),
    ("ANNOUNCER", "#F8D878"), ("THE VOICE OF HWW", "#FCFCFC"), ("", None),
    ("SPECIAL THANKS", "#F8D878"), ("THE FANS", "#FCFCFC"), ("EVERYONE WHO", "#FCFCFC"),
    ("NEVER GAVE UP", "#FCFCFC"), ("", None), ("", None),
    ("TM AND @ 1990", "#BCBCBC"), ("BEST FRIEND GAMES LTD.", "#BCBCBC"), ("LICENSED BY", "#7C7C7C"),
    ("FRIENDS OF JAPAN INC.", "#7C7C7C"), ("", None), ("", None), ("", None),
    ("THANK YOU FOR PLAYING!", "#F8D878"),
]
LINE = 14


def credits(scroll, frame):
    img = blank()
    stars(img, frame, seed=21, n=60)
    y = SH - scroll
    for text, col in CREDITS:
        if text == "LOGO":
            if -LOGO.height < y < SH:
                img.alpha_composite(LOGO, ((SW - LOGO.width) // 2, y))
            y += LOGO.height + 4
            continue
        if text and -8 < y < SH:
            center(img, y, text, col)
        y += LINE
    return img


def credits_len():
    return LOGO.height + 4 + (len(CREDITS) - 1) * LINE


# ---------------------------------------------------------------- the demo
def build():
    frames, labels = [], []

    def add(im, n=1):
        for _ in range(n):
            frames.append(im)

    for f in range(12):
        add(title(f))
    for f in range(8):
        add(title(12 + f, menu=0 if f < 4 else 1))
    for f in range(8):
        add(title(20 + f, menu=0))
    # password: type B7KM-Q2WF
    word, cur = "B7KMQ2WF", 0
    entered = ""
    for ch in word:
        tgt = KEYS.index(ch)
        while cur != tgt:
            cur += 1 if tgt > cur else -1
            add(password(entered, cur, len(frames)))
            if abs(tgt - cur) > 3:
                cur += 2 if tgt > cur else -2
        add(password(entered, cur, len(frames)), 2)
        entered += ch
    for f in range(8):
        add(password(entered, len(KEYS) + 1, f, "PASSWORD OK! MATCH 2" if f > 2 else None))
    for f in range(18):
        add(vs("mike", "stew", 2, f))
    import arenas
    m = arenas.scene(2, 0)
    live = hud.compose(m, lambda s: hud.top_bar(s, "mike", "stew", 0.55, 0.62, 74, 1),
                       lambda s: hud.announcer_bar(s, "BIG BEEFY STEW IS", "ON THE MOVE!", frame=1))
    for f in range(10):
        add(pause(live, [0, 0, 1, 1, 2, 2, 1, 1, 0, 0][f], f))
    for f in range(18):
        add(win("mike", "niko", f))
    for f in range(18):
        add(lose("niko", f, "DDT"))
    total = credits_len() + SH
    for s in range(0, total, 4):
        add(credits(s, s // 4))
    return frames


if __name__ == "__main__":
    fr = build()
    big = [f.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST) for f in fr]
    big[0].save(OUT + "screens_demo.gif", save_all=True, append_images=big[1:], duration=150, loop=0, disposal=1)
    import arenas
    m = arenas.scene(2, 0)
    live = hud.compose(m, lambda s: hud.top_bar(s, "mike", "stew", 0.55, 0.62, 74, 1),
                       lambda s: hud.announcer_bar(s, "BIG BEEFY STEW IS", "ON THE MOVE!", frame=1))
    stills = {"title": title(0), "title_menu": title(1, menu=0), "vs": vs("mike", "jim", 1, 12),
              "win": win("mike", "stew", 2), "champion": win("mike", None, 3),
              "lose": lose("niko", 10, "DDT"), "password": password("B7KM", 13, 0),
              "pause": pause(live, 0, 0), "credits": credits(260, 0)}
    for k, im in stills.items():
        im.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST).save(OUT + f"screen_{k}.png")
    print(len(fr))
