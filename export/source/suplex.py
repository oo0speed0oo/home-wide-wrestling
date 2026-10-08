"""Home Wide Wrestling - animation test: Mighty Mike suplexes Big Beefy Stew.

Side-view sprites in the chosen Tecmo-style look (black outlines, far limbs
shaded darker). Figures are built from a tiny skeleton (joint angles), so
every frame is drawn straight at pixel size, never resized or rotated as an
image.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"

C = {
    "black": "#000000", "white": "#FCFCFC", "grey": "#BCBCBC", "dgrey": "#7C7C7C",
    "red": "#F83800", "red_s": "#A81000", "blue": "#0058F8", "blue_s": "#0000BC",
    "sing": "#303030", "volt": "#F8D878", "brown": "#503000", "brown_s": "#281800",
    "mike": "#C68642", "mike_s": "#8D5524", "stew": "#F4C0A0", "stew_s": "#D89078",
    "curl": "#503000", "mouth": "#A81000",
}


def rgb(c):
    c = C.get(c, c)
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def d(a):
    r = math.radians(a)
    return math.sin(r), -math.cos(r)


def add(p, a, L):
    dx, dy = d(a)
    return p[0] + dx * L, p[1] + dy * L


def rot(p, a, piv=(0, 0)):
    r = math.radians(a)
    x, y = p[0] - piv[0], p[1] - piv[1]
    return piv[0] + x * math.cos(r) - y * math.sin(r), piv[1] + x * math.sin(r) + y * math.cos(r)


# ---------------------------------------------------------------- primitives
class Cap:      # capsule: segment with radius
    def __init__(self, p0, p1, r, mat, far=False, clip=False):
        self.p0, self.p1, self.r, self.mat, self.far, self.clip = p0, p1, r, mat, far, clip

    def xf(self, f, s=1.0):
        return Cap(f(self.p0), f(self.p1), self.r * s, self.mat, self.far, self.clip)

    def bbox(self):
        return (min(self.p0[0], self.p1[0]) - self.r, min(self.p0[1], self.p1[1]) - self.r,
                max(self.p0[0], self.p1[0]) + self.r, max(self.p0[1], self.p1[1]) + self.r)

    def hit(self, x, y):
        (ax, ay), (bx, by) = self.p0, self.p1
        vx, vy = bx - ax, by - ay
        L2 = vx * vx + vy * vy
        t = 0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2))
        px, py = ax + t * vx - x, ay + t * vy - y
        return px * px + py * py <= self.r * self.r


class Ell:      # rotated ellipse; ang in degrees, clockwise
    def __init__(self, c, rx, ry, ang, mat, far=False, tag=None):
        self.c, self.rx, self.ry, self.ang, self.mat, self.far = c, rx, ry, ang, mat, far
        self.tag = tag

    def xf(self, f, s=1.0, dang=0.0, mirror=False):
        a = -self.ang if mirror else self.ang
        return Ell(f(self.c), self.rx * s, self.ry * s, a + dang, self.mat, self.far)

    def bbox(self):
        m = max(self.rx, self.ry)
        return self.c[0] - m, self.c[1] - m, self.c[0] + m, self.c[1] + m

    def hit(self, x, y):
        r = math.radians(-self.ang)
        dx, dy = x - self.c[0], y - self.c[1]
        lx, ly = dx * math.cos(r) - dy * math.sin(r), dx * math.sin(r) + dy * math.cos(r)
        return (lx / self.rx) ** 2 + (ly / self.ry) ** 2 <= 1.0


class Pix:      # a single face-detail pixel
    def __init__(self, p, mat):
        self.p, self.mat, self.far = p, mat, False

    def xf(self, f, *a, **k):
        return Pix(f(self.p), self.mat)


# ---------------------------------------------------------------- characters (unit space)
CH = {
    "mike": dict(Lt=15.0, rt=5.4, Lth=9.0, rth=3.0, Lsh=8.6, rsh=2.6, Lu=6.6, Lf=6.4, ra=2.5,
                 Rh=4.6, belly=(2.6, 5.0, 6.0), foot=3.0,
                 skin="mike", skin_s="mike_s"),
    "stew": dict(Lt=18.0, rt=6.2, Lth=10.6, rth=3.6, Lsh=9.8, rsh=3.0, Lu=7.6, Lf=7.2, ra=2.5,
                 Rh=5.2, belly=(4.8, 7.4, 8.4), foot=3.4,
                 skin="stew", skin_s="stew_s"),
}
# "tecmo" (chosen look): outlines, far limbs shaded.  "wm": WrestleMania look - bigger, chunkier,
# flat colours, no black outlines.
STYLE = sys.argv[1] if len(sys.argv) > 1 else "tecmo"
HS = {"wm": 1.45, "tt": 1.6}.get(STYLE, 1.35)   # NES big heads


def figure(name, P):
    """Build a wrestler facing right, hip at (0,0), in unit space. P = joint angles (degrees)."""
    c = CH[name]
    sk = c["skin"]
    hip = (0.0, 0.0)
    t = P["t"]
    sh = add(hip, t, c["Lt"])
    Rh = c["Rh"] * HS
    ha = t + P.get("nk", 0)
    hc = add(sh, ha, 1.0 + Rh)
    out = []

    def arm(u, f, far):
        e = add(sh, u, c["Lu"])
        w = add(e, f, c["Lf"])
        parts = []
        if not far:   # thin dark line so the near arm reads in front of the body
            parts += [Cap(sh, e, c["ra"] + 0.9, "line"), Cap(e, w, c["ra"] + 0.9, "line"),
                      Ell(w, c["ra"] + 1.6, c["ra"] + 1.6, 0, "line")]
        parts += [Cap(sh, e, c["ra"], sk, far), Cap(e, w, c["ra"] * 0.92, sk, far),
                  Ell(w, c["ra"] + 0.7, c["ra"] + 0.7, 0, sk, far)]
        if name == "mike":
            parts.append(Cap(add(w, f + 180, 1.2), add(w, f + 180, 2.4), c["ra"] + 0.25, "white", far))
        return parts

    def leg(th, shn, far):
        k = add(hip, th, c["Lth"])
        a = add(k, shn, c["Lsh"])
        toe = add(a, shn - 90, c["foot"])
        boot = "red" if name == "mike" else "black"
        parts = [Cap(hip, k, c["rth"], sk, far), Cap(k, a, c["rsh"], sk, far)]
        # trunks / singlet leg openings
        parts.append(Cap(hip, add(hip, th, 3.2), c["rth"] + 0.25, "red" if name == "mike" else "blue", far))
        if name == "mike":
            parts.append(Ell(k, c["rsh"] + 0.7, c["rsh"] + 0.7, 0, "white", far))   # kneepad
        parts += [Cap(add(k, shn, c["Lsh"] - 3.2), a, c["rsh"] + 0.35, boot, far),
                  Cap(a, toe, 1.7, boot, far)]
        return parts

    out += arm(P["fu"], P["ff"], True)
    out += leg(P["fth"], P["fsh"], True)
    if name == "mike":   # big curly mane behind the head
        mc = add(hc, ha - 90, 2.6 * HS)
        mc = add(mc, ha + 180, -1.0 * HS)
        out.append(Ell(mc, 5.0 * HS, 6.2 * HS, ha, "hair"))
        for k in range(150, 390, 30):
            out.append(Ell(add(mc, ha + k, 5.2 * HS), 1.5 * HS, 1.5 * HS, 0, "hair"))
    # torso + belly
    torso = "mike" if name == "mike" else "blue"
    out.append(Cap(hip, sh, c["rt"], torso))
    bf, brx, bry = c["belly"]
    bc = add(add(hip, t, c["Lt"] * 0.42), t + 90, bf)
    if name == "stew":
        # blue singlet with a black band wrapped round the belly, white edges, yellow zigzag line
        out.append(Ell(bc, brx, bry, t, "blue"))
        out.append(Cap(hip, add(hip, t, 3.0), c["rt"] + 0.2, "blue"))
        b0 = add(bc, t + 90, -(brx + c["rt"] + 3))
        b1 = add(bc, t + 90, brx + 3)
        out.append(Cap(b0, b1, 3.4, "white", clip=True))
        out.append(Cap(b0, b1, 2.6, "sing", clip=True))
        zz = [add(add(bc, t + 90, -(brx + c["rt"]) + k * 2.2), t, (0.9 if k % 2 else -0.9))
              for k in range(int((2 * brx + c["rt"]) / 2.2) + 2)]
        for a_, b_ in zip(zz, zz[1:]):
            out.append(Cap(a_, b_, 0.45, "volt", clip=True))
    else:
        out.append(Ell(bc, brx, bry, t, sk))
        out.append(Cap(hip, add(hip, t, 3.0), c["rt"] + 0.3, "red"))
    out += leg(P["nth"], P["nsh"], False)
    # neck + head
    out.append(Cap(sh, add(sh, ha, 1.5), c["rt"] * 0.55, sk))
    head = Ell(hc, Rh, Rh, 0, sk)
    head.tag = "head"
    out.append(head)

    def hl(x, y):   # head-local offset -> point
        p = add(hc, ha + 90, x * HS)
        return add(p, ha + 180, y * HS)

    if name == "mike":
        out.append(Ell(hl(-0.4, -2.8), 4.3 * HS, 2.4 * HS, ha, "hair"))
        out.append(Ell(hl(1.4, 3.4), 3.0 * HS, 1.6 * HS, ha + 18, "hair"))     # short beard
        out.append(Pix(hl(3.0, 2.2), "white"))                                   # grin
        out.append(Pix(hl(2.4, -0.5), "black"))                                  # eye
    else:
        out.append(Ell(hl(1.0, 3.9), 3.3 * HS, 1.8 * HS, ha, sk))                # double chin
        out.append(Ell(hl(-0.9, -2.7), 4.9 * HS, 3.0 * HS, ha, "hair"))
        out.append(Ell(hl(1.8, -4.3), 2.1 * HS, 1.3 * HS, ha, "hair"))           # swept-up front
        out.append(Pix(hl(2.7, -0.5), "black"))
        if P.get("yell"):
            out.append(Ell(hl(3.6, 2.5), 1.0 * HS, 1.1 * HS, 0, "mouth"))
        else:
            out.append(Pix(hl(3.6, 2.4), "black"))
    out += arm(P["nu"], P["nf"], False)
    return out


def place(prims, s, at, facing=1, R=0.0):
    """unit space -> screen px: rotate R about the hip, mirror if facing left, scale, move hip to `at`."""
    def f(p):
        x, y = rot(p, R)
        x *= facing
        return at[0] + x * s, at[1] + y * s
    out = []
    for p in prims:
        if isinstance(p, Ell):
            out.append(Ell(f(p.c), p.rx * s, p.ry * s, (p.ang + R) * facing, p.mat, p.far, p.tag))
        else:
            out.append(p.xf(f, s))
    return out


def group_rot(prims, G, piv):
    out = []
    for p in prims:
        f = lambda q: rot(q, G, piv)
        if isinstance(p, Ell):
            out.append(Ell(f(p.c), p.rx, p.ry, p.ang + G, p.mat, p.far, p.tag))
        else:
            out.append(p.xf(f))
    return out


def shift(prims, dx, dy):
    f = lambda q: (q[0] + dx, q[1] + dy)
    return [Ell(f(p.c), p.rx, p.ry, p.ang, p.mat, p.far, p.tag) if isinstance(p, Ell) else p.xf(f)
            for p in prims]


def head_of(prims):
    return [p for p in prims if isinstance(p, Ell) and p.tag == "head"][0].c


def extent(prims):
    bb = [p.bbox() for p in prims if not isinstance(p, Pix)]
    return min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb)


def ground(prims, floor):
    return shift(prims, 0, floor - extent(prims)[3])


NES3 = {
    "mike": {"mike": "mike", "red": "red", "white": "red", "hair": "black", "black": "black",
             "line": "black", "grin": "mike"},
    "stew": {"stew": "stew", "blue": "blue", "sing": "black", "white": "blue", "volt": "black",
             "hair": "black", "black": "black", "mouth": "black", "line": "black"},
}


def colour(name, p):
    if STYLE == "tt":
        m = p.mat
        if name == "mike" and m == "white" and isinstance(p, Pix):
            m = "grin"
        return rgb(NES3[name].get(m, "black"))
    c = CH[name]
    m = p.mat
    if m == "line":
        return rgb("black") if STYLE != "wm" else rgb(c["skin_s"])
    if p.far:   # far limbs one shade darker, the Tecmo way of separating them
        m = {c["skin"]: c["skin_s"], "red": "red_s", "blue": "blue_s", "white": "grey",
             "black": "black"}.get(m, m)
    if m == "hair":
        m = "black" if name == "mike" else "brown"
    return rgb(m)


def raster(name, prims, W, H):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    for p in prims:
        col = colour(name, p)
        if isinstance(p, Pix):
            x, y = int(p.p[0]), int(p.p[1])
            if 0 <= x < W and 0 <= y < H and px[x, y][3]:
                px[x, y] = col
            continue
        x0, y0, x1, y1 = p.bbox()
        for y in range(max(0, int(y0) - 1), min(H, int(y1) + 2)):
            for x in range(max(0, int(x0) - 1), min(W, int(x1) + 2)):
                if p.hit(x + 0.5, y + 0.5):
                    if getattr(p, "clip", False) and not px[x, y][3]:
                        continue
                    px[x, y] = col
    if STYLE in ("wm", "tt"):   # flat looks: no outlines at all
        return img
    # outer black outline
    src = img.copy().load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                qx, qy = x + dx, y + dy
                if 0 <= qx < W and 0 <= qy < H and src[qx, qy][3]:
                    px[x, y] = rgb("black")
                    break
    return img


# ---------------------------------------------------------------- poses (facing right)
STAND = dict(t=0, fu=158, ff=100, nu=165, nf=105, fth=188, fsh=182, nth=172, nsh=178)
WALK_A = dict(STAND, fth=200, fsh=192, nth=160, nsh=172)
WALK_B = dict(STAND, fth=165, fsh=176, nth=197, nsh=190)
TIE_A = dict(t=18, fu=78, ff=55, nu=68, nf=35, fth=205, fsh=196, nth=162, nsh=176)
TIE_B = dict(t=24, fu=84, ff=62, nu=74, nf=42, fth=200, fsh=192, nth=166, nsh=178)
HOOK = dict(t=6, fu=35, ff=-5, nu=48, nf=5, fth=196, fsh=182, nth=166, nsh=178)
BENT = dict(t=78, nk=10, fu=165, ff=172, nu=160, nf=168, fth=188, fsh=180, nth=176, nsh=180)
LIFT = dict(t=-12, fu=-8, ff=-22, nu=-2, nf=-16, fth=198, fsh=188, nth=168, nsh=184)
LIMP = dict(t=0, fu=172, ff=178, nu=168, nf=176, fth=184, fsh=180, nth=178, nsh=180, yell=True)
FLAT = dict(t=0, fu=150, ff=160, nu=160, nf=170, fth=182, fsh=180, nth=178, nsh=180)
SIT = dict(t=12, fu=190, ff=175, nu=165, nf=160, fth=92, fsh=98, nth=86, nsh=94)
POSE_UP = dict(STAND, nu=-18, nf=-8, fu=160, ff=110)

# ---------------------------------------------------------------- screen
W, H = 256, 200
FLOOR = 142
S = {"wm": 1.2, "tt": 0.8}.get(STYLE, 1.1)
K = S / 1.1   # spacing scales with sprite size


def backdrop():
    img = Image.new("RGBA", (W, H), rgb("black"))
    d_ = ImageDraw.Draw(img)
    d_.rectangle((0, 24, W, 44), fill=rgb("black"))
    for y in range(27, 43, 4):
        for x in range((y // 4) % 2 * 3, W, 6):
            img.putpixel((x, y), rgb("dgrey"))
    mat, apron = {"wm": ("#FCE0A8", "#AC7C00"), "tt": ("#F8D878", "#AC7C00")}.get(STYLE, ("grey", "dgrey"))
    d_.rectangle((0, 45, W, 150), fill=rgb(mat))
    d_.rectangle((0, 151, W, 158), fill=rgb(apron))
    for ry in (34, 39, 44):
        d_.line((0, ry, W, ry), fill=rgb("white"))
    return img


FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 8)


def text(d_, xy, s, col="white"):
    d_.fontmode = "1"
    d_.text(xy, s, font=FONT, fill=rgb(col))


def hud(img, e_mike, e_stew, line, tug=None, tug_xy=None):
    d_ = ImageDraw.Draw(img)
    d_.fontmode = "1"
    # energy bars
    text(d_, (8, 4), "MIKE", "white")
    text(d_, (W - 8 - 24, 4), "STEW", "white")
    for (x, val, col) in ((8, e_mike, "red"), (W - 8 - 80, e_stew, "blue")):
        d_.rectangle((x, 14, x + 80, 19), fill=rgb("dgrey"))
        w = int(79 * val)
        if x > W / 2:
            d_.rectangle((x + 80 - w, 15, x + 79, 18), fill=rgb(col))
        else:
            d_.rectangle((x + 1, 15, x + w, 18), fill=rgb(col))
    # commentary bar with a generic announcer
    d_.rectangle((0, 160, W, H), fill=rgb("black"))
    d_.rectangle((6, 166, 33, 193), outline=rgb("white"))
    d_.rectangle((12, 170, 27, 186), fill=rgb("#F0B090"))       # face
    d_.rectangle((12, 169, 27, 172), fill=rgb("dgrey"))         # grey hair
    d_.rectangle((10, 173, 11, 179), fill=rgb("dgrey"))         # headset
    d_.rectangle((28, 173, 29, 179), fill=rgb("dgrey"))
    d_.point((16, 176), fill=rgb("black"))
    d_.point((23, 176), fill=rgb("black"))
    d_.line((17, 182, 22, 182), fill=rgb("red_s"))
    d_.rectangle((24, 184, 30, 186), fill=rgb("dgrey"))         # mic
    for i, ln in enumerate(line.split("\n")):
        text(d_, (42, 168 + i * 11), ln)
    if tug is not None:   # tug-of-war meter above the tie-up
        x, y = tug_xy
        d_.rectangle((x - 25, y, x + 25, y + 5), fill=rgb("black"))
        mid = int(x - 24 + 48 * tug)
        d_.rectangle((x - 24, y + 1, mid, y + 4), fill=rgb("red"))
        d_.rectangle((mid, y + 1, x + 24, y + 4), fill=rgb("blue"))
        d_.rectangle((mid - 1, y - 1, mid + 1, y + 6), fill=rgb("white"))


def star(img, c, r, col="white"):
    d_ = ImageDraw.Draw(img)
    x, y = c
    for a in range(0, 360, 45):
        L = r if a % 90 == 0 else r * 0.6
        dx, dy = d(a)
        d_.line((x, y, x + dx * L, y + dy * L), fill=rgb(col))


def dizzy(img, c, phase):
    for k in range(3):
        a = phase * 60 + k * 120
        dx, dy = d(a)
        x, y = int(c[0] + dx * 7), int(c[1] + dy * 2.5)
        for ox, oy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            img.putpixel((x + ox, y + oy), rgb("volt"))


# ---------------------------------------------------------------- the sequence
def scene(mike, stew, e_m, e_s, line, extra=None, shake=0, tug=None, stew_front=False):
    img = backdrop()
    if shake:
        mike, stew = shift(mike, shake, 0), shift(stew, shake, 0)
    layers = [("stew", stew), ("mike", mike)] if not stew_front else [("mike", mike), ("stew", stew)]
    for name, prims in layers:
        img.alpha_composite(raster(name, prims, W, H))
    if extra:
        extra(img)
    hud(img, e_m, e_s, line, *(tug if tug else (None, None)))
    return img


def mike_at(pose, x, R=0):
    return ground(place(figure("mike", pose), S, (x, 0), 1, R), FLOOR)


def stew_at(pose, x, R=0):
    return ground(place(figure("stew", pose), S, (x, 0), -1, R), FLOOR)


def build():
    frames = []   # (image, ms)
    L_IN = "HERE WE GO! MIGHTY MIKE\nAND BIG BEEFY STEW!"
    # walk in
    mx, sx = 44, 214
    for i in range(6):
        pm = WALK_A if i % 2 == 0 else WALK_B
        frames.append((scene(mike_at(pm, mx), stew_at(pm, sx), 1, 1, L_IN), 140))
        mx += 10
        sx -= 10
    # tie-up with the tug-of-war meter
    L_TIE = "THEY LOCK UP IN THE\nCENTER OF THE RING!"
    tugs = [0.5, 0.45, 0.52, 0.4, 0.44, 0.33, 0.36, 0.25, 0.18, 0.08]
    for i, tv in enumerate(tugs):
        pm, ps = (TIE_A, TIE_B) if i % 2 == 0 else (TIE_B, TIE_A)
        m = mike_at(pm, 104)
        s_ = stew_at(ps, 104 + 47 * K)
        frames.append((scene(m, s_, 1, 1, L_TIE, tug=(tv, (int(104 + 23 * K), int(FLOOR - 70 * K)))), 150))
    # hook: Mike grabs a front facelock, Stew bent over
    L_UP = "MIKE HOOKS HIM...\nHE'S GOING UP!"
    m = mike_at(HOOK, 104)
    s_ = stew_at(BENT, 104 + 37 * K)
    frames.append((scene(m, s_, 1, 1, L_UP), 350))
    # the lift: Stew straight up, upside down, head at Mike's chest
    m = mike_at(LIFT, 104)
    mk = figure("mike", LIFT)
    chest = place([Pix(add((0, 0), LIFT["t"], CH["mike"]["Lt"] * 0.85), "x")], S, (104, 0))[0].p
    chest = (chest[0], chest[1] + (FLOOR - extent(place(mk, S, (104, 0)))[3]))
    s_raw = place(figure("stew", LIMP), S, (0, 0), -1, 180)
    head = head_of(s_raw)
    s_ = shift(s_raw, chest[0] + 9 * K - head[0], chest[1] + 2 - head[1])
    L_HANG = "LOOK AT THE HANG TIME!\nSTEW IS UPSIDE DOWN!"
    frames.append((scene(m, s_, 1, 1, L_UP), 250))
    frames.append((scene(m, s_, 1, 1, L_HANG), 700))
    # falling back: the whole pair rotates backwards about Mike's feet
    both_m, both_s = m, s_
    piv = (104, FLOOR)
    for G in (-35, -65):
        gm = group_rot(both_m, G, piv)
        gs = group_rot(both_s, G, piv)
        dy = FLOOR - extent(gm)[3]
        frames.append((scene(shift(gm, 0, dy), shift(gs, 0, dy), 1, 1, L_HANG), 90))
    # impact: both flat on their backs
    gm = ground(group_rot(both_m, -90, piv), FLOOR)
    gs = ground(group_rot(both_s, -90, piv), FLOOR)
    gs = shift(gs, (extent(gm)[0] + 10 * K) - head_of(gs)[0], 0)
    L_BOOM = "SUPLEX!!!\nWHAT A MOVE BY MIKE!"
    hx_, hy_ = head_of(gs)
    boom = lambda img: (star(img, (int(hx_), int(FLOOR - 6)), 16, "volt"),
                        star(img, (int(hx_), int(FLOOR - 6)), 9, "white"))
    frames.append((scene(gm, gs, 1, 0.72, L_BOOM, extra=boom, shake=3), 70))
    frames.append((scene(gm, gs, 1, 0.72, L_BOOM, extra=boom, shake=-3), 70))
    frames.append((scene(gm, gs, 1, 0.72, L_BOOM, shake=2), 70))
    frames.append((scene(gm, gs, 1, 0.72, L_BOOM), 600))
    stew_star_c = (int(hx_), int(hy_) - 12)
    # Mike sits up, then stands and poses while Stew sees stars
    L_UP2 = "STEW IS SEEING STARS!\nMIKE IS UP FIRST!"
    mike_hip_x = 104 - (CH["mike"]["Lth"] + CH["mike"]["Lsh"]) * S
    sit = ground(place(figure("mike", SIT), S, (mike_hip_x + 4 * K, 0), 1), FLOOR)
    for i in range(3):
        frames.append((scene(sit, gs, 1, 0.72, L_UP2, extra=lambda img, i=i: dizzy(img, stew_star_c, i)), 220))
    stand = mike_at(STAND, mike_hip_x + 10 * K)
    for i in range(2):
        frames.append((scene(stand, gs, 1, 0.72, L_UP2, extra=lambda img, i=i: dizzy(img, stew_star_c, i + 3)), 220))
    L_WIN = "SMALL BODY.\nBIG POWER!"
    pose = mike_at(POSE_UP, mike_hip_x + 10 * K)
    for i in range(5):
        frames.append((scene(pose, gs, 1, 0.72, L_WIN, extra=lambda img, i=i: dizzy(img, stew_star_c, i + 5)), 260))
    return frames


if __name__ == "__main__":
    frames = build()
    big = [f.convert("RGB").resize((W * 3, H * 3), Image.NEAREST) for f, _ in frames]
    durs = [ms for _, ms in frames]
    big[0].save(OUT + {"wm": "suplex_wm.gif", "tt": "suplex_tt.gif"}.get(STYLE, "suplex.gif"), save_all=True, append_images=big[1:], duration=durs, loop=0,
                optimize=False, disposal=1)
    # contact sheet of key frames for checking
    keys = [0, 7, 16, 17, 19, 21, 22, 23, 26, 30, 32, 36]
    keys = [k for k in keys if k < len(frames)]
    sheet = Image.new("RGB", (W * 2 * 3, H * 2 * ((len(keys) + 2) // 3)), (40, 40, 40))
    for i, k in enumerate(keys):
        sheet.paste(frames[k][0].convert("RGB").resize((W * 2, H * 2), Image.NEAREST),
                    ((i % 3) * W * 2, (i // 3) * H * 2))
    sheet.save(OUT + {"wm": "suplex_wm_sheet.png", "tt": "suplex_tt_sheet.png"}.get(STYLE, "suplex_sheet.png"))
    print(len(frames), "frames", sum(durs), "ms")
