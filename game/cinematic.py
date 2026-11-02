"""Timed GIF playback with compressed frame storage and a one-frame surface cache."""
from bisect import bisect_right
from functools import lru_cache
import zlib
import pygame
from PIL import Image
from .resources import ROOT, SIZE
from .rendering import blit


@lru_cache(maxsize=2)
def decode_gif(path):
    frames, ends = [], []
    elapsed = 0.0
    with Image.open(ROOT / path) as gif:
        size = gif.size
        for i in range(gif.n_frames):
            gif.seek(i)  # Pillow applies GIF disposal and compositing.
            elapsed += 1.12 * max(10, gif.info.get('duration', 100)) / 1000
            frames.append(zlib.compress(gif.convert('RGB').tobytes(), 1))
            ends.append(elapsed)
    return size, tuple(frames), tuple(ends)


class CinematicClip:
    def __init__(self, path):
        self.size, self.frames, self.ends = decode_gif(path)
        self.duration = self.ends[-1]
        self.index = None
        self.surface = None

    def frame_index(self, seconds):
        return min(len(self.frames)-1, bisect_right(self.ends, seconds % self.duration))

    def draw(self, target, seconds, progress):
        index = self.frame_index(seconds)
        if self.index != index:
            self.surface = pygame.image.frombytes(zlib.decompress(self.frames[index]), self.size, 'RGB')
            self.index = index
        # Keep the original aspect ratio, with portrait cinematic letterboxing.
        viewport = pygame.Rect(0, 122, SIZE[0], 780)
        zoom = 1 + .025 * max(0, min(1, progress))
        scale = min(viewport.w/self.size[0], viewport.h/self.size[1]) * zoom
        size = tuple(round(v*scale) for v in self.size)
        frame = pygame.transform.scale(self.surface, size)
        target.fill((0, 0, 0))
        previous = target.get_clip()
        target.set_clip(viewport)
        blit(target, frame, frame.get_rect(center=viewport.center))
        target.set_clip(previous)
