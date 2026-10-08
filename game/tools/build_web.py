"""The web version, to play on your website (pygbag: Python + pygame in the browser).

    python game/tools/build_web.py ["Version 1"]

  1. makes a web copy: build_web/home-wide-wrestling/ (main.py, hww/, assets/, export/sprites, export/sound)
  2. pygbag builds it into build_web/home-wide-wrestling/build/web/  (index.html + the game file)
  3. packs "Home Wide Wrestling - Website Upload (<name>).zip" in the main project folder:
        home-wide-wrestling/     the game: upload this folder next to wp-admin, play at YOUR-SITE/home-wide-wrestling/
        extras/embed_snippet.html  to show it inside a WordPress page (Custom HTML block)
        READ ME FIRST.txt
Needs pygbag and soundfile (python -m pip install pygbag soundfile) and an internet connection (pygbag downloads its page template the
first time; players' browsers load pygbag's small Python engine from the internet too).
Try it here first:  python -m pygbag build_web/home-wide-wrestling   then open http://localhost:8000
"""
import os
import shutil
import subprocess
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GAME = os.path.join(ROOT, "game")
SLUG = "home-wide-wrestling"
TITLE = "Home Wide Wrestling"
COPY = os.path.join(ROOT, "build_web", SLUG)
SKIP_DIRS = {"__pycache__", "previews", "tools", "build"}
SIZE_LIMIT_MB = 20

# a black page with the game centred, sharp pixels, nothing scrolling (pygbag's page is grey by default)
PAGE_CSS = """<style>
        html, body { background-color: #000000 !important; overflow: hidden; margin: 0; }
        canvas { image-rendering: pixelated; image-rendering: crisp-edges; }
    </style>"""

EMBED = f"""<!--
  {TITLE}: paste this into your website page (WordPress: a "Custom HTML" block).
  Change the src address to where you uploaded the game (see READ ME FIRST.txt).
-->
<div style="max-width:768px;margin:0 auto;">
  <div style="position:relative;width:100%;padding-top:93.75%;background:#000;">
    <iframe
      src="https://YOUR-SITE/{SLUG}/"
      title="{TITLE}"
      style="position:absolute;inset:0;width:100%;height:100%;border:0;"
      allow="autoplay; fullscreen; gamepad"
      allowfullscreen
      loading="lazy"></iframe>
  </div>
  <p style="text-align:center;font:14px sans-serif;color:#555;">
    Click the game, then: arrow keys move, A punch, S kick, D block / taunt, Enter starts and pauses.
    Best on a computer with a keyboard.
  </p>
</div>
"""

README = f"""{TITLE.upper()} - UPLOAD TO YOUR WORDPRESS SITE
{"=" * (len(TITLE) + 31)}

Inside this zip:

  {SLUG}/        ->  https://YOUR-SITE/{SLUG}/     (the game, ready to go)
  extras/embed_snippet.html                             (to show it inside a page)

Typing that address opens the game straight away (after a few seconds of
"Loading, please wait..." you see a message to click: browsers need one click
before a game may play sound).

HOW TO UPLOAD (easiest: your web host's "File Manager")
  1. Log in to your web hosting control panel (where you manage the site, not
     the WordPress dashboard) and open "File Manager".
  2. Open your website's main folder: the one with wp-admin, wp-content and
     wp-config.php inside (often called public_html, or www, or your domain name).
  3. Upload THIS ZIP into that folder, then right-click it -> "Extract" / "Unzip".
  4. You now have the folder {SLUG} next to wp-admin.
     Delete the zip, this text file and the extras folder from the server if you like.
  5. Type  https://YOUR-SITE/{SLUG}/  in a browser. Done.

  Using an FTP app instead (FileZilla etc.): unzip on your computer first, then
  drag the {SLUG} folder into the main folder (next to wp-admin).

  Note: the normal WordPress "Media" uploader can't do this (it doesn't take
  folders); use the hosting File Manager or FTP.

ADD IT TO YOUR SITE'S MENU (optional)
  WordPress dashboard -> Appearance -> Menus (or the Site Editor) ->
  Custom Links -> URL: https://YOUR-SITE/{SLUG}/  Text: {TITLE}.

SHOW IT INSIDE A PAGE (optional)
  Edit a page -> add a "Custom HTML" block -> paste the code from
  extras/embed_snippet.html -> change https://YOUR-SITE/{SLUG}/ to your address.

GOOD TO KNOW
  - Players must be online; keyboard only, best on a computer.
  - Click the game first so it gets the keys. M turns the sound on and off.
  - Each player's Hall of Fame is kept in their own browser.
  - After an update, upload the new {SLUG} folder over the old one. If players
    still see the old version: Ctrl + Shift + R (Mac: Cmd + Shift + R).
"""


def to_ogg(src, dst):
    """browsers want OGG: every .wav becomes an .ogg (Vorbis), the web copy carries only those.
    The game picks whichever it finds (hww/sound.py)."""
    import soundfile as sf
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not f.endswith(".wav"):
            continue
        data, rate = sf.read(os.path.join(src, f), dtype="float32")
        channels = 1 if data.ndim == 1 else data.shape[1]
        # written a block at a time: one big write of a whole song overflows the stack on Windows
        with sf.SoundFile(os.path.join(dst, f[:-4] + ".ogg"), "w", rate, channels, format="OGG",
                          subtype="VORBIS") as out:
            for i in range(0, len(data), 4096):
                out.write(data[i:i + 4096])


def make_copy():
    """the game folder the browser gets: main.py at the top, with its assets and the exported art and sound."""
    if os.path.exists(COPY):
        shutil.rmtree(COPY)
    for base, dirs, files in os.walk(GAME):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(base, GAME)
        os.makedirs(os.path.join(COPY, rel), exist_ok=True)
        for f in files:
            if not f.endswith((".pyc", ".txt", "_8frames.png")):     # (the exported arena previews aren't used)
                shutil.copy2(os.path.join(base, f), os.path.join(COPY, rel, f))
    shutil.copytree(os.path.join(ROOT, "export", "sprites"), os.path.join(COPY, "export", "sprites"))
    to_ogg(os.path.join(ROOT, "export", "sound"), os.path.join(COPY, "export", "sound"))
    logo = Image.open(os.path.join(GAME, "assets", "screens", "logo.png")).convert("RGBA")
    side = max(logo.size) + 8
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 255))
    sq.alpha_composite(logo, ((side - logo.width) // 2, (side - logo.height) // 2))
    sq.resize((64, 64), Image.NEAREST).save(os.path.join(COPY, "favicon.png"))


def build():
    print("building with pygbag ...", flush=True)
    result = subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", TITLE, COPY],
                            cwd=ROOT, capture_output=True, text=True)
    web = os.path.join(COPY, "build", "web")
    if result.returncode != 0 or not os.path.isfile(os.path.join(web, "index.html")):
        print(result.stdout[-3000:], result.stderr[-3000:])
        raise SystemExit("pygbag could not build the web version (see above).")
    page_path = os.path.join(web, "index.html")
    page = open(page_path, encoding="utf-8").read()
    if "</head>" in page:
        page = page.replace("</head>", f"    {PAGE_CSS}\n</head>", 1)
    open(page_path, "w", encoding="utf-8").write(page)
    return web


def folder_size(path):
    return sum(os.path.getsize(os.path.join(b, f)) for b, _, fs in os.walk(path) for f in fs)


def pack(web, name):
    zpath = os.path.join(ROOT, f"{TITLE} - Website Upload ({name}).zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(web):
            for f in files:
                full = os.path.join(base, f)
                z.write(full, os.path.join(SLUG, os.path.relpath(full, web)).replace("\\", "/"))
        z.writestr("READ ME FIRST.txt", README.replace("\n", "\r\n"))
        z.writestr("extras/embed_snippet.html", EMBED)
    return zpath


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Version 1"
    make_copy()
    web = build()
    mb = folder_size(web) / 1e6
    zpath = pack(web, name)
    print(f"web version: {web}   {mb:.1f} MB" + ("   <- over the limit!" if mb >= SIZE_LIMIT_MB else ""))
    print("upload zip: ", zpath)
    print(f"try it here:  python -m pygbag {os.path.relpath(COPY, ROOT)}   (then open http://localhost:8000)")
