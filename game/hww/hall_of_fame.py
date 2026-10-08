"""The Hall of Fame: the top 5 scores with full names (up to 10 letters), kept between games.

Saved in the user's own folder (%APPDATA%\\HomeWideWrestling on Windows) so it survives a rebuilt game.
In a browser it's kept in that browser's own storage for the site (each player has their own).
"""
import json
import os

from .settings import WEB

STORAGE_KEY = "hww_hall_of_fame"


def web_storage():
    import platform as web     # pygbag's bridge to the page: platform.window is the browser's window
    return web.window.localStorage

SIZE = 5
NAME_LEN = 10
# who's on the board before anyone has played
DEFAULT = [("MIKE", "mike", 48300), ("STEW", "stew", 41900), ("JIM", "jim", 37200), ("NIKO", "niko", 30100),
           ("BFG", "mike", 10000)]


def save_dir():
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "HomeWideWrestling")


class HallOfFame:
    def __init__(self, path=None):
        self.path = path or os.path.join(save_dir(), "hall_of_fame.json")
        self.entries = self.load()

    def load(self):
        try:
            if WEB:
                text = web_storage().getItem(STORAGE_KEY)
                data = json.loads(text) if text else []
            else:
                data = json.load(open(self.path))
            entries = [(str(n)[:NAME_LEN], w, int(s)) for n, w, s in data][:SIZE]
            return entries if entries else list(DEFAULT)
        except Exception:
            return list(DEFAULT)

    def save(self):
        try:
            if WEB:
                web_storage().setItem(STORAGE_KEY, json.dumps(self.entries))
                return
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            json.dump(self.entries, open(self.path, "w"))
        except Exception:       # a read-only disk or a private browser window: the scores just don't stick
            pass

    def qualifies(self, score):
        return score > 0 and (len(self.entries) < SIZE or score > self.entries[-1][2])

    def add(self, name, who, score):
        """put a new score in its place; returns its rank (0 = 1ST)."""
        self.entries.append((name[:NAME_LEN] or "???", who, score))
        self.entries.sort(key=lambda e: -e[2])
        rank = next(i for i, e in enumerate(self.entries) if e == (name[:NAME_LEN] or "???", who, score))
        self.entries = self.entries[:SIZE]
        self.save()
        return rank
