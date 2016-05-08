import numpy as np
import ipdb
from cStringIO import StringIO

class LightKey():

    def __init__(self, rng, EMPTY_TILE="X"):
        self._max = 10
        self._min = 5

        self.percent = 0.2 #percent of water and unmoveable blocks added
        self.block_strings = ["GOA", "SSW_1", "AG", "WA", "BU"] #blocks we use

        self.map_str = None 
        self.rng = rng
        self.EMPTY_TILE = EMPTY_TILE
        self.generate()

    def generate(self):
        w, h = self.rng.uniform(self._min, self._max + 1, size=(2)).astype(int)
        self.map_str = np.zeros([h, w], dtype=object)
        locs = np.where( self.map_str == 0 )
        self.map_str[ locs ] = self.EMPTY_TILE
        
        #select a column as the wall
        col = self.rng.choice(np.arange(w/2 - 1, w/2 + 1))
        self.map_str[:, col] = "BU"

        #pick a location for the door
        door = self.rng.randint(0, high=h-1)
        self.map_str[door, col] = "DO_1"

        ranges = [(0, col), (col+1, w-1)]
        side = self.rng.choice([0, 1])
        side = ranges[side]

        pos_h, pos_w = 0, col
        while self.map_str[ pos_h, pos_w ] != self.EMPTY_TILE:
            pos_w = self.rng.randint(side[0], high=side[1])
            pos_h = self.rng.randint(0, high=h-1)

        #random side for agent
        self.map_str[pos_h, pos_w] = "AG"

        while self.map_str[ pos_h, pos_w ] != self.EMPTY_TILE:
            pos_w = self.rng.randint(side[0], high=side[1])
            pos_h = self.rng.randint(0, high=h-1)

        #put switch here too
        self.map_str[pos_h, pos_w] = "SSW_1"

        #random side for goal
        side = self.rng.choice([0, 1])
        side = ranges[side]
        while self.map_str[ pos_h, pos_w ] != self.EMPTY_TILE:
            pos_w = self.rng.randint(side[0], high=side[1])
            pos_h = self.rng.randint(0, high=h-1)
        
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

    def _occupied(self, pos_w, pos_h):
        pos = self.map_str[ pos_h, pos_w ]
        return pos in self.block_strings

    def _blocking(self, pos_w, pos_h):
        #if a block were placed in pos_w, pos_h would it stop the level from being completed?
        pos = np.array([pos_h, pos_w])
        pos = np.array([ [1,0], [-1, 0], [0, 1], [0, -1] ]) + pos

        h = np.clip(pos[:, 0], 0, self.map_str.shape[0]-1) #the heights
        w = np.clip(pos[:, 1], 0, self.map_str.shape[1]-1)
        area = self.map_str[(h, w)].tolist()
       
        if "DO_1" in area:
            return True #its blocking a door

        if "BU" in area: #we dont want too many blocks near e/o
            return True

        #checks if this would block the player or door.
        return False

    def toString(self):
        #should be a way better way to do this...
        map_str = StringIO()
        np.savetxt(map_str, self.map_str, fmt="%s", newline="\n", delimiter=",")
        return map_str.getvalue()

    def info(self):
        return "Info: Visit the Goal.\n"

    def is_complete(self, goals):
        if goals[0].visited: #there is only one goal
            return True
        else:
            return False
