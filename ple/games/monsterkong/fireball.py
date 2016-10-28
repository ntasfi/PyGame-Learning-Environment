__author__ = 'Erilyth'
import pygame
import math
import os
from .onBoard import OnBoard

'''
This class defines all our fireballs.
A fireball inherits from the OnBoard class since we will use it as an inanimate object on our board.
Each fireball can check for collisions in order to decide when to turn and when they hit a player.
'''


class Fireball(OnBoard):

    def __init__(self, raw_image, position, index, speed, rng, dir):
        super(Fireball, self).__init__(raw_image, position)
        # Set the fireball direction randomly
        self.rng = rng
        self.__direction = int(math.floor(self.rng.rand() * 100)) % 2
        self.index = index
        self.wallsBelow = []
        self.laddersBelow = []

        self.IMAGES = {
            "fireballright": pygame.transform.scale(pygame.image.load(os.path.join(dir, 'assets/fireballright.png')), (20, 20)).convert_alpha(),
            "fireballleft": pygame.transform.scale(pygame.image.load(os.path.join(dir, 'assets/fireballleft.png')), (20, 20)).convert_alpha()
        }
        # The newly spawned fireball is not falling
        self.__fall = 0
        # The speed of a fireball is set
        self.__speed = speed

    # Update the image of a fireball
    def updateImage(self, raw_image):
        self.image = raw_image

    # Getters and Setters for some private variables
    def getSpeed(self):
        return self.__speed

    def setSpeed(self, speed):
        self.__speed = speed

    def getFall(self):
        return self.__fall

    def getDirection(self):
        return self.__direction

    # Moves the fireball in the required direction
    def continuousUpdate(self, wallGroup, ladderGroup):

        # The fireball is falling
        if self.__fall == 1:
            # We move the fireball downwards with speed of self.__speed
            self.update(self.image, "V", self.__speed)
            if self.checkCollision(wallGroup, "V"):
                # We have collided with a wall below, so the fireball can stop
                # falling
                self.__fall = 0
                # Set the direction randomly
                self.__direction = int(math.floor(self.rng.rand() * 100)) % 2

        else:

            # While we are on the ladder, we use a probability of 4/20 to make
            # the fireball start falling
            if self.checkCollision(ladderGroup, "V") and len(
                    self.checkCollision(wallGroup, "V")) == 0:
                randVal = int(math.floor(self.rng.rand() * 100)) % 20
                if randVal < 15:
                    self.__fall = 0
                else:
                    self.__fall = 1

            # We are at the edge of the floor so the fireball starts falling
            if len(self.checkCollision(ladderGroup, "V")) == 0 and len(
                    self.checkCollision(wallGroup, "V")) == 0:
                self.__fall = 1

            # We are moving right, so update the fireball image to the right
            if self.__direction == 0:
                self.update(self.IMAGES["fireballright"], "H", self.__speed)
                # When we hit a wall, we change direction
                if self.checkCollision(wallGroup, "H"):
                    self.__direction = 1
                    self.update(self.image, "H", -self.__speed)

            # We are moving left, so update the fireball image to the left
            else:
                self.update(self.IMAGES["fireballleft"], "H", -self.__speed)
                # When we hit a wall, we change direction
                if self.checkCollision(wallGroup, "H"):
                    self.__direction = 0
                    self.update(self.image, "H", self.__speed)

    # Move the fireball in the required direction with the required value and
    # also set the image of the fireball
    def update(self, raw_image, direction, value):
        if direction == "H":
            self.setPosition(
                (self.getPosition()[0] + value,
                 self.getPosition()[1]))
            self.image = raw_image
        if direction == "V":
            self.setPosition(
                (self.getPosition()[0],
                 self.getPosition()[1] + value))
        self.rect.center = self.getPosition()

    '''
    We check for collisions in the direction in which we are moving if the parameter direction is "H".
    The way we do this is move a little forward in the direction in which we are moving, then check for collisions then move back to the original location
    We check for collisions below the fireball if the parameter direction is "V"
    We do this by moving down a little, then check for collisions then move back up to the original location
    '''

    def checkCollision(self, colliderGroup, direction):
        if direction == "H":
            if self.__direction == 0:
                self.update(self.image, "H", self.__speed)  # Right collision
            if self.__direction == 1:
                self.update(self.image, "H", -self.__speed)  # Left collision
            Colliders = pygame.sprite.spritecollide(self, colliderGroup, False)
            if self.__direction == 0:
                self.update(self.image, "H", -self.__speed)  # Right collision
            if self.__direction == 1:
                self.update(self.image, "H", self.__speed)  # Left collision
        else:
            self.update(self.image, "V", self.__speed)  # Bottom collision
            Colliders = pygame.sprite.spritecollide(self, colliderGroup, False)
            self.update(self.image, "V", -self.__speed)
        return Colliders
