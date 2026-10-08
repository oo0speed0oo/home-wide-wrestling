"""Wrestler select screen (2x2 portraits) and the profile card for each wrestler."""
from PIL import Image, ImageDraw
import font
import hud
import portraits as pt

OUT = "/tmp/claude-0/-home-claude/9c1f5f17-409b-551e-82e7-add3eb6403e9/scratchpad/sprites/"
SW, SH = 256, 240
ORDER = ["mike", "stew", "jim", "niko"]
NAME2 = {"mike": ("MIGHTY", "MIKE"), "stew": ("BIG BEEFY", "STEW"), "jim": ("JIM", "\"THE GOAT\""),
         "niko": ("NIMBLE", "NIKO")}
TITLE = {"mike": "MIGHTY MIKE", "stew": "BIG BEEFY STEW", "jim": "JIM \"THE GOAT\"", "niko": "NIMBLE NIKO"}

# billed like the real thing: hometowns, birthdays, tale of the tape, records and specialties
STATS = {
    "mike": [("FROM", "THE IRON DUNGEON"), ("BORN", "7.4.1965"), ("HEIGHT", "5' 7\""), ("WEIGHT", "244 LB"),
             ("RECORD", "88-1-0"), ("SPECIALTY", "POWERBOMB")],
    "stew": [("FROM", "THE ALL-YOU-CAN-EAT BUFFET"), ("BORN", "11.23.1961"), ("HEIGHT", "6' 8\""),
             ("WEIGHT", "412 LB"), ("RECORD", "71-9-3"), ("SPECIALTY", "RUNNING LARIAT")],
    "jim": [("FROM", "THE TOP OF THE MOUNTAIN"), ("BORN", "2.29.1964"), ("HEIGHT", "6' 5\""), ("WEIGHT", "318 LB"),
            ("RECORD", "99-0-1"), ("SPECIALTY", "SLEEPER HOLD")],
    "niko": [("FROM", "HIGH ABOVE THE CLOUDS"), ("BORN", "9.9.1968"), ("HEIGHT", "7' 1\""), ("WEIGHT", "221 LB"),
             ("RECORD", "64-2-0"), ("SPECIALTY", "DDT")],
}
QUOTE = {"mike": "\"SMALL BODY. BIG POWER!\"", "stew": "\"ALL ABOARD|THE BEEF TRAIN!\"",
         "jim": "\"THE GOAT NEVER SLEEPS...|YOU DO.\"", "niko": "\"FROM UP HERE,|YOU LOOK TINY!\""}

PORT = {k: pt.PORTRAITS[k]() for k in ORDER}
SLOTS = {"mike": (24, 18), "stew": (152, 18), "jim": (24, 120), "niko": (152, 120)}


def hx(c):
    return font._hx(c)


def center(img, y, text, col, shadow=None):
    font.draw_text(img, (SW - font.width(text)) // 2, y, text, col, shadow)


def wrap(text, n):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def select(sel, frame):
    img = Image.new("RGBA", (SW, SH), hx("#000000"))
    d = ImageDraw.Draw(img)
    center(img, 5, "SELECT YOUR WRESTLER", "#F8D878")
    for k in ORDER:
        x, y = SLOTS[k]
        img.alpha_composite(PORT[k], (x, y))
        col = hud.HUD_COL[k] if k == sel else "#FCFCFC"
        for i, line in enumerate(NAME2[k]):
            font.draw_text(img, x + 40 - font.width(line) // 2, y + 76 + i * 9, line, col)
        if k == sel and (frame // 2) % 2 == 0:
            d.rectangle((x - 6, y - 3, x + 85, y + 96), outline=hx("#FCFCFC"), width=2)
    center(img, 226, "A:PICK  S:PROFILE", "#7C7C7C")
    return img


def profile(k, rows_shown=99):
    img = Image.new("RGBA", (SW, SH), hx("#000000"))
    img.alpha_composite(PORT[k], ((SW - pt.PW) // 2, 6))
    center(img, 84, TITLE[k], hud.HUD_COL[k])
    y = 102
    for i, (lab, val) in enumerate(STATS[k]):
        if i >= rows_shown:
            break
        lines = wrap(val, 15)
        font.draw_text(img, 104 - font.width(lab), y, lab, "#FCFCFC")
        font.draw_text(img, 108, y, ":", "#FCFCFC")
        for j, ln in enumerate(lines):
            font.draw_text(img, 124, y + j * 10, ln, "#FCFCFC")
        y += 10 * len(lines) + 3
    if rows_shown > len(STATS[k]):
        qy = max(y + 8, 204 if "|" in QUOTE[k] else 212)
        for j, ln in enumerate(QUOTE[k].split("|")):
            center(img, qy + j * 10, ln, "#F8D878")
    return img


if __name__ == "__main__":
    frames = []
    for k in ORDER:
        for f in range(6):
            frames.append(select(k, f))
    for k in ORDER:
        for f in range(4):
            frames.append(select(k, f))
        for r in range(1, 8):
            frames.append(profile(k, r))
        frames += [profile(k)] * 12
    big = [f.convert("RGB").resize((SW * 3, SH * 3), Image.NEAREST) for f in frames]
    big[0].save(OUT + "select_demo.gif", save_all=True, append_images=big[1:], duration=150, loop=0, disposal=1)
    select("mike", 0).convert("RGB").resize((768, 720), Image.NEAREST).save(OUT + "select_screen.png")
    for k in ORDER:
        profile(k).convert("RGB").resize((768, 720), Image.NEAREST).save(OUT + f"profile_{k}.png")
    print(len(frames))
