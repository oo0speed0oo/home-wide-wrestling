"""Builds the screens' fixed art from the art source (export/source) and the exported reels.

  assets/screens/logo.png              the big HWW logo (screens.LOGO)
  assets/screens/title_bg.png          30 frames of the title backdrop: stars + sweeping searchlights
  assets/screens/entrance_<who>.png    the four ramp entrances, 70 frames each (from export/entrance_<who>.gif)
  assets/screens/champion.png          the champion ending demo, 64 frames (from export/champion_demo.gif)
  assets/screens/font_8x8_full.png     every glyph the font source has
  assets/screens/champion_<who>.png    the champion ending for each wrestler, 72 frames (slow: run with
                                       the argument "champions")
Frames are 256x240, stored in a grid 10 across.

Run from anywhere:  python game/tools/build_screen_assets.py [champions]
"""
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT = os.path.join(HERE, "..", "..", "export")
sys.path.insert(0, os.path.join(EXPORT, "source"))
import screens as sc  # noqa: E402

OUT = os.path.join(HERE, "..", "assets", "screens")
SW, SH = 256, 240
COLS = 10


def grid(frames):
    rows = (len(frames) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (SW * COLS, SH * rows), (0, 0, 0, 255))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % COLS) * SW, (i // COLS) * SH))
    return sheet


def title_bg(frame):
    img = sc.blank()
    sc.stars(img, frame, n=50, bottom=150)
    for top_x, sway in ((20, 1), (236, -1)):
        bx = 128 + sway * 40 * math.sin(frame / 10 * 2 * math.pi)
        sc.dither(img, lambda x, y, t=top_x, b=bx: abs(x - (t + (b - t) * y / 150)) <= 2 + 26 * y / 150,
                  "#24188C", 2, (0, 0, SW, 150))
    return img


def gif_frames(path):
    """a 3x preview GIF back to native 256x240 frames."""
    g = Image.open(path)
    out = []
    for i in range(g.n_frames):
        g.seek(i)
        out.append(g.convert("RGBA").resize((SW, SH), Image.NEAREST))
    return out


def full_font():
    """every glyph the font source has (the exported sheet leaves out < > * % + =, which the menus need)."""
    import json
    import font
    order = "".join(ch for ch in font.G if ch != " ") + " "
    cols = 16
    rows = (len(order) + cols - 1) // cols
    img = Image.new("RGBA", (cols * 8, rows * 8), (0, 0, 0, 0))
    for k, ch in enumerate(order):
        font.draw_text(img, (k % cols) * 8, (k // cols) * 8, ch, "#FCFCFC")
    img.save(os.path.join(OUT, "font_8x8_full.png"))
    json.dump({"cell": [8, 8], "columns": cols, "order": order, "note": "@ is the copyright sign"},
              open(os.path.join(OUT, "font_8x8_full.json"), "w"), indent=1)


CHAMP_FRAMES = 72           # the announcer's line has typed out by frame 36; the game loops 36..71


def champions():
    """the champion ending for each wrestler: belt overhead, fireworks, the announcer (screens2.champion)."""
    import screens2
    for who in ("mike", "stew", "jim", "niko"):
        grid([screens2.champion(who, f) for f in range(CHAMP_FRAMES)]).save(
            os.path.join(OUT, f"champion_{who}.png"))
        print("champion", who, flush=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:] == ["champions"]:
        champions()
        sys.exit()
    full_font()
    sc.LOGO.save(os.path.join(OUT, "logo.png"))
    grid([title_bg(f) for f in range(30)]).save(os.path.join(OUT, "title_bg.png"))
    print("logo, title")
    for who in ("mike", "stew", "jim", "niko"):
        fr = gif_frames(os.path.join(EXPORT, f"entrance_{who}.gif"))
        grid(fr).save(os.path.join(OUT, f"entrance_{who}.png"))
        print("entrance", who, len(fr))
    fr = gif_frames(os.path.join(EXPORT, "champion_demo.gif"))
    grid(fr).save(os.path.join(OUT, "champion.png"))
    print("champion", len(fr))
