HOME WIDE WRESTLING - the playable game (Pygame)

Run:   python game/main.py        (needs pygame-ce; Pillow only for the tools)
Keys:  arrows, A, S, D, Enter = pause.  F11 = fullscreen.  M = mute.  Esc = quit.
       Menus: arrows move, A or Enter picks, S goes back.  Intros, VS screens and entrances: A skips.
       F3 = debug on/off: the test keys below work in matches, and F2 opens the sprite viewer.

main.py              window, 60 fps loop, sharp 3x scaling
hww/settings.py      screen size, layout, paths, names and colours
hww/assets.py        loads sprite sheets (by row name from the JSON), the 8x8 font, arena layers
hww/ring.py          mat position -> screen pixel (same angled view as the art), the floor outside,
                     the corners
hww/controls.py      keyboard: held buttons and buttons pressed this frame
hww/wrestler.py      a wrestler: position, facing, walk/run/bounce, body stats, strikes,
                     stun, knockdown, get-up, energy recovery (all timings at the top)
hww/match.py         the match screen: you vs the CPU, the ref, top bar, announcer
hww/hud.py           top bar (names, 24 energy pips) and the announcer bar
hww/cpu.py           the CPU: presses buttons like a player, the difficulty ladder (top of the file),
                     each wrestler's habit; test brains WANDER / STILL
hww/effects.py       hit sparks, the finisher flash, the slam shake
hww/specials.py      which special replaces which move, and each finisher (under 30%)
hww/grapple.py       tie-ups (the meter, energy gap, don't give up yet, too early) and the
                     two-person moves played from the pair sheets (damage and timings at the top)
hww/game_text.py     every word in the game (copied from export/source; edit THIS copy for the game)
hww/referee.py       the ref: keeps out of the way, counts pins, checks submissions, raises the hand
hww/sound.py         sound effects and music from ../export/sound (M mutes)
hww/game.py          the whole game screen to screen: the 1-player run, VS mode, passwords
hww/screens.py       title + menu + difficulty, select + profiles, VS mode setup, VS screen, entrances,
                     win, lose, password entry, how to play
hww/ui.py            menu windows, arrows, dimming, stars
hww/hall_of_fame.py  top 5 scores, saved in %APPDATA%\HomeWideWrestling\hall_of_fame.json
tools/build_bighead_sheets.py  rebuilds assets/bighead/ (every sheet with double heads, for HVGE-HEDS)
tools/balance_sim.py           CPU vs CPU, every matchup: win rates, how matches end, finishers
tools/build_exe.py             builds dist/HomeWideWrestling.exe (PyInstaller, with an HWW icon)
tools/make_release.py          the Windows/Mac/Linux release folder + zip in the main project folder
tools/build_web.py             the website version (pygbag): build_web/ and the Website Upload zip
hww/profiles.py      the wrestlers' profile cards, catchphrases, and the run order
tools/build_screen_assets.py  rebuilds assets/screens/ (logo, title backdrop, entrances, champion, full font)
hww/viewer.py        step 1 test screen (F2): any wrestler, any move, any facing
previews/            screenshots and GIFs from each step
tools/build_arena_layers.py   rebuilds assets/arenas/ from export/source/arenas.py
assets/arenas/       arena<N>_back.png (behind the wrestlers) + arena<N>_front.png (front ropes),
                     8 frames of 256x216 in a row each

Art is read straight from ../export/sprites, so re-exporting art updates the game.

Build steps (13):
  [x] 1  Window and loading       Mike standing in arena 1; every sheet loads
  [x] 2  Movement                 walk 8 ways, double-tap run, bounce off all 4 ropes
  [x] 3  Two wrestlers and HUD    CPU wanders, energy pips, announcer types the intro
  [x] 4  Striking                 punch, kick, block/taunt, stun, knockdown, get up
  [x] 5  Tie-ups                  tug-of-war meter, 7 tie-up moves, whip + shoulder throw
  [x] 6  Running and ground       clothesline, dropkick, collisions, pin + count, crab, win
  [x] 7  Ropes, outside, top      out over the front ropes, count-out, post slam, dives
  [x] 8  Specials and finishers   2 specials + finisher each, flash, slam shake
  [x] 9  Ref, announcer, sound    intro + bell, DING!, every sound effect, match music, jingles
  [x] 10 CPU                      difficulty ladder, a habit per wrestler, taunt bait
  [x] 11 Screens and flow         title, menu, select, VS, entrances, win/lose, password, pause
  [x] 12 The single-player run    score, Hall of Fame, secret codes, crooked ref, ending, credits
  [x] 13 Tuning and build         balance pass (CPU vs CPU), dist/HomeWideWrestling.exe

RELEASES (made after every update, in the main project folder):
  "Home Wide Wrestling - Version N" folder + .zip: the Windows .exe, launchers for Windows (.bat),
  Mac (.command) and Linux (.sh), HOW TO PLAY.txt, the game and its assets.
  Make one:  python game/tools/make_release.py "Version 2"
  It also makes "Home Wide Wrestling - Website Upload (Version N).zip": the browser version for your
  WordPress site (unzip it next to wp-admin; READ ME FIRST.txt inside). Web version alone:
  python game/tools/build_web.py "Version 2"   (needs: python -m pip install pygbag soundfile)
The Windows game alone:  dist/HomeWideWrestling.exe  (one file, ~21 MB, no Python needed; copy it anywhere)
  Rebuild after any change:  python game/tools/build_exe.py   (needs: python -m pip install pyinstaller pillow)
Balance check after changing numbers:  python game/tools/balance_sim.py 16 2   (add "nohabits" to measure
  the wrestlers without their CPU habits). Where the numbers live:
  hww/wrestler.py  speeds, reach, strike damage, Power, stun/block/get-up timings, energy recovery
  hww/grapple.py   tie-up meter, every two-person move's damage, holds, pins, tap-out line
  hww/cpu.py       the difficulty ladder and each CPU habit
  hww/specials.py  which moves are specials and finishers

Match keys: arrows walk, double-tap to run, A punch, S kick,
  D block (close) / taunt (far) / stop running, mash A or S when stunned or down.
  Walk into him to tie up, then hold a direction and mash: A headlock, Up+A body slam, S knee lift,
  Up+S brain buster, Left/Right+S back drop, Down+S pile driver, D+arrow rope whip.
  A or S as he runs back at you = shoulder throw.
  Running: A clothesline, S dropkick. He's down: A pin, Up/Down+A stomp, Left/Right+A Boston crab,
  S knee/elbow drop (Stew: seated butt drop). Pinned or in the crab: mash A, S or D.
  Keep walking into a front rope to climb out; outside, walk into the apron to climb back in.
  On the floor: tie-up Left/Right+A = post slam. Walk into a corner (or Up there) to climb:
  S diving body attack, A flying knee drop, walk away from the post to climb down.
  Specials (always): Mike Up+A military press, A bear hug; Jim L/R+S vertical suplex, S hip toss;
  Niko running S flying crossbody, top rope A missile dropkick; Stew A headbutt, S on the ground butt drop.
  Finishers (him under 30%): Mike Down+S powerbomb, Niko Up+S DDT, Jim A sleeper hold, Stew running A lariat.
  Enter pauses: CONTINUE, MOVES LIST (Left/Right pages), PASSWORD, QUIT MATCH.
Debug test keys (F3 first): K CPU brain (FIGHT / WANDER / STILL), L difficulty (EASY / MEDIUM / HARD), J match (1 / 2 / NEMESIS).
  Tab your wrestler, C the CPU's wrestler, 1 / 2 / 4 arena, - / = your energy, 9 / 0 CPU energy,
  N makes the announcer say something.
F2 sprite viewer: arrows turn, A/S move, D animation, Tab wrestler or ref, 1 / 2 / 4 arena.
