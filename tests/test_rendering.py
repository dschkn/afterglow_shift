"""Pixel-level regressions: glyphs, backgrounds and an opaque final frame."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
import pygame
from game.app import Game
from game.rendering import canvas, blit
from game.scenes.base import Scene


class RenderingTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game.scene.leave()
        pygame.quit()

    def test_text_fade_has_visible_glyphs_without_black_rectangle(self):
        for alpha in (0, 128, 255):
            target = canvas((576, 1024))
            target.fill((40, 50, 60, 255))
            self.game.scene.line(target, 'Этот город', 180, alpha)
            pixels = [target.get_at((x, y)) for x in range(220, 360) for y in range(180, 204)]
            self.assertTrue(all(p.a == 255 for p in pixels))
            self.assertTrue(all(p.r >= 40 and p.g >= 50 and p.b >= 60 for p in pixels))
            self.assertEqual(any(p.r > 40 for p in pixels), alpha > 0)

    def test_zero_shade_does_not_erase_scene(self):
        target = canvas((576, 1024))
        target.fill((120, 100, 80, 255))
        before = pygame.image.tobytes(target, 'RGBA')
        Scene.shade(target, 0)
        self.assertEqual(before, pygame.image.tobytes(target, 'RGBA'))
        Scene.shade(target, 128)
        pixel = target.get_at((100, 100))
        self.assertEqual(pixel.a, 255)
        self.assertTrue(55 <= pixel.r <= 65)

    def test_each_scene_survives_scaling_and_rgba_display_composition(self):
        for name, seconds in [('menu', 15), ('intro', 20), ('bedroom', 5)]:
            self.game.change(name)
            self.game.scene.update(seconds)
            self.game.draw()
            raw = pygame.image.tobytes(self.game.canvas, 'RGBA')
            self.assertEqual(set(raw[3::4]), {255}, name)
            # Sample upper background away from all text/buttons.
            colors = {tuple(self.game.canvas.get_at((x,y))[:3])
                      for x in range(0, 576, 8) for y in range(0, 160, 8)}
            self.assertGreater(len(colors), 3, name)
            display = pygame.Surface((432, 768), pygame.SRCALPHA, 32)
            display.fill((0, 0, 0, 255))
            blit(display, pygame.transform.scale(self.game.canvas, display.get_size()), (0, 0))
            self.assertEqual(set(pygame.image.tobytes(display, 'RGBA')[3::4]), {255}, name)
