import pygame
import sys
import math

import base

from utils import percent_round_int
from pygame.constants import K_w, K_a, K_s, K_d
from primitives import Player, Creep

class WaterWorld(base.Game):
    """
    Based Karpthy's WaterWorld in `REINFORCEjs`_.
    
    .. _REINFORCEjs: https://github.com/karpathy/reinforcejs 

    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    num_creeps : int (default: 3)
        The number of creeps on the screen at once.
    """
    def __init__(self,
        width=48,
        height=48,
        num_creeps=3):

        actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s
        }

        base.Game.__init__(self, width, height, actions=actions)

        self.BG_COLOR = (255, 255, 255)
        self.N_CREEPS = num_creeps
        self.CREEP_TYPES = [ "GOOD", "BAD" ]
        self.CREEP_COLORS = [ (40, 140, 40), (150, 95, 95) ]
        radius = percent_round_int(width, 0.047)
        self.CREEP_RADII = [ radius, radius ]
        self.CREEP_REWARD = [ 1, -1 ]
        self.CREEP_SPEED = 0.25*width 
        self.AGENT_COLOR = (60, 60, 140)
        self.AGENT_SPEED = 0.25*width 
        self.AGENT_RADIUS = radius 
        self.AGENT_INIT_POS = (self.width/2, self.height/2)
        
        self.creep_counts = {
            "GOOD": 0,
            "BAD": 0
        }

        self.dx = 0
        self.dy = 0

    def _handle_player_events(self):
        self.dx = 0
        self.dy = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                
                if key == self.actions["left"]:
                    self.dx -= self.AGENT_SPEED

                if key == self.actions["right"]:
                    self.dx += self.AGENT_SPEED

                if key == self.actions["up"]:
                    self.dy -= self.AGENT_SPEED

                if key == self.actions["down"]:
                    self.dy += self.AGENT_SPEED

    def _add_creep(self):
        #lame way to do weighted selection. Its 50/50 atm.
        creep_type = self.rng.choice([0]*50 + [1]*50) 

        creep = None
        creep_hits = [None]
        pos = ( 0,0 )
        dist = 0.0

        while len(creep_hits) > 0 and dist < 2.0:
            radius = self.CREEP_RADII[creep_type]*3
            pos = ( 
                int(self.rng.uniform(radius, self.width-radius)), 
                int(self.rng.uniform(radius, self.height-radius)) 
            )  
            dist = math.sqrt( (self.player.pos.x - pos[0])**2 + (self.player.pos.y - pos[1])**2 )
  
            creep = Creep(
                self.CREEP_COLORS[creep_type], 
                self.CREEP_RADII[creep_type], 
                pos,
                ( self.rng.choice([-1,1]), self.rng.choice([-1,1]) ), 
                self.CREEP_SPEED,
                self.CREEP_REWARD[creep_type],
                self.CREEP_TYPES[creep_type], 
                self.width, 
                self.height
            )

            creep_hits = pygame.sprite.spritecollide(creep, self.creeps, False) #check if we are hitting another other creeps if it was placed here

        self.creeps.add(creep)

        self.creep_counts[ self.CREEP_TYPES[creep_type] ] += 1

    def getGameState(self):
        """

        Returns
        -------

        dict
            * player x position.
            * player y position.
            * player x velocity.
            * player y velocity.
            * player distance to each creep


        """

        state = {
            "player": {
                "x": self.player.pos.x,
                "y": self.player.pos.y,
                "velocity": {
                    "x": self.player.vel.x,
                    "y": self.player.vel.y
                }
            },
            "creep_dist": {
                "GOOD": [],
                "BAD": []
            }
        }

        for c in self.creeps:
            dist = math.sqrt( (self.player.pos.x - c.pos.x)**2 + (self.player.pos.y - c.pos.y)**2 )
            state["creep_dist"][c.TYPE].append(dist)

        return state

    def getScore(self):
        return self.score

    def game_over(self):
        """
            Return bool if the game has 'finished'
        """
        self.score += self.N_CREEPS/2
        return ( self.creep_counts['GOOD'] == 0 )

    def init(self):
        """
            Starts/Resets the game to its inital state
        """
        self.creep_counts = { "GOOD":0, "BAD":0 }

        self.player = Player(self.AGENT_RADIUS, self.AGENT_COLOR, self.AGENT_SPEED, self.AGENT_INIT_POS, self.width, self.height) 
        self.player_group = pygame.sprite.Group()
        self.player_group.add( self.player )

        self.creeps = pygame.sprite.Group()

        for i in range(self.N_CREEPS):
            self._add_creep()

        self.score = 0
        self.ticks = 0
        self.lives = -1

    def step(self, dt):
        """
            Perform one step of game emulation.
        """
        dt /= 1000.0
        self.screen.fill(self.BG_COLOR)

        self._handle_player_events()
        self.player_group.update(self.dx, self.dy, dt)
        
        hits = pygame.sprite.spritecollide(self.player, self.creeps, True)
        for creep in hits:
            self.creep_counts[creep.TYPE] -= 1
            self.score += creep.reward
            self._add_creep()

        self.creeps.update(dt)
        
        self.player_group.draw(self.screen)
        self.creeps.draw(self.screen)

if __name__ == "__main__":
        import numpy as np

        pygame.init()
        game = WaterWorld(width=256, height=256, num_creeps=8)
        game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
        game.clock = pygame.time.Clock()
        game.rng = np.random.RandomState(24)
        game.init()

        while True:
            dt = game.clock.tick_busy_loop(30)
            game.step(dt)
            pygame.display.update()
