import pygame
import sys
import math

import base

from pygame.constants import K_w, K_a, K_s, K_d
from utils.vec2d import vec2d
from utils import percent_round_int
import random

class Food(pygame.sprite.Sprite):

    def __init__(self, pos_init, width, color, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)        

        self.pos = vec2d(pos_init)
        self.color = color

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.width = width

        image = pygame.Surface((width, width))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0,0,0))       
        pygame.draw.rect(
                image,
                color,
                (0, 0, self.width, self.width),
                0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def new_position(self, snake):
        new_pos = snake.body[0].pos
        snake_body = [ s.pos for s in snake.body ]

        while ( new_pos in snake_body ):
            _x = random.randrange(self.width*2, self.SCREEN_WIDTH-self.width*2, self.width)
            _y = random.randrange(self.width*2, self.SCREEN_HEIGHT-self.width*2, self.width)
            new_pos = vec2d((_x, _y))

        self.pos = new_pos
        self.rect.center = (self.pos.x, self.pos.y)    

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

class SnakeSegment(pygame.sprite.Sprite):

    def __init__(self, pos_init, width, color):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.color = color
        self.width = width

        image = pygame.Surface((width, width))
        image.fill((0,0,0))
        image.set_colorkey((0,0,0))
        
        pygame.draw.rect(
                image,
                color,
                (0, 0, self.width, self.width),
                0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def draw(self, screen):
        self.rect.center = (self.pos.x, self.pos.y)
        screen.blit(self.image, self.rect.center)


#basically just holds onto all of them
class SnakePlayer():

    def __init__(self, speed, length, pos_init, width, color, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.dir = vec2d((1, 0))
        self.speed = speed
        self.pos = vec2d(pos_init)
        self.color = color
        self.width = width
        self.length = length
        self.body = []

        #build our body up
        for i in range(self.length):
            self.body.append(
                    #makes a neat "zapping" in effect
                        SnakeSegment( 
                            (self.pos.x - (width)*i, self.pos.y),
                            self.width,
                            tuple([c-100 for c in self.color]) if i == 0 else self.color
                            
                        )
            )
        #we dont add the first few because it cause never actually hit it
        self.body_group = pygame.sprite.Group()
        self.head = self.body[0]

    def update(self, dt):
        for i in range(self.length-1, 0, -1):
            self.body[i].pos = vec2d((
                (0.9*self.body[i-1].pos.x+0.1*self.body[i].pos.x), 
                (0.9*self.body[i-1].pos.y+0.1*self.body[i].pos.y) 
                ))

        self.head.pos.x += self.dir.x*self.speed*dt
        self.head.pos.y += self.dir.y*self.speed*dt

    def grow(self):
        self.length += 1
        add = 100 if self.length % 2 == 0 else -100
        color = (self.color[0]+add, self.color[1], self.color[2]+add)
        last = self.body[-1].pos
        
        self.body.append(
                    SnakeSegment( 
                        (last.x, last.y), #initially off screen?
                        self.width,
                        color
                    )
        )
        if self.length > 7: #we cant actually hit another segment until this point.
            self.body_group.add(self.body[-1])

    def draw(self, screen):
        for b in self.body:
            b.draw(screen)

class Snake(base.Game):

    def __init__(self,
        width=64,
        height=64,
        init_length=3):

        actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s
        }

        base.Game.__init__(self, width, height, actions=actions)
        self.allowed_fps = 30 #strange things happen at 60.

        self.speed = percent_round_int(width, 0.45) 

        self.player_width = percent_round_int(width, 0.05)
        self.food_width = percent_round_int(width, 0.09)
        self.player_color = (100, 255, 100)
        self.food_color = (255, 100, 100)

        self.INIT_POS = (width/2, height/2)
        self.init_length = init_length

        self.BG_COLOR = (25, 25, 25)

    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                
                #left = -1
                #right = 1
                #up = -1
                #down = 1

                if key == self.actions["left"] and self.player.dir.x != 1:
                    self.player.dir = vec2d((-1, 0))

                if key == self.actions["right"] and self.player.dir.x != -1:
                    self.player.dir = vec2d((1, 0))

                if key == self.actions["up"] and self.player.dir.y != 1:
                    self.player.dir = vec2d((0, -1))

                if key == self.actions["down"] and self.player.dir.y != -1:
                    self.player.dir = vec2d((0, 1))

    def getScore(self):
        return self.score

    def game_over(self):
        return self.lives == -1 

    def init(self):
        """
            Starts/Resets the game to its inital state
        """

        self.player = SnakePlayer(
                self.speed, 
                self.init_length, 
                self.INIT_POS, 
                self.player_width, 
                self.player_color, 
                self.width, 
                self.height
        )

        self.food = Food((0,0), 
                self.food_width, 
                self.food_color, 
                self.width, 
                self.height
        )

        self.food.new_position(self.player)

        self.score = 0
        self.ticks = 0
        self.lives = 1

    def step(self, dt):
        """
            Perform one step of game emulation.
        """
        dt /= 1000.0

        self.ticks += 1
        self.screen.fill(self.BG_COLOR)

        hit = pygame.sprite.collide_rect(self.player.head, self.food)
        if hit: #it hit
            self.score += 1
            self.player.grow()
            self.food.new_position(self.player)

        hits = pygame.sprite.spritecollide(self.player.head, self.player.body_group, False)
        if len(hits) > 0:
            self.lives = -1

        x_check = (self.player.head.pos.x < 0) or (self.player.head.pos.x+self.player_width/2 > self.width)
        y_check = (self.player.head.pos.y < 0) or (self.player.head.pos.y+self.player_width/2 > self.height)
        
        if x_check or y_check:
            self.lives = -1

        self._handle_player_events()
        self.player.update(dt)

        self.player.draw(self.screen)
        self.food.draw(self.screen)


if __name__ == "__main__":
        pygame.init()
        game = Snake(width=64, height=64)
        game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
        game.clock = pygame.time.Clock()
        game.init()

        while True:
            if game.game_over():
                game.init()
            
            dt = game.clock.tick_busy_loop(30)
            game.step(dt)
            pygame.display.update()
