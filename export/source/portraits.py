"""Big NES-style bust portraits (80x72) for the select screen and the profile cards.
Flat fills, a darker shade for muscle lines and a 1px outline where the figure meets the black."""
from PIL import Image, ImageDraw

PW, PH = 80, 72
HAIR, HAIR_HI = "#24188C", "#6844FC"      # NES "black" hair: deep navy with a blue highlight


def hx(c):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)


class Pen:
    def __init__(self):
        self.im = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def e(self, box, c):
        self.d.ellipse(box, fill=hx(c))

    def r(self, box, c):
        self.d.rectangle(box, fill=hx(c))

    def p(self, pts, c):
        self.d.polygon(pts, fill=hx(c))

    def l(self, a, b, c, w=1):
        self.d.line((a, b), fill=hx(c), width=w)

    def limb(self, a, b, c, w):
        """a thick arm segment with round ends."""
        self.d.line((a, b), fill=hx(c), width=w)
        for (x, y) in (a, b):
            h = w // 2
            self.d.ellipse((x - h, y - h, x + h, y + h), fill=hx(c))

    def px(self, x, y, c):
        self.d.point((x, y), fill=hx(c))

    def outline(self, c):
        """darken every figure pixel that touches the background (not the bottom edge: the bust is cut there)."""
        src = self.im.copy()
        s, o = src.load(), self.im.load()
        for y in range(PH):
            for x in range(PW):
                if not s[x, y][3]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + dx, y + dy
                    if 0 <= X < PW and 0 <= Y < PH and not s[X, Y][3]:
                        o[x, y] = hx(c)
                        break
        return self.im


def torso(pen, cx, top, half, skin):
    """neck to the bottom edge: a wide trapezoid with round shoulders."""
    pen.p([(cx - half + 6, top), (cx + half - 6, top), (cx + half, top + 8), (cx + half + 1, PH),
           (cx - half - 1, PH), (cx - half, top + 8)], skin)
    pen.e((cx - half - 2, top - 1, cx - half + 12, top + 13), skin)
    pen.e((cx + half - 12, top - 1, cx + half + 2, top + 13), skin)


def pecs(pen, cx, y, w, sh):
    pen.l((cx - w, y), (cx - 3, y + 4), sh)
    pen.l((cx - 3, y + 4), (cx - 1, y + 3), sh)
    pen.l((cx + w, y), (cx + 3, y + 4), sh)
    pen.l((cx + 3, y + 4), (cx + 1, y + 3), sh)
    pen.l((cx, y - 3), (cx, y + 8), sh)


def eyes(pen, cx, y, gap, brow, white="#FCFCFC", mean=False):
    for sd in (-1, 1):
        x = cx + sd * gap
        pen.r((x - 1, y, x + 1, y + 1), white)
        pen.px(x + (0 if mean else sd * 0), y + 1, "#000000")
        pen.px(x, y, "#000000")
        # heavy brow slanting in
        pen.l((x - 3 * sd * -1 if False else x - 2, y - 2 - (1 if (mean and sd == -1) else 0)),
              (x + 2, y - 2 - (1 if (mean and sd == 1) else 0)), brow)


# ---------------------------------------------------------------- the four
def mike():
    sk, sh, ol = "#D8904C", "#984410", "#5C2000"
    pen = Pen()
    torso(pen, 40, 44, 22, sk)
    # double biceps: upper arms out, forearms up, fists by the head, red wristbands
    for sd in (-1, 1):
        sx = 40 + sd * 22
        el = (40 + sd * 33, 42)
        fi = (40 + sd * 30, 17)
        pen.limb((sx, 48), el, sk, 11)
        pen.e((el[0] - 7 if sd < 0 else el[0] - 7, 33, el[0] + 7, 45), sk)       # bicep peak
        pen.limb(el, fi, sk, 9)
        pen.e((fi[0] - 6, fi[1] - 6, fi[0] + 6, fi[1] + 5), sk)                 # fist
        pen.r((fi[0] - 5, fi[1] + 5, fi[0] + 5, fi[1] + 8), "#F83800")         # wristband
        pen.l((fi[0] - 4, fi[1] - 1), (fi[0] + 4, fi[1] - 1), sh)             # knuckles
        pen.l((el[0] - 5 * sd, 37), (sx + 2 * sd, 44), sh)                     # bicep line
    # head: big black curly hair, beard
    for (x, y, r) in ((40, 15, 14), (29, 12, 6), (51, 12, 6), (34, 5, 6), (46, 5, 6), (27, 21, 5), (53, 21, 5)):
        pen.e((x - r, y - r, x + r, y + r), HAIR)
    for (x, y) in ((31, 7), (37, 3), (45, 4), (50, 9), (26, 16), (54, 16)):
        pen.l((x, y), (x + 2, y + 1), HAIR_HI)
    pen.r((35, 36, 45, 46), sk)                                                 # neck
    pen.e((30, 12, 50, 40), sk)                                                 # face
    pen.p([(30, 27), (50, 27), (48, 40), (40, 44), (32, 40)], HAIR)            # beard
    pen.r((36, 33, 44, 34), sk)                                                 # upper lip shows
    pen.l((37, 36), (43, 36), "#F8F8F8")                                         # gritted teeth
    pen.r((31, 13, 49, 17), HAIR)                                              # hairline
    eyes(pen, 40, 21, 5, HAIR)
    pen.l((40, 23), (39, 28), sh)                                               # nose
    pen.l((38, 28), (42, 28), sh)
    pecs(pen, 40, 55, 13, sh)
    pen.l((24, 50), (28, 58), sh)
    pen.l((56, 50), (52, 58), sh)
    return pen.outline(ol)


def stew():
    sk, sh, ol = "#FCC0A0", "#D8664C", "#A0301C"
    blue, blk = "#0058F8", "#000000"
    pen = Pen()
    torso(pen, 40, 42, 30, sk)
    # singlet: blue body and straps, black belly band just peeking at the bottom
    pen.p([(14, 62), (66, 62), (70, PH), (10, PH)], blue)
    pen.r((10, 69, 70, PH), blk)
    for x in (27, 53):
        pen.p([(x - 3, 42), (x + 3, 42), (x + 2 if x < 40 else x + 4, 63), (x - 4 if x < 40 else x - 2, 63)], blue)
    # fist pump: left arm thrust high, right fist by the jaw
    pen.limb((13, 48), (6, 28), sk, 12)
    pen.limb((6, 28), (12, 9), sk, 10)
    pen.e((6, 0, 19, 12), sk)
    pen.l((8, 5), (17, 5), sh)
    pen.limb((66, 50), (70, 66), sk, 12)
    pen.limb((70, 66), (58, 46), sk, 10)
    pen.e((52, 36, 64, 48), sk)
    pen.l((54, 41), (62, 41), sh)
    # head: short flat black hair, yelling
    pen.r((34, 34, 46, 44), sk)
    pen.e((27, 10, 53, 40), sk)
    pen.p([(28, 18), (30, 10), (50, 10), (52, 18), (48, 15), (32, 15)], HAIR)
    pen.r((30, 8, 50, 13), HAIR)
    pen.l((33, 10), (46, 10), HAIR_HI)
    pen.e((24, 20, 29, 27), sk)                                                 # ears
    pen.e((51, 20, 56, 27), sk)
    eyes(pen, 40, 21, 6, HAIR, mean=True)
    pen.l((40, 23), (39, 27), sh)
    pen.e((34, 29, 46, 38), "#000000")                                          # yelling mouth
    pen.r((36, 29, 44, 30), "#FCFCFC")                                          # top teeth
    pen.e((37, 34, 43, 38), "#D82800")                                          # tongue
    pecs(pen, 40, 52, 16, sh)
    return pen.outline(ol)


def jim():
    sk, sh, ol = "#FCD0B0", "#D07850", "#8C3810"
    green, blond, bsh = "#00A800", "#F8B800", "#AC7C00"
    pen = Pen()
    torso(pen, 40, 44, 26, sk)
    # one-strap green singlet over his left shoulder
    pen.p([(50, 43), (57, 44), (46, 64), (38, 64)], green)
    pen.p([(12, 64), (68, 62), (69, PH), (11, PH)], green)
    # arms crossed high on the chest
    pen.limb((15, 50), (18, 64), sk, 11)
    pen.limb((65, 50), (62, 64), sk, 11)
    pen.limb((18, 63), (58, 57), sk, 10)
    pen.limb((62, 63), (24, 58), sk, 10)
    pen.e((54, 52, 64, 61), sk)                                                 # hands tucked
    pen.e((16, 53, 26, 62), sk)
    pen.l((24, 60), (58, 55), sh)                                               # the fold between forearms
    pen.l((21, 50), (19, 60), sh)
    pen.l((59, 50), (61, 60), sh)
    # head: big feathered blond hair, smug half-smile, little goatee
    pen.e((25, 3, 55, 27), blond)
    pen.e((25, 11, 33, 29), blond)
    pen.e((47, 11, 55, 29), blond)
    pen.r((35, 36, 45, 46), sk)
    pen.e((29, 12, 51, 41), sk)
    pen.p([(28, 18), (32, 8), (46, 7), (52, 16), (44, 13), (36, 16)], blond)    # swept fringe
    pen.l((33, 11), (44, 9), bsh)
    pen.l((30, 16), (36, 13), bsh)
    eyes(pen, 40, 22, 5, bsh, mean=True)
    pen.l((40, 24), (39, 29), sh)
    pen.l((36, 33), (44, 32), "#8C3810")                                        # smirk
    pen.px(45, 31, "#8C3810")
    pen.r((38, 36, 42, 39), blond)                                              # goatee
    pen.px(40, 40, blond)
    return pen.outline(ol)


def niko():
    sk, sh, ol = "#F4CCA0", "#C07840", "#6C3000"
    pen = Pen()
    torso(pen, 38, 46, 18, sk)
    # the long left arm stretched straight up, one finger to the sky
    pen.limb((52, 50), (60, 26), sk, 9)
    pen.limb((60, 26), (64, 6), sk, 8)
    pen.e((59, 0, 69, 10), sk)
    pen.r((62, -4, 65, 2), sk)                                                  # finger
    pen.r((58, 11, 69, 14), "#0000BC")                                          # navy wristband
    pen.l((54, 44), (58, 30), sh)
    # right arm hangs, just the shoulder and upper arm
    pen.limb((20, 52), (17, PH), sk, 9)
    # head: shaggy black bowl, face peeking under the bangs
    pen.r((33, 38, 43, 48), sk)
    pen.e((27, 14, 49, 42), sk)
    pen.e((24, 6, 52, 32), HAIR)
    for x in range(25, 52, 4):                                                  # jagged bangs
        pen.p([(x, 26), (x + 4, 26), (x + 2, 30)], HAIR)
    pen.e((22, 16, 30, 36), HAIR)
    pen.e((46, 16, 54, 36), HAIR)
    for (x, y) in ((30, 11), (36, 8), (44, 9), (26, 20), (49, 20)):
        pen.l((x, y), (x + 3, y + 2), HAIR_HI)
    pen.px(33, 31, "#000000")                                                   # eyes glinting under the fringe
    pen.px(43, 31, "#000000")
    pen.px(32, 31, "#FCFCFC")
    pen.px(42, 31, "#FCFCFC")
    pen.l((38, 31), (37, 35), sh)
    pen.l((34, 38), (42, 37), "#6C3000")                                        # cool grin
    pen.px(43, 36, "#6C3000")
    # lean chest: ribs and collarbones
    pen.l((28, 50), (36, 52), sh)
    pen.l((48, 50), (40, 52), sh)
    pen.l((38, 53), (38, 62), sh)
    for y in (60, 64, 68):
        pen.l((28, y), (33, y + 1), sh)
        pen.l((48, y), (43, y + 1), sh)
    return pen.outline(ol)


PORTRAITS = {"mike": mike, "stew": stew, "jim": jim, "niko": niko}

if __name__ == "__main__":
    out = Image.new("RGBA", (PW * 4 + 30, PH), hx("#000000"))
    for i, k in enumerate(("mike", "stew", "jim", "niko")):
        out.alpha_composite(PORTRAITS[k](), (i * (PW + 10), 0))
    out.resize((out.width * 5, out.height * 5), Image.NEAREST).save(
        "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/rev.png")
