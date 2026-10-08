"""Builds the game's arena layers from the art source (export/source/arenas.py).

The exported arena strips have the front ropes painted in. The game needs the ring in two layers so the
wrestlers stand between them:
  arena<N>_back.png              everything behind the wrestlers (8 frames in a row, 256x216 each)
  arena<N>_front.png             the front ropes and front post, drawn over the wrestlers (transparent)
  arena<N>_<p1>_vs_<p2>_back.png the back layer for one matchup: since Oct 6 the crowd's signs follow the
                                 match (both names plus a fan sign each). p1 = the player's wrestler.
                                 Arena 1 has no signs, so it only has the plain back layer.

Run from anywhere:  python game/tools/build_arena_layers.py
"""
import os
import sys

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "export", "source"))
import arenas  # noqa: E402

OUT = os.path.join(HERE, "..", "assets", "arenas")
FRAMES = 8
WHO = ("mike", "stew", "jim", "niko")
SIGNED = (2, 4)             # the arenas whose crowd holds signs


def layers(arena, frame, fighters=None):
    grab = {}

    def keep_back(img, P):
        grab["back"] = img.copy()

    full = arenas.scene(arena, frame, actors_fn=keep_back, fighters=fighters)
    back = grab["back"]
    # the front layer is whatever got drawn after the wrestlers' turn: the front ropes and post
    diff = ImageChops.difference(full.convert("RGB"), back.convert("RGB")).convert("L")
    mask = diff.point(lambda v: 255 if v else 0)
    front = Image.new("RGBA", full.size, (0, 0, 0, 0))
    front.paste(full, (0, 0), mask)
    return back, front


def strips(arena, fighters=None):
    back_strip = Image.new("RGBA", (arenas.W * FRAMES, arenas.H), (0, 0, 0, 0))
    front_strip = Image.new("RGBA", (arenas.W * FRAMES, arenas.H), (0, 0, 0, 0))
    for f in range(FRAMES):
        back, front = layers(arena, f, fighters)
        back_strip.paste(back, (f * arenas.W, 0))
        front_strip.paste(front, (f * arenas.W, 0))
    return back_strip, front_strip


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for a in (1, 2, 4):
        back, front = strips(a)
        back.save(os.path.join(OUT, f"arena{a}_back.png"))
        front.save(os.path.join(OUT, f"arena{a}_front.png"))
        print("arena", a, flush=True)
        if a not in SIGNED:
            continue
        for p1 in WHO:
            for p2 in WHO:
                if p1 != p2:
                    strips(a, (p1, p2))[0].save(os.path.join(OUT, f"arena{a}_{p1}_vs_{p2}_back.png"))
        print("arena", a, "matchups", flush=True)
