import pygame
import sys
import math

from pygame.constants import K_w, K_a, K_s, K_d
from creepCommon.primatives import Player, Creep
from random import uniform, choice

class WaterWorld(object):

    def __init__(self, 
        creeps_speed=0.0035, 
        agent_speed=0.009,
        num_creeps=3):

        actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s
        }

        #Required fields
        self.actions = actions #holds actions
        self.score = 0.0
        self.screen = None
        self.clock = None
        self.lives = -1 #doesnt apply
        self.screen_dim = ( 48, 48 )

        #end required

        self.BG_COLOR = (255, 255, 255)
        self.N_CREEPS = num_creeps
        self.CREEP_TYPES = [ "GOOD", "BAD" ]
        self.CREEP_COLORS = [ (40, 140, 40), (150, 95, 95) ]
        self.CREEP_RADII = [ 3, 3 ]
        self.CREEP_REWARD = [ 1, -1 ]
        self.CREEP_LIFE = [ 10, 20 ]
        self.CREEP_SPEED = creeps_speed
        self.AGENT_COLOR = (60, 60, 140)
        self.AGENT_SPEED = agent_speed 
        self.AGENT_RADIUS = 3
        self.AGENT_INIT_POS = (self.screen_dim[0]/2, self.screen_dim[1]/2)

        self.creep_counts = {
            "GOOD": 0,
            "BAD": 0
        }

        self.dx = 0
        self.dy = 0

    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key
                
                self.dx *= 0.9
                self.dy *= 0.9

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
        creep_type = choice([0]*50 + [1]*50) 

        creep = None
        creep_hits = [None]
        pos = ( 0,0 )
        dist = 0.0

        while len(creep_hits) > 0 and dist < 2.0:
            pos = ( 
                int(uniform(self.CREEP_RADII[creep_type]*2.5, self.screen_dim[0]-self.CREEP_RADII[creep_type]*2.5)), 
                int(uniform(self.CREEP_RADII[creep_type]*2.5, self.screen_dim[1]-self.CREEP_RADII[creep_type]*2.5)) 
            )  
            dist = math.sqrt( (self.player.pos.x - pos[0])**2 + (self.player.pos.y - pos[1])**2 )
  
            creep = Creep(
                self.CREEP_COLORS[creep_type], 
                self.CREEP_RADII[creep_type], 
                pos,
                ( choice([-1,1]), choice([-1,1]) ), 
                self.CREEP_SPEED,
                self.CREEP_REWARD[creep_type],
                self.CREEP_TYPES[creep_type], 
                self.screen_dim[0], 
                self.screen_dim[1],
                self.CREEP_LIFE[creep_type]
            )

            creep_hits = pygame.sprite.spritecollide(creep, self.creeps, False) #check if we are hitting another other creeps if it was placed here

        self.creeps.add(creep)

        self.creep_counts[ self.CREEP_TYPES[creep_type] ] += 1

    def getScreenDims(self):
        return self.screen_dim

    def getActions(self):
        return self.actions.values()

    def getScore(self):
        return self.score

    def game_over(self):
        """
            Return bool if the game has 'finished'
        """
        return ( self.creep_counts['GOOD'] == 0 )

    def init(self):
        """
            Starts/Resets the game to its inital state
        """
        self.creep_counts = { "GOOD":0, "BAD":0 }

        self.player = Player(self.AGENT_RADIUS, self.AGENT_COLOR, self.AGENT_SPEED, self.AGENT_INIT_POS, self.screen_dim[0], self.screen_dim[1]) 
        self.player_group = pygame.sprite.Group()
        self.player_group.add( self.player )

        self.creeps = pygame.sprite.Group()

        for i in range(self.N_CREEPS):
            self._add_creep()

        self.score = 0
        self.ticks = 0
        self.lives = -1

    def reset(self):
        self.init()

    def step(self, time_elapsed):
        """
            Perform one step of game emulation.
        """

        self.screen.fill(self.BG_COLOR)

        self._handle_player_events()
        self.player_group.update(self.dx, self.dy, time_elapsed)
        
        hits = pygame.sprite.spritecollide(self.player, self.creeps, True)
        for creep in hits:
            self.creep_counts[creep.TYPE] -= 1
            self.score += creep.reward
            self._add_creep()

        self.creeps.update(time_elapsed)

        self.player_group.draw(self.screen)
        self.creeps.draw(self.screen)

if __name__ == "__main__":
        pygame.init()
        game = WaterWorld()
        game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
        game.clock = pygame.time.Clock()
        game.init()

        while True:
            time_elapsed = game.clock.tick_busy_loop(30)
            game.step(time_elapsed)
            pygame.display.update()