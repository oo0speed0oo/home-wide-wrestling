"""The wrestlers as the select screen bills them (from export/source/select_screen.py), and the 1-player run."""

ORDER = ["mike", "stew", "jim", "niko"]
NAME2 = {"mike": ("MIGHTY", "MIKE"), "stew": ("BIG BEEFY", "STEW"), "jim": ("JIM", "\"THE GOAT\""),
         "niko": ("NIMBLE", "NIKO")}
TITLE = {"mike": "MIGHTY MIKE", "stew": "BIG BEEFY STEW", "jim": "JIM \"THE GOAT\"", "niko": "NIMBLE NIKO"}
STATS = {
    "mike": [("FROM", "THE IRON DUNGEON"), ("BORN", "7.4.1965"), ("HEIGHT", "5' 7\""), ("WEIGHT", "244 LB"),
             ("RECORD", "88-1-0"), ("SPECIALTY", "POWERBOMB")],
    "stew": [("FROM", "THE ALL-YOU-CAN-EAT BUFFET"), ("BORN", "11.23.1961"), ("HEIGHT", "6' 8\""),
             ("WEIGHT", "412 LB"), ("RECORD", "71-9-3"), ("SPECIALTY", "RUNNING LARIAT")],
    "jim": [("FROM", "THE TOP OF THE MOUNTAIN"), ("BORN", "2.29.1964"), ("HEIGHT", "6' 5\""), ("WEIGHT", "318 LB"),
            ("RECORD", "99-0-1"), ("SPECIALTY", "SLEEPER HOLD")],
    "niko": [("FROM", "HIGH ABOVE THE CLOUDS"), ("BORN", "9.9.1968"), ("HEIGHT", "7' 1\""), ("WEIGHT", "221 LB"),
             ("RECORD", "64-2-0"), ("SPECIALTY", "DDT")],
}
TAPE = {k: dict(v) for k, v in STATS.items()}
QUOTE = {"mike": "\"SMALL BODY. BIG POWER!\"", "stew": "\"ALL ABOARD|THE BEEF TRAIN!\"",
         "jim": "\"THE GOAT NEVER SLEEPS...|YOU DO.\"", "niko": "\"FROM UP HERE,|YOU LOOK TINY!\""}

# the 1-player run (decided): the other two first, your nemesis last, for the title. One arena per match.
RUN = {"mike": ["jim", "stew", "niko"], "niko": ["mike", "jim", "stew"], "stew": ["mike", "niko", "jim"],
       "jim": ["niko", "stew", "mike"]}
ARENA_FOR_MATCH = {1: 1, 2: 2, 3: 4}


def wrap(text, n):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]
