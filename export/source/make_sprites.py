"""Home Wide Wrestling - static sprite style test.

Draws the four wrestlers (original characters based on the user's friends)
in four NES-era looks. Each character is built from simple shapes in "unit"
space, then rasterised pixel-by-pixel at the style's resolution, so every
style really is drawn at its own pixel size (not just a resize).
"""
import math
from PIL import Image

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"

# ---------------------------------------------------------------- colours
# Mostly entries from the NES master palette; skin tones are custom so the
# four friends read as themselves.
C = {
    "black": "#000000", "white": "#FCFCFC", "grey": "#BCBCBC", "dgrey": "#7C7C7C",
    "red": "#F83800", "red_s": "#A81000", "red_h": "#F87858",
    "navy": "#0000BC", "navy_s": "#00007C", "navy_h": "#0058F8",
    "lblue": "#3CBCFC", "lblue_s": "#0078F8",
    "orange": "#E45C10", "orange_s": "#881400", "orange_h": "#FCA044",
    "blue": "#0058F8", "blue_s": "#0000BC", "blue_h": "#6888FC",
    "blond": "#F8B800", "blond_s": "#AC7C00", "blond_h": "#F8D878",
    "ginger": "#C86020", "ginger_s": "#881400",
    "brown": "#503000", "brown_s": "#000000", "brown_h": "#881400",
    "curl": "#503000",
    # skin (custom)
    "mike": "#C68642", "mike_s": "#8D5524", "mike_h": "#E0A868",
    "niko": "#F2D0A8", "niko_s": "#D8A878", "niko_h": "#FCE8CC",
    "jim": "#F8D0B8", "jim_s": "#E0A088", "jim_h": "#FCE4D8",
    "stew": "#F4C0A0", "stew_s": "#D89078", "stew_h": "#FCD8C0",
    "cheek": "#F87858",
    "green": "#00A800", "green_s": "#006800", "green_h": "#58D854",
    "pink": "#F85898", "pink_s": "#B8286C", "pink_h": "#F8A4C0",
    "volt": "#F8D878", "volt_s": "#F8B800",
    "sing": "#303030", "sing_s": "#000000", "sing_h": "#7C7C7C",
}


def hx(c):
    c = C.get(c, c)
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


# ---------------------------------------------------------------- shapes
class Shape:
    def __init__(self, kind, p, mat, head=False, pattern=None):
        self.kind, self.p, self.mat, self.head, self.pattern = kind, p, mat, head, pattern

    def scaled(self, k, pivot):
        """Scale about pivot (used to enlarge heads for chunkier styles)."""
        if not self.head or k == 1:
            return self
        px, py = pivot
        f = lambda x, y: (px + (x - px) * k, py + (y - py) * k)
        if self.kind == "ell":
            cx, cy, rx, ry = self.p
            nx, ny = f(cx, cy)
            p = (nx, ny, rx * k, ry * k)
        elif self.kind == "rect":
            x0, y0, x1, y1 = self.p
            a, b = f(x0, y0)
            c, d = f(x1, y1)
            p = (a, b, c, d)
        else:
            p = [f(x, y) for x, y in self.p]
        return Shape(self.kind, p, self.mat, self.head, self.pattern)

    def bbox(self):
        if self.kind == "ell":
            cx, cy, rx, ry = self.p
            return cx - rx, cy - ry, cx + rx, cy + ry
        if self.kind == "rect":
            return self.p
        xs = [x for x, _ in self.p]
        ys = [y for _, y in self.p]
        return min(xs), min(ys), max(xs), max(ys)

    def hit(self, u, v):
        if self.kind == "ell":
            cx, cy, rx, ry = self.p
            return ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 <= 1.0
        if self.kind == "rect":
            x0, y0, x1, y1 = self.p
            return x0 <= u <= x1 and y0 <= v <= y1
        # polygon, even-odd
        pts, inside, j = self.p, False, len(self.p) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > v) != (yj > v) and u < (xj - xi) * (v - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        return inside


def capsule(p0, p1, r, mat):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0) or 1e-6
    nx, ny = -(y1 - y0) / L * r, (x1 - x0) / L * r
    return [Shape("poly", [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], mat),
            Shape("ell", (x0, y0, r, r), mat), Shape("ell", (x1, y1, r, r), mat)]


def mirror(shapes):
    out = []
    for s in shapes:
        if s.kind == "ell":
            cx, cy, rx, ry = s.p
            p = (-cx, cy, rx, ry)
        elif s.kind == "rect":
            x0, y0, x1, y1 = s.p
            p = (-x1, y0, -x0, y1)
        else:
            p = [(-x, y) for x, y in s.p]
        out.append(Shape(s.kind, p, s.mat, s.head, s.pattern))
    return out


# ---------------------------------------------------------------- characters
def build(ch):
    """Return (shapes, features) for one wrestler in unit space.
    y=0 is the top of the head, feet at y=H, x centred on 0."""
    H, sw, ww = ch["H"], ch["sw"], ch["ww"]
    ysh, ycr, lc, lw, at, ua = ch["ysh"], ch["ycr"], ch["lc"], ch["lw"], ch["at"], ch["ua"]
    yfist, bh = ch["yfist"], ch["boot"]
    skin, suit = "skin", "suit"
    S = []
    back, front = [], []

    # hair behind the head (Mike's mane)
    if ch["name"] == "mike":
        back += [Shape("ell", (0, 9.0, 8.6, 10.0), "hair", True, "curls")]
        for a in range(-40, 230, 25):
            r = math.radians(a)
            back.append(Shape("ell", (8.0 * math.cos(r), 9.0 + 9.2 * math.sin(r), 2.2, 2.2),
                              "hair", True, "curls"))
        for x in (-5.5, -2.8, 0, 2.8, 5.5):
            back.append(Shape("ell", (x, 0.2 + abs(x) * 0.25, 2.3, 2.1), "hair", True, "curls"))

    # legs + boots
    leg = [Shape("rect", (lc - lw, ycr - 1, lc + lw, H - bh), ch.get("legmat", skin)),
           Shape("rect", (lc - lw - 0.4, H - bh, lc + lw + 0.4, H), "boot")]
    if ch.get("stripe"):
        leg.append(Shape("rect", (lc + lw - 1.1, ycr, lc + lw, H - bh), "stripe"))
    if ch["name"] == "mike":
        kn = ycr + (H - bh - ycr) * 0.45
        leg.append(Shape("rect", (lc - lw - 0.3, kn, lc + lw + 0.3, kn + 2.6), "pad"))
        leg.append(Shape("rect", (lc - lw - 0.4, H - bh, lc + lw + 0.4, H - bh + 1.2), "pad"))
    S += leg + mirror(leg)

    # torso
    torso_mat = suit if (ch.get("singlet") or ch.get("onestrap")) else skin
    S.append(Shape("poly", [(-sw, ysh), (sw, ysh), (ww, ycr - 3), (-ww, ycr - 3)], torso_mat,
                   pattern=ch.get("pattern")))
    if ch.get("belly"):
        bx, by, brx, bry = ch["belly"]
        S.append(Shape("ell", (0, by, brx, bry), torso_mat, pattern=ch.get("pattern")))
    # hips / trunks
    S.append(Shape("rect", (-ww, ycr - 4, ww, ycr + 2), ch.get("hipmat", suit),
                   pattern=ch.get("pattern")))
    if ch.get("singlet"):
        # low-cut singlet: skin shows at upper chest between the straps
        S.append(Shape("poly", [(-sw + 3.0, ysh - 0.5), (sw - 3.0, ysh - 0.5),
                                (sw - 5.0, ysh + 4.5), (-sw + 5.0, ysh + 4.5)], skin))
    if ch.get("onestrap"):
        # one strap over the left shoulder, neckline runs diagonally to the right armpit
        S.append(Shape("poly", [(-sw + 3.8, ysh - 0.5), (sw + 0.5, ysh - 0.5),
                                (sw + 0.5, ysh + at + 5.5), (-sw + 3.8, ysh + 1.0)], skin))

    arms_front = []
    if ch.get("pose") == "pump":
        # Stew's own signature pose: yelling fist pump.
        # viewer's left arm: elbow down at his side, fist pulled up in front by his jaw
        S += [Shape("ell", (-sw + 0.6, ysh + 2.2, at * 0.85, at * 0.8), skin)]
        S += capsule((-sw - 0.4, ysh + 2.5), (-sw - 1.6, ysh + 10.5), at * 0.55, skin)
        # a thin dark line behind the front arm so it separates from his body
        fa0, fa1, fist = (-sw - 1.6, ysh + 10.5), (-sw + 2.4, ysh + 2.6), (-sw + 2.6, ysh + 1.4)
        arms_front += capsule(fa0, fa1, at * 0.5 + 0.9, "line")
        arms_front += [Shape("ell", (fist[0], fist[1], at * 0.6 + 0.9, at * 0.6 + 0.9), "line")]
        arms_front += capsule(fa0, fa1, at * 0.5, skin)
        arms_front += [Shape("ell", (fist[0], fist[1], at * 0.6, at * 0.6), skin)]
        # viewer's right arm: thrust up and out, fist above head height
        S += [Shape("ell", (sw - 0.6, ysh + 2.2, at * 0.85, at * 0.8), skin)]
        S += capsule((sw - 0.2, ysh + 1.8), (sw + 6.4, ysh - 2.6), at * 0.55, skin)
        S += [Shape("ell", (sw + 3.8, ysh - 1.8, at * 0.75, at * 0.55), skin)]   # bicep
        S += capsule((sw + 6.4, ysh - 2.6), (sw + 7.6, ysh - 10.6), at * 0.5, skin)
        S += [Shape("ell", (sw + 7.8, ysh - 11.8, at * 0.62, at * 0.62), skin)]
    if ch.get("pose") != "pump":
        pass
    # arms: double-bicep flex (the signature / victory pose)
    ex = sw + ua
    arm = [Shape("ell", (sw - 0.6, ysh + at * 0.45, at * 0.85, at * 0.8), skin),        # deltoid
           Shape("rect", (sw - 1, ysh, ex, ysh + at), skin),                               # upper arm
           Shape("ell", (ex - at * 1.3, ysh - at * 0.05, at * ch["bicep"], at * 0.7), skin),  # bicep
           Shape("rect", (ex - at, yfist, ex, ysh + at), skin),                            # forearm
           Shape("ell", (ex - at / 2, yfist, at * 0.62, at * 0.62), skin)]                 # fist
    if ch.get("wrist"):
        arm.append(Shape("rect", (ex - at - 0.2, yfist + 1.4, ex + 0.2, yfist + 3.2), ch["wrist"]))
    if ch.get("elbow"):
        arm.append(Shape("rect", (ex - at - 0.3, ysh - 1.4, ex + 0.3, ysh + at + 0.3), "elbow"))
    if ch.get("pose") != "pump":
        S += arm + mirror(arm)
    if ch.get("singlet"):
        # visible singlet straps over both shoulders
        strap = [Shape("rect", (sw - 3.4, ysh - 1.0, sw - 1.4, ysh + 4.8), suit)]
        S += strap + mirror(strap)
    if ch.get("onestrap"):
        # the single strap sits on top of the left shoulder, over the deltoid
        S.append(Shape("poly", [(-sw + 0.6, ysh - 1.2), (-sw + 3.8, ysh - 1.2),
                                (-sw + 3.8, ysh + 2.5), (-sw + 1.2, ysh + 4.0)], suit))

    # neck + head
    head = [Shape("rect", (-ch["neck"], 8.5, ch["neck"], ysh + 1), skin, True),
            Shape("ell", (-ch["hw"] + 0.2, 5.6, 1.2, 1.6), skin, True),
            Shape("ell", (ch["hw"] - 0.2, 5.6, 1.2, 1.6), skin, True),
            Shape("ell", (0, 5.2, ch["hw"], ch["hh"]), skin, True)]
    if ch["name"] == "stew":
        head.append(Shape("ell", (0, 8.6, ch["hw"] * 0.8, 2.2), skin, True))  # double chin
    S = back + S + head

    # hair on top / beards / headband
    n = ch["name"]
    if n == "mike":
        front += [Shape("ell", (0, 1.1, 4.7, 2.1), "hair", True, "curls"),
                  # short beard hugging the jaw only
                  Shape("poly", [(-4.1, 6.6), (-3.0, 9.6), (0, 10.8), (3.0, 9.6), (4.1, 6.6),
                                 (3.4, 7.3), (2.3, 9.0), (0, 9.8), (-2.3, 9.0), (-3.4, 7.3)],
                        "beard", True)]
    elif n == "niko":
        front += [Shape("ell", (0, 2.3, 4.9, 3.0), "hair", True),
                  Shape("rect", (-5.0, 2.3, -3.9, 7.6), "hair", True),
                  Shape("rect", (3.9, 2.3, 5.0, 7.6), "hair", True),
                  # jagged bangs, stopping above the eyes
                  Shape("poly", [(-4.6, 2.6), (4.6, 2.6), (4.4, 4.2), (2.8, 3.5), (1.5, 4.2),
                                 (0, 3.5), (-1.5, 4.2), (-2.8, 3.5), (-4.4, 4.2)], "hair", True)]
    elif n == "jim":
        front += [Shape("ell", (0, 1.9, 4.6, 2.6), "hair", True)]
        for x in (-3.2, -1.1, 1.1, 3.2):
            front.append(Shape("ell", (x, 0.5, 1.5, 1.3), "hair", True))
        front.append(Shape("rect", (-1.9, 7.1, 1.9, 7.8), "beard", True))        # moustache
        front.append(Shape("poly", [(-1.4, 8.8), (1.4, 8.8), (1.1, 10.6), (0, 11.2), (-1.1, 10.6)],
                           "beard", True))                                         # chin
    elif n == "stew":
        front += [Shape("ell", (0, 1.6, 5.0, 2.3), "hair", True),
                  Shape("ell", (0.6, 0.3, 2.6, 1.6), "hair", True),        # swept-up front
                  Shape("rect", (-5.2, 1.6, -4.1, 4.4), "hair", True),
                  Shape("rect", (4.1, 1.6, 5.2, 4.4), "hair", True),
                  Shape("ell", (0, 8.4, 1.9, 1.7), "mouthopen", True)]     # yelling
    S += front + arms_front

    # point features: (u, v, what) - placed as single pixels after rasterising
    ey = 6.1 if n == "niko" else 5.5
    feats = [(-1.6, ey, "eye"), (1.6, ey, "eye")]
    if n == "mike":
        feats += [(-0.8, 8.0, "teeth"), (0, 8.0, "teeth"), (0.8, 8.0, "teeth")]
    elif n == "stew":
        feats += [(-3.1, 7.2, "cheek"), (3.1, 7.2, "cheek"), (-0.6, 7.2, "teeth"), (0.6, 7.2, "teeth"),
                  (-2.5, 4.2, "brow"), (-1.3, 4.7, "brow"), (1.3, 4.7, "brow"), (2.5, 4.2, "brow")]
    else:
        feats += [(-0.6, 8.3, "mouth"), (0.6, 8.3, "mouth")]
    return S, feats


CHARS = {
    "mike": dict(name="mike", label="Mighty Mike", H=50, sw=12.5, ww=10, ysh=12.0, ycr=31, lc=5.4, lw=4.6,
                 at=5.0, ua=6.0, yfist=4.2, boot=5, neck=3.0, hw=4.4, hh=5.1, bicep=1.05,
                 belly=(0, 24.5, 10.5, 6.5), hipmat="suit", wrist="pad",
                 mats=dict(skin=("mike", "mike_s", "mike_h"), suit=("red", "red_s", "red_h"),
                           boot=("red", "red_s", "red_h"), pad=("white", "grey", "white"),
                           hair=("black", "black", "curl"), beard=("black", "black", "curl")),
                 nes3=dict(skin="mike", suit="red", boot="red", pad="red", hair="black", beard="black",
                           eye="black", teeth="mike", mouth="black", cheek="mike")),
    "niko": dict(name="niko", label="Nimble Niko", H=64, sw=8.5, ww=6.3, ysh=12.0, ycr=35, lc=3.6, lw=3.0,
                 at=3.2, ua=7.0, yfist=3.2, boot=4.5, neck=2.1, hw=4.2, hh=5.0, bicep=0.8,
                 legmat="suit", hipmat="suit", stripe=True, wrist="band",
                 mats=dict(skin=("niko", "niko_s", "niko_h"), suit=("navy", "navy_s", "navy_h"),
                           boot=("navy", "navy_s", "navy_h"), stripe=("lblue", "lblue_s", "white"),
                           band=("lblue", "lblue_s", "white"), hair=("black", "black", "dgrey")),
                 nes3=dict(skin="niko", suit="navy", boot="navy", stripe="navy", band="black",
                           hair="black", eye="black", mouth="niko", cheek="niko")),
    # Jim: old-school giant look - green one-strap singlet, tall red boots, wrist tape
    "jim": dict(name="jim", label='Jim "The Goat"', H=60, sw=10.8, ww=9.5, ysh=12.0, ycr=34, lc=4.9, lw=4.2,
                at=4.0, ua=6.5, yfist=3.6, boot=9, neck=2.6, hw=4.3, hh=5.0, bicep=0.85,
                onestrap=True, belly=(0, 25.5, 11.3, 8.5), wrist="tape",
                mats=dict(skin=("jim", "jim_s", "jim_h"), suit=("green", "green_s", "green_h"),
                          boot=("red", "red_s", "red_h"), tape=("white", "grey", "white"),
                          hair=("blond", "blond_s", "blond_h"), beard=("blond_s", "brown", "blond")),
                nes3=dict(skin="jim", suit="green", boot="green", tape="jim", hair="blond", beard="blond",
                          eye="green", mouth="green", cheek="jim")),
    # Stew: fist-pump pose; blue singlet with a black jagged band and a yellow zigzag
    "stew": dict(name="stew", label="Big Beefy Stew", H=57, sw=12.8, ww=12.5, ysh=12.5, ycr=36, lc=6.4, lw=5.6,
                 at=5.0, ua=6.2, yfist=4.0, boot=5, neck=3.6, hw=5.5, hh=5.6, bicep=0.8,
                 singlet=True, belly=(0, 26.5, 15.2, 11.0), hipmat="suit", pattern="quake", pose="pump",
                 mats=dict(skin=("stew", "stew_s", "stew_h"), suit=("blue", "blue_s", "blue_h"),
                           suit2=("sing", "sing_s", "sing_h"), edge=("white", "grey", "white"),
                           volt=("volt", "volt_s", "white"), boot=("black", "black", "dgrey"),
                           hair=("brown", "brown_s", "brown_h"), mouthopen=("red_s", "black", "red_s")),
                 nes3=dict(skin="stew", suit="blue", suit2="black", edge="blue", volt="black", boot="black",
                           hair="black", mouthopen="black", eye="black", teeth="stew", cheek="stew",
                           brow="black", line="black")),
}
ORDER = ["mike", "niko", "jim", "stew"]

# ---------------------------------------------------------------- styles
# target = pixel height of Niko (the tallest); head = head enlargement.
STYLES = {
    1: dict(key="wm89", target=60, head=1.4, outline=False, shade=0, feats={"eye"},
            bg=("#000000", "#6888FC", "#0000BC")),
    2: dict(key="tecmo", target=56, head=1.45, outline=True, shade=2, feats={"eye", "mouth", "teeth", "brow"},
            bg=("#000000", "#BCBCBC", "#7C7C7C")),
    3: dict(key="tagteam", target=38, head=1.65, outline=False, shade=0, nes3=True, feats={"eye"},
            bg=("#000000", "#F8D878", "#AC7C00")),
    4: dict(key="steelcage", target=72, head=1.2, outline=True, shade=3,
            feats={"eye", "mouth", "teeth", "cheek", "brow"}, bg=("#000000", "#A4E4FC", "#3CBCFC")),
}


def colour_for(ch, st, shape, u, v, xr, yr, px, py):
    mat = shape.mat
    if shape.pattern == "hoops" and mat == "suit":
        if int((v - ch["ysh"]) // 2.7) % 2 == 1:
            mat = "suit2"
    if shape.pattern == "quake" and mat == "suit":
        def zig(x, per, amp):
            return amp * (abs(((x / per) % 2) - 1) * 2 - 1)
        top = ch["ysh"] + 8.5 + zig(u, 3.2, 1.4)
        bot = ch["ycr"] - 7.0 + zig(u + 1.6, 3.2, 1.4)
        if top - 0.9 <= v < top or bot < v <= bot + 0.9:
            mat = "edge"
        elif top <= v <= bot:
            mid = (top + bot) / 2 + zig(u, 2.2, 1.0)
            mat = "volt" if abs(v - mid) < 0.75 else "suit2"
    if mat == "line":
        if st.get("nes3"):
            return hx(ch["nes3"].get("line", "black"))
        return hx("black") if st["outline"] else hx(ch["mats"]["skin"][1])
    if st.get("nes3"):
        return hx(ch["nes3"].get(mat, "black"))
    base, sh, hi = ch["mats"][mat]
    if shape.pattern == "curls" and st["shade"] >= 2 and (px * 2 + py * 3) % 7 == 0:
        return hx(hi)
    # distance to this shape's own left/right edge on this row
    if shape.kind == "ell":
        cx, cy, rx, ry = shape.p
        half = rx * math.sqrt(max(0.0, 1 - ((v - cy) / ry) ** 2))
        left, right = cx - half, cx + half
    else:
        bx0, _, bx1, _ = shape.bbox()
        left, right = bx0, bx1
    w = max(right - left, 1e-6)
    if st["shade"] >= 2 and (right - u) < min(0.34 * w, 3.2):
        return hx(sh)
    if st["shade"] >= 3 and (u - left) < min(0.22 * w, 1.8) and yr < 0.6 and shape.pattern != "curls":
        return hx(hi)
    return hx(base)


def render(chname, st, s, minx_pad=1):
    ch = CHARS[chname]
    shapes, feats = build(ch)
    k = st["head"]
    pivot = (0, ch["ysh"] + 0.5)
    shapes = [sh.scaled(k, pivot) for sh in shapes]
    feats = [(pivot[0] + (u - pivot[0]) * k, pivot[1] + (v - pivot[1]) * k, w) for u, v, w in feats]
    bb = [sh.bbox() for sh in shapes]
    x0, y0 = min(b[0] for b in bb), min(b[1] for b in bb)
    x1, y1 = max(b[2] for b in bb), max(b[3] for b in bb)
    W = int(math.ceil((x1 - x0) * s)) + 2 * minx_pad + 2
    Hh = int(math.ceil((y1 - y0) * s)) + 2 * minx_pad + 1
    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    pix = img.load()
    ox, oy = minx_pad + 1, minx_pad
    for py in range(Hh):
        for px in range(W):
            u = x0 + (px - ox + 0.5) / s
            v = y0 + (py - oy + 0.5) / s
            col = None
            for sh in shapes:
                if sh.hit(u, v):
                    bx0, by0, bx1, by1 = sh.bbox()
                    xr = (u - bx0) / max(bx1 - bx0, 1e-6)
                    yr = (v - by0) / max(by1 - by0, 1e-6)
                    col = colour_for(ch, st, sh, u, v, xr, yr, px, py)
            if col:
                pix[px, py] = col
    # single-pixel face details
    for u, v, what in feats:
        if what not in st["feats"]:
            continue
        px = int((u - x0) * s + ox)
        py = int((v - y0) * s + oy)
        if 0 <= px < W and 0 <= py < Hh and pix[px, py][3]:
            if st.get("nes3"):
                col = hx(ch["nes3"].get(what, "black"))
            else:
                col = hx({"eye": "black", "mouth": "black", "teeth": "white", "cheek": "cheek",
                          "brow": "brown"}[what])
            if what == "mouth" and chname == "mike":
                continue
            pix[px, py] = col
    if st["outline"]:
        src = img.copy().load()
        for py in range(Hh):
            for px in range(W):
                if src[px, py][3]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    qx, qy = px + dx, py + dy
                    if 0 <= qx < W and 0 <= qy < Hh and src[qx, qy][3]:
                        pix[px, py] = hx("black")
                        break
    # feet baseline in pixels (for lining everyone up)
    feet = int((ch["H"] - y0) * s + oy)
    return img, feet


def scale_for(st):
    ch = CHARS["niko"]
    shapes, _ = build(ch)
    shapes = [sh.scaled(st["head"], (0, ch["ysh"] + 0.5)) for sh in shapes]
    bb = [sh.bbox() for sh in shapes]
    return st["target"] / (max(b[3] for b in bb) - min(b[1] for b in bb))


def stage(n, st):
    """Line the four wrestlers up on a 256-wide NES-sized strip."""
    s = scale_for(st)
    sprites = [render(c, st, s) for c in ORDER]
    W, H = 256, 120
    crowd, mat, apron = (hx(x) for x in st["bg"])
    img = Image.new("RGBA", (W, H), crowd)
    p = img.load()
    floor = 104
    for y in range(20, H):
        for x in range(W):
            p[x, y] = mat if y < floor + 6 else apron
    # simple crowd dots + ring ropes, same in every style
    for y in range(2, 18, 4):
        for x in range((y // 4) % 2 * 3, W, 6):
            p[x, y] = hx("#7C7C7C") if n != 4 else hx("#BCBCBC")
    if n == 4:  # cage mesh behind the ring
        for y in range(0, 20):
            for x in range(W):
                if (x + y) % 8 == 0 or (x - y) % 8 == 0:
                    p[x, y] = hx("#787878")
    for ry in (8, 13, 18):
        for x in range(W):
            p[x, ry] = hx("#F8F8F8")
    total = sum(sp.width for sp, _ in sprites)
    gap = (W - total) // 5
    x = gap
    for sp, feet in sprites:
        img.alpha_composite(sp, (x, floor - feet))
        x += sp.width + gap
    return img, sprites


if __name__ == "__main__":
    for n, st in STYLES.items():
        img, sprites = stage(n, st)
        img.convert("RGB").resize((img.width * 4, img.height * 4), Image.NEAREST).save(
            OUT + f"style{n}_{st['key']}.png")
        for c, (sp, _) in zip(ORDER, sprites):
            sp.resize((sp.width * 6, sp.height * 6), Image.NEAREST).save(OUT + f"s{n}_{c}.png")
        print(n, st["key"], [(c, sp.size) for c, (sp, _) in zip(ORDER, sprites)])
