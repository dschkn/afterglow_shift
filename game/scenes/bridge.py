"""Guided cinematic crossing of five foreground bridge sections."""
import bisect
import math
import pygame
from .base import Scene
from ..resources import SIZE, ROOT, config, picture, font
from ..rendering import blit

SECTION_NAMES = (
    "01_bridge_section_01_crane.png",
    "02_bridge_section_02_overhead_catwalk.png",
    "03_bridge_section_03_excavator.png",
    "04_bridge_section_04_tank_complex.png",
    "05_bridge_section_05_tower03_final.png",
)

class Bridge(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.data = config("bridge")
        self.scale = self.data["scale"]
        directory = ROOT / "levels/bridge/assets"
        self.missing = [str(directory / "sections" / n) for n in SECTION_NAMES if not (directory / "sections" / n).exists()]
        self.missing += [str(directory / "parallax" / n) for n in self.data["background_order"] if not (directory / "parallax" / n).exists()]
        self.sections = []
        if not self.missing:
            for name in SECTION_NAMES:
                image = picture("levels/bridge/assets/sections/" + name)
                self.sections.append(pygame.transform.scale(image, (round(image.get_width()*self.scale), round(image.get_height()*self.scale))))
        self.background = []
        if not self.missing:
            speeds = (0, .03, .08, .15, .25, .40, 0)
            for i,name in enumerate(self.data["background_order"]):
                image = picture("levels/bridge/assets/parallax/" + name)
                image = pygame.transform.scale(image, (max(SIZE[0], round(image.get_width()*1.6)), round(image.get_height()*1.6)))
                self.background.append((image,speeds[i]))
        self.route = [tuple(p) for p in self.data["route"]]
        self.route_x = [p[0] for p in self.route]
        self.x = 0.
        self.anim = 0.
        self.holding = False
        self.active_pointer = None
        self.button = pygame.Rect(SIZE[0]-126, SIZE[1]-174, 98, 98)
        self.button_font = font(18)
        self.actor = None
        self.roy = None
        if (directory / "tony_sprites.png").exists():
            self.actor = picture("levels/bridge/assets/tony_sprites.png")
        if (directory / "roy_idle.png").exists():
            self.roy = picture("levels/bridge/assets/roy_idle.png")
        self.app.audio.music("street_rain.mp3", fade_ms=1000)

    def route_y(self,x):
        i = max(0,min(len(self.route)-2,bisect.bisect_right(self.route_x,x)-1))
        x0,y0 = self.route[i]
        x1,y1 = self.route[i+1]
        t = min(1,max(0,(x-x0)/max(1,x1-x0)))
        return y0+(y1-y0)*t

    def pointer_down(self,pos,pointer_id="mouse"):
        if self.button.collidepoint(pos):
            self.holding = True
            self.active_pointer = pointer_id

    def pointer_up(self,pointer_id="mouse"):
        if self.active_pointer == pointer_id:
            self.holding = False
            self.active_pointer = None

    def update(self,dt):
        super().update(dt)
        if self.holding:
            self.x = min(self.data["roy_x"],self.x+self.data["movement_speed"]*dt)
            self.anim += dt
            if self.data["roy_x"]-self.x <= self.data["roy_trigger_distance"]:
                self.holding = False
                self.app.change("roy_meeting")

    def draw(self,target):
        target.fill((23,22,32))
        wx = self.x*self.scale
        cam = max(0,wx-SIZE[0]*.30)
        for image,speed in self.background[:-1]:
            width=image.get_width()
            start=-round(cam*speed)%width
            for j in range(-1,math.ceil(SIZE[0]/width)+2):
                blit(target,image,(start+j*width,250))
        base_y=self.data["deck_y_offset"]
        section_x=0
        for image in self.sections:
            sx=round(section_x-cam)
            if sx+image.get_width()>=0 and sx<SIZE[0]:
                blit(target,image,(sx,base_y))
            section_x += image.get_width()
        px=round(wx-cam)
        py=round(base_y+self.route_y(self.x)*self.scale)
        if self.actor is not None:
            cw=self.actor.get_width()//9
            index=0
            if self.holding:
                slope=self.route_y(min(self.x+18,self.data["roy_x"]))-self.route_y(self.x)
                index=(3+int(self.anim*4)%2) if slope < -3 else (6 if slope > 3 else (1+int(self.anim*5)%2))
            frame=self.actor.subsurface((index*cw,0,cw,self.actor.get_height()))
            target.blit(frame,(px-cw//2,py-frame.get_height()+5))
        else:
            pygame.draw.rect(target,(32,35,43),(px-7,py-28,14,28))
        rx=round(self.data["roy_x"]*self.scale-cam)
        if self.roy is not None and -60<rx<SIZE[0]+60:
            ry=round(base_y+self.route_y(self.data["roy_x"])*self.scale)
            target.blit(self.roy,(rx-self.roy.get_width()//2,ry-self.roy.get_height()+5))
        if self.background:
            haze=self.background[-1][0].copy()
            haze.set_alpha(55)
            target.blit(haze,(0,250))
        if self.missing:
            self.line(target,"BRIDGE ASSETS MISSING",80,color=(230,175,170))
            self.line(target,"See levels/bridge/README.md",118,color=(220,205,205))
        pygame.draw.circle(target,(115,91,104) if self.holding else (57,54,68),self.button.center,49)
        pygame.draw.circle(target,(166,137,148),self.button.center,49,2)
        text=self.button_font.render("ИДТИ",True,(232,222,225))
        target.blit(text,text.get_rect(center=self.button.center))
