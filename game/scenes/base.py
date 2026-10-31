from ..rendering import blit, rgba
import pygame
from ..resources import SIZE, font


class Scene:
    def __init__(self, app):
        self.app = app
        self.time = 0.0
        self.font = font()

    def update(self, dt):
        self.time += dt

    def activate(self, pos=None):
        pass

    def leave(self):
        self.app.audio.stop_effects()

    def line(self, target, text, y, alpha=255, color=(160, 160, 160)):
        # The original pixel font lacks typographic quotes and long dashes.
        text = text.replace('«', '[').replace('»', ']').replace('—', '-').replace('–', '-')
        rendered = rgba(self.font.render(text, True, color))
        rendered.set_alpha(max(0, min(255, round(alpha))))
        blit(target, rendered, ((SIZE[0] - rendered.get_width()) // 2, y))

    @staticmethod
    def shade(target, alpha, color=(0, 0, 0)):
        alpha = max(0, min(255, round(alpha)))
        if alpha == 0:
            return
        overlay = pygame.Surface(SIZE, pygame.SRCALPHA, 32)
        overlay.fill((*color, alpha))
        blit(target, overlay, (0, 0))
