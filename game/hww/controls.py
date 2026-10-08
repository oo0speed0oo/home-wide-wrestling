"""Keyboard: arrows plus A, S, D, with Enter to pause (see the Controls section of the design doc)."""
import pygame

KEYS = {
    "up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
    "a": pygame.K_a, "s": pygame.K_s, "d": pygame.K_d, "start": pygame.K_RETURN,
}


class Controls:
    """Which buttons are held, and which were pressed this frame."""

    def __init__(self):
        self.held = {b: False for b in KEYS}
        self.pressed = set()

    def begin_frame(self):
        self.pressed.clear()

    def handle(self, event):
        if event.type not in (pygame.KEYDOWN, pygame.KEYUP):
            return
        for button, key in KEYS.items():
            if event.key == key:
                down = event.type == pygame.KEYDOWN
                if down and not self.held[button]:
                    self.pressed.add(button)
                self.held[button] = down

    def was_pressed(self, button):
        return button in self.pressed
