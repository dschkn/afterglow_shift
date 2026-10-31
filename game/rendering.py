"""Opaque RGB frames and RGBA sprites with explicit SDL2 compositing."""
import pygame


def rgba(surface):
    # Do not inherit the Cocoa display's channel masks through convert_alpha().
    return pygame.image.frombytes(
        pygame.image.tobytes(surface, 'RGBA'), surface.get_size(), 'RGBA')


def canvas(size):
    surface = pygame.Surface(size, depth=24)
    surface.fill((0, 0, 0, 255))
    return surface


def blit(target, source, position):
    # Use SDL2 rather than pygame's default SDL1-style alpha blitter.
    return target.blit(source, position, special_flags=pygame.BLEND_ALPHA_SDL2)
