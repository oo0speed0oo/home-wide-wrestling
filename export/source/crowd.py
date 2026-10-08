"""A packed NES-style crowd with some character: dark back rows, bright front rows,
signs, camera flashes, a photographer, a foam finger, and fans throwing their arms up.
draw_crowd(img, frame) paints rows 0..TOP_H-1 of `img`; frames loop every 8."""
import random
from PIL import ImageDraw

TOP_H = 62

SKINS = ["#F4C0A0", "#C68642", "#F2D0A8", "#8D5524", "#F8D0B8", "#E0A868"]
HAIR = ["#000000", "#503000", "#881400", "#F8B800", "#7C7C7C", None]          # None = bald
SHIRTS = ["#F83800", "#FCFCFC", "#F8B800", "#0058F8", "#00A800", "#F85898", "#6888FC", "#E45C10"]

# 3x5 / 5x5 pixel letters for the signs
GLYPHS = {
    "M": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X"],
    "W": ["X...X", "X...X", "X.X.X", "XX.XX", "X...X"],
    "H": ["X.X", "X.X", "XXX", "X.X", "X.X"],
    "I": ["XXX", ".X.", ".X.", ".X.", "XXX"],
    "K": ["X.X", "XX.", "X..", "XX.", "X.X"],
    "E": ["XXX", "X..", "XX.", "X..", "XXX"],
    "S": ["XXX", "X..", "XXX", "..X", "XXX"],
    "T": ["XXX", ".X.", ".X.", ".X.", ".X."],
    "G": ["XXX", "X..", "X.X", "X.X", "XXX"],
    "O": ["XXX", "X.X", "X.X", "X.X", "XXX"],
    "N": ["X..X", "XX.X", "X.XX", "X..X", "X..X"],
    "J": ["..X", "..X", "..X", "X.X", "XXX"],
    "A": ["XXX", "X.X", "XXX", "X.X", "X.X"],
    "B": ["XX.", "X.X", "XX.", "X.X", "XX."],
    "C": ["XXX", "X..", "X..", "X..", "XXX"],
    "D": ["XX.", "X.X", "X.X", "X.X", "XX."],
    "F": ["XXX", "X..", "XX.", "X..", "X.."],
    "L": ["X..", "X..", "X..", "X..", "XXX"],
    "P": ["XXX", "X.X", "XXX", "X..", "X.."],
    "R": ["XX.", "X.X", "XX.", "X.X", "X.X"],
    "U": ["X.X", "X.X", "X.X", "X.X", "XXX"],
    "V": ["X.X", "X.X", "X.X", "X.X", ".X."],
    "Y": ["X.X", "X.X", ".X.", ".X.", ".X."],
    "Z": ["XXX", "..X", ".X.", "X..", "XXX"],
    "#": [".X.X.", "XXXXX", ".X.X.", "XXXXX", ".X.X."],
    "1": [".X", "XX", ".X", ".X", ".X"],
    "!": ["X", "X", "X", ".", "X"],
    " ": ["..", "..", "..", "..", ".."],
}


def hx(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def dim(c, k=0.5):
    r, g, b, a = hx(c)
    return (int(r * k), int(g * k), int(b * k) + 18, 255)


def text_w(s):
    return sum(len(GLYPHS[ch][0]) + 1 for ch in s) - 1


def put_text(img, x, y, s, col):
    p = img.load()
    for ch in s:
        g = GLYPHS[ch]
        for gy, line in enumerate(g):
            for gx, v in enumerate(line):
                if v == "X" and 0 <= x + gx < img.width and 0 <= y + gy < img.height:
                    p[x + gx, y + gy] = hx(col)
        x += len(g[0]) + 1


LEVELS = {
    # fill: share of seats with a fan; hype: fans with arms up; light: how lit the stands are
    1: dict(fill=0.2, hype=0.0, signs=0, foam=False, photo=False, flashes=0, light=0.95),
    2: dict(fill=0.55, hype=0.15, signs=2, foam=False, photo=True, flashes=1, light=0.9),
    4: dict(fill=1.0, hype=0.35, signs=6, foam=True, photo=True, flashes=4, light=0.8),
}


# fan signs follow whoever is in the match: (name sign, second sign, sign colour, letter colour)
FAN_SIGNS = {
    "mike": ("MIKE!", "MIGHTY", "#FCFCFC", "#F83800"),
    "stew": ("STEW!", "BEEF!", "#F8D878", "#0000BC"),
    "jim": ("JIM!", "GOAT", "#FCFCFC", "#00A800"),
    "niko": ("NIKO!", "TALL", "#F8D878", "#24188C"),
}
SIGN_SPOTS = [(18, 2), (122, 3), (70, 1), (168, 1), (200, 2), (226, 3)]   # x, rows back from the front


def sign_list(fighters):
    a, b = fighters
    A, B = FAN_SIGNS[a], FAN_SIGNS[b]
    words = [(A[0], A[2], A[3]), (B[0], B[2], B[3]), ("HWW", "#FCFCFC", "#0000BC"),
             ("#1", "#F85898", "#000000"), (B[1], B[2], B[3]), (A[1], A[2], A[3])]
    return [(x, row, w, bg, fg) for (x, row), (w, bg, fg) in zip(SIGN_SPOTS, words)]


def draw_crowd(img, frame, level=4, fighters=("mike", "stew")):
    L = LEVELS[level]
    d = ImageDraw.Draw(img)
    W = img.width
    d.rectangle((0, 0, W, TOP_H - 1), fill=hx("#000000"))
    rows = list(range(1, TOP_H - 6, 7))          # head-top y of each row, back to front
    nrows = len(rows)
    rnd = random.Random(11)
    fans = []
    for r, y in enumerate(rows):
        front = r >= nrows - 4                    # the front rows get full colour and faces
        for x in range((r % 2) * 3 - 3, W + 3, 6):
            fans.append(dict(x=x, y=y, r=r, front=front, skin=rnd.choice(SKINS),
                             hair=rnd.choice(HAIR), shirt=rnd.choice(SHIRTS),
                             here=rnd.random() < L["fill"], hype=rnd.random() < L["hype"],
                             cap=rnd.random() < 0.15, phase=rnd.randrange(4)))
    back_k = lambda r: (0.45 + 0.1 * r / max(1, nrows - 4)) * (L["light"] / 0.8)
    for r, y in enumerate(rows):
        d.line((0, y + 7, W, y + 7), fill=dim("#881400", min(1, 0.35 * L["light"] / 0.8) if r < nrows - 4 else 0.7))
    for f in fans:
        x, y = f["x"], f["y"]
        k = 1.0 if f["front"] else min(1.0, back_k(f["r"]))
        col = (lambda c: hx(c)) if f["front"] else (lambda c, k=k: dim(c, k))
        if not f["here"]:          # empty seat: a seat back and a gap
            d.rectangle((x + 1, y + 4, x + 3, y + 7), fill=col("#881400"))
            d.line((x + 1, y + 4, x + 3, y + 4), fill=col("#A81000"))
            continue
        up = f["hype"] and ((frame + f["phase"]) // 2) % 2 == 0
        d.rectangle((x, y + 4, x + 4, y + 7), fill=col(f["shirt"]))          # shirt
        d.rectangle((x + 1, y + 1, x + 3, y + 3), fill=col(f["skin"]))       # head
        if f["cap"]:
            d.line((x + 1, y, x + 3, y), fill=col(f["shirt"]))
            d.line((x + 1, y + 1, x + 4, y + 1), fill=col(f["shirt"]))
        elif f["hair"]:
            d.line((x + 1, y + 1, x + 3, y + 1), fill=col(f["hair"]))
        if f["front"]:
            d.point((x + 1, y + 2), fill=hx("#000000"))
            d.point((x + 3, y + 2), fill=hx("#000000"))
        if up:
            d.line((x - 1, y - 1, x - 1, y + 4), fill=col(f["skin"]))
            d.line((x + 5, y - 1, x + 5, y + 4), fill=col(f["skin"]))
            d.line((x - 2, y - 2, x - 1, y - 2), fill=col(f["skin"]))
            d.line((x + 5, y - 2, x + 6, y - 2), fill=col(f["skin"]))

    signs = sign_list(fighters)[:L["signs"]]
    for sx, row_back, word, bg, fg in signs:
        y = rows[nrows - row_back] - 8 + ((frame // 2 + sx) % 2)
        w = text_w(word) + 4
        sx = min(sx, W - w - 2)                    # keep the whole sign on screen
        d.rectangle((sx - 1, y - 1, sx + w, y + 7), fill=hx("#000000"))
        d.rectangle((sx, y, sx + w - 1, y + 6), fill=hx(bg))
        put_text(img, sx + 2, y + 1, word, fg)
        d.line((sx + 1, y + 7, sx + 1, y + 9), fill=hx("#F4C0A0"))
        d.line((sx + w - 2, y + 7, sx + w - 2, y + 9), fill=hx("#F4C0A0"))

    if L["foam"]:
        fx, fy = 150, rows[nrows - 2] - 7 + (frame // 2) % 2
        d.rectangle((fx, fy + 3, fx + 3, fy + 8), fill=hx("#F8B800"))
        d.rectangle((fx + 1, fy, fx + 2, fy + 3), fill=hx("#F8B800"))
        d.point((fx + 1, fy + 5), fill=hx("#000000"))
    flashes = []
    if L["photo"]:
        px_, py_ = 96, rows[-1]
        d.rectangle((px_, py_ + 4, px_ + 5, py_ + 7), fill=hx("#303030"))
        d.rectangle((px_ + 1, py_ + 1, px_ + 3, py_ + 3), fill=hx("#F2D0A8"))
        d.rectangle((px_ + 1, py_ + 2, px_ + 4, py_ + 3), fill=hx("#7C7C7C"))
        if frame % 4 == 1:
            flashes.append((px_ + 4, py_ + 2))
    frnd = random.Random(100 + frame)
    present = [f for f in fans if f["here"]]
    for _ in range(L["flashes"]):
        f = frnd.choice(present)
        flashes.append((f["x"] + 2, f["y"] + 2))
    for cx, cy in flashes:
        for dx, dy, c in ((0, 0, "#FCFCFC"), (1, 0, "#FCFCFC"), (-1, 0, "#FCFCFC"), (0, 1, "#FCFCFC"),
                          (0, -1, "#FCFCFC"), (2, 0, "#F8D878"), (-2, 0, "#F8D878"), (0, 2, "#F8D878"),
                          (0, -2, "#F8D878")):
            if 0 <= cx + dx < W and 0 <= cy + dy < TOP_H:
                img.putpixel((cx + dx, cy + dy), hx(c))
