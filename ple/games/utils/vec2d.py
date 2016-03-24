import math

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

