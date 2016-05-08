import ipdb

import sys
import math
import pygame
import importlib

from io import StringIO
import numpy as np
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

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, map_str=None, scenario=None):
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
        self.EMPTY_TILE = "X"
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.scenario = scenario

        if self.scenario is not None:
            self.raw_str = scenario.toString()
        elif map_str is not None:
            self.raw_str = map_str
        else:
            raise ValueError("Scenario object or map_str must be given.")

    def init(self):
        tile_str = StringIO( unicode(self.raw_str) )
        self.map_str = np.genfromtxt(tile_str, dtype="str", delimiter=",")
        self.map_obj = self.map_str.astype(object)

        #the rows are the height!
        map_height, map_width = self.map_str.shape
        self.tile_width = math.ceil( self.SCREEN_WIDTH/ float(map_width) )
        self.tile_height = math.ceil( self.SCREEN_HEIGHT/ float(map_height) ) #ceil so it fills the screen

        self._parse_map()
       
        #let the scenario do any setup if needed
        if self.scenario is not None:
            self.scenario.setup(self.tile_list)

    def reset(self):
        if self.scenario is not None:
            self.scenario.generate()
            self.raw_str = self.scenario.toString()

        self.init()

    def _parse_map(self):
        #not sure if its kosher to use numpy like this. makes life easy though
        self.map_obj[ np.where( np.char.find( self.map_str, self.EMPTY_TILE) > -1 ) ] = None

        tile_kwargs = {
            "width": self.tile_width,
            "height": self.tile_height,
        }

        reward = 0.0

        if len(self.tile_list) > 0:
            self.tile_list = []

        for block_str in self.tile_objs.keys():
            sel = np.char.find( self.map_str, block_str ) > -1
            locs = np.where( sel )
            n = len(locs[0])
            
            arr = []

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

        #always add corners as they are used in all tasks.
        height, width = self.map_str.shape
        height, width = height - 1, width - 1
        corners = [[0,0], [width, 0], [0, height], [width, height]]
        for c in corners:
            self.tile_list.append( tiles.Corner(0.0, x=c[0], y=c[1]) )

        self.map_goal_obj = self.map_obj[ np.where( np.char.find( self.map_str, "GO" ) > -1 ) ].tolist()
        
        if len(self.map_goal_obj) == 0:
            raise Warning("No goal objects were created. The map will never end")

    def info(self):
        if len(self.map_goal_obj) == 0:
            return "Info: No goals given.\n"
        
        if self.scenario is None:
            return "Info: Visit all the goals.\n"
        else:
            return self.scenario.info()

    def complete(self):
        if self.scenario is None and len(self.map_goal_obj) > 0:
            return len([ None for g in self.map_goal_obj if not g.visited ]) == 0 
        elif self.scenario is not None: #scenario obj was passed
            return self.scenario.is_complete() 
        else:
            raise Warning("No goal objects were created. The map will never end.")

class TileBase(base.Game):

    def __init__(self, map_str=None, scenario=None, width=128, height=128):
        actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s,
            "toggle_tile": K_e
        }

        base.Game.__init__(self, width, height, actions=actions)

        self.map_str = map_str
        self.scenario = scenario
        self.tile_map = None

        self.dx, self.dy = 0, 0
        self.toggle_action = False

    def init_tilemap(self):
        if self.scenario is not None and isinstance(self.scenario, str):
            try:
                ipdb.set_trace()
                scenario = getattr(
                        importlib.import_module(
                            "scenarios.%s" % self.scenario.lower()
                            ), self.scenario
                        )
            except ImportError:
                raise ValueError("scenario %s not found." % self.scenario)
            scenario = scenario(self.rng)
            self.tile_map = TileMap(
                    self.width,
                    self.height,
                    scenario=scenario
            )
        elif map_str is not None: 
            self.tile_map = TileMap(
                    self.width,
                    self.height,
                    map_str=map_str
            )
        else:
            raise ValueError("Need map_str or a scenario name specified.")

    def _handle_player_events(self):
        self.dx, self.dy = 0, 0
        self.toggle_action = False

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
                    self.toggle_action = True

    def new_map(self, scenario=None, map_str=None, map_obj=None):
        self._init(scenario=scenario, map_str=map_str, map_obj=map_obj)

    def init(self):
        self.lives = 1
        self.score = 0.0

        if self.tile_map is None:
            self.init_tilemap()

        self.tile_map.reset()

        self.player = Player(
            self.tile_map.agent_init, 
            self.tile_map.tile_width,
            self.tile_map.tile_height, 
            (235, 20, 20)
        )

    def getGameState(self):
        return_str = ""
        for tile in self.tile_map.tile_list:
            if self.dx != 0 or self.dy != 0 or self.toggle_action != False:
                return_str += tile.toString(self.player.pos[0], self.player.pos[1])

        if self.tile_map.map_obj is None:
            return_str += "Info: Visit all the Goals.\n" #default assumption

        if len(return_str) > 0:
            return return_str
        else:
            return None

    def game_over(self):
        return self.tile_map.complete()

    def step(self, dt):
        self.screen.fill((255, 255, 255))
        self._handle_player_events()

        self.score += self.rewards["tick"]
        
        self.player.update(self.dx, self.dy, self.toggle_action, self.tile_map)
       

        #could be done in pygame group
        #but it does some strange offsetting.
        for tile in self.tile_map.tile_list:
            tile.draw(self.screen)

        self.player.draw(self.screen)

if __name__ == "__main__":
    maps = []
    objs = []

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
    objs.append([])

    maps.append(u"""
        BU,BU,BU,X,GOT_1,X,BU,BU,BU
        BU,BU,BU,X,X,X,BU,BU,BU
        BU,BU,BU,BU,DO_1,BU,BU,BU,BU
        X,X,BU,X,X,X,BU,X,X
        GOT_2,X,DO_2,X,MSW_A,AG,DO_4,X,GOT_4
        X,X,BU,X,X,X,BU,X,X
        BU,BU,BU,BU,DO_3,BU,BU,BU,BU
        BU,BU,BU,X,X,X,BU,BU,BU
        BU,BU,BU,X,GOT_3,X,BU,BU,BU
    """)
    objs.append(["GOT_4", "GOT_2", "GOT_3", "GOT_1"])

    maps.append(u"""
        X,X,X,X,BU,X,X,X,X,X
        SSW_3,X,WA,WA,BU,X,WA,X,X,X
        X,X,WA,AG,BU,GOA,X,X,X,X
        BU,X,X,X,BU,WA,X,X,X,X
        X,X,WA,X,BU,X,X,X,X,WA
        X,BU,X,X,DO_3,X,X,X,X,WA
    """)
    objs.append([])

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

    game = TileBase(width=256, height=224, scenario="LightKey")
    game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init() 
    tick = 0

    while True:
        dt = game.clock.tick_busy_loop(30)
        if game.game_over():
            game.reset()

        game.step(dt)
        state = game.getGameState() 
        if state is not None:
            print state

        if tick%30 == 0:
            game.reset()

        tick += 1
        pygame.display.update()
