"""Builds the Windows game: dist/HomeWideWrestling.exe, one file, no Python needed to play it.

    python game/tools/build_exe.py

Needs PyInstaller (python -m pip install pyinstaller) and Pillow (for the icon). It packs in the game code,
export/sprites, export/sound and game/assets (arenas, screens, big heads). The Hall of Fame is saved outside
the .exe, in %APPDATA%\\HomeWideWrestling, so it survives a new build.
The other platforms (Mac, Linux) need their own build, made on that system with the same command.
"""
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GAME = os.path.join(ROOT, "game")
BUILD = os.path.join(ROOT, "build")


def make_icon():
    """the HWW logo on a black square, at the usual Windows icon sizes (sharp pixels)."""
    logo = Image.open(os.path.join(GAME, "assets", "screens", "logo.png")).convert("RGBA")
    side = max(logo.size) + 8
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 255))
    sq.alpha_composite(logo, ((side - logo.width) // 2, (side - logo.height) // 2))
    path = os.path.join(BUILD, "hww.ico")
    os.makedirs(BUILD, exist_ok=True)
    big = sq.resize((256, 256), Image.NEAREST)
    big.save(path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return path


def main():
    sep = os.pathsep            # PyInstaller's --add-data uses ';' on Windows, ':' elsewhere
    data = [
        (os.path.join(ROOT, "export", "sprites"), "export/sprites"),
        (os.path.join(ROOT, "export", "sound"), "export/sound"),
        (os.path.join(GAME, "assets"), "game/assets"),
    ]
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", "HomeWideWrestling", "--icon", make_icon(),
            "--distpath", os.path.join(ROOT, "dist"), "--workpath", BUILD, "--specpath", BUILD,
            "--paths", GAME, "--exclude-module", "PIL", "--exclude-module", "numpy", "--exclude-module", "tkinter"]
    for src, dst in data:
        args += ["--add-data", f"{src}{sep}{dst}"]
    args.append(os.path.join(GAME, "main.py"))
    print(" ".join(args))
    subprocess.run(args, check=True, cwd=ROOT)
    exe = os.path.join(ROOT, "dist", "HomeWideWrestling.exe")
    print("built", exe, f"{os.path.getsize(exe) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
