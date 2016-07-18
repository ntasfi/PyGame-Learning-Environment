__author__ = 'Batchu Vishal'
from onBoard import OnBoard
import pygame

'''
This class defines all our walls in the game.
Currently not much is done here, but we can add traps to certain walls such as spiked walls etc to damage the player
'''


class Wall(OnBoard):

    def __init__(self, raw_image, position):
        super(Wall, self).__init__(raw_image, position)

    # Update the ladder image
    def updateImage(self, raw_image):
        self.image = raw_image
        self.image = pygame.transform.scale(self.image, (15, 15))
