"""Bedroom loop and an incoming call answered using the phone's green key."""
import pygame
from .base import Scene
from ..resources import SIZE, config, picture, frame_paths, font
from ..rendering import blit
from ..cinematic import CinematicClip


class Bedroom(Scene):
    PHONE_SIZE = (552, 1196)
    PHONE_X = 12
    PHONE_Y = 210
    RISE_SECONDS = 1.0
    # Coordinates follow the original 736 x 1595 phone sprite.
    GREEN_KEY = pygame.Rect(205, 934, 106, 65)

    def __init__(self, app):
        super().__init__(app)
        self.data = config('bedroom')
        paths = frame_paths('levels/bedroom/' + self.data['frames'])
        if not paths:
            raise FileNotFoundError('Bedroom animation frames are missing')
        self.frames = [picture(p, SIZE) for p in paths]
        repair = picture('levels/bedroom/assets/wall-repair.png', SIZE)
        # Use only the static wall behind the signature; preserve the 39-frame animation.
        patch_rect = pygame.Rect(240, 75, 94, 24)
        for frame in self.frames:
            frame.blit(repair, patch_rect, patch_rect)
        self.phone = picture('levels/bedroom/assets/phone.png', self.PHONE_SIZE)
        self.lcd_font = font(18)
        self.ringing = False
        self.answered = False
        self.voice = None
        self.voice_playing = False
        self.answered_at = None
        self.continue_at = None
        self.call_duration = self.data['cinematic']['silent_duration']
        self.clips = [CinematicClip('levels/bedroom/' + path)
                      for path in self.data['cinematic']['clips']]
        self.app.audio.music('street_rain.mp3', fade_ms=1500)

    @property
    def can_continue(self):
        return self.continue_at is not None and self.time - self.continue_at >= 2.5

    @property
    def phone_progress(self):
        return min(1.0, max(0.0, (self.time - self.data['ring_at']) / self.data.get('phone_slide_seconds', self.RISE_SECONDS)))

    @property
    def phone_rect(self):
        p = self.phone_progress
        eased = 1 - (1 - p) ** 3
        y = round(SIZE[1] + (self.PHONE_Y - SIZE[1]) * eased)
        return pygame.Rect(self.PHONE_X, y, *self.PHONE_SIZE)

    @property
    def answer_rect(self):
        phone = self.phone_rect
        r = self.GREEN_KEY
        return pygame.Rect(phone.x + round(r.x * .75), phone.y + round(r.y * .75),
                           round(r.w * .75), round(r.h * .75))

    def update(self, dt):
        super().update(dt)
        if self.voice_playing and self.voice.get_num_channels() == 0:
            self.voice_playing = False
            self.app.audio.volume(1.0)
        if self.answered_at is not None and self.continue_at is None:
            if self.time-self.answered_at >= self.call_duration:
                self.continue_at = self.time
        if self.time >= self.data['ring_at'] and not self.ringing and not self.answered:
            self.app.audio.effect('nokia_ringtone.mp3', loops=-1, gain=self.data.get('ring_gain', 0.18))
            self.ringing = True

    def activate(self, pos=None):
        if self.can_continue:
            self.app.change('bridge')
            return
        if (not self.ringing or self.answered or self.phone_progress < 1
                or pos is None or not self.answer_rect.collidepoint(pos)):
            return
        self.answered = True
        self.answered_at = self.time
        self.ringing = False
        self.app.audio.stop_effects()
        self.voice = self.app.audio.effect('roy_call.mp3', gain=self.data['voice_gain'])
        if self.voice is not None:
            self.call_duration = self.voice.get_length()
            self.voice_playing = True
            self.app.audio.volume(self.data['voice_background_gain'])

    def _draw_phone_scene(self, target):
        index = int(self.time * self.data['fps']) % len(self.frames)
        blit(target, self.frames[index], (0, 0))
        self.shade(target, 255 * (1 - min(1, self.time / 3)))
        if self.time < self.data['ring_at']:
            return
        rect = self.phone_rect
        blit(target, self.phone, rect)
        # Render without antialiasing and scale by an integer for an LCD pixel grid.
        labels = ['Входящий', 'вызов'] if not self.answered else ['Вызов', 'принят']
        for i, label in enumerate(labels):
            text = self.lcd_font.render(label, False, (44, 52, 28))
            text = pygame.transform.scale(text, (text.get_width()*2, text.get_height()*2))
            x = rect.x + round(371 * .75) - text.get_width() // 2
            blit(target, text, (x, rect.y + 420 + i * 42))
        if not self.answered:
            self.line(target, '[Ответить на звонок]', 300, color=(215, 215, 195))

    def cinematic_state(self):
        settings = self.data['cinematic']
        elapsed = max(0, self.time - self.answered_at)
        first = max(5.4, settings['phone_hold'] + settings['fade_seconds'])
        second = max(first + 7.5, self.call_duration * settings['second_shot_fraction'])
        if self.call_duration > first + 3:
            second = min(second, self.call_duration - 3)
        second = max(first + .8, second)
        stage = 0 if elapsed + 1e-9 < first else (1 if elapsed + 1e-9 < second else 2)
        fade = max(0, 1 - min(abs(elapsed-first), abs(elapsed-second)) / settings['fade_seconds'])
        return elapsed, first, second, stage, fade

    def draw(self, target):
        if self.answered_at is None:
            self._draw_phone_scene(target)
            return
        elapsed, first, second, stage, fade = self.cinematic_state()
        if stage == 0:
            self._draw_phone_scene(target)
        else:
            start = first if stage == 1 else second
            end = second if stage == 1 else max(second+1, self.call_duration)
            self.clips[stage-1].draw(target, elapsed-start, (elapsed-start)/(end-start))
        self.shade(target, round(255*fade))
        if self.can_continue:
            self.line(target, '[ Продолжить ]', 950, color=(214,204,208))
