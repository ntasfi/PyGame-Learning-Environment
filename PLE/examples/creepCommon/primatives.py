import pygame
import math
from random import random

class vec2d():

    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def __add__(self, o):
        x = self.x + o.x
        y = self.y + o.y

        return vec2d((x,y))

    def normalize(self):
        norm = math.sqrt( self.x**2 + self.y**2 )
        self.x /= norm
        self.y /= norm

class PuckCreep(pygame.sprite.Sprite):

    def __init__(self, pos_init, attr, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)        

        self.pos = vec2d(pos_init)
        self.attr = attr
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        image = pygame.Surface((self.attr["radius_outer"]*2, self.attr["radius_outer"]*2))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0,0,0))       
        pygame.draw.circle(
                image,
                self.attr["color_outer"],
                (self.attr["radius_outer"], self.attr["radius_outer"]),
                self.attr["radius_outer"],
                0
        )

        image.set_alpha(int(255*0.75))

        pygame.draw.circle(
                image,
                self.attr["color_center"],
                (self.attr["radius_outer"],self.attr["radius_outer"]),
                self.attr["radius_center"],
                0
        )

        self.vel = vec2d((0,0))
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, ndx, ndy, time_elapsed):
        self.vel.x += ndx * self.attr['speed'] * time_elapsed
        self.vel.y += ndy * self.attr['speed'] * time_elapsed

        self.vel.x = self.vel.x*0.5
        self.vel.y = self.vel.y*0.5

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.pos.x < self.attr["radius_outer"]:
            self.pos.x = self.attr["radius_outer"]
            self.vel.x = 0
            self.vel.y = 0

        if self.pos.x > self.SCREEN_WIDTH-(self.attr["radius_outer"]):
            self.pos.x = self.SCREEN_WIDTH-(self.attr["radius_outer"])
            self.vel.x = 0
            self.vel.y = 0

        if self.pos.y < self.attr["radius_outer"]:
            self.pos.y = self.attr["radius_outer"]
            self.vel.x = 0
            self.vel.y = 0

        if self.pos.y > self.SCREEN_HEIGHT-(self.attr["radius_outer"]):
            self.pos.y = self.SCREEN_HEIGHT-(self.attr["radius_outer"])
            self.vel.x = 0
            self.vel.y = 0

        self.rect.center = (self.pos.x, self.pos.y)    

class Creep(pygame.sprite.Sprite):

    def __init__(self, 
            color, 
            radius, 
            pos_init, 
            dir_init, 
            speed, 
            reward, 
            TYPE,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            life):

        pygame.sprite.Sprite.__init__(self)
        
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.TYPE = TYPE
        self.jitter_speed = 0.003
        self.speed = speed
        self.reward = reward
        self.life = life
        self.radius = radius
        self.pos = vec2d(pos_init)

        self.direction = vec2d(dir_init)
        self.direction.normalize() #normalized
        
        image = pygame.Surface((radius*2, radius*2))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0,0,0))
 
        pygame.draw.circle(
                image,
                color,
                (radius, radius),
                radius,
                0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, time_passed):
        jitter_x, jitter_y = 0, 0
        if self.pos.x-self.radius > self.SCREEN_WIDTH-1 or self.pos.x <= self.radius*3:
            self.direction.x *= -1
            jitter_x = self.jitter_speed*self.direction.x*random()

        if self.pos.y-self.radius > self.SCREEN_HEIGHT-1 or self.pos.y <= self.radius*3:
            self.direction.y *= -1
            jitter_y = self.jitter_speed*self.direction.y*random()

        displacement = vec2d((
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed))

        self.pos += displacement

        self.rect.center = ((
                self.pos.x - self.image.get_size()[0],
                self.pos.y - self.image.get_size()[1]))


class Wall(pygame.sprite.Sprite):

    def __init__(self, pos, w, h):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos)
        self.w = w
        self.h = h
        
        image = pygame.Surface([w, h])
        image.fill( (10, 10, 10) )
        self.image = image.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = pos

    def draw(self, screen):
        pygame.draw.rect(screen, (10, 10, 10), [self.pos.x, self.pos.y, self.w, self.h], 0)

class Player(pygame.sprite.Sprite):

    def __init__(self, 
            radius, 
            color, 
            speed, 
            pos_init,
            SCREEN_WIDTH,
            SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)
        
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
 
        self.pos = vec2d(pos_init)
        self.vel = vec2d((0,0))

        image = pygame.Surface([radius*2, radius*2])
        image.set_colorkey((0,0,0))
        
        pygame.draw.circle(
                image,
                color,
                (radius, radius),
                radius,
                0
        )
        
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect()
        self.radius = radius

    def update(self, dx, dy, time_passed):
        self.vel.x += dx
        self.vel.y += dy

        self.vel.x = self.vel.x*0.9
        self.vel.y = self.vel.y*0.9

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.pos.x < 0.0:
            self.pos.x = 0.0

        if self.pos.y < 0.0:
            self.pos.y = 0.0

        if self.pos.x < self.radius:
            self.pos.x = self.radius
            self.vel.x = 0
            self.vel.y = 0

        if self.pos.x > self.SCREEN_WIDTH-(self.radius):
            self.pos.x = self.SCREEN_WIDTH-(self.radius)
            self.vel.x = 0
            self.vel.y = 0

        if self.pos.y < self.radius:
            self.pos.y = self.radius
            self.vel.x = 0
            self.vel.y = 0

        if self.pos.y > self.SCREEN_HEIGHT-(self.radius):
            self.pos.y = self.SCREEN_HEIGHT-(self.radius)
            self.vel.x = 0
            self.vel.y = 0

        self.rect.center = (self.pos.x, self.pos.y)     

