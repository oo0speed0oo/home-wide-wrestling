DESIGN_DOC.md = the full game design doc (every rule and decision). Read this first.

HOME WIDE WRESTLING - art save point (2026-09-30)

sprites/   game-ready sheets, native NES size (1x), transparent. Scale 3x with nearest-neighbor in Pygame.
  <name>_solo.png    every move for one wrestler: rows = moves, columns = 4 facings x 2 frames (64x76 cells)
  <name>_pairs.png   two-person moves drawn with the victim: rows = moves, columns = 4 facings x 2 frames (96x88 cells)
  <name>_sheets.json row names, cell sizes and foot points for both sheets
arenas/    arena 1, 2, 4 at 256x216, 8 animation frames each (crowd + lights), wrestlers included for reference
*.gif      preview reels (moves, two-person moves, arenas)
source/    the Python that draws everything (chars3d.py = wrestlers, pairs.py = two-person moves,
           arenas.py + crowd.py = arenas, export_sheets.py = rebuilds the sheets in sprites/)

Added (Sep 30, afternoon):
  sprites/ref_solo.png + ref_sheets.json      the referee, same layout as the wrestlers' solo sheets
  sprites/font_8x8.png + font_8x8.json        the 8x8 font, white on transparent (tint it in game)
  sprites/announcer_24x24_2frames.png         announcer portrait, mouth shut / open
  screen_demo.gif                             the full 256x240 match screen with top bar and announcer bar
  source/hud.py                               how the top bar, mash meter and announcer bar are laid out
  sprites/portraits_80x72.png                 big bust portraits (mike, stew, jim, niko) for select + profile screens
  select_demo.gif                             the wrestler select screen and the four profile cards
  source/select_screen.py                     layout + every wrestler's stats
  screens/ + screens_demo.gif                 title, VS, win, champion, game over, password, pause, credits (3x previews)
  source/screens.py                           how each screen is drawn
  sound/*.wav                                 8 sound effects + pitch reuses, 3 music tracks (22kHz mono WAV, Pygame-ready)
  source/nes_audio.py                         makes every sound from NES-style voices; edit and re-run to tweak

Added Oct 5:
  sprites/<who>_solo.png        now 37 rows: + headlock, knee lift, clothesline, dropkick, knee/elbow drop,
                                back drop, pile driver, rope whip, shoulder throw, climb, on top rope
  sprites/<a>_vs_<b>_pairs.png  two-person moves for all 12 matchups (96x96 cells, attacker feet at 48,70)
  sprites/belt_96x32.png        the HWW title belt
  entrance_<who>.gif            the four ramp entrances
  effects_demo.gif              hit sparks, slam shake, finisher flash, kick-out meter
  champion_demo.gif             the champion ending with the belt
  screens/s2_*.png              title menu, difficulty, VS mode, moves list, how to play, hall of fame, name entry
  source/game_text.py           announcer lines, the 12 passwords, secret codes, moves lists, score values

Added Oct 6 (crowd signs follow the match):
  arenas/arena<N>_<p1>_vs_<p2>_8frames.png   empty-ring arena for every matchup (36 files). The crowd signs show
                                              both wrestlers' names plus a fan sign each (MIGHTY, BEEF!, GOAT, TALL).
                                              Use these as the match background instead of arena<N>_8frames.png.
                                              p1 = the player's wrestler. Arena 1 has no signs (it's the small crowd).
  source/crowd.py                             draw_crowd(img, frame, level, fighters=(p1, p2)) if you draw live

Next up: the playable game.
