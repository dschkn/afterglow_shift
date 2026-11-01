"""All resource paths are project-relative, never working-directory-relative."""
import json
from pathlib import Path
import pygame
from .rendering import rgba

ROOT = Path(__file__).resolve().parents[1]
SIZE = (576, 1024)


def config(level):
    return json.loads((ROOT / 'levels' / level / 'scene.json').read_text(encoding='utf-8'))


def picture(path, size=None):
    surface = rgba(pygame.image.load(str(ROOT / path)))
    return pygame.transform.scale(surface, size) if size else surface


def font(size=20):
    return pygame.font.Font(str(ROOT / 'assets/fonts/20051.ttf'), size)


def frame_paths(directory):
    return sorted((ROOT / directory).glob('*.gif'), key=lambda p: int(p.stem))
