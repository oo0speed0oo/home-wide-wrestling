"""Each wrestler's 2 special moves and his finisher (design doc: Special moves, Finishers).

A special replaces a default move on the same input, always. The finisher replaces the move in the
situation that fits it, but only once the opponent is under 30%; before that the normal move comes out.
Specials count as big moves for the too-early rule; a finisher can't be too early.
"""
FINISH_UNDER = 0.3

SPECIALS = {
    "mike": {"body slam": "military press", "headlock": "bear hug"},
    "niko": {"dropkick": "flying crossbody", "flying knee drop": "missile dropkick"},
    "jim": {"back drop": "vertical suplex", "knee lift": "hip toss"},
    "stew": {"headlock": "headbutt"},       # his other special, the seated butt drop, is his ground drop
}
FINISHERS = {
    "mike": ("pile driver", "powerbomb"),        # tie-up Down+S
    "niko": ("brain buster", "ddt"),             # tie-up Up+S
    "jim": ("headlock", "sleeper hold"),         # tie-up A
    "stew": ("clothesline", "running lariat"),   # running A
}
FINISHER_NAMES = {f for _, f in FINISHERS.values()}
SPECIAL_NAMES = {s for table in SPECIALS.values() for s in table.values()} | {"seated butt drop"}


def resolve(att, vic, move):
    """the move att actually does when he goes for `move` on vic."""
    default, finisher = FINISHERS.get(att.who, (None, None))
    if move == default and vic.energy < FINISH_UNDER:
        return finisher
    return SPECIALS.get(att.who, {}).get(move, move)


def is_finisher(move):
    return move in FINISHER_NAMES
