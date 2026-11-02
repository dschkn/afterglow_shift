import argparse
import os
from pathlib import Path
import pygame
from .resources import SIZE
from .rendering import canvas, blit
from .audio import Audio
from .scenes.menu import Menu
from .scenes.intro import Intro
from .scenes.bedroom import Bedroom
from .scenes.bridge import Bridge
from .scenes.roy_meeting import RoyMeeting

SCENES = {'menu': Menu, 'intro': Intro, 'bedroom': Bedroom, 'bridge': Bridge, 'roy_meeting': RoyMeeting}


class Game:
    def __init__(self, start='menu', window_size=(432, 768)):
        pygame.init()
        self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        pygame.display.set_caption('Afterglow Shift')
        self.canvas = canvas(SIZE)
        self.clock = pygame.time.Clock()
        self.audio = Audio()
        self.running = True
        self.scene = None
        self.change(start)

    def change(self, name):
        if self.scene is not None:
            self.scene.leave()
        self.scene_name = name
        self.scene = SCENES[name](self)

    def viewport(self):
        w, h = self.window.get_size()
        scale = min(w / SIZE[0], h / SIZE[1])
        vw, vh = max(1, round(SIZE[0] * scale)), max(1, round(SIZE[1] * scale))
        return pygame.Rect((w - vw) // 2, (h - vh) // 2, vw, vh)

    def logical_pos(self, pos):
        rect = self.viewport()
        if not rect.collidepoint(pos):
            return None
        return ((pos[0] - rect.x) * SIZE[0] / rect.w,
                (pos[1] - rect.y) * SIZE[1] / rect.h)

    def handle(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.scene_name == 'menu':
                    self.running = False
                else:
                    self.change('menu')
            elif event.key == pygame.K_m:
                self.audio.toggle()
            elif event.key in (pygame.K_SPACE, pygame.K_RIGHT) and self.scene_name == 'bridge':
                self.scene.holding = True
                self.scene.active_pointer = 'keyboard'
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.scene.activate()
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_SPACE, pygame.K_RIGHT) and hasattr(self.scene, 'pointer_up'):
                self.scene.pointer_up('keyboard')
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if hasattr(self.scene, 'pointer_up'):
                self.scene.pointer_up('mouse')
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # SDL emits synthetic mouse events for touch; process fingers only once.
            if not getattr(event, 'touch', False):
                point = self.logical_pos(event.pos)
                if point is not None:
                    if self.scene_name == 'bridge':
                        self.scene.pointer_down(point, 'mouse')
                    else:
                        self.scene.activate(point)
        elif event.type == pygame.FINGERDOWN:
            w, h = self.window.get_size()
            point = self.logical_pos((event.x * w, event.y * h))
            if point is not None:
                if self.scene_name == 'bridge':
                    self.scene.pointer_down(point, event.finger_id)
                else:
                    self.scene.activate(point)
        elif event.type in (pygame.FINGERUP, getattr(pygame, 'FINGERCANCEL', -999)):
            if hasattr(self.scene, 'pointer_up'):
                self.scene.pointer_up(event.finger_id)
        elif event.type == pygame.WINDOWFOCUSLOST:
            if hasattr(self.scene, 'pointer_up'):
                self.scene.holding = False
                self.scene.active_pointer = None

    def draw(self):
        self.scene.draw(self.canvas)
        self.window.fill((0, 0, 0))
        rect = self.viewport()
        blit(self.window, pygame.transform.scale(self.canvas, rect.size), rect)
        pygame.display.flip()

    def run(self, frames=None, fixed_dt=None, screenshot=None):
        count = 0
        try:
            while self.running and (frames is None or count < frames):
                elapsed = self.clock.tick(60) / 1000
                dt = fixed_dt if fixed_dt is not None else min(elapsed, 0.1)
                for event in pygame.event.get():
                    self.handle(event)
                self.scene.update(dt)
                self.draw()
                count += 1
            if screenshot:
                pygame.image.save(self.canvas, str(screenshot))
        finally:
            self.scene.leave()
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description='Afterglow Shift restored prototype')
    parser.add_argument('--scene', choices=SCENES, default='menu')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--frames', type=int, help='Exit after N frames (smoke test)')
    parser.add_argument('--fixed-dt', type=float, help='Deterministic seconds per frame for QA')
    parser.add_argument('--screenshot', type=Path)
    args = parser.parse_args()
    if args.headless:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
    if args.frames is not None and args.frames < 1:
        parser.error('--frames must be positive')
    if args.fixed_dt is not None and args.fixed_dt <= 0:
        parser.error('--fixed-dt must be positive')
    Game(args.scene).run(args.frames, args.fixed_dt, args.screenshot)
