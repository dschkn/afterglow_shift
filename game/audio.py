"""One music stream, optional effects; silent devices remain playable."""
import logging
import io
import pygame
from .resources import ROOT


class Audio:
    def __init__(self):
        self.enabled = pygame.mixer.get_init() is not None
        self.muted = False
        self.gain = 1.0
        self.effects = []
        self.music_stream = None

    def music(self, name, fade_ms=0):
        if not self.enabled:
            return
        try:
            path = ROOT / 'assets/audio' / name
            parts = sorted(path.parent.glob(path.name + '.part[0-9][0-9]'))
            if path.is_file():
                pygame.mixer.music.load(str(path))
                self.music_stream = None
            elif parts:
                # Lossless segments keep large assets below the upload API limit.
                stream = io.BytesIO(b''.join(part.read_bytes() for part in parts))
                pygame.mixer.music.load(stream, path.suffix.lstrip('.'))
                self.music_stream = stream
            else:
                raise FileNotFoundError(path)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)
            self.volume(1.0)
        except (pygame.error, FileNotFoundError) as exc:
            logging.warning('Audio unavailable: %s', exc)

    def volume(self, gain):
        self.gain = max(0, min(1, gain))
        if self.enabled:
            pygame.mixer.music.set_volume(0 if self.muted else self.gain)

    def effect(self, name, loops=0):
        if not self.enabled:
            return
        try:
            sound = pygame.mixer.Sound(str(ROOT / 'assets/audio' / name))
            sound.set_volume(0 if self.muted else 0.65)
            sound.play(loops=loops)
            self.effects.append(sound)
        except (pygame.error, FileNotFoundError) as exc:
            logging.warning('Effect unavailable: %s', exc)

    def stop_effects(self):
        for sound in self.effects:
            sound.stop()
        self.effects.clear()

    def toggle(self):
        self.muted = not self.muted
        self.volume(self.gain)
        for sound in self.effects:
            sound.set_volume(0 if self.muted else 0.65)
