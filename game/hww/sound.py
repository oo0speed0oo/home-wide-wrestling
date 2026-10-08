"""Sound and music, straight from export/sound (made in code from NES voices by export/source/nes_audio.py).

8 effects, reused at other pitches (design doc: Sound):
  blip      menu cursor, password letters, announcer text      blip_mash (higher) mash presses, blip_error
  select    pick an option, PUSH START, password OK, finishers
  hit       punch, stomp      hit_kick (lower) kick      hit_ref_slap (lower, quieter) the ref's count
  slam      slams, throws, powerbomb, suplex, knockdown, dive
  grunt     big hit taken, lifting, getting up: grunt_<who>, pitched per wrestler
  whiff     missed punch or kick      whiff_block (shorter) blocked hit, rope bounce
  bell      match start and end, tap-out
  crowd     cheer after big moves, taunts, kick-outs, the win
Music: menu theme, match theme (faster for the nemesis), win jingle, lose jingle.
M mutes everything.
"""
import os

import pygame

from .settings import EXPORT_DIR

SOUND_DIR = os.path.join(EXPORT_DIR, "sound")
EFFECTS = {
    "blip": "01_blip", "select": "02_select", "hit": "03_hit", "slam": "04_slam", "whiff": "06_whiff",
    "bell": "07_bell", "crowd": "08_crowd", "blip_mash": "blip_mash", "blip_error": "blip_error",
    "kick": "hit_kick", "ref_slap": "hit_ref_slap", "block": "whiff_block",
    "grunt_mike": "grunt_mike", "grunt_stew": "grunt_stew", "grunt_jim": "grunt_jim", "grunt_niko": "grunt_niko",
}
VOLUME = {"blip": 0.35, "crowd": 0.7, "blip_mash": 0.6}
MUSIC = {"menu": "music_1_menu", "match": "music_2_match", "nemesis": "music_2_match_nemesis",
         "win": "music_3_jingle_win", "lose": "music_3_jingle_lose"}
MUSIC_VOLUME = 0.55


def sound_file(name):
    """the .wav (computers), or the .ogg the web copy carries instead (browsers want OGG)."""
    wav = os.path.join(SOUND_DIR, name + ".wav")
    return wav if os.path.exists(wav) else os.path.join(SOUND_DIR, name + ".ogg")


class Sound:
    def __init__(self):
        self.ok = False
        self.muted = False
        self.fx = {}
        self.playing = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(12)
            for name, f in EFFECTS.items():
                s = pygame.mixer.Sound(sound_file(f))
                s.set_volume(VOLUME.get(name, 0.8))
                self.fx[name] = s
            self.ok = True
        except (pygame.error, FileNotFoundError):
            self.ok = False         # no sound card or no files: the game still runs, just quietly

    def play(self, name):
        if self.ok and not self.muted and name in self.fx:
            self.fx[name].play()

    def grunt(self, who):
        self.play(f"grunt_{who}")

    def music(self, name, loop=True):
        """start a track (no restart if it's already playing)."""
        if not self.ok or name == self.playing:
            return
        self.playing = name
        pygame.mixer.music.load(sound_file(MUSIC[name]))
        pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        if self.ok:
            pygame.mixer.music.stop()
        self.playing = None

    def toggle_mute(self):
        self.muted = not self.muted
        if self.ok:
            pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)
            if self.muted:
                pygame.mixer.stop()


class Silent(Sound):
    """for tests and tools: same calls, no sound."""

    def __init__(self):
        self.ok = False
        self.muted = True
        self.fx = {}
        self.playing = None
