"""Home Wide Wrestling 8x8 font: bold NES-style capitals, 2-pixel strokes, 7x7 glyph in an 8x8 cell."""
from PIL import Image

G = {
    "A": ["..XXX..", ".XX.XX.", "XX...XX", "XX...XX", "XXXXXXX", "XX...XX", "XX...XX"],
    "B": ["XXXXXX.", "XX...XX", "XX...XX", "XXXXXX.", "XX...XX", "XX...XX", "XXXXXX."],
    "C": ["..XXXX.", ".XX..XX", "XX.....", "XX.....", "XX.....", ".XX..XX", "..XXXX."],
    "D": ["XXXXX..", "XX..XX.", "XX...XX", "XX...XX", "XX...XX", "XX..XX.", "XXXXX.."],
    "E": ["XXXXXXX", "XX.....", "XX.....", "XXXXXX.", "XX.....", "XX.....", "XXXXXXX"],
    "F": ["XXXXXXX", "XX.....", "XX.....", "XXXXXX.", "XX.....", "XX.....", "XX....."],
    "G": ["..XXXXX", ".XX....", "XX.....", "XX..XXX", "XX...XX", ".XX..XX", "..XXXXX"],
    "H": ["XX...XX", "XX...XX", "XX...XX", "XXXXXXX", "XX...XX", "XX...XX", "XX...XX"],
    "I": [".XXXXXX", "...XX..", "...XX..", "...XX..", "...XX..", "...XX..", ".XXXXXX"],
    "J": ["....XXX", ".....XX", ".....XX", ".....XX", "XX...XX", "XX...XX", ".XXXXX."],
    "K": ["XX...XX", "XX..XX.", "XX.XX..", "XXXX...", "XXXXX..", "XX..XX.", "XX...XX"],
    "L": ["XX.....", "XX.....", "XX.....", "XX.....", "XX.....", "XX.....", "XXXXXXX"],
    "M": ["XX...XX", "XXX.XXX", "XXXXXXX", "XX.X.XX", "XX...XX", "XX...XX", "XX...XX"],
    "N": ["XX...XX", "XXX..XX", "XXXX.XX", "XX.XXXX", "XX..XXX", "XX...XX", "XX...XX"],
    "O": [".XXXXX.", "XX...XX", "XX...XX", "XX...XX", "XX...XX", "XX...XX", ".XXXXX."],
    "P": ["XXXXXX.", "XX...XX", "XX...XX", "XXXXXX.", "XX.....", "XX.....", "XX....."],
    "Q": [".XXXXX.", "XX...XX", "XX...XX", "XX...XX", "XX.X.XX", "XX..XX.", ".XXX.XX"],
    "R": ["XXXXXX.", "XX...XX", "XX...XX", "XXXXXX.", "XXXX...", "XX.XXX.", "XX..XXX"],
    "S": [".XXXXX.", "XX...XX", "XX.....", ".XXXXX.", ".....XX", "XX...XX", ".XXXXX."],
    "T": ["XXXXXX.", "..XX...", "..XX...", "..XX...", "..XX...", "..XX...", "..XX..."],
    "U": ["XX...XX", "XX...XX", "XX...XX", "XX...XX", "XX...XX", "XX...XX", ".XXXXX."],
    "V": ["XX...XX", "XX...XX", "XX...XX", "XXX.XXX", ".XXXXX.", "..XXX..", "...X..."],
    "W": ["XX...XX", "XX...XX", "XX.X.XX", "XXXXXXX", "XXXXXXX", "XXX.XXX", "XX...XX"],
    "X": ["XX...XX", "XXX.XXX", ".XXXXX.", "..XXX..", ".XXXXX.", "XXX.XXX", "XX...XX"],
    "Y": ["XX..XX.", "XX..XX.", "XX..XX.", ".XXXX..", "..XX...", "..XX...", "..XX..."],
    "Z": ["XXXXXXX", "....XXX", "...XXX.", "..XXX..", ".XXX...", "XXX....", "XXXXXXX"],
    "0": [".XXXXX.", "XX..XXX", "XX.XXXX", "XXXX.XX", "XXX..XX", "XX...XX", ".XXXXX."],
    "1": ["..XX...", ".XXX...", "..XX...", "..XX...", "..XX...", "..XX...", "XXXXXX."],
    "2": [".XXXXX.", "XX...XX", ".....XX", "...XXX.", ".XXX...", "XX.....", "XXXXXXX"],
    "3": ["XXXXXXX", "....XX.", "...XX..", "..XXXX.", ".....XX", "XX...XX", ".XXXXX."],
    "4": ["...XXX.", "..XXXX.", ".XX.XX.", "XX..XX.", "XXXXXXX", "....XX.", "....XX."],
    "5": ["XXXXXX.", "XX.....", "XXXXXX.", ".....XX", ".....XX", "XX...XX", ".XXXXX."],
    "6": ["..XXXX.", ".XX....", "XX.....", "XXXXXX.", "XX...XX", "XX...XX", ".XXXXX."],
    "7": ["XXXXXXX", "XX...XX", "....XX.", "...XX..", "..XX...", "..XX...", "..XX..."],
    "8": [".XXXXX.", "XX...XX", "XX...XX", ".XXXXX.", "XX...XX", "XX...XX", ".XXXXX."],
    "9": [".XXXXX.", "XX...XX", "XX...XX", ".XXXXXX", ".....XX", "....XX.", ".XXXX.."],
    "!": ["..XX...", "..XX...", "..XX...", "..XX...", "..XX...", ".......", "..XX..."],
    "?": [".XXXXX.", "XX...XX", "....XX.", "...XX..", "...XX..", ".......", "...XX.."],
    ".": [".......", ".......", ".......", ".......", ".......", ".XX....", ".XX...."],
    ",": [".......", ".......", ".......", ".......", ".XX....", ".XX....", "XX....."],
    "'": ["..XX...", "..XX...", ".XX....", ".......", ".......", ".......", "......."],
    "\"": [".XX.XX.", ".XX.XX.", ".X..X..", ".......", ".......", ".......", "......."],
    "-": [".......", ".......", ".......", "XXXXXX.", ".......", ".......", "......."],
    ":": [".......", ".XX....", ".XX....", ".......", ".XX....", ".XX....", "......."],
    "/": [".....XX", "....XX.", "...XX..", "..XX...", ".XX....", "XX.....", "......."],
    "#": [".XX.XX.", "XXXXXXX", ".XX.XX.", ".XX.XX.", "XXXXXXX", ".XX.XX.", "......."],
    "&": [".XXX...", "XX.XX..", ".XXX...", ".XXX.XX", "XX.XXX.", "XX..XX.", ".XXX.XX"],
    "(": ["...XX..", "..XX...", ".XX....", ".XX....", ".XX....", "..XX...", "...XX.."],
    ")": [".XX....", "..XX...", "...XX..", "...XX..", "...XX..", "..XX...", ".XX...."],
    "@": [".XXXXX.", "X.....X", "X.XXX.X", "X.X...X", "X.XXX.X", "X.....X", ".XXXXX."],   # (c)
    "+": [".......", "..XX...", "..XX...", "XXXXXX.", "..XX...", "..XX...", "......."],
    "%": ["XX...X.", "XX..XX.", "...XX..", "..XX...", ".XX..XX", "XX...XX", "......."],
    "<": ["....XX.", "...XX..", "..XX...", ".XX....", "..XX...", "...XX..", "....XX."],
    ">": [".XX....", "..XX...", "...XX..", "....XX.", "...XX..", "..XX...", ".XX...."],
    "*": [".......", ".X.X.X.", "..XXX..", "XXXXXXX", "..XXX..", ".X.X.X.", "......."],
    "=": [".......", ".......", "XXXXXX.", ".......", "XXXXXX.", ".......", "......."],
    " ": ["......."] * 7,
}


def _hx(c):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (255,)
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)


def width(text, scale=1):
    return len(text) * 8 * scale


def draw_text(img, x, y, text, color="#FCFCFC", shadow=None, scale=1):
    """Draw text with its top-left at (x, y). shadow = colour of a 1px drop shadow (down-right)."""
    px = img.load()
    W, H = img.size
    layers = ([(1, _hx(shadow))] if shadow else []) + [(0, _hx(color))]
    for off, col in layers:
        for i, ch in enumerate(text.upper()):
            rows = G.get(ch, G["?"])
            for r, row in enumerate(rows):
                for c, bit in enumerate(row):
                    if bit != "X":
                        continue
                    for sy in range(scale):
                        for sx in range(scale):
                            X = x + (i * 8 + c) * scale + sx + off * scale
                            Y = y + r * scale + sy + off * scale
                            if 0 <= X < W and 0 <= Y < H:
                                px[X, Y] = col


def sheet(path):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?.,'\"-:/#&()@"
    img = Image.new("RGBA", (16 * 8 + 16, 4 * 8 + 16), _hx("#000000"))
    for k, ch in enumerate(chars):
        draw_text(img, 8 + (k % 16) * 8, 8 + (k // 16) * 8, ch)
    img.save(path)
    return img
