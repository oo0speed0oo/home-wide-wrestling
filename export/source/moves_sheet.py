"""Move sheet + reel for one wrestler: every move, 2 frames, all 4 facings."""
import sys
from PIL import Image, ImageDraw
import chars3d as c3

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
who = sys.argv[1] if len(sys.argv) > 1 else "mike"
FACINGS = ["down-right", "down-left", "up-right", "up-left"]
CW, CHh = 64, 76
MAT = c3.hx("#BCBCBC")
LINE = c3.hx("#A4A4A4")


def cell(pose, face):
    im = Image.new("RGBA", (CW, CHh), MAT)
    feet = (CW / 2, CHh - 10)
    ImageDraw.Draw(im).ellipse((feet[0] - 8, feet[1] - 2, feet[0] + 8, feet[1] + 2), fill=LINE)
    c3.render(who, pose, face, feet, CW, CHh, im)
    return im


def sheet():
    rows = c3.moves_for(who)
    img = Image.new("RGBA", (CW * 8, CHh * len(rows)), c3.hx("#141210"))
    for r, (name, frames) in enumerate(rows):
        for i, face in enumerate(FACINGS):
            for j in range(2):
                pose = frames[min(j, len(frames) - 1)]
                if j == 1 and len(frames) == 1:
                    continue
                img.paste(cell(pose, face), ((i * 2 + j) * CW, r * CHh))
        ImageDraw.Draw(img).line((0, r * CHh, img.width, r * CHh), fill=c3.hx("#141210"))
    for i in range(1, 4):
        ImageDraw.Draw(img).line((i * 2 * CW, 0, i * 2 * CW, img.height), fill=c3.hx("#141210"), width=2)
    img.convert("RGB").resize((img.width * 3, img.height * 3), Image.NEAREST).save(OUT + f"{who}_moves_sheet.png")
    return img.size


def reel():
    frames = []
    for name, fr in c3.moves_for(who):
        seq = fr * (3 if len(fr) > 1 else 4)
        for pose in seq:
            frames.append(cell(pose, "down-right").convert("RGB").resize((CW * 4, CHh * 4), Image.NEAREST))
    frames[0].save(OUT + f"{who}_moves_reel.gif", save_all=True, append_images=frames[1:], duration=220,
                   loop=0, disposal=1)
    return len(frames)


if __name__ == "__main__":
    print(sheet(), reel())
