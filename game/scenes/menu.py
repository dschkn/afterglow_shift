import pygame
from .base import Scene
from ..resources import SIZE, picture


class Menu(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.background = picture('assets/menu/background.jpg', SIZE)
        self.buttons = [pygame.Rect(40, 780 + i * 60, 260, 55) for i in range(3)]
        self.settings = False
        self.music_started = False

    def update(self, dt):
        super().update(dt)
        if self.time >= 1.5 and not self.music_started:
            self.app.audio.music('afterglow_shift_main.wav')
            self.music_started = True
        if self.music_started:
            self.app.audio.volume(min(1, (self.time - 1.5) / 10))

    def activate(self, pos=None):
        if self.time < 13.5:
            self.time = 13.5
            return
        if self.settings:
            if pos is None or self.buttons[0].collidepoint(pos):
                self.app.audio.toggle()
            elif self.buttons[1].collidepoint(pos):
                self.settings = False
            return
        if pos is None or self.buttons[0].collidepoint(pos):
            self.app.change('intro')
        elif self.buttons[1].collidepoint(pos):
            self.settings = True
        elif self.buttons[2].collidepoint(pos):
            self.app.running = False

    def draw(self, target):
        target.blit(self.background, (0, 0))
        self.shade(target, 255 * (1 - min(1, max(0, (self.time - 1.5) / 10))))
        labels = (['sound: off' if self.app.audio.muted else 'sound: on', 'back']
                  if self.settings else ['new game', 'settings', 'exit'])
        alpha = min(255, max(0, (self.time - 11.5) * 127.5))
        for label, rect in zip(labels, self.buttons):
            text = self.font.render(label, True, (160, 160, 160))
            text.set_alpha(round(alpha))
            target.blit(text, (50, rect.y + 20))
