"""Recovered 39-frame bedroom loop; phone is a prototype endpoint."""
from ..rendering import blit, rgba
from .base import Scene
from ..resources import SIZE, config, picture, frame_paths


class Bedroom(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.data = config('bedroom')
        paths = frame_paths('levels/bedroom/' + self.data['frames'])
        if not paths:
            raise FileNotFoundError('Bedroom animation frames are missing')
        self.frames = [picture(p, SIZE) for p in paths]
        self.phone = picture('levels/bedroom/assets/phone.png', (180, 390))
        self.ringing = False
        self.answered = False
        self.app.audio.music('street_rain.mp3', fade_ms=1500)

    def update(self, dt):
        super().update(dt)
        if self.time >= self.data['ring_at'] and not self.ringing and not self.answered:
            self.app.audio.effect('nokia_ringtone.mp3', loops=-1)
            self.ringing = True

    def activate(self, pos=None):
        if self.time < self.data['prompt_at']:
            return
        if self.answered:
            self.app.change('menu')
        else:
            self.answered = True
            self.app.audio.stop_effects()

    def draw(self, target):
        index = int(self.time * self.data['fps']) % len(self.frames)
        blit(target, self.frames[index], (0, 0))
        self.shade(target, 255 * (1 - min(1, self.time / 3)))
        if self.answered:
            self.shade(target, 150)
            blit(target, self.phone, (198, 280))
            self.line(target, 'конец восстановленного фрагмента', 730)
            self.line(target, '[ нажмите, чтобы вернуться в меню ]', 850)
        elif self.time >= self.data['prompt_at']:
            self.line(target, '[ ответить на звонок ]', 924)
