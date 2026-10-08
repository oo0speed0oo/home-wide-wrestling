"""Home Wide Wrestling screen furniture: the top bar, the mash meter, and the announcer bar.

Full NES screen is 256x240:
  y   0-23   top bar (names, stamina, clock)          - black, drawn over the back rows of the crowd
  y  24-207  the arena (arena scene shifted up 8 px)
  y 208-239  announcer bar (portrait + 2 lines of text)
"""
import math
from PIL import Image, ImageDraw
import font

SW, SH = 256, 240
TOP_H, BOT_Y = 24, 208
ARENA_SHIFT = -8

HUD_COL = {"mike": "#F83800", "stew": "#3CBCFC", "jim": "#58D854", "niko": "#9878F8"}
FULL = {"mike": "MIGHTY MIKE", "stew": "BIG BEEFY STEW", "jim": "JIM THE GOAT", "niko": "NIMBLE NIKO"}
SHORT = {"mike": "MIKE", "stew": "STEW", "jim": "JIM", "niko": "NIKO"}


def hx(c):
    return font._hx(c)


def shade(c, k):
    r, g, b, a = hx(c)
    return (int(r * k), int(g * k), int(b * k), 255)


# ---------------------------------------------------------------- top bar
PIPS = 24          # stamina shown as 24 NES-style pips


def stamina_bar(d, x, y, frac, col, mirror=False, blink=False):
    """a row of 3x6 pips with a 1px gap; low stamina (under 30%) flashes white."""
    on = max(0, min(PIPS, round(frac * PIPS)))
    low = frac < 0.3
    for i in range(PIPS):
        k = PIPS - 1 - i if mirror else i
        px = x + k * 4
        filled = i < on
        if filled:
            c = "#FCFCFC" if (low and blink) else col
        else:
            c = "#3C3C3C"
        d.rectangle((px, y, px + 2, y + 5), fill=hx(c))


def top_bar(img, p1, p2, st1, st2, clock, frame=0):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, SW - 1, TOP_H - 1), fill=hx("#000000"))
    d.line((0, TOP_H - 1, SW - 1, TOP_H - 1), fill=hx("#3C3C3C"))
    n1, n2 = FULL[p1], FULL[p2]
    if font.width(n1) > 112:
        n1 = SHORT[p1]
    if font.width(n2) > 112:
        n2 = SHORT[p2]
    font.draw_text(img, 4, 3, n1, HUD_COL[p1])
    font.draw_text(img, SW - 4 - font.width(n2), 3, n2, HUD_COL[p2])
    blink = (frame // 2) % 2 == 0
    stamina_bar(d, 4, 14, st1, HUD_COL[p1], blink=blink)
    stamina_bar(d, SW - 4 - PIPS * 4 + 1, 14, st2, HUD_COL[p2], mirror=True, blink=blink)
    # no clock on screen (decided Oct 1); the match time only shows on the win screen


# ---------------------------------------------------------------- mash meter (tug of war during grapples)
def mash_meter(img, p1, p2, pos, frame=0, y=30):
    """pos -1..1: -1 = all the way to P1 (left) wins, +1 = P2 wins. Drawn just under the top bar."""
    d = ImageDraw.Draw(img)
    w, h = 112, 8
    x0 = (SW - w) // 2
    d.rectangle((x0 - 2, y - 2, x0 + w + 1, y + h + 1), fill=hx("#000000"))
    d.rectangle((x0 - 1, y - 1, x0 + w, y + h), outline=hx("#FCFCFC"))
    mid = x0 + w // 2 + round(pos * (w // 2 - 2))
    d.rectangle((x0, y, mid - 1, y + h - 1), fill=hx(HUD_COL[p1]))
    d.rectangle((mid, y, x0 + w - 1, y + h - 1), fill=hx(HUD_COL[p2]))
    d.rectangle((mid - 1, y - 3, mid, y + h + 2), fill=hx("#FCFCFC"))
    if (frame // 2) % 2 == 0:
        t = "MASH!"
        font.draw_text(img, (SW - font.width(t)) // 2, y + h + 4, t, "#FCFCFC", shadow="#000000")


# ---------------------------------------------------------------- the announcer
def portrait(talk=0):
    """24x24 announcer: slick hair, headset mic, blue blazer, red tie. talk 0 = mouth shut, 1 = open."""
    im = Image.new("RGBA", (24, 24), hx("#000000"))
    d = ImageDraw.Draw(im)
    skin, sh = hx("#FCBCB0"), hx("#E09078")
    hair = hx("#7C0800")
    d.polygon([(2, 23), (4, 18), (9, 16), (15, 16), (20, 18), (22, 23)], fill=hx("#0000BC"))   # blazer
    d.polygon([(9, 16), (12, 21), (15, 16)], fill=hx("#FCFCFC"))                               # shirt
    d.line((12, 18, 12, 23), fill=hx("#D82800"))                                              # tie
    d.point((11, 18), fill=hx("#D82800")); d.point((13, 18), fill=hx("#D82800"))
    d.rectangle((10, 14, 14, 16), fill=sh)                                                     # neck
    d.ellipse((6, 3, 18, 16), fill=skin)                                                       # face
    d.ellipse((6, 1, 18, 8), fill=hair)                                                        # hair
    d.rectangle((6, 4, 7, 9), fill=hair)
    d.polygon([(8, 5), (18, 4), (17, 6), (10, 6)], fill=hair)                                  # side part
    d.rectangle((9, 8, 10, 9), fill=hx("#000000"))                                             # eyes
    d.rectangle((14, 8, 15, 9), fill=hx("#000000"))
    d.line((12, 10, 12, 11), fill=sh)                                                          # nose
    if talk:
        d.rectangle((10, 12, 14, 14), fill=hx("#000000"))
        d.line((11, 14, 13, 14), fill=hx("#D82800"))
    else:
        d.line((10, 13, 14, 13), fill=hx("#000000"))
    d.arc((4, 1, 20, 17), 180, 360, fill=hx("#BCBCBC"))                                        # headset band
    d.rectangle((4, 8, 6, 11), fill=hx("#545454"))                                             # ear cup
    d.line((6, 12, 9, 14), fill=hx("#BCBCBC"))                                                 # mic arm
    d.rectangle((9, 13, 10, 14), fill=hx("#545454"))
    return im


def announcer_bar(img, line1, line2="", chars=None, frame=0, speaker="ANNOUNCER"):
    """black bar with the portrait and up to 2 lines of 27 characters. chars = how many are typed so far."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, BOT_Y, SW - 1, SH - 1), fill=hx("#000000"))
    d.line((0, BOT_Y, SW - 1, BOT_Y), fill=hx("#3C3C3C"))
    total = len(line1) + len(line2)
    n = total if chars is None else min(chars, total)
    typing = n < total
    img.alpha_composite(portrait(1 if typing and (frame % 2 == 0) else 0), (4, BOT_Y + 5))
    t1 = line1[:n]
    t2 = line2[:max(0, n - len(line1))]
    font.draw_text(img, 34, BOT_Y + 7, t1, "#FCFCFC")
    font.draw_text(img, 34, BOT_Y + 19, t2, "#FCFCFC")
    if not typing and (frame // 2) % 2 == 0:       # "more" arrow once the line is out
        x, y = SW - 10, SH - 7
        d.polygon([(x, y), (x + 5, y), (x + 2, y + 3)], fill=hx("#F8D878"))


# ---------------------------------------------------------------- one full screen
def compose(arena_img, top, bottom):
    """arena_img: 256x216 arena. top/bottom: callables that draw the bars onto the 256x240 screen."""
    scr = Image.new("RGBA", (SW, SH), hx("#000000"))
    scr.alpha_composite(arena_img, (0, 0), (0, -ARENA_SHIFT))
    top(scr)
    bottom(scr)
    return scr


def one_meter(img, who, prog, label, frame=0, y=30):
    """one-sided meter (pins, getting up, shaking off a stun): only you mash, fill toward the white target line."""
    d = ImageDraw.Draw(img)
    w, h = 112, 8
    x0 = (SW - w) // 2
    d.rectangle((x0 - 2, y - 2, x0 + w + 1, y + h + 1), fill=hx("#000000"))
    d.rectangle((x0 - 1, y - 1, x0 + w, y + h), outline=hx("#7C7C7C"))
    fill = round(max(0.0, min(1.0, prog)) * (w - 1))
    if fill:
        d.rectangle((x0, y, x0 + fill - 1, y + h - 1), fill=hx(HUD_COL[who]))
    d.rectangle((x0 + w - 2, y - 3, x0 + w - 1, y + h + 2), fill=hx("#FCFCFC"))
    if (frame // 2) % 2 == 0:
        font.draw_text(img, (SW - font.width(label)) // 2, y + h + 4, label, "#FCFCFC", shadow="#000000")
