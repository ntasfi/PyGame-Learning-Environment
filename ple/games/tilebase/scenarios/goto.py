import numpy as np
import ipdb
from cStringIO import StringIO
from . import base
from .. import tiles

class Goto(base.Scenario):

    def __init__(self, rng):
        block_strings = ["GTA", "AG", "WA", "BU"] #blocks we use
        base.Scenario.__init__(self, rng, block_strings)    

    def generate(self):
        self.goto = None 
        
        w, h = self.rng.uniform(self._min, self._max + 1, size=(2)).astype(int)
        self.map_str = np.zeros([h, w], dtype=object)
        locs = np.where(self.map_str == 0)
        self.map_str[locs] = self.EMPTY_TILE
        
        pos_h, pos_w = self.rng.randint(0, high=np.min([w,h])-1, size=(2))
        while self.map_str[pos_h, pos_w] != self.EMPTY_TILE:
            pos_w = self.rng.randint(0, high=w-1)
            pos_h = self.rng.randint(0, high=h-1)

        #random side for agent
        self.map_str[pos_h, pos_w] = "AG"
        
        pos_h, pos_w = self.rng.randint(0, high=np.min([w,h])-1, size=(2))
        while self.map_str[pos_h, pos_w] != self.EMPTY_TILE:
            pos_w = self.rng.randint(0, high=w-1)
            pos_h = self.rng.randint(0, high=h-1)

        self.map_str[pos_h, pos_w] = "GTA"

        #make 20% of remaining blocks randomly water or unmoveable blocks
        empty_blocks = len(np.where( self.map_str == self.EMPTY_TILE )[0])
        num_blocks = empty_blocks*self.percent
        num_placed = 0
        while num_placed < num_blocks:
            tries = 0
            while self._occupied(pos_w, pos_h) or self._blocking(pos_w, pos_h):
                pos_w = self.rng.randint(0, high=w-1)
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
       
        if "BU" in area: #we dont want too many blocks near e/o
            return True

        for sq in area:
            if "GOT_" in sq:
                return True

        #checks if this would block the player or door.
        return False

    def info(self):
        info_str = "Info: Go to location [%s, %s]" % (self.goto.x, self.goto.y)
        
        return info_str + ".\n"

    def setup(self, tile_objs):
        for t in tile_objs:
            if isinstance(t, tiles.GotoTarget):
                self.goto = t
                break

    def is_complete(self):
        if self.goto.visited:
            return True

        return False
