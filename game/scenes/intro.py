"""Reconstructed layered city and accumulating narration from the recording."""
import pygame
from .base import Scene
from ..resources import SIZE, config, picture


class Intro(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.data = config('intro')
        self.layers = []
        for layer in self.data['layers']:
            image = picture('levels/intro/' + layer['image'])
            # The reference stretches the landscape layers to the portrait viewport.
            self.layers.append((pygame.transform.scale(image, SIZE), layer['speed']))
        self.page = 0
        self.page_time = 0.0
        self.exit_time = None
        self.app.audio.music('Symmetry.mp3', fade_ms=2500)

    @property
    def ready(self):
        return self.page_time >= len(self.data['pages'][self.page]) * self.data['line_seconds']

    def update(self, dt):
        super().update(dt)
        self.page_time += dt
        if self.exit_time is not None:
            progress = (self.time - self.exit_time) / self.data['fade_seconds']
            self.app.audio.volume(1 - progress)
            if progress >= 1:
                self.app.change('bedroom')

    def activate(self, pos=None):
        if self.exit_time is not None:
            return
        if not self.ready:
            self.page_time = len(self.data['pages'][self.page]) * self.data['line_seconds']
        elif self.page + 1 < len(self.data['pages']):
            self.page += 1
            self.page_time = 0
        else:
            self.exit_time = self.time

    def draw(self, target):
        target.fill((28, 25, 35))
        for image, speed in self.layers:
            # Modulo wrapping never leaves a gap, including after long pauses.
            x = -round((self.time * speed) % image.get_width())
            target.blit(image, (x, 0))
            target.blit(image, (x + image.get_width(), 0))
        self.shade(target, self.data['darkness'], self.data['tint'])
        for i, text in enumerate(self.data['pages'][self.page]):
            age = self.page_time - i * self.data['line_seconds']
            if age >= 0:
                self.line(target, text, 180 + i * 50, min(255, age * 170))
        if round(self.page_time, 6) > 1:
            self.line(target, '[ нажмите чтобы продолжить ]' if self.ready else '[ пропустить ]', 950)
        self.shade(target, 255 * (1 - min(1, self.time / self.data['fade_seconds'])))
        if self.exit_time is not None:
            self.shade(target, 255 * (self.time - self.exit_time) / self.data['fade_seconds'])
