__author__ = 'Erilyth'
import pygame
from Person import Person
import random

'''
This class defines all the Donkey Kongs present in our game.
Each donkey kong can only move on the top floor and cannot move vertically.
'''


class DonkeyKong(Person):
    def __init__(self, raw_image, position):
        super(DonkeyKong, self).__init__(raw_image, position)
        self.__speed = 2
        self.__direction = int(random.random() * 100) % 2
        self.__cycles = 0
        self.__stopDuration = 0

    # Getters and Setters
    def getSpeed(self):
        return self.__speed

    def setSpeed(self):
        return self.__speed

    def getStopDuration(self):
        return self.__stopDuration

    def setStopDuration(self, stopDuration):
        self.__stopDuration = stopDuration

    # Checks for collisions with walls in order to change direction when hit by a wall
    def checkWall(self, colliderGroup):
        if self.__direction == 0:
            self.updateWH(self.image, "H", 20, 40, 40)  # Right collision with wall
        if self.__direction == 1:
            self.updateWH(self.image, "H", -20, 40, 40)  # Left collision with wall
        Colliders = pygame.sprite.spritecollide(self, colliderGroup, False)
        if self.__direction == 0:
            self.updateWH(self.image, "H", -20, 40, 40)  # Right collision with wall
        if self.__direction == 1:
            self.updateWH(self.image, "H", 20, 40, 40)  # Left collision with wall
        return Colliders

    # This is used to animate the donkey kong
    def continuousUpdate(self, GroupList, GroupList2):

        # If the stop duration is 0 then kong is currently moving either left or right
        if self.__stopDuration == 0:

            # Currently moving right
            if self.__direction == 0:
                self.__cycles += 1
                if self.__cycles % 24 < 6:
                    self.updateWH(pygame.image.load('Assets/kong0.png'), "H", self.__speed, 40, 40)
                elif self.__cycles % 24 < 12:
                    self.updateWH(pygame.image.load('Assets/kong1.png'), "H", self.__speed, 40, 40)
                elif self.__cycles % 24 < 18:
                    self.updateWH(pygame.image.load('Assets/kong2.png'), "H", self.__speed, 40, 40)
                else:
                    self.updateWH(pygame.image.load('Assets/kong3.png'), "H", self.__speed, 40, 40)
                if self.checkWall(GroupList):
                    self.__direction = 1
                    self.__cycles = 0
                    self.updateWH(self.image, "H", -self.__speed, 40, 40)

            # Currently moving left
            else:
                self.__cycles += 1
                if self.__cycles % 24 < 6:
                    self.updateWH(pygame.image.load('Assets/kong01.png'), "H", -self.__speed, 45, 45)
                elif self.__cycles % 24 < 12:
                    self.updateWH(pygame.image.load('Assets/kong11.png'), "H", -self.__speed, 45, 45)
                elif self.__cycles % 24 < 18:
                    self.updateWH(pygame.image.load('Assets/kong21.png'), "H", -self.__speed, 45, 45)
                else:
                    self.updateWH(pygame.image.load('Assets/kong31.png'), "H", -self.__speed, 45, 45)
                if self.checkWall(GroupList):
                    self.__direction = 0
                    self.__cycles = 0
                    self.updateWH(self.image, "H", self.__speed, 45, 45)

        # Donkey Kong is currently not moving, which means he is launching a fireball
        else:
            self.__stopDuration -= 1
            if self.__stopDuration == 0:  # Once he finishes launching a fireball, we go back to our normal movement animation
                self.updateWH(self.image, "V", 12, 50, 50)
            if self.__stopDuration >= 10:
                if self.__direction == 0:
                    self.updateWH(pygame.image.load('Assets/kongstill0.png'), "H", 0, 50, 50)
                else:
                    self.updateWH(pygame.image.load('Assets/kongstill10.png'), "H", 0, 50, 50)
            elif self.__stopDuration >= 5:
                if self.__direction == 0:
                    self.updateWH(pygame.image.load('Assets/kongstill1.png'), "H", 0, 50, 50)
                else:
                    self.updateWH(pygame.image.load('Assets/kongstill11.png'), "H", 0, 50, 50)
            else:
                if self.__direction == 0:
                    self.updateWH(pygame.image.load('Assets/kongstill0.png'), "H", 0, 50, 50)
                else:
                    self.updateWH(pygame.image.load('Assets/kongstill10.png'), "H", 0, 50, 50)
