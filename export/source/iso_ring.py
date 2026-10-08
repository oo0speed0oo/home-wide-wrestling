"""Mockup: angled 3/4 ring view with Mike and Stew in the Tag Team look.
Our own ring and crowd; only the camera angle is inspired by the reference."""
import random
import sys

sys.argv = [sys.argv[0], "tt"]          # use the Tag Team sprite settings
import suplex as sp                      # noqa: E402
from PIL import Image, ImageDraw        # noqa: E402
import crowd                             # noqa: E402

OUT = sp.OUT
W, H = 256, 216
CX, CY, R = 128, 80, 104                 # ring top corner on screen, ring size (world units)


def P(X, Y, Z=0.0):
    return (CX + (X - Y), CY + (X + Y) / 2 - Z)


def rgb(c):
    return sp.rgb(c)


def main(frame=0, actors=None):
    img = Image.new("RGBA", (W, H), rgb("#00007C"))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)

    crowd.draw_crowd(img, frame)
    d.rectangle((0, 62, W, 64), fill=rgb("#BCBCBC"))                    # barrier rail
    d.rectangle((0, 65, W, 67), fill=rgb("#7C7C7C"))

    ropes = [(8, "#0058F8"), (14, "#FCFCFC"), (20, "#F83800")]
    corners = {"top": (0, 0), "right": (R, 0), "bottom": (R, R), "left": (0, R)}

    def post(name):
        X, Y = corners[name]
        x0, y0 = P(X, Y, 0)
        x1, y1 = P(X, Y, 26)
        d.rectangle((x0 - 1, y1, x0 + 1, y0), fill=rgb("#0058F8"))
        d.rectangle((x0 - 1, y1, x0 + 1, y1 + 1), fill=rgb("#FCFCFC"))
        for z, _ in ropes:
            _, yz = P(X, Y, z)
            d.rectangle((x0 - 2, yz - 1, x0 + 2, yz + 1), fill=rgb("#F83800"))

    def rope_edge(a, b):
        for z, col in ropes:
            d.line((P(*corners[a], z), P(*corners[b], z)), fill=rgb(col))

    # apron (the two front sides) and mat
    L, B, Rt = P(0, R), P(R, R), P(R, 0)
    drop = 18
    d.polygon([L, B, (B[0], B[1] + drop), (L[0], L[1] + drop)], fill=rgb("#0000BC"))
    d.polygon([B, Rt, (Rt[0], Rt[1] + drop), (B[0], B[1] + drop)], fill=rgb("#24188C"))
    for k in range(1, 8):          # skirt folds
        x, y = P(k * R / 8, R)
        d.line((x, y + 3, x, y + drop - 1), fill=rgb("#00007C"))
        x, y = P(R, k * R / 8)
        d.line((x, y + 3, x, y + drop - 1), fill=rgb("#00007C"))
    d.line((L, B), fill=rgb("#FCFCFC"))
    d.line((B, Rt), fill=rgb("#FCFCFC"))
    d.polygon([P(0, 0), P(R, 0), P(R, R), P(0, R)], fill=rgb("#BCBCBC"))
    d.polygon([P(4, 4), P(R - 4, 4), P(R - 4, R - 4), P(4, R - 4)], outline=rgb("#A4A4A4"))

    # ring steps at the right corner
    sx, sy = P(R + 6, 6)
    for i in range(3):
        top = sy + 8 - i * 5
        d.polygon([(sx - 8 + i * 3, top), (sx + 6 + i * 3, top - 4), (sx + 6 + i * 3, top + 2),
                   (sx - 8 + i * 3, top + 6)], fill=rgb("#7C7C7C"))
        d.line(((sx - 8 + i * 3, top), (sx + 6 + i * 3, top - 4)), fill=rgb("#BCBCBC"))

    # back ropes and posts sit behind the wrestlers
    rope_edge("left", "top")
    rope_edge("top", "right")
    for name in ("top", "left", "right"):
        post(name)

    if actors is not None:
        # actors: list of (feet_xy, draw_fn); nearer the camera (lower on screen) drawn last
        for feet, fn in sorted(actors, key=lambda a: a[0][1]):
            fx, fy = feet
            d.ellipse((fx - 7, fy - 2, fx + 7, fy + 2), fill=rgb("#A4A4A4"))
            fn(img)
        d = ImageDraw.Draw(img)
    else:
        # wrestlers, facing off in the middle of the ring
        s_ = sp.S * 0.9
        mike_feet = P(38, 68)
        stew_feet = P(70, 46)
        mike = sp.ground(sp.place(sp.figure("mike", sp.STAND), s_, (mike_feet[0], 0), 1), mike_feet[1])
        stew = sp.ground(sp.place(sp.figure("stew", sp.STAND), s_, (stew_feet[0], 0), -1), stew_feet[1])
        for name, prims, feet in sorted([("mike", mike, mike_feet), ("stew", stew, stew_feet)],
                                        key=lambda t: t[2][1]):
            # small shadow under each wrestler
            fx, fy = feet
            d.ellipse((fx - 9, fy - 2, fx + 9, fy + 2), fill=rgb("#A4A4A4"))
            img.alpha_composite(sp.raster(name, prims, W, H))
        d = ImageDraw.Draw(img)

    # front ropes and front post go over the wrestlers
    rope_edge("left", "bottom")
    rope_edge("bottom", "right")
    post("bottom")

    return img.convert("RGB").resize((W * 3, H * 3), Image.NEAREST)


if __name__ == "__main__":
    frames = [main(f) for f in range(8)]
    frames[0].save(OUT + "iso_ring.png")
    frames[0].save(OUT + "iso_ring_crowd.gif", save_all=True, append_images=frames[1:],
                   duration=180, loop=0, disposal=1)
    frames[0].crop((0, 0, W * 3, 70 * 3)).save(OUT + "crowd_f0.png")
    frames[2].crop((0, 0, W * 3, 70 * 3)).save(OUT + "crowd_f2.png")
