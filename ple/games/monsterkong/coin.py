__author__ = 'Batchu Vishal'
import pygame
import os
from .onBoard import OnBoard


class Coin(OnBoard):
    """
    This class defines all our coins.
    Each coin will increase our score by an amount of 'value'
    We animate each coin with 5 images
    A coin inherits from the OnBoard class since we will use it as an inanimate object on our board.
    """

    def __init__(self, raw_image, position, _dir):
        OnBoard.__init__(self, raw_image, position)
        self.__coinAnimState = 0  # Initialize animation state to 0
        self.IMAGES = {
            "coin1": pygame.transform.scale(pygame.image.load(os.path.join(_dir, 'assets/coin1.png')), (15, 15)).convert_alpha(),
            "coin2": pygame.transform.scale(pygame.image.load(os.path.join(_dir, 'assets/coin2.png')), (15, 15)).convert_alpha(),
            "coin3": pygame.transform.scale(pygame.image.load(os.path.join(_dir, 'assets/coin3.png')), (15, 15)).convert_alpha(),
            "coin4": pygame.transform.scale(pygame.image.load(os.path.join(_dir, 'assets/coin4.png')), (15, 15)).convert_alpha(),
            "coin5": pygame.transform.scale(pygame.image.load(os.path.join(_dir, 'assets/coin5.png')), (15, 15)).convert_alpha()
        }

    # Update the image of the coin
    def updateImage(self, raw_image):
        self.image = raw_image

    # Animate the coin
    def animateCoin(self):
        self.__coinAnimState = (self.__coinAnimState + 1) % 25
        if self.__coinAnimState / 5 == 0:
            self.updateImage(self.IMAGES["coin1"])
        if self.__coinAnimState / 5 == 1:
            self.updateImage(self.IMAGES["coin2"])
        if self.__coinAnimState / 5 == 2:
            self.updateImage(self.IMAGES["coin3"])
        if self.__coinAnimState / 5 == 3:
            self.updateImage(self.IMAGES["coin4"])
        if self.__coinAnimState / 5 == 4:
            self.updateImage(self.IMAGES["coin5"])
