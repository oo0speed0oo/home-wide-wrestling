"""Rough first-pass title logo for Home Wide Wrestling.
Original chunky 80s-style block initials (HWW) plus the full name. Not a copy of any real logo."""
from PIL import Image, ImageDraw, ImageFont

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"

H_ = """\
XXX...XXX
XXX...XXX
XXX...XXX
XXX...XXX
XXXXXXXXX
XXXXXXXXX
XXX...XXX
XXX...XXX
XXX...XXX
XXX...XXX
XXX...XXX"""
W_ = """\
XXX.......XXX
XXX.......XXX
XXX.......XXX
XXX..XXX..XXX
XXX..XXX..XXX
XXX..XXX..XXX
XXX.XXXXX.XXX
XXXXXX.XXXXXX
XXXXX...XXXXX
XXXX.....XXXX
XXX.......XXX"""

BANDS = ["#FCFCFC", "#F8D878", "#F8B800", "#F8B800", "#FCA044", "#E45C10",
         "#E45C10", "#F83800", "#F83800", "#A81000", "#A81000"]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


def letters(glyphs, gap=2):
    rows = [g.split("\n") for g in glyphs]
    w = sum(len(r[0]) for r in rows) + gap * (len(rows) - 1)
    h = len(rows[0])
    slant = h // 3 + 1
    img = Image.new("RGBA", (w + slant + 8, h + 8), (0, 0, 0, 0))
    p = img.load()
    x0 = 0
    for r in rows:
        for y, line in enumerate(r):
            shift = (h - 1 - y) // 3          # italic lean
            for x, ch in enumerate(line):
                if ch == "X":
                    p[4 + x0 + x + shift, 4 + y] = rgb(BANDS[y])
        x0 += len(r[0]) + gap
    return img


def outline(img, col, grow=1):
    out = img.copy()
    src = img.load()
    p = out.load()
    for y in range(img.height):
        for x in range(img.width):
            if src[x, y][3]:
                continue
            for dx in range(-grow, grow + 1):
                for dy in range(-grow, grow + 1):
                    qx, qy = x + dx, y + dy
                    if 0 <= qx < img.width and 0 <= qy < img.height and src[qx, qy][3]:
                        p[x, y] = rgb(col)
    return out


def main():
    big = letters([H_, W_, W_])
    big = big.resize((big.width * 2, big.height * 2), Image.NEAREST)   # chunky 2x pixels
    big = outline(big, "#000000", 1)
    shadow = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sp, bp = shadow.load(), big.load()
    for y in range(big.height):
        for x in range(big.width):
            if bp[x, y][3]:
                sp[x, y] = rgb("#000000")
    W, H = 176, 64
    logo = Image.new("RGBA", (W, H), rgb("#0000BC"))
    d = ImageDraw.Draw(logo)
    for y in range(0, H, 4):                       # scanline stripes in the backdrop
        d.line((0, y, W, y), fill=rgb("#00007C"))
    bx = (W - big.width) // 2
    logo.alpha_composite(shadow, (bx + 3, 2))
    logo.alpha_composite(big, (bx, -1))
    d.fontmode = "1"
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 9)
    text = "HOME WIDE WRESTLING"
    tw = d.textlength(text, font=font)
    d.rectangle((8, 46, W - 9, 58), fill=rgb("#A81000"))
    d.rectangle((8, 46, W - 9, 46), fill=rgb("#F87858"))
    d.rectangle((8, 58, W - 9, 58), fill=rgb("#000000"))
    d.text(((W - tw) / 2 + 1, 48), text, font=font, fill=rgb("#000000"))
    d.text(((W - tw) / 2, 47), text, font=font, fill=rgb("#FCFCFC"))
    logo.convert("RGB").resize((W * 5, H * 5), Image.NEAREST).save(OUT + "logo_draft.png")


if __name__ == "__main__":
    main()
