import numpy as np
from cStringIO import StringIO

class Scenario():

    def __init__(self, rng, block_strings, EMPTY_TILE="X"):
        self._max = 10
        self._min = 5
        self.percent = 0.2
        self.map_str = None
        self.rng = rng
        self.EMPTY_TILE = EMPTY_TILE
        self.block_strings = block_strings

        self.generate()

    def generate(self):
        raise NotImplementedError("Please implement generate() method")

    def _occupied(self, pos_w, pos_h):
        pos = self.map_str[ pos_h, pos_w ]
        return pos in self.block_strings

    def toString(self):
        map_str = StringIO()
        np.savetxt(map_str, self.map_str, fmt="%s", newline="\n", delimiter=",")
        return map_str.getvalue()

    def info(self):
        raise NotImplementedError("Please implement info() method")
    
    def is_complete(self):
        raise NotImplementedError("Please implement is_complete() method")

    def setup(self, tiles):
        raise NotImplmentedError("Please implement setup() method")
