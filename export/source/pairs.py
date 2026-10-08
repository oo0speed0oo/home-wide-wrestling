"""Two-person moves: the attacker and the defender drawn together, sorted as one scene.

Each move frame = (attacker pose, defender pose, defender offset (forward, side, up) in the
attacker's frame, defender turn relative to the attacker in degrees: 180 = facing him).
"""
import sys
from PIL import Image, ImageDraw
import chars3d as c3
from chars3d import pose, both, DANGLE, SPREAD, FLAIL, LOCKED, UP

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"


def mv(who, name, i=0):
    for n, fr in c3.moves_for(who):
        if n == name:
            return fr[min(i, len(fr) - 1)]
    raise KeyError(name)


# ---------------------------------------------------------------- defender poses
S = lambda n, i=0: mv("mike", n, i)          # shared poses are the same for everyone
HIT = S("hit")
STUN = S("stunned")
TIE = S("tie-up")
DOWN = S("knocked down", 1)                 # flat on his back
FLY = S("being thrown", 0)
FLY2 = S("being thrown", 1)
LIFTED = pose(0, ((0, 0, 4), (0, 0, 4)), DANGLE, pitch=-90, lift=43, air=True)
PRESSED = pose(0, ((10, 5, 4), (-5, 0, 4)), FLAIL, pitch=-90, lift=44, air=True)
FACEDOWN = pose(0, ((0, 0, 8), (0, 0, 8)), SPREAD, pitch=90)
CRABBED = pose(0, ((-55, -55, 4), (-55, -55, 4)), both((0.8, 0.4, 0), (0.8, 0.2, 0)), pitch=88)
BENT = pose(60, ((6, 0, 6), (-6, 0, 6)), DANGLE)
UPSIDE = pose(0, ((0, 0, 3), (0, 0, 3)), DANGLE, pitch=180, lift=30, air=True)
ONSHOULDER = pose(0, ((60, 60, 6), (60, 60, 6)), DANGLE, pitch=150, lift=30, air=True)
SITBACK = pose(-10, ((85, 90, 10), (80, 88, 10)), both((0.3, 0.5, 0.6), (0.4, 0, 1)))   # sitting, hands at head
SAG = pose(-20, ((8, 0, 6), (-8, 0, 6)), DANGLE, fx="stars")                         # held, going limp
DDT_D = pose(0, ((10, 0, 6), (10, 0, 6)), DANGLE, pitch=110)
BUSTED = pose(0, ((0, 0, 3), (0, 0, 3)), DANGLE, pitch=170, lift=6, air=True)        # landed on his head
PILED = pose(0, ((0, 0, 3), (0, 0, 3)), DANGLE, pitch=180, lift=10, air=True)
RUN0, RUN1 = S("run", 0), S("run", 1)
OVERBACK = pose(0, ((10, 5, 4), (-5, 0, 4)), FLAIL, pitch=-150, lift=24, air=True)
POSTED = pose(40, ((-10, -20, 0), (10, 0, 0)), both((0.9, 0.2, -0.2), (0.9, 0, 0)), fx="stars")
LIFTKNEE = pose(30, ((12, 0, 0), (-8, 0, 0)), both((0.3, 0.6, -0.6), (0.3, 0.3, -0.9)))

# ---------------------------------------------------------------- the moves
def G(extra):     # distance = both bellies + extra
    return ("g", extra)


SHARED = [
    ("punch", [(S("punch", 0), S("stand"), (G(5), 0, 0), 180), (S("punch", 1), HIT, (G(5), 0, 0), 180)]),
    ("kick", [(S("kick", 0), S("stand"), (G(7), 0, 0), 180), (S("kick", 1), HIT, (G(8), 0, 0), 180)]),
    ("tie-up", [(S("tie-up", 0), TIE, (G(0), 0, 0), 180), (S("tie-up", 1), TIE, (G(-1), 0, 0), 180)]),
    ("lift", [(S("lift", 0), LIFTED, (0, 0, 0), 90), (S("lift", 1), PRESSED, (0, 0, 0), 90)]),
    ("throw", [(S("throw", 0), LIFTED, (0, 0, 0), 90), (S("throw", 1), FLY2, (22, 0, 0), 180)]),
    ("stomp", [(S("stomp", 0), DOWN, (14, 0, 0), 90), (S("stomp", 1), DOWN, (14, 0, 0), 90)]),
    ("pin", [(S("pin", 0), DOWN, (12, 0, 0), 90, "belly"), (S("pin", 1), DOWN, (12, 0, 0), 90, "belly")]),
    ("boston crab", [(S("boston crab", 0), CRABBED, (10, 0, 0), 0), (S("boston crab", 1), CRABBED, (9, 0, 0), 0)]),
    ("dive", [(S("dive", 0), DOWN, (24, 0, 0), 90), (S("dive", 1), DOWN, (12, 0, 0), 90)]),
    # ---- added Oct 5: the rest of the Tecmo set
    ("headlock", [(S("headlock", 0), BENT, (3, 12, 0), 270), (S("headlock", 1), BENT, (3, 11, 0), 270)]),
    ("knee lift", [(S("knee lift", 0), TIE, (G(0), 0, 0), 180), (S("knee lift", 1), LIFTKNEE, (G(1), 0, 4), 180)]),
    ("brain buster", [(mv("jim", "vertical suplex", 0), UPSIDE, (4, 0, 0), 180),
                      (mv("jim", "vertical suplex", 1), BUSTED, (-16, 0, 0), 180)]),
    ("pile driver", [(S("pile driver", 0), UPSIDE, (5, 0, 0), 180), (S("pile driver", 1), PILED, (6, 0, 0), 180)]),
    ("back drop", [(S("back drop", 0), S("stand"), (G(-6), 0, 0), 0), (S("back drop", 1), FLY2, (-16, 0, 0), 180)]),
    ("rope whip", [(S("rope whip", 0), RUN0, (14, 0, 0), 0), (S("rope whip", 1), RUN1, (30, 0, 0), 0)]),
    ("shoulder throw", [(S("shoulder throw", 0), RUN0, (22, 0, 0), 180), (S("shoulder throw", 1), OVERBACK, (-4, 0, 0), 180)]),
    ("clothesline", [(S("clothesline", 0), S("stand"), (G(16), 0, 0), 180), (S("clothesline", 1), FLY, (G(2), 6, 0), 180)]),
    ("dropkick", [(S("dropkick", 0), S("stand"), (40, 0, 0), 180), (S("dropkick", 1), FLY, (30, 0, 0), 180)]),
    ("flying knee drop", [(S("knee drop", 0), DOWN, (30, 0, 0), 90, 18), (S("knee drop", 1), DOWN, (8, 0, 0), 90)]),
    ("post slam", [(S("tie-up", 0), TIE, (G(0), 0, 0), 180), (S("throw", 1), POSTED, (G(10), 0, 0), 180)]),
]
# the ground drop is per wrestler: Mike elbow, Jim and Niko knee, Stew his seated butt drop (already his own)
DROP = {
    "mike": ("elbow drop", [(S("elbow drop", 0), DOWN, (10, 0, 0), 90), (S("elbow drop", 1), DOWN, (6, 0, 0), 90)]),
    "jim": ("knee drop", [(S("knee drop", 0), DOWN, (12, 0, 0), 90), (S("knee drop", 1), DOWN, (6, 0, 0), 90)]),
    "niko": ("knee drop", [(S("knee drop", 0), DOWN, (12, 0, 0), 90), (S("knee drop", 1), DOWN, (6, 0, 0), 90)]),
}

OWN = {
    "mike": [
        ("powerbomb", [(mv("mike", "powerbomb", 0), ONSHOULDER, (3, 0, 0), 180),
                       (mv("mike", "powerbomb", 1), DOWN, (18, 0, 0), 180)]),
        ("military press", [(mv("mike", "military press", 0), LIFTED, (0, 0, 0), 90),
                            (mv("mike", "military press", 1), PRESSED, (0, 0, 4), 90)]),
        ("bear hug", [(mv("mike", "bear hug", 0), HIT, (G(-7), 0, 2), 180),
                      (mv("mike", "bear hug", 1), SAG, (G(-8), 0, 5), 180)]),
    ],
    "stew": [
        ("running lariat", [(mv("stew", "running lariat", 0), S("stand"), (G(16), 0, 0), 180),
                            (mv("stew", "running lariat", 1), FLY, (G(2), 6, 0), 180)]),
        ("headbutt", [(mv("stew", "headbutt", 0), TIE, (G(0), 0, 0), 180),
                      (mv("stew", "headbutt", 1), STUN, (G(2), 0, 0), 180)]),
        ("seated butt drop", [(mv("stew", "seated butt drop", 0), DOWN, (2, 0, 0), 90),
                              (mv("stew", "seated butt drop", 1), DOWN, (2, 0, 0), 90)]),
    ],
    "jim": [
        ("sleeper hold", [(mv("jim", "sleeper hold", 0), SITBACK, (9, 0, 0), 0),
                          (mv("jim", "sleeper hold", 1), SITBACK, (9, 0, 0), 0)]),
        ("vertical suplex", [(mv("jim", "vertical suplex", 0), UPSIDE, (4, 0, 0), 180),
                             (mv("jim", "vertical suplex", 1), DOWN, (-18, 0, 0), 180)]),
        ("hip toss", [(mv("jim", "hip toss", 0), TIE, (G(-4), 5, 0), 180),
                      (mv("jim", "hip toss", 1), FLY2, (18, -4, 0), 180)]),
    ],
    "niko": [
        ("ddt", [(mv("niko", "ddt", 0), BENT, (G(0), 0, 0), 180),
                 (mv("niko", "ddt", 1), DDT_D, (G(0), 0, 0), 180)]),
        ("flying crossbody", [(mv("niko", "flying crossbody", 0), S("stand"), (58, 0, 0), 180),
                              (mv("niko", "flying crossbody", 1), FLY, (36, 0, 0), 180)]),
        ("missile dropkick", [(mv("niko", "missile dropkick", 0), S("stand"), (54, 0, 0), 180),
                              (mv("niko", "missile dropkick", 1), FLY, (36, 0, 0), 180)]),
    ],
}

# who takes the moves on each sheet
VICTIM = {"mike": "stew", "stew": "mike", "jim": "mike", "niko": "mike"}


def pair_moves(who):
    return SHARED + ([DROP[who]] if who in DROP else []) + OWN[who]


def front(name):
    """how far a wrestler's front sticks out from his middle (the belly on the big guys)."""
    c = c3.CH[name]
    return c["belly"][0] + c["belly"][1] if c["belly"] else c["rt"]


def render_pair(att, dfn, frame, facing, feet, W, H, img):
    import math
    a_pose, d_pose, (fo, so, uo), rel = frame[:4]
    au = frame[4] if len(frame) > 4 else 0
    if au == "belly":
        au = front(dfn) * 0.55
    if isinstance(fo, tuple):
        fo = front(att) + front(dfn) + fo[1]
    a = c3.FACE[facing]
    th = math.radians(a)
    f, s = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
    prims = c3.shift(c3.build(att, a_pose, a), 0, 0, au)
    dp = c3.build(dfn, d_pose, (a + rel) % 360)
    c3.shift(dp, f[0] * fo + s[0] * so, f[1] * fo + s[1] * so, uo)
    return c3.render_prims(prims + dp, feet, W, H, img)


FACINGS = ["down-right", "down-left", "up-right", "up-left"]
CW, CHh = 96, 88
MAT, LINE = c3.hx("#BCBCBC"), c3.hx("#A4A4A4")


def cell(att, dfn, frame, face):
    im = Image.new("RGBA", (CW, CHh), MAT)
    feet = (CW / 2, CHh - 26)
    ImageDraw.Draw(im).ellipse((feet[0] - 8, feet[1] - 2, feet[0] + 8, feet[1] + 2), fill=LINE)
    return render_pair(att, dfn, frame, face, feet, CW, CHh, im)


def sheet(who):
    dfn = VICTIM[who]
    rows = pair_moves(who)
    img = Image.new("RGBA", (CW * 8, CHh * len(rows)), c3.hx("#141210"))
    for r, (name, frames) in enumerate(rows):
        for i, face in enumerate(FACINGS):
            for j, fr in enumerate(frames):
                img.paste(cell(who, dfn, fr, face), ((i * 2 + j) * CW, r * CHh))
        ImageDraw.Draw(img).line((0, r * CHh, img.width, r * CHh), fill=c3.hx("#141210"))
    for i in range(1, 4):
        ImageDraw.Draw(img).line((i * 2 * CW, 0, i * 2 * CW, img.height), fill=c3.hx("#141210"), width=2)
    img.convert("RGB").resize((img.width * 3, img.height * 3), Image.NEAREST).save(OUT + f"{who}_pairs_sheet.png")
    return img.size, len(rows)


def reel(who):
    dfn = VICTIM[who]
    frames = []
    for name, fr in pair_moves(who):
        for k in range(3):
            for f in fr:
                frames.append(cell(who, dfn, f, "down-right").convert("RGB").resize((CW * 4, CHh * 4), Image.NEAREST))
    frames[0].save(OUT + f"{who}_pairs_reel.gif", save_all=True, append_images=frames[1:], duration=260,
                   loop=0, disposal=1)
    return len(frames)


if __name__ == "__main__":
    for who in sys.argv[1:] or ["mike"]:
        print(who, sheet(who), reel(who))
