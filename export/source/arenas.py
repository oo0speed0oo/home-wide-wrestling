"""Home Wide Wrestling - the three v1 arenas on the angled ring.

Arena 1: few fans, bright and plain.     Arena 2: fuller, colourful lights.
Arena 4: packed, dark, big spotlights (the nemesis title match).
Every arena: the same ring, padded floor mats around it, and the HWW logo on the apron skirt.
"""
import math
import random
import sys

from PIL import Image, ImageDraw

import chars3d as c3
import crowd
import make_logo

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
W, H = 256, 216
CX, CY, R = 128, 80, 104
BARRIER = 62


def P(X, Y, Z=0.0):
    return (CX + (X - Y), CY + (X + Y) / 2 - Z)


def world(x, y):
    """screen point on the floor -> ring-world X, Y."""
    a, b = x - CX, 2 * (y - CY)
    return (a + b) / 2, (b - a) / 2


def hx(c):
    return c3.hx(c)


def shade(col, k):
    r, g, b, a = col
    return (int(r * k), int(g * k), int(b * k), a)


# ---------------------------------------------------------------- the logo, small, for the apron
def small_logo():
    big = make_logo.letters([make_logo.H_, make_logo.W_, make_logo.W_])
    big = make_logo.outline(big, "#000000", 1)
    bb = big.getbbox()
    return big.crop(bb)


def paste_sheared(img, logo, x0, y0, slope):
    """paste the logo so each column follows the apron's slant."""
    px = img.load()
    lp = logo.load()
    for i in range(logo.width):
        dy = round(i * slope)
        for j in range(logo.height):
            c = lp[i, j]
            if c[3]:
                x, y = x0 + i, y0 + j + dy
                if 0 <= x < W and 0 <= y < H:
                    px[x, y] = c


# ---------------------------------------------------------------- scene pieces
MATS = {1: ("#0000BC", "#00008C", "#6888FC"), 2: ("#0000BC", "#00008C", "#6888FC"),
        4: ("#00007C", "#000058", "#24188C")}


def floor_mats(img, arena, light):
    """padded mats around the ring: square panels with lighter seams, in perspective."""
    a_col, b_col, seam = (shade(hx(c), light) for c in MATS[arena])
    px = img.load()
    panel = 13.0
    for y in range(BARRIER + 6, H):
        for x in range(W):
            X, Y = world(x + 0.5, y + 0.5)
            u, v = X / panel, Y / panel
            if min(abs(u - round(u)), abs(v - round(v))) * panel < 0.55:
                px[x, y] = seam
            else:
                px[x, y] = a_col if (math.floor(u) + math.floor(v)) % 2 == 0 else b_col


def barrier(d, arena):
    d.rectangle((0, BARRIER, W, BARRIER + 2), fill=hx("#BCBCBC"))
    d.rectangle((0, BARRIER + 3, W, BARRIER + 5), fill=hx("#7C7C7C"))


def ring(img, d, logo):
    ropes = [(8, "#0058F8"), (14, "#FCFCFC"), (20, "#F83800")]
    corners = {"top": (0, 0), "right": (R, 0), "bottom": (R, R), "left": (0, R)}
    L, B, Rt = P(0, R), P(R, R), P(R, 0)
    drop = 18
    d.polygon([L, B, (B[0], B[1] + drop), (L[0], L[1] + drop)], fill=hx("#0000BC"))
    d.polygon([B, Rt, (Rt[0], Rt[1] + drop), (B[0], B[1] + drop)], fill=hx("#24188C"))
    for k in range(1, 8):          # skirt folds
        x, y = P(k * R / 8, R)
        d.line((x, y + 3, x, y + drop - 1), fill=hx("#00007C"))
        x, y = P(R, k * R / 8)
        d.line((x, y + 3, x, y + drop - 1), fill=hx("#00007C"))
    d.line((L, B), fill=hx("#FCFCFC"))
    d.line((B, Rt), fill=hx("#FCFCFC"))
    # the HWW logo on both front skirts, following their slant
    for (p0, p1, slope) in ((L, B, 0.5), (B, Rt, -0.5)):
        mx = (p0[0] + p1[0]) / 2
        x0 = int(mx - logo.width / 2)
        top_at_x0 = p0[1] + (x0 - p0[0]) * slope
        y0 = int(top_at_x0 + (drop - logo.height) / 2 + 1)
        paste_sheared(img, logo, x0, y0, slope)
    d.polygon([P(0, 0), P(R, 0), P(R, R), P(0, R)], fill=hx("#BCBCBC"))
    d.polygon([P(4, 4), P(R - 4, 4), P(R - 4, R - 4), P(4, R - 4)], outline=hx("#A4A4A4"))
    sx, sy = P(R + 6, 6)                   # steps
    for i in range(3):
        top = sy + 8 - i * 5
        d.polygon([(sx - 8 + i * 3, top), (sx + 6 + i * 3, top - 4), (sx + 6 + i * 3, top + 2),
                   (sx - 8 + i * 3, top + 6)], fill=hx("#7C7C7C"))
        d.line(((sx - 8 + i * 3, top), (sx + 6 + i * 3, top - 4)), fill=hx("#BCBCBC"))

    def post(name):
        X, Y = corners[name]
        x0, y0 = P(X, Y, 0)
        x1, y1 = P(X, Y, 26)
        d.rectangle((x0 - 1, y1, x0 + 1, y0), fill=hx("#0058F8"))
        d.rectangle((x0 - 1, y1, x0 + 1, y1 + 1), fill=hx("#FCFCFC"))
        for z, _ in ropes:
            _, yz = P(X, Y, z)
            d.rectangle((x0 - 2, yz - 1, x0 + 2, yz + 1), fill=hx("#F83800"))

    def rope_edge(a, b):
        for z, col in ropes:
            d.line((P(*corners[a], z), P(*corners[b], z)), fill=hx(col))

    return post, rope_edge


def dither(img, poly_fn, col, density=2, box=None):
    """NES-style see-through light: colour every other pixel inside the shape."""
    px = img.load()
    x0, y0, x1, y1 = box or (0, 0, W, H)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if (x + y) % density == 0 and poly_fn(x, y):
                px[x, y] = col


def in_ellipse(cx, cy, rx, ry):
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1


def in_beam(top_x, spread, bottom_x, bottom_y):
    """a light beam from the ceiling (top_x, 0) widening down to bottom_x at bottom_y."""
    def f(x, y):
        if y < 0 or y > bottom_y:
            return False
        t = y / bottom_y
        cx = top_x + (bottom_x - top_x) * t
        return abs(x - cx) <= 1 + spread * t
    return f


# ---------------------------------------------------------------- one frame
MATCHUP = {1: "jim", 2: "stew", 4: "niko"}


def scene(arena, frame, actors_fn=None, fighters=None):
    """actors_fn(img, P) draws whoever is in the ring; default = the arena's match-up standing off."""
    img = Image.new("RGBA", (W, H), hx("#000000"))
    d = ImageDraw.Draw(img)
    light = {1: 1.0, 2: 0.95, 4: 0.55}[arena]
    crowd.draw_crowd(img, frame, arena, fighters or ("mike", MATCHUP[arena]))
    if arena == 4:     # dark house: dim the stands, keep the signs and flashes readable
        px = img.load()
        for y in range(0, BARRIER):
            for x in range(W):
                c = px[x, y]
                if c[:3] not in ((252, 252, 252), (248, 216, 120)):
                    px[x, y] = shade(c, 0.7)
    barrier(d, arena)
    floor_mats(img, arena, light)
    if arena == 4:     # HWW logos along the barrier
        for x in range(8, W, 64):
            d.rectangle((x - 1, BARRIER - 1, x + 17, BARRIER + 5), fill=hx("#0000BC"))
            crowd.put_text(img, x + 1, BARRIER, "HWW", "#F8D878")
    if arena == 2:     # coloured lights sweeping across the floor mats
        for k, col in enumerate(("#F85898", "#3CBCFC", "#F8D878")):
            a = frame / 8 * 2 * math.pi + k * 2.1
            cx = 128 + math.cos(a) * 95
            cy = 150 + math.sin(a) * 34
            dither(img, in_ellipse(cx, cy, 26, 11), hx(col), 2, (int(cx - 27), int(cy - 12), int(cx + 28), int(cy + 13)))
    logo = small_logo()
    post, rope_edge = ring(img, d, logo)
    if arena == 4:     # two big spotlights from the rafters onto the ring
        for top_x, sway in ((40, 1), (216, -1)):
            bx = 128 + sway * 4 * math.sin(frame / 8 * 2 * math.pi)
            dither(img, in_beam(top_x, 30, bx, 138), hx("#FCFCFC"), 4, (0, 0, W, 140))
    rope_edge("left", "top")
    rope_edge("top", "right")
    for n in ("top", "left", "right"):
        post(n)
    # the match-up: Mike (back to us) facing his opponent
    if actors_fn:
        actors_fn(img, P)
        d = ImageDraw.Draw(img)
        rope_edge("left", "bottom")
        rope_edge("bottom", "right")
        post("bottom")
        return img
    opp = MATCHUP[arena]
    actors = [((48, 80), "mike", "up-right"), ((48, 42), opp, "down-left")]
    for (X, Y), who, face in sorted(actors, key=lambda a: a[0][0] + a[0][1]):
        feet = P(X, Y)
        d.ellipse((feet[0] - 7, feet[1] - 2, feet[0] + 7, feet[1] + 2), fill=hx("#A4A4A4"))
        pose = "stand" if (frame // 2) % 2 == 0 else "walkA"
        c3.render(who, pose if who == "mike" else "stand", face, feet, W, H, img)
    d = ImageDraw.Draw(img)
    rope_edge("left", "bottom")
    rope_edge("bottom", "right")
    post("bottom")
    return img


if __name__ == "__main__":
    arenas = [int(a) for a in sys.argv[1:]] or [1, 2, 4]
    for a in arenas:
        frames = [scene(a, f).convert("RGB").resize((W * 3, H * 3), Image.NEAREST) for f in range(8)]
        frames[0].save(OUT + f"arena{a}.png")
        frames[0].save(OUT + f"arena{a}.gif", save_all=True, append_images=frames[1:], duration=180,
                       loop=0, disposal=1)
        print("arena", a)
