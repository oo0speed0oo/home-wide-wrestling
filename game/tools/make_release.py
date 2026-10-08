"""Makes a ready-to-play release in the main project folder, for Windows, Mac and Linux:

    "Home Wide Wrestling - <name>/"       the game, ready to play (folder)
    "Home Wide Wrestling - <name>.zip"    the same folder, zipped to send to people

Inside:
    Home Wide Wrestling - Windows.exe     Windows: double-click, no Python needed (built with PyInstaller)
    <name> - Windows.bat                   Windows with Python instead of the .exe
    <name> - Mac.command                   Mac: double-click (needs Python 3; installs pygame the first time)
    <name> - Linux.sh                      Linux: run it (needs Python 3; installs pygame the first time)
    HOW TO PLAY.txt, DESIGN_DOC.md, game/ (code + assets), export/sprites, export/sound

It also makes "Home Wide Wrestling - Website Upload (<name>).zip" (tools/build_web.py) for your website.

Usage:  python game/tools/make_release.py "Version 1"
        (--no-exe skips rebuilding the .exe, --no-web skips the website version)
A Mac or Linux program that runs without Python can only be built on a Mac or Linux machine.
"""
import os
import shutil
import stat
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
TITLE = "Home Wide Wrestling"
SKIP_DIRS = {"__pycache__", "previews", "tools", "bighead_src"}


def launchers(name, exe=True):
    """the three launchers. exe=False for the copies at the top of the GitHub repo (no .exe there)."""
    skip = f'\nrem (Or skip Python: double-click "{TITLE} - Windows.exe".)' if exe else ""
    no_py = f'\n    echo Or just double-click "{TITLE} - Windows.exe", which needs no Python.' if exe else ""
    bat = f"""@echo off
rem {TITLE} - {name} (Windows, with Python)
rem Double-click this file to play.{skip}
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 is not installed. Get it from https://www.python.org/downloads/
    echo During the install, tick "Add python.exe to PATH". Then double-click this file again.{no_py}
    pause
    exit /b
)

python -c "import pygame" >nul 2>nul
if errorlevel 1 (
    echo Installing pygame, one moment...
    python -m pip install pygame-ce
)

start "" pythonw game\\main.py
"""
    mac = f"""#!/bin/bash
# {TITLE} - {name} (Mac)
# Double-click this file to play. It runs game/main.py in this folder with Python 3.
# The first time, macOS may block it: right-click it and choose Open
# (or System Settings > Privacy & Security > Open Anyway).

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Get it from https://www.python.org/downloads/ and try again."
    read -r -p "Press Enter to close."
    exit 1
fi

if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame, one moment..."
    python3 -m pip install --user pygame-ce || python3 -m pip install --user --break-system-packages pygame-ce
fi

python3 game/main.py
"""
    linux = f"""#!/bin/bash
# {TITLE} - {name} (Linux)
# Run it from a terminal:   ./"{name} - Linux.sh"
# (or right-click it in your file manager and choose "Run as a Program").

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed. Install it with your package manager, for example:"
    echo "    sudo apt install python3 python3-pip"
    exit 1
fi

if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame, one moment..."
    if ! python3 -m pip install --user pygame-ce; then
        echo "pip could not install pygame here. Try your package manager instead, for example:"
        echo "    sudo apt install python3-pygame"
        exit 1
    fi
fi

python3 game/main.py
"""
    return {f"{name} - Windows.bat": bat, f"{name} - Mac.command": mac, f"{name} - Linux.sh": linux}


def how_to_play(name):
    return f"""{TITLE.upper()} - {name.upper()}
{"=" * (len(TITLE) + len(name) + 3)}

An NES-style wrestling game starring Mighty Mike, Big Beefy Stew, Jim "The Goat" and Nimble Niko.
Win three matches, beat your nemesis, and become the Home Wide Champion.

HOW TO START IT
  Windows:  double-click  "{TITLE} - Windows.exe"   (nothing else needed)
            Windows may say it protected your PC: click "More info", then "Run anyway".
            With Python instead: double-click "{name} - Windows.bat".
  Mac:      double-click  "{name} - Mac.command"
            Needs Python 3 (free, from https://www.python.org/downloads/); it installs pygame
            by itself the first time. The first time, macOS may block it: right-click it,
            choose Open, then Open again (or System Settings > Privacy & Security > Open Anyway).
  Linux:    in a terminal in this folder, run:  ./"{name} - Linux.sh"
            (or right-click it and choose "Run as a Program"). Needs Python 3.

  Any system, by hand:  open a terminal in this folder and run
      python game/main.py        (Windows)
      python3 game/main.py       (Mac and Linux)

CONTROLS (keyboard)
  Arrow keys .... walk (double-tap to run), move around the menus
  A ............. punch, and the "light" button everywhere
  S ............. kick, and the "heavy" button everywhere
  D ............. block when he's close, taunt when he's far, stop running
  Enter ......... start / pause (moves list, password, quit match)
  M ............. sound on/off        F11 ... full screen        Esc ... quit

  Walk into him to lock up, then hold a direction and mash A or S: the button picks your move.
  When he's down: A pins, Up/Down+A stomps, Left/Right+A Boston crab, S drops on him.
  Finishers work once he's under 30% energy. Pause during a match to see your own moves list.
  Win by pinfall, submission or count-out.

The Hall of Fame is saved on this computer, so it lasts between games.
"""


def copy_tree(src, dst):
    for base, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(base, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            if f.endswith((".pyc", ".spec", "_8frames.png")):      # (the exported arena previews aren't used)
                continue
            shutil.copy2(os.path.join(base, f), os.path.join(dst, rel, f))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    name = args[0] if args else "Version 1"
    folder = f"{TITLE} - {name}"
    out = os.path.join(ROOT, folder)
    if "--no-exe" not in sys.argv:
        subprocess.run([sys.executable, os.path.join(HERE, "build_exe.py")], check=True)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    copy_tree(os.path.join(ROOT, "game"), os.path.join(out, "game"))
    for sub in ("sprites", "sound"):
        copy_tree(os.path.join(ROOT, "export", sub), os.path.join(out, "export", sub))
    shutil.copy2(os.path.join(ROOT, "DESIGN_DOC.md"), out)
    shutil.copy2(os.path.join(ROOT, "dist", "HomeWideWrestling.exe"), os.path.join(out, f"{TITLE} - Windows.exe"))
    with open(os.path.join(out, "HOW TO PLAY.txt"), "w", newline="\r\n") as f:
        f.write(how_to_play(name))
    for fname, text in launchers(name).items():
        path = os.path.join(out, fname)
        with open(path, "w", newline="\r\n" if fname.endswith(".bat") else "\n") as f:
            f.write(text)
        if not fname.endswith(".bat"):
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    # zip it, marking the Mac and Linux launchers as runnable so they still work after unzipping there
    zpath = out + ".zip"
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(out):
            for f in files:
                full = os.path.join(base, f)
                arc = os.path.join(folder, os.path.relpath(full, out)).replace("\\", "/")
                info = zipfile.ZipInfo.from_file(full, arc)
                info.compress_type = zipfile.ZIP_DEFLATED
                mode = 0o755 if f.endswith((".sh", ".command")) else 0o644
                info.external_attr = (stat.S_IFREG | mode) << 16
                with open(full, "rb") as fh:
                    z.writestr(info, fh.read())
    print("release:", out)
    print("zip:    ", zpath, f"{os.path.getsize(zpath) / 1e6:.1f} MB")
    if "--no-web" not in sys.argv:          # and the website version, as its own upload zip
        subprocess.run([sys.executable, os.path.join(HERE, "build_web.py"), name], check=True)


if __name__ == "__main__":
    main()
