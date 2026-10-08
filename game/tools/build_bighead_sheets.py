"""The HVGE-HEDS secret code: every sprite sheet again, with the heads drawn twice as big.

Same layout as export/sprites (same rows, same JSON), just taller cells so the heads fit:
  assets/bighead/<who>_solo.png, <who>_sheets.json, <a>_vs_<b>_pairs.png   (and the ref)

Slow (a few minutes): run from anywhere with  python game/tools/build_bighead_sheets.py
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "export", "source"))
import chars3d as c3  # noqa: E402
import pairs  # noqa: E402

OUT = os.path.join(HERE, "..", "assets", "bighead")
F = ["down-right", "down-left", "up-right", "up-left"]
SOLO, SOLO_FEET = (64, 100), (32, 90)          # 24 px taller than the normal sheets
PAIR, PAIR_FEET = (96, 120), (48, 94)
WHO = ("mike", "stew", "jim", "niko")

c3.HS = c3.HS * 2           # the whole trick


def solo(who):
    rows = c3.moves_for(who)
    w, h = SOLO
    img = Image.new("RGBA", (w * 8, h * len(rows)), (0, 0, 0, 0))
    for r, (name, frames) in enumerate(rows):
        for i, face in enumerate(F):
            for j in range(2):
                cell = Image.new("RGBA", SOLO, (0, 0, 0, 0))
                c3.render(who, frames[min(j, len(frames) - 1)], face, SOLO_FEET, w, h, cell)
                img.alpha_composite(cell, ((i * 2 + j) * w, r * h))
    img.save(os.path.join(OUT, f"{who}_solo.png"))
    return [n for n, _ in rows]


def pair_sheets(who):
    prow = pairs.pair_moves(who)
    w, h = PAIR
    for vic in WHO:
        if vic == who:
            continue
        pim = Image.new("RGBA", (w * 8, h * len(prow)), (0, 0, 0, 0))
        for r, (name, frames) in enumerate(prow):
            for i, face in enumerate(F):
                for j, fr in enumerate(frames):
                    cell = Image.new("RGBA", PAIR, (0, 0, 0, 0))
                    pairs.render_pair(who, vic, fr, face, PAIR_FEET, w, h, cell)
                    pim.alpha_composite(cell, ((i * 2 + j) * w, r * h))
        pim.save(os.path.join(OUT, f"{who}_vs_{vic}_pairs.png"))
    return [n for n, _ in prow]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cols = [f"{f} frame {k + 1}" for f in F for k in range(2)]
    for who in WHO + ("ref",):
        rows = solo(who)
        meta = {"solo": {"cell": list(SOLO), "feet": list(SOLO_FEET), "columns": cols, "rows": rows}}
        if who != "ref":
            prow = pair_sheets(who)
            meta["pairs"] = {"cell": list(PAIR), "attacker_feet": list(PAIR_FEET),
                             "files": f"{who}_vs_<victim>_pairs.png", "columns": cols, "rows": prow}
        json.dump(meta, open(os.path.join(OUT, f"{who}_sheets.json"), "w"), indent=1)
        print(who, "done", flush=True)
