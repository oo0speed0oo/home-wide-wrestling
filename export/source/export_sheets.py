"""Game-ready sprite sheets at native NES size (1x), transparent background.
Solo sheet: one row per move; columns = 4 facings x 2 frames (64x76 cells), feet at (32, 66).
Pair sheet: one row per two-person move; columns = 4 facings x 2 frames (96x88 cells), attacker feet at (48, 62).
A .txt beside each sheet lists the rows in order."""
import json
from PIL import Image
import chars3d as c3
import pairs

OUT = "../export/sprites/"
F = ["down-right", "down-left", "up-right", "up-left"]
for who in ("mike", "stew", "jim", "niko"):
    rows = c3.moves_for(who)
    img = Image.new("RGBA", (64 * 8, 76 * len(rows)), (0, 0, 0, 0))
    for r, (name, frames) in enumerate(rows):
        for i, face in enumerate(F):
            for j in range(2):
                cell = Image.new("RGBA", (64, 76), (0, 0, 0, 0))
                c3.render(who, frames[min(j, len(frames) - 1)], face, (32, 66), 64, 76, cell)
                img.alpha_composite(cell, ((i * 2 + j) * 64, r * 76))
    img.save(OUT + f"{who}_solo.png")
    prow = pairs.pair_moves(who)
    for vic in ("mike", "stew", "jim", "niko"):
        if vic == who:
            continue
        pim = Image.new("RGBA", (96 * 8, 96 * len(prow)), (0, 0, 0, 0))
        for r, (name, frames) in enumerate(prow):
            for i, face in enumerate(F):
                for j, fr in enumerate(frames):
                    cell = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
                    pairs.render_pair(who, vic, fr, face, (48, 70), 96, 96, cell)
                    pim.alpha_composite(cell, ((i * 2 + j) * 96, r * 96))
        pim.save(OUT + f"{who}_vs_{vic}_pairs.png")
    json.dump({"solo": {"cell": [64, 76], "feet": [32, 66], "columns": [f"{f} frame {k+1}" for f in F for k in range(2)],
                        "rows": [n for n, _ in rows]},
               "pairs": {"cell": [96, 96], "attacker_feet": [48, 70], "files": f"{who}_vs_<victim>_pairs.png",
                         "columns": [f"{f} frame {k+1}" for f in F for k in range(2)],
                         "rows": [n for n, _ in prow]}},
              open(OUT + f"{who}_sheets.json", "w"), indent=1)
    print(who, img.size, pim.size)
