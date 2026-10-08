"""Home Wide Wrestling - start here:  python game/main.py

Keys: arrows, A, S, D, Enter.  F11 fullscreen (whole-number scaling, so the pixels stay sharp).  M mutes.
Esc quits.  F3 turns debug on or off (test keys in matches, F2 sprite viewer).

The same file runs the web version (pygbag, game/tools/build_web.py): every frame it hands control back
to the browser with `await asyncio.sleep(0)`. In a browser there's no quitting and no F11 (the page has
its own full-screen button).
"""
import asyncio
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hww import settings  # noqa: E402
from hww.assets import Arenas, Font, SoloSheet  # noqa: E402
from hww.controls import Controls  # noqa: E402
from hww.game import Game  # noqa: E402
from hww.settings import FPS, SCALE, SCREEN_H, SCREEN_W, WEB, WRESTLERS  # noqa: E402
from hww.sound import Sound  # noqa: E402
from hww.viewer import Viewer  # noqa: E402


def present(window, screen):
    """scale the 256x240 screen up by a whole number and centre it."""
    ww, wh = window.get_size()
    k = max(1, min(ww // SCREEN_W, wh // SCREEN_H))
    w, h = SCREEN_W * k, SCREEN_H * k
    window.fill((0, 0, 0))
    window.blit(pygame.transform.scale(screen, (w, h)), ((ww - w) // 2, (wh - h) // 2))
    pygame.display.flip()


async def main():
    pygame.init()
    pygame.display.set_caption("Home Wide Wrestling")
    window = pygame.display.set_mode((SCREEN_W * SCALE, SCREEN_H * SCALE))
    screen = pygame.Surface((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    controls = Controls()
    font = Font()
    sheets = {who: SoloSheet(who) for who in WRESTLERS + ("ref",)}
    arenas = Arenas()
    sound = Sound()
    game = Game(font, sheets, arenas, sound)
    viewer = Viewer(font, sheets, arenas)
    scene = game
    fullscreen = False

    while True:
        controls.begin_frame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                                             and not WEB):
                pygame.quit()
                return
            if event.type != pygame.KEYDOWN:
                controls.handle(event)
                continue
            if event.key == pygame.K_F11 and not WEB:
                fullscreen = not fullscreen
                if fullscreen:
                    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    window = pygame.display.set_mode((SCREEN_W * SCALE, SCREEN_H * SCALE))
            elif event.key == pygame.K_m:
                sound.toggle_mute()
            elif event.key == pygame.K_F3:
                settings.DEBUG = not settings.DEBUG
                pygame.display.set_caption("Home Wide Wrestling" + ("  [DEBUG]" if settings.DEBUG else ""))
                if not settings.DEBUG:
                    scene = game
            elif event.key == pygame.K_F2 and settings.DEBUG:
                scene = viewer if scene is game else game
            else:
                scene.handle_key(event.key)
            controls.handle(event)
        scene.update(controls)
        scene.draw(screen)
        present(window, screen)
        clock.tick(FPS)
        await asyncio.sleep(0)          # the browser's turn (does nothing on a computer)


if __name__ == "__main__":
    asyncio.run(main())
