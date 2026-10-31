import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import pygame
from game.app import Game
from game.resources import config, frame_paths, font


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game.scene.leave()
        pygame.quit()

    def test_complete_flow_and_restart(self):
        g = self.game
        g.scene.activate()
        g.scene.update(0)
        g.scene.activate()
        self.assertEqual(g.scene_name, 'intro')
        g.scene.update(84)
        self.assertTrue(g.scene.ready)
        g.scene.activate()
        self.assertEqual(g.scene.page, 1)
        g.scene.update(54)
        g.scene.activate()
        g.scene.update(3)
        self.assertEqual(g.scene_name, 'bedroom')
        g.scene.update(4)
        self.assertTrue(g.scene.ringing)
        g.scene.activate()
        self.assertTrue(g.scene.answered)
        self.assertEqual(g.audio.effects, [])
        g.scene.activate()
        self.assertEqual(g.scene_name, 'menu')
        g.scene.activate()
        g.scene.update(0)
        g.scene.activate()
        self.assertEqual(g.scene.page, 0)
        self.assertEqual(g.scene.time, 0)

    def test_skip_only_reveals_current_page(self):
        g = self.game
        g.change('intro')
        g.scene.activate()
        self.assertTrue(g.scene.ready)
        self.assertEqual(g.scene.page, 0)
        g.scene.activate()
        self.assertEqual(g.scene.page, 1)
        self.assertEqual(g.scene.page_time, 0)
        g.scene.activate()
        self.assertTrue(g.scene.ready)
        self.assertIsNone(g.scene.exit_time)

    def test_letterbox_and_touch_no_duplicate_mouse(self):
        g = self.game
        g.window = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
        self.assertIsNone(g.logical_pos((0, 350)))
        self.assertAlmostEqual(g.logical_pos((500, 350))[0], 288, delta=1)
        g.change('intro')
        g.handle(pygame.event.Event(pygame.FINGERDOWN, x=0.5, y=0.5))
        self.assertTrue(g.scene.ready)
        g.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(500,350), button=1, touch=True))
        self.assertEqual(g.scene.page, 0)
        g.handle(pygame.event.Event(pygame.FINGERDOWN, x=0.5, y=0.5))
        self.assertEqual(g.scene.page, 1)

    def test_resource_paths_independent_of_cwd_and_all_scenes_draw(self):
        previous = Path.cwd()
        try:
            with TemporaryDirectory() as folder:
                os.chdir(folder)
                for name in ('menu', 'intro', 'bedroom'):
                    self.game.change(name)
                    self.game.scene.update(10)
                    self.game.draw()
        finally:
            os.chdir(previous)

    def test_frames_and_text_fit(self):
        paths = frame_paths('levels/bedroom/assets/frames')
        self.assertEqual([int(p.stem) for p in paths], list(range(39)))
        for page in config('intro')['pages']:
            self.assertLess(180 + (len(page)-1)*50 + 20, 950)
            for line in page:
                self.assertLessEqual(font().size(line)[0], 556, line)

    def test_motion_frame_rate_independent(self):
        self.game.change('intro')
        for _ in range(60):
            self.game.scene.update(1 / 60)
        self.game.scene.draw(self.game.canvas)
        first = pygame.image.tobytes(self.game.canvas, 'RGB')
        self.game.change('intro')
        for _ in range(30):
            self.game.scene.update(1 / 30)
        self.game.scene.draw(self.game.canvas)
        self.assertEqual(first, pygame.image.tobytes(self.game.canvas, 'RGB'))

    def test_no_audio_device(self):
        pygame.mixer.quit()
        self.game.audio.enabled = False
        for name in ('intro', 'bedroom', 'menu'):
            self.game.change(name)
            self.game.scene.update(4)
            self.game.audio.toggle()
            self.game.draw()

    def test_segmented_music_loads_and_plays(self):
        self.game.audio.music('Symmetry.mp3')
        self.assertTrue(pygame.mixer.music.get_busy())
        self.assertIsNotNone(self.game.audio.music_stream)
        self.game.audio.music('street_rain.mp3')
        self.assertTrue(pygame.mixer.music.get_busy())
        self.assertIsNone(self.game.audio.music_stream)

    def test_escape_and_quit(self):
        g = self.game
        g.change('intro')
        g.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertEqual(g.scene_name, 'menu')
        g.handle(pygame.event.Event(pygame.QUIT))
        self.assertFalse(g.running)


if __name__ == '__main__':
    unittest.main()
