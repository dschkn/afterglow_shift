"""Placeholder dialogue after Tony reaches Roy."""
import pygame
from .base import Scene
from ..resources import SIZE
from ..rendering import blit

class RoyMeeting(Scene):
    def __init__(self,app):
        super().__init__(app)
        self.backdrop=app.canvas.copy()
        self.pages=[("РОЙ","Ты пришёл."),("ТОНИ","У тебя десять минут."),("РОЙ","Я рассчитывал на пять.")]
        self.page=0
        self.app.audio.stop_effects()

    def update(self,dt):
        super().update(dt)
        if self.page==0 and self.time>4:self.page=1
        if self.page==1 and self.time>8:self.page=2

    def activate(self,pos=None):
        if self.page<len(self.pages)-1:self.page+=1

    def draw(self,target):
        blit(target,self.backdrop,(0,0))
        veil=pygame.Surface(SIZE,pygame.SRCALPHA)
        veil.fill((8,8,14,125))
        target.blit(veil,(0,0))
        name,words=self.pages[self.page]
        self.line(target,name,760,color=(206,169,174))
        self.line(target,words,815,color=(231,227,221))
