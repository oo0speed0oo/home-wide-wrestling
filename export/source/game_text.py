"""All the game's words in one place: announcer lines, passwords, secret codes, and each wrestler's moves list.
Lines are 2 rows of up to 27 characters (the announcer bar). {name} = the wrestler the line is about,
{opp} = the other one, {town} = his hometown from the profile card."""

# ---------------------------------------------------------------- announcer (generic for now; Mike may swap in his own)
ANNOUNCER = {
    "intro": [("THE FOLLOWING CONTEST IS", "SCHEDULED FOR ONE FALL!")],
    "intro_from": [("FROM", "{town},")],
    "intro_name": [("{name}!!!", "")],
    "bell": [("THERE'S THE BELL!", "HERE WE GO!"), ("AND WE ARE UNDERWAY", "HERE TONIGHT!")],
    "strike": [("WHAT A SHOT!", ""), ("RIGHT ON THE BUTTON!", ""), ("{name} IS LIGHTING", "HIM UP!")],
    "stun": [("{opp} IS SEEING", "STARS!"), ("HE'S OUT ON HIS FEET!", "")],
    "tieup": [("THEY LOCK UP IN THE", "MIDDLE OF THE RING!"), ("A TEST OF STRENGTH!", "")],
    "slam": [("WHAT A SLAM!", ""), ("{opp} IS DOWN!", ""), ("THE RING SHOOK ON", "THAT ONE!")],
    "top_rope": [("{name} IS GOING UP", "TOP!"), ("HE'S FLYING!", "")],
    "taunt": [("{name} IS SHOWING OFF", "FOR THE CROWD!"), ("THE FANS ARE GOING", "WILD!")],
    "finisher": [("HERE IT COMES...", "THE {move}!!!"), ("THAT'S HIS FINISHER!", "IT COULD BE OVER!")],
    "pin": [("THE COVER!", ""), ("HE HOOKS THE LEG!", "")],
    "count": [("ONE...", ""), ("ONE... TWO...", ""), ("ONE... TWO... THREE!", "")],
    "kickout": [("NO! HE KICKED OUT!", ""), ("ONLY TWO! THIS ONE", "ISN'T OVER!")],
    "submission": [("HE'S GOT IT LOCKED IN!", "WILL HE TAP?"), ("{opp} IS IN TROUBLE!", "")],
    "escape": [("HE GOT TO THE ROPES!", "WHAT A FIGHTER!")],
    "outside": [("THEY'RE FIGHTING ON", "THE OUTSIDE!"), ("THE REF IS COUNTING!", "")],
    "dont_give_up": [("DON'T GIVE UP YET!", "THE CROWD IS BEHIND YOU!")],
    "low_energy": [("{name} IS RUNNING", "ON EMPTY!")],
    "reversal": [("REVERSAL! TOO SOON", "FOR THE BIG ONE!")],
    "win_pin": [("THE WINNER BY PINFALL...", "{name}!")],
    "win_sub": [("HE TAPPED OUT!", "{name} WINS!")],
    "win_countout": [("COUNTED OUT!", "{name} WINS IT!")],
    "champion": [("THE NEW HOME WIDE", "CHAMPION... {name}!!!")],
}

# ---------------------------------------------------------------- passwords
# letters only from the password grid (no I, O, 0, 1). First half = the wrestler's coded name,
# second half = the match. All 12 are fixed, so you can write them on a sticky note like 1990.
CODE_NAME = {"mike": "MGHT", "stew": "BEEF", "jim": "BAAH", "niko": "TALL"}
PASSWORDS = {
    ("mike", 1): "MGHT-K7RQ", ("mike", 2): "MGHT-Z4WD", ("mike", 3): "MGHT-X9PB",
    ("stew", 1): "BEEF-H3NV", ("stew", 2): "BEEF-Q8MT", ("stew", 3): "BEEF-W2CJ",
    ("jim", 1): "BAAH-R6FZ", ("jim", 2): "BAAH-D5KX", ("jim", 3): "BAAH-N7YG",
    ("niko", 1): "TALL-P4SE", ("niko", 2): "TALL-J9VA", ("niko", 3): "TALL-U3HM",
}
# secret codes: typed on the password screen like a normal password
SECRETS = {
    "HVGE-HEDS": "Big heads for everyone (heads drawn at double size). Works until you turn the game off.",
    "THNK-YALL": "Plays the ending and credits straight away.",
    "BELT-TYME": "Skip to your nemesis title match with the first wrestler on the select screen.",
}

# ---------------------------------------------------------------- moves list (pause menu), per wrestler
# each page: (title, [(keys, move, kind)]) where kind = "" normal, "special", or "finisher"
BASE = {
    "STANDING": [("A", "PUNCH", ""), ("S", "KICK", ""), ("D", "BLOCK (CLOSE)", ""), ("D", "TAUNT (FAR)", ""),
                 ("WALK IN", "TIE-UP", ""), ("ARROWx2", "RUN", "")],
    "TIE-UP": [("A", "HEADLOCK", ""), ("S", "KNEE LIFT", ""), ("UP+A", "BODY SLAM", ""), ("UP+S", "BRAIN BUSTER", ""),
               ("L/R+S", "BACK DROP", ""), ("DOWN+S", "PILE DRIVER", ""), ("D+ARROW", "ROPE WHIP", "")],
    "RUNNING": [("A", "CLOTHESLINE", ""), ("S", "DROPKICK", ""), ("D", "STOP", ""), ("A OR S", "SHOULDER THROW", "")],
    "OPPONENT DOWN": [("A", "PIN", ""), ("UP/DN+A", "STOMP", ""), ("L/R+S", "KNEE DROP", ""),
                      ("L/R+A", "BOSTON CRAB", "")],
    "TOP ROPE": [("CORNER+UP", "CLIMB", ""), ("S", "DIVING ATTACK", ""), ("A", "FLYING KNEE DROP", "")],
    "OUTSIDE": [("PUSH ROPES", "GO OUT / IN", ""), ("L/R+A", "POST SLAM", ""), ("MASH A/S", "GET UP/KICK OUT", "")],
}
# (page, keys) -> (new move, kind)
SWAPS = {
    "mike": {("TIE-UP", "UP+A"): ("MILITARY PRESS", "special"), ("TIE-UP", "A"): ("BEAR HUG", "special"),
             ("TIE-UP", "DOWN+S"): ("POWERBOMB", "finisher"), ("OPPONENT DOWN", "L/R+S"): ("ELBOW DROP", "")},
    "stew": {("TIE-UP", "A"): ("HEADBUTT", "special"), ("OPPONENT DOWN", "L/R+S"): ("SEATED BUTT DROP", "special"),
             ("RUNNING", "A"): ("RUNNING LARIAT", "finisher")},
    "jim": {("TIE-UP", "L/R+S"): ("VERTICAL SUPLEX", "special"), ("TIE-UP", "S"): ("HIP TOSS", "special"),
            ("TIE-UP", "A"): ("SLEEPER HOLD", "finisher")},
    "niko": {("RUNNING", "S"): ("FLYING CROSSBODY", "special"), ("TOP ROPE", "A"): ("MISSILE DROPKICK", "special"),
             ("TIE-UP", "UP+S"): ("DDT", "finisher")},
}
FINISHER = {"mike": ("POWERBOMB", "TIE-UP: DOWN+S"), "stew": ("RUNNING LARIAT", "RUNNING: A"),
            "jim": ("SLEEPER HOLD", "TIE-UP: A"), "niko": ("DDT", "TIE-UP: UP+S")}


def moves_list(who):
    """pages for this wrestler: specials swapped in, finisher marked (it only works when the opponent is under 30%;
    before that the normal move on that button is used)."""
    pages = []
    for title, rows in BASE.items():
        out = []
        for keys, move, kind in rows:
            sw = SWAPS[who].get((title, keys))
            if sw and sw[1] == "finisher":
                out.append((keys, move, ""))
                out.append((keys, sw[0], "finisher"))
            elif sw:
                out.append((keys, sw[0], sw[1]))
            else:
                out.append((keys, move, kind))
        pages.append((title, out))
    name, where = FINISHER[who]
    pages.append(("FINISHER", [("", name, "finisher"), ("", where, ""), ("", "WHEN HE IS UNDER 30%", ""),
                               ("", "THEN PIN HIM TO WIN!", "")]))
    return pages


HOW_TO_PLAY = [
    ("ARROWS", "MOVE"), ("ARROWx2", "RUN"), ("A", "PUNCH / LIGHT"), ("S", "KICK / HEAVY"),
    ("D", "BLOCK / TAUNT"), ("WALK IN", "TIE-UP"), ("MASH A/S", "WIN STRUGGLES"), ("ENTER", "PAUSE + MOVES"),
]

SCORE = {"hit": 100, "slam": 300, "taunt": 300, "finisher": 2000, "win": 5000, "quick_win_under_60s": 3000,
         "quick_win_under_120s": 1500}
