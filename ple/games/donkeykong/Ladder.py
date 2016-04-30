__author__ = 'Batchu Vishal'

import pygame
from OnBoard import OnBoard

'''
This class defines all our ladders in the game.
Currently not much is done here, but we can add features such as ladder climb sounds etc here
'''


class Ladder(OnBoard):
    def __init__(self, raw_image, position, rng):
        super(Ladder, self).__init__(raw_image, position)
        self.rng = rng

    # Update the ladder image
    def updateImage(self, raw_image):
        self.image = raw_image
        self.image = pygame.transform.scale(self.image, (15, 15))
