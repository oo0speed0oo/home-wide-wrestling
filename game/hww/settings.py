"""Home Wide Wrestling - fixed numbers for the whole game."""
import os
import sys

# the NES screen; everything is drawn at this size, then scaled up with sharp pixels
SCREEN_W, SCREEN_H = 256, 240
SCALE = 3                    # window = 768x720
FPS = 60
DEBUG = False                # F3: test keys in matches, F2 sprite viewer

# match screen layout (see export/source/hud.py)
TOP_H = 24                   # black top bar: names and energy
BOT_Y = 208                  # black announcer bar from here down
ARENA_SHIFT = -8             # the arena art is nudged up 8 px so the whole ring fits

WEB = sys.platform == "emscripten"      # running in a browser (pygbag)

# paths. Built into an .exe (tools/build_exe.py), everything is unpacked under sys._MEIPASS instead.
# The web copy (tools/build_web.py) carries export/ inside the game folder.
if getattr(sys, "frozen", False):
    GAME_DIR = os.path.join(sys._MEIPASS, "game")
    EXPORT_DIR = os.path.join(sys._MEIPASS, "export")
else:
    GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXPORT_DIR = os.path.join(GAME_DIR, "export")
    if not os.path.isdir(EXPORT_DIR):
        EXPORT_DIR = os.path.join(GAME_DIR, "..", "export")
SPRITES_DIR = os.path.join(EXPORT_DIR, "sprites")
ARENA_DIR = os.path.join(GAME_DIR, "assets", "arenas")

# wrestlers
WRESTLERS = ("mike", "stew", "jim", "niko")
FULL_NAME = {"mike": "MIGHTY MIKE", "stew": "BIG BEEFY STEW", "jim": "JIM THE GOAT", "niko": "NIMBLE NIKO",
             "ref": "REFEREE"}
SHORT_NAME = {"mike": "MIKE", "stew": "STEW", "jim": "JIM", "niko": "NIKO"}
TOWN = {"mike": "THE IRON DUNGEON", "stew": "THE ALL-YOU-CAN-EAT BUFFET", "jim": "THE TOP OF THE MOUNTAIN",
        "niko": "HIGH ABOVE THE CLOUDS"}
HUD_COL = {"mike": "#F83800", "stew": "#3CBCFC", "jim": "#58D854", "niko": "#9878F8", "ref": "#FCFCFC"}

# sprite sheet columns: 4 facings x 2 frames
FACINGS = ("down-right", "down-left", "up-right", "up-left")
ANIM_TICKS = 16              # frames of game time per animation frame (2-frame animations)
