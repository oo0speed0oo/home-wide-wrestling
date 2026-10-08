"""Home Wide Wrestling sound: NES-style chiptune made from the console's own parts.
Two pulse (square) waves, one stepped triangle for bass, one noise channel (15-bit LFSR) for drums and impacts.

8 sound effects (reused with pitch/speed changes) + 3 music tracks.
Run:  python3 nes_audio.py   -> writes WAV files into ./out
"""
import os
import numpy as np
from scipy.io import wavfile

SR = 22050
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# ---------------------------------------------------------------- the four NES voices
def t_of(n):
    return np.arange(n) / SR


def pulse(freq, dur, duty=0.5):
    """square wave; freq may be a number or an array (for pitch sweeps)."""
    n = int(dur * SR)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    ph = np.cumsum(f) / SR
    return np.where((ph % 1.0) < duty, 1.0, -1.0)


def triangle(freq, dur):
    """the NES triangle is a 32-step staircase, not a smooth ramp."""
    n = int(dur * SR)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    ph = (np.cumsum(f) / SR) % 1.0
    tri = 1 - 4 * np.abs(ph - 0.5)          # -1..1
    return np.round(tri * 7.5) / 7.5        # 16 levels


_LFSR = {}


def _lfsr_bits(short):
    key = short
    if key not in _LFSR:
        reg, out = 1, []
        tap = 6 if short else 1
        for _ in range(32767 if not short else 93):
            fb = (reg & 1) ^ ((reg >> tap) & 1)
            reg = (reg >> 1) | (fb << 14)
            out.append(1.0 if reg & 1 else -1.0)
        _LFSR[key] = np.array(out)
    return _LFSR[key]


def noise(rate, dur, short=False):
    """NES noise: an LFSR clocked at `rate` Hz (higher = hissier). short=True gives the metallic mode."""
    n = int(dur * SR)
    r = np.broadcast_to(np.asarray(rate, dtype=float), (n,))
    idx = (np.cumsum(r) / SR).astype(int)
    bits = _lfsr_bits(short)
    return bits[idx % len(bits)]


def env(n, attack=0.002, decay=0.1, sustain=0.0, release=0.0, dur=None):
    """simple volume envelope, stepped to 16 levels like the NES."""
    t = t_of(n)
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    d = sustain + (1 - sustain) * np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-6))
    e = a * d
    if release and dur:
        e *= np.clip((dur - t) / release, 0, 1)
    return np.round(e * 15) / 15


def sweep(f0, f1, dur, curve=1.0):
    n = int(dur * SR)
    x = np.linspace(0, 1, n) ** curve
    return f0 + (f1 - f0) * x


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def save(name, x, peak=0.85):
    os.makedirs(OUT, exist_ok=True)
    m = np.max(np.abs(x)) or 1
    y = (x / m * peak * 32767).astype(np.int16)
    wavfile.write(os.path.join(OUT, name + ".wav"), SR, y)
    return y


def pitch(x, k):
    """play a sound faster/higher (k>1) or slower/lower (k<1): the cheap way NES games reused sounds."""
    idx = np.arange(0, len(x) - 1, k)
    return np.interp(idx, np.arange(len(x)), x)


# ---------------------------------------------------------------- the 8 sound effects
def sfx_blip():
    d = 0.045
    return pulse(sweep(1568, 1760, d), d, 0.5) * env(int(d * SR), decay=0.03)


def sfx_select():
    notes = [(1047, 0.05), (1319, 0.05), (1568, 0.05), (2093, 0.12)]
    return np.concatenate([pulse(f, d, 0.125) * env(int(d * SR), decay=0.08 if d > 0.1 else 0.2) for f, d in notes])


def sfx_hit():
    d = 0.11
    n = int(d * SR)
    crack = noise(sweep(18000, 6000, d), d) * env(n, decay=0.025)
    thump = pulse(sweep(320, 90, d, 0.5), d, 0.25) * env(n, decay=0.04) * 0.8
    return mix(crack, thump)


def sfx_slam():
    d = 0.55
    n = int(d * SR)
    boom = noise(sweep(3000, 400, d, 0.6), d) * env(n, decay=0.14)
    drop = triangle(sweep(160, 38, d, 0.4), d) * env(n, decay=0.2) * 1.2
    smack = noise(22000, 0.03) * env(int(0.03 * SR), decay=0.01)
    return mix(boom, drop, smack)


def sfx_grunt():
    """a gruff 'HUH!': a low buzzy square that bends down, roughed up with a little noise."""
    d = 0.22
    n = int(d * SR)
    f = sweep(210, 140, d, 0.7) * (1 + 0.04 * np.sin(2 * np.pi * 28 * t_of(n)))
    voice = pulse(f, d, 0.25) * env(n, attack=0.01, decay=0.09, sustain=0.2, release=0.06, dur=d)
    breath = noise(5000, d) * env(n, attack=0.005, decay=0.05) * 0.35
    return mix(voice, breath)


def sfx_whiff():
    d = 0.14
    n = int(d * SR)
    return noise(sweep(9000, 1500, d), d) * env(n, attack=0.03, decay=0.05) * 0.6


def sfx_bell():
    """boxing-style bell: two bright tones with a long ring, struck twice."""
    def ding(d=0.7):
        n = int(d * SR)
        return mix(pulse(1319, d, 0.5) * env(n, decay=0.25), pulse(1976, d, 0.125) * env(n, decay=0.15) * 0.6,
                   triangle(659, d) * env(n, decay=0.35) * 0.8)
    a = ding()
    gap = int(0.16 * SR)
    out = np.zeros(gap + len(a))
    out[:len(a)] += a
    out[gap:gap + len(a)] += ding()
    return out


def sfx_crowd():
    """a cheer that swells and fades: noise with wobbling volume (lots of people, not one)."""
    d = 1.8
    n = int(d * SR)
    t = t_of(n)
    swell = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.8
    wobble = 0.75 + 0.25 * np.sin(2 * np.pi * 7.3 * t) * np.sin(2 * np.pi * 3.1 * t + 1)
    roar = noise(sweep(4200, 5200, d), d) * 0.7 + noise(1800, d) * 0.4
    whistle = pulse(2637 + 60 * np.sin(2 * np.pi * 5 * t), d, 0.5) * 0.08 * (t > 0.5) * (t < 1.1)
    return (roar + whistle) * swell * wobble


# ---------------------------------------------------------------- music: a tiny tracker
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "AB": 8, "A": 9,
        "A#": 10, "BB": 10, "B": 11}


def freq(tok):
    tok = tok.upper()
    name, octv = tok[:-1], int(tok[-1])
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octv + 1) - 69) / 12)


def track(line, step, voice, vol=1.0, duty=0.5, stacc=1.0):
    """line: space-separated tokens, one per step. note / '-' hold / '.' rest."""
    toks = line.split()
    out = np.zeros(int(len(toks) * step * SR) + SR)
    i = 0
    while i < len(toks):
        tok = toks[i]
        if tok in ("-", "."):
            i += 1
            continue
        j = i + 1
        while j < len(toks) and toks[j] == "-":
            j += 1
        d = (j - i) * step * stacc
        n = int(d * SR)
        f = freq(tok)
        if voice == "pulse":
            w = pulse(f, d, duty) * env(n, attack=0.004, decay=0.12, sustain=0.55, release=0.02, dur=d)
        else:
            w = triangle(f, d) * np.clip((d - t_of(n)) / 0.01, 0, 1)
        s = int(i * step * SR)
        out[s:s + n] += w * vol
        i = j
    return out


def drums(line, step, vol=1.0):
    """k = kick, s = snare, h = hat, . = nothing."""
    toks = line.split()
    out = np.zeros(int(len(toks) * step * SR) + SR)
    for i, tk in enumerate(toks):
        s = int(i * step * SR)
        if tk == "k":
            d = 0.12
            w = mix(triangle(sweep(130, 45, d, 0.5), d) * env(int(d * SR), decay=0.06) * 1.3,
                    noise(3000, 0.03) * env(int(0.03 * SR), decay=0.01) * 0.5)
        elif tk == "s":
            d = 0.13
            w = noise(9000, d) * env(int(d * SR), decay=0.045)
        elif tk == "h":
            d = 0.03
            w = noise(20000, d, short=True) * env(int(d * SR), decay=0.01) * 0.35
        else:
            continue
        out[s:s + len(w)] += w * vol
    return out


def song(parts, loops=1):
    x = mix(*parts)
    return np.tile(x, loops) if loops > 1 else x


def expand(bars, per):
    """bars of eighth-note tokens -> 16th steps (each eighth = token + hold)."""
    out = []
    for b in bars:
        for tok in b.split():
            out += [tok, "-" if tok not in (".",) else "."]
    return " ".join(out)


# 1. MENU THEME: title, select, password, credits. Heroic, C major.
MENU_MEL = ["C5 - - G4 C5 E5 G5 -", "A5 - G5 E5 - C5 E5 -", "F5 - A5 - C6 - A5 F5", "G5 - - - D5 - G5 -",
            "E5 - G5 - C6 - - B5", "A5 - E5 - A5 - C6 -", "A5 G5 F5 A5 G5 F5 E5 D5", "C5 - - - G4 - - -"]
MENU_HAR = ["E4 G4 E4 G4 E4 G4 E4 G4", "E4 A4 E4 A4 E4 A4 E4 A4", "F4 A4 F4 A4 F4 A4 F4 A4",
            "D4 G4 D4 G4 D4 G4 B4 G4", "E4 G4 E4 G4 E4 G4 E4 G4", "E4 A4 E4 A4 E4 A4 E4 A4",
            "F4 A4 F4 A4 D4 G4 D4 G4", "E4 G4 C5 G4 E4 G4 C5 -"]
MENU_BAS = ["C3 . G3 . C3 . G3 .", "A2 . E3 . A2 . E3 .", "F2 . C3 . F2 . C3 .", "G2 . D3 . G2 . D3 .",
            "C3 . G3 . C3 . G3 .", "A2 . E3 . A2 . E3 .", "F2 . C3 . G2 . D3 .", "C3 . G2 . C3 - - ."]
MENU_DRM = "k . h . s . h . k . k . s . h ."


def music_menu():
    step = 60 / 140 / 4
    mel = track(expand(MENU_MEL, 8), step, "pulse", 0.30, 0.5, 0.92)
    har = track(expand(MENU_HAR, 8), step, "pulse", 0.13, 0.25, 0.6)
    bas = track(expand(MENU_BAS, 8), step, "tri", 0.42)
    drm = drums(" ".join([MENU_DRM] * 8), step, 0.30)
    n = int(len(MENU_MEL) * 16 * step * SR)
    one = mix(mel, har, bas, drm)[:n]
    return np.tile(one, 2)


# 2. MATCH THEME: every match (the nemesis match plays it faster). Driving, A minor.
MATCH_MEL = ["A4 - C5 - E5 - D5 C5", "E5 - D5 C5 D5 - E5 -", "F5 - E5 D5 C5 - A4 -", "G4 - B4 - D5 - G5 -",
             "A5 - G5 E5 - E5 G5 A5", "C6 - B5 A5 G5 - E5 -", "F5 - A5 - F5 E5 D5 C5", "B4 - E5 - G#5 - B5 -"]
MATCH_BAS = ["A2 A3 A2 A3 A2 A3 A2 A3", "A2 A3 A2 A3 G2 G3 G2 G3", "F2 F3 F2 F3 F2 F3 F2 F3",
             "G2 G3 G2 G3 G2 G3 G2 G3", "A2 A3 A2 A3 A2 A3 A2 A3", "A2 A3 A2 A3 G2 G3 G2 G3",
             "F2 F3 F2 F3 F2 F3 F2 F3", "E2 E3 E2 E3 E2 E3 G#2 B2"]
MATCH_HAR = [". E4 . E4 . E4 . E4", ". E4 . E4 . D4 . D4", ". C4 . C4 . C4 . C4", ". D4 . D4 . D4 . D4",
             ". E4 . E4 . E4 . E4", ". E4 . E4 . D4 . D4", ". C4 . C4 . C4 . C4", ". G#4 . G#4 . B4 . B4"]
MATCH_DRM = "k h h h s h k h k h k h s h h h"


def music_match(fast=False):
    bpm = 184 if fast else 160
    step = 60 / bpm / 4
    mel = track(expand(MATCH_MEL, 8), step, "pulse", 0.30, 0.25, 0.9)
    har = track(expand(MATCH_HAR, 8), step, "pulse", 0.12, 0.125, 0.5)
    bas = track(expand(MATCH_BAS, 8), step, "tri", 0.45, stacc=0.8)
    drm = drums(" ".join([MATCH_DRM] * 8), step, 0.32)
    n = int(len(MATCH_MEL) * 16 * step * SR)
    one = mix(mel, har, bas, drm)[:n]
    return np.tile(one, 2)


# 3. JINGLE: a short fanfare. Lose = the same notes in minor, slower and lower.
JINGLE_MEL = "G4 C5 E5 G5 - E5 G5 - C6 - - - - - - -"
JINGLE_BAS = "C3 - - - G2 - - - C3 - - - C2 - - -"
JINGLE_HAR = "E4 E4 G4 C5 - G4 C5 - E5 - - - - - - -"


def minor(line):
    rep = {"E": "EB", "A": "AB", "B": "BB"}
    return " ".join(rep.get(t[:-1], t[:-1]) + t[-1] if t not in ("-", ".") else t for t in line.split())


def music_jingle(lose=False):
    bpm = 90 if lose else 150
    step = 60 / bpm / 4
    mel, har, bas = JINGLE_MEL, JINGLE_HAR, JINGLE_BAS
    if lose:
        mel, har, bas = minor(mel), minor(har), minor(bas)
    parts = [track(mel, step, "pulse", 0.32, 0.5, 0.95), track(har, step, "pulse", 0.14, 0.25, 0.9),
             track(bas, step, "tri", 0.45)]
    if not lose:
        parts.append(drums("k . . . k . . . s . s s k . . .", step, 0.3))
    x = mix(*parts)
    return x[:int((16 * step + 0.4) * SR)]


# ---------------------------------------------------------------- write everything
SFX = {
    # the 8 base sounds
    "01_blip": sfx_blip, "02_select": sfx_select, "03_hit": sfx_hit, "04_slam": sfx_slam,
    "05_grunt": sfx_grunt, "06_whiff": sfx_whiff, "07_bell": sfx_bell, "08_crowd": sfx_crowd,
}
# reuses: the same sound played at another pitch/speed, or backwards
VARIANTS = {
    "blip_mash": ("01_blip", 1.25, False), "blip_error": ("01_blip", 0.45, True),
    "hit_kick": ("03_hit", 0.8, False), "hit_ref_slap": ("03_hit", 0.7, False),
    "whiff_block": ("06_whiff", 1.6, False),
    "grunt_stew": ("05_grunt", 0.78, False), "grunt_mike": ("05_grunt", 1.0, False),
    "grunt_jim": ("05_grunt", 0.9, False), "grunt_niko": ("05_grunt", 1.25, False),
}

if __name__ == "__main__":
    base = {}
    LEVEL = {"01_blip": 0.5, "02_select": 0.5, "05_grunt": 0.7, "06_whiff": 0.7}   # square waves sound loud
    for k, fn in SFX.items():
        base[k] = fn()
        save(k, base[k], LEVEL.get(k, 0.85))
    for k, (src, kk, rev) in VARIANTS.items():
        x = pitch(base[src], kk)
        if rev:
            x = x[::-1]
        if k == "hit_ref_slap":
            x = x * 0.6
        lv = {"blip_mash": 0.5, "blip_error": 0.55, "hit_ref_slap": 0.55, "whiff_block": 0.6}.get(k, 0.7 if "grunt" in k else 0.85)
        save(k, x, lv)
    save("music_1_menu", music_menu(), 0.8)
    save("music_2_match", music_match(), 0.8)
    save("music_2_match_nemesis", music_match(fast=True), 0.8)
    save("music_3_jingle_win", music_jingle(), 0.8)
    save("music_3_jingle_lose", music_jingle(lose=True), 0.8)
    for f in sorted(os.listdir(OUT)):
        sr, y = wavfile.read(os.path.join(OUT, f))
        print(f"{f:32s} {len(y) / sr:6.2f}s")
