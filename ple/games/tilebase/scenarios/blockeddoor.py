import ipdb
import numpy as np
from . import base
from .. import tiles

class BlockedDoor(base.Scenario):

    def __init__(self, rng):
        block_strings = ["GOA", "BM", "AG", "WA", "BU"] #blocks we use
        base.Scenario.__init__(self, rng, block_strings)

    def generate(self):
        w, h = self.rng.uniform(self._min, self._max + 1, size=(2)).astype(int)
        self.map_str = np.zeros([h, w], dtype=object)
        locs = np.where( self.map_str == 0 )
        self.map_str[ locs ] = self.EMPTY_TILE
        
        #select a column as the wall
        col = self.rng.choice(np.arange(w/2, w/2 + 1))
        self.map_str[:, col] = "BU"

        #pick a location for the door
        door = self.rng.randint(0, high=h-1)
        self.map_str[door, col] = "BM"
        self.door_pos = [door, col]

        ranges = [(0, col), (col+1, w-1)]
        side = self.rng.choice([0, 1])
        side = ranges[side]

        pos_h, pos_w = 0, col
        while self.map_str[ pos_h, pos_w ] != self.EMPTY_TILE:
            pos_w = self.rng.randint(side[0], high=side[1])
            pos_h = self.rng.randint(0, high=h-1)

        #random side for agent
        self.map_str[pos_h, pos_w] = "AG"

        #random side for goal
        side = self.rng.choice([0, 1])
        side = ranges[side]
        tries = 0
        while self.map_str[ pos_h, pos_w ] != self.EMPTY_TILE or self._blocking(pos_w, pos_h):
            pos_w = self.rng.randint(side[0], high=side[1])
            pos_h = self.rng.randint(0, high=h-1)
            tries += 1 
            if tries > 30:
                break
            
        self.map_str[pos_h, pos_w] = "GOA"

        #make 20% of remaining blocks randomly water or unmoveable blocks
        empty_blocks = len(np.where( self.map_str == self.EMPTY_TILE )[0])
        num_blocks = empty_blocks*self.percent
        num_placed = 0
        while num_placed < num_blocks:
            tries = 0
            while self._occupied(pos_w, pos_h) or self._blocking(pos_w, pos_h):
                side = self.rng.choice([0, 1])
                side = ranges[side]
                pos_w = self.rng.randint(side[0], high=side[1])
                pos_h = self.rng.randint(0, high=h-1)
                tries += 1

                if tries > empty_blocks:
                    break
            
            if tries > empty_blocks:
                break 

            block = self.rng.choice(["WA", "BU"])
            self.map_str[ pos_h, pos_w ] = block
            num_placed += 1


    def _blocking(self, pos_w, pos_h):
        #if a block were placed in pos_w, pos_h would it stop the level from being completed?
        pos = np.array([pos_h, pos_w])
        pos = np.array([ [1,0], [-1, 0], [0, 1], [0, -1] ]) + pos

        h = np.clip(pos[:, 0], 0, self.map_str.shape[0]-1) #the heights
        w = np.clip(pos[:, 1], 0, self.map_str.shape[1]-1)
        area = self.map_str[(h, w)].tolist()
     
        w_dist = np.absolute(self.door_pos[1]-pos_w)
        if w_dist < 3 and pos_h == self.door_pos[0]: #same level AND its close enough to block 
            return True

        if "BM" in area:
            return True #its blocking a door

        if "BU" in area: #we dont want too many blocks near e/o
            return True

        #checks if this would block the player or door.
        return False

    def info(self):
        return "Info: Visit the Goal.\n"

    def is_complete(self):
        if self.goal_obj.visited: #there is only one goal
            return True
        else:
            return False

    def setup(self, tile_objs):
        self.goal_objs = None 
        for t in tile_objs:
            if isinstance(t, tiles.Goal):
                self.goal_obj = t
                break
