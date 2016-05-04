import ipdb

import sys
import copy
from io import StringIO
import numpy as np

import pygame
from pygame.constants import K_a, K_w, K_s, K_d, K_e

import tiles
from ple.games import base

class Player():

    def __init__(self, pos_init, width, height, color):
        self.pos = list(pos_init)
        width = int(width)
        height = int(height)
       
        image = pygame.Surface((width, height))
        image.fill((0,0,0))
        image.set_colorkey((0,0,0))

        radius = min(width, height)/2

        pygame.draw.circle(
            image,
            color,
            (radius, radius),
            int(radius*0.8),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dx, dy, action, tile_map):
        reward = 0.0

        nx = np.clip(self.pos[0] + dx, 0, tile_map.map_str.shape[1]-1)
        ny = np.clip(self.pos[1] + dy, 0, tile_map.map_str.shape[0]-1)

        obj = tile_map.map_obj[ny, nx]
        obj_prev = tile_map.map_obj[self.pos[1], self.pos[0]]

        #we moved
        if nx != self.pos[0] or ny != self.pos[1]:
            if obj != None:
                allowed, r = obj.on_enter(dx, dy, tile_map)
                if allowed:
                    self.pos[0] = nx
                    self.pos[1] = ny

                reward += r
            else:
                self.pos[0] = nx
                self.pos[1] = ny

            if obj_prev != None:
                reward += obj_prev.on_exit(tile_map)

        #we didnt move
        else:
            #we are on an object
            if obj != None:
                reward += obj.on_top(action, tile_map)

        self.rect.center = (self.pos[0]*tile_map.tile_width, self.pos[1]*tile_map.tile_height)
        
        return reward

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

class TileMap():

    def __init__(self, tile_str, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.tile_objs = {
                "WA": tiles.Water,
                "BU": tiles.BlockUnmoveable,
                "BM": tiles.BlockMoveable,
                "DO_": tiles.Door,
                "SSW_": tiles.SingleSwitch,
                "MSW_": tiles.MultiSwitch,
                "GOA": tiles.Goal, #Goal Active?
                "GOT_": tiles.GoalToggle
        }
       
        self.tile_list = []
        self.empty_tile = "X"
        self.tile_str = tile_str
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

    def init(self):
        tile_str = StringIO( unicode(self.tile_str) )
        self.map_str = np.genfromtxt(tile_str, dtype="str", delimiter=",")
        self.map_obj = self.map_str.astype(object)

        #the rows are the height!
        map_height, map_width = self.map_str.shape
        self.tile_width = self.SCREEN_WIDTH/ float(map_width)
        self.tile_height = self.SCREEN_HEIGHT/ float(map_height)

        self._parse_map()

    def reset(self):
        self.init()

    def _parse_map(self):
        #not sure if its kosher to use numpy like this. makes life easy though
        self.map_obj[ np.where( np.char.find( self.map_str, self.empty_tile) > -1 ) ] = None

        tile_kwargs = {
            "width": self.tile_width,
            "height": self.tile_height,
        }

        if len(self.tile_list) > 0:
            self.tile_list = []

        for block_str in self.tile_objs.keys():
            sel = np.char.find( self.map_str, block_str ) > -1
            locs = np.where( sel )
            n = len(locs[0])
            
            arr = []

            if block_str == "WA":
                reward = -0.2
            else:
                reward = 0.0

            for i in range(n): #locs returns back a tuple
                if block_str in ["MSW_", "SSW_", "DO_", "GOT_"]:
                    num = self.map_str[locs][i].split("_")[1]
                    if len(num) == 0:
                        num = None

                    arr.append(
                        self.tile_objs[block_str](
                            reward,
                            x=locs[1][i], 
                            y=locs[0][i], 
                            toggles=num, 
                            **tile_kwargs
                            ) 
                    )
                else:
                    arr.append(
                        self.tile_objs[block_str](
                            reward, 
                            x=locs[1][i], 
                            y=locs[0][i], 
                            **tile_kwargs
                        )
                    )

            
            self.map_obj[locs] = arr
            self.tile_list.extend(arr)

        agent_loc =  np.where( np.char.find( self.map_str, "AG") > -1 ) 
        self.agent_init = np.hstack(agent_loc) 
        self.agent_init = self.agent_init[::-1] #reverse it
        self.map_obj[ agent_loc ] = None

        self.goals = self.map_obj[ np.where( np.char.find( self.map_str, "GO" ) > -1 ) ].tolist()

    def complete(self):
        #have all the goals been visited?
        if len(self.goals) == 0:
            return False
        else:
            return len([ None for g in self.goals if not g.visited ]) == 0 

class TileBase(base.Game):

    def __init__(self, width=128, height=128, map_str=None):
        actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s,
            "toggle_tile": K_e
        }

        base.Game.__init__(self, width, height, actions=actions)

        self.tile_map = TileMap(
                map_str,
                width,
                height
        )
        
        self.dx, self.dy = 0, 0
        self.action = False

    def _handle_player_events(self):
        self.dx, self.dy = 0, 0
        self.action = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key

                if key == self.actions["left"]:
                    self.dx = -1

                if key == self.actions["right"]:
                    self.dx = 1

                if key == self.actions["up"]:
                    self.dy = -1

                if key == self.actions["down"]:
                    self.dy = 1

                if key == self.actions["toggle_tile"]:
                    self.action = True

    def new_map(self, map_str):
        self.tile_map.tile_str = map_str

    def init(self):
        self.lives = 1
        self.score = 0.0

        self.tile_map.reset()

        self.player = Player(
            self.tile_map.agent_init, 
            self.tile_map.tile_width,
            self.tile_map.tile_height, 
            (235, 20, 20)
        )

    def gameState(self):
        return None

    def game_over(self):
        return self.tile_map.complete()

    def step(self, dt):
        self.screen.fill((255, 255, 255))
        self._handle_player_events()

        self.score += self.rewards["tick"]
        
        self.player.update(self.dx, self.dy, self.action, self.tile_map)
       

        #could be done in pygame group
        #but it does some strange offsetting.
        for tile in self.tile_map.tile_list:
            if self.dx != 0 or self.dy != 0 or self.action != False:
                print tile.toString(self.player.pos[0], self.player.pos[1])
            tile.draw(self.screen)

        self.player.draw(self.screen)

if __name__ == "__main__":
    maps = []
    
    maps.append(u"""
        X,X,X,X,X,X,X,X,X,X
        X,X,AG,X,X,X,X,X,X,X
        X,X,X,X,X,X,X,X,X,X
        X,X,X,X,MSW_X,X,X,X,X,X
        X,X,X,X,X,X,X,X,X,X
        X,X,X,X,MSW_X,X,X,X,X,X
        X,X,X,X,X,X,X,X,X,X
        X,X,X,X,X,X,X,X,X,X
    """)

    maps.append(u"""
        BU,BU,BU,X,GOA,X,BU,BU,BU
        BU,BU,BU,X,X,X,BU,BU,BU
        BU,BU,BU,BU,DO_1,BU,BU,BU,BU
        X,X,BU,X,X,X,BU,X,X
        GOA,X,DO_2,X,MSW_A,AG,DO_4,X,GOA
        X,X,BU,X,X,X,BU,X,X
        BU,BU,BU,BU,DO_3,BU,BU,BU,BU
        BU,BU,BU,X,X,X,BU,BU,BU
        BU,BU,BU,X,GOA,X,BU,BU,BU
    """)

    maps.append(u"""
        X,X,X,X,BU,X,X,X,X,X
        SSW_3,X,WA,WA,BU,X,WA,X,X,X
        X,X,WA,AG,BU,GOA,X,X,X,X
        BU,X,X,X,BU,WA,X,X,X,X
        X,X,WA,X,BU,X,X,X,X,WA
        X,BU,X,X,DO_3,X,X,X,X,WA
    """)

    maps.append(u"""
        X,X,X,WA,X,X,X,X,X,X,X
        X,X,X,X,SSW_1,X,WA,X,X,X,X
        X,X,X,X,X,X,X,X,X,AG,X
        DO_1,BU,BU,BU,BU,BU,BU,BU,BU,BU,BU
        X,X,X,WA,X,X,X,X,X,X,X
        X,WA,X,X,GOA,X,X,X,X,X,X
        X,X,X,X,X,X,X,X,X,X,X
    """)

    maps.append(u"""
        BU,X,AG,BU,GOA,WA,X,X,X,BU
        X,X,BU,X,WA,X,X,X,WA,X
        X,X,BU,BU,WA,X,X,X,X,GOA
        X,X,X,X,X,X,BU,WA,X,GOA
        X,X,X,X,X,BU,X,X,GOA,X
        X,X,X,WA,X,BU,WA,BU,X,BU
        X,X,WA,X,BU,GOA,X,WA,WA,X
    """)

    maps.append(u"""
        AG,X,X,X,BU,GOA,BU
        X,X,X,X,X,BM,DO_2
        X,X,X,X,BU,X,DO_2
        X,X,X,X,BU,X,BU
        SSW_1,X,X,X,DO_3,X,BU
        SSW_3,X,DO_1,DO_1,BU,X,BU
        X,X,DO_1,GOT_3,BU,SSW_2,BU
    """)

    i = 1 
    game = TileBase(width=256, height=224, map_str=maps[i])
    game.rng = np.random.RandomState(24)
    game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.init() 
    tick = 0

    while True:
        dt = game.clock.tick_busy_loop(30)
        if game.game_over():
            i += 1
            game.new_map( maps[i])
            game.reset()

        game.step(dt)
        
        pygame.display.update()
        tick += 1
