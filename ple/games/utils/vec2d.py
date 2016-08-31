import math


class vec2d():

    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def __add__(self, o):
        x = self.x + o.x
        y = self.y + o.y

        return vec2d((x, y))

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y

    def normalize(self):
        norm = math.sqrt(self.x * self.x + self.y * self.y)
        self.x /= norm
        self.y /= norm
