__author__ = 'Erilyth'
import pygame
import os
from .person import Person

'''
This class defines all the Monsters present in our game.
Each Monster can only move on the top floor and cannot move vertically.
'''


class MonsterPerson(Person):

    def __init__(self, raw_image, position, rng, dir, width=15, height=15):
        super(MonsterPerson, self).__init__(raw_image, position, width, height)
        self.__speed = 2
        self.rng = rng
        self.__direction = int(self.rng.rand() * 100) % 2
        self.__cycles = 0
        self.__stopDuration = 0
        self.IMAGES = {
            "monster0": pygame.image.load(os.path.join(dir, 'assets/monster0.png')).convert_alpha(),
            "monster1": pygame.image.load(os.path.join(dir, 'assets/monster1.png')).convert_alpha(),
            "monster2": pygame.image.load(os.path.join(dir, 'assets/monster2.png')).convert_alpha(),
            "monster3": pygame.image.load(os.path.join(dir, 'assets/monster3.png')).convert_alpha(),
            "monster01": pygame.image.load(os.path.join(dir, 'assets/monster01.png')).convert_alpha(),
            "monster11": pygame.image.load(os.path.join(dir, 'assets/monster11.png')).convert_alpha(),
            "monster21": pygame.image.load(os.path.join(dir, 'assets/monster21.png')).convert_alpha(),
            "monster31": pygame.image.load(os.path.join(dir, 'assets/monster31.png')).convert_alpha(),
            "monsterstill0": pygame.image.load(os.path.join(dir, 'assets/monsterstill0.png')).convert_alpha(),
            "monsterstill10": pygame.image.load(os.path.join(dir, 'assets/monsterstill10.png')).convert_alpha(),
            "monsterstill1": pygame.image.load(os.path.join(dir, 'assets/monsterstill1.png')).convert_alpha(),
            "monsterstill11": pygame.image.load(os.path.join(dir, 'assets/monsterstill11.png')).convert_alpha()
        }

    # Getters and Setters
    def getSpeed(self):
        return self.__speed

    def setSpeed(self):
        return self.__speed

    def getStopDuration(self):
        return self.__stopDuration

    def setStopDuration(self, stopDuration):
        self.__stopDuration = stopDuration

    # Checks for collisions with walls in order to change direction when hit
    # by a wall
    def checkWall(self, colliderGroup):
        if self.__direction == 0:
            # Right collision with wall
            self.updateWH(self.image, "H", 20, 40, 40)
        if self.__direction == 1:
            # Left collision with wall
            self.updateWH(self.image, "H", -20, 40, 40)
        Colliders = pygame.sprite.spritecollide(self, colliderGroup, False)
        if self.__direction == 0:
            # Right collision with wall
            self.updateWH(self.image, "H", -20, 40, 40)
        if self.__direction == 1:
            # Left collision with wall
            self.updateWH(self.image, "H", 20, 40, 40)
        return Colliders

    # This is used to animate the monster
    def continuousUpdate(self, GroupList, GroupList2):

        # If the stop duration is 0 then monster is currently moving either
        # left or right
        if self.__stopDuration == 0:

            # Currently moving right
            if self.__direction == 0:
                self.__cycles += 1
                if self.__cycles % 24 < 6:
                    self.updateWH(
                        self.IMAGES["monster0"], "H", self.__speed, 45, 45)
                elif self.__cycles % 24 < 12:
                    self.updateWH(
                        self.IMAGES["monster1"], "H", self.__speed, 45, 45)
                elif self.__cycles % 24 < 18:
                    self.updateWH(
                        self.IMAGES["monster2"], "H", self.__speed, 45, 45)
                else:
                    self.updateWH(
                        self.IMAGES["monster3"], "H", self.__speed, 45, 45)
                if self.checkWall(GroupList):
                    self.__direction = 1
                    self.__cycles = 0
                    self.updateWH(self.image, "H", -self.__speed, 45, 45)

            # Currently moving left
            else:
                self.__cycles += 1
                if self.__cycles % 24 < 6:
                    self.updateWH(
                        self.IMAGES["monster01"], "H", -self.__speed, 45, 45)
                elif self.__cycles % 24 < 12:
                    self.updateWH(
                        self.IMAGES["monster11"], "H", -self.__speed, 45, 45)
                elif self.__cycles % 24 < 18:
                    self.updateWH(
                        self.IMAGES["monster21"], "H", -self.__speed, 45, 45)
                else:
                    self.updateWH(
                        self.IMAGES["monster31"], "H", -self.__speed, 45, 45)
                if self.checkWall(GroupList):
                    self.__direction = 0
                    self.__cycles = 0
                    self.updateWH(self.image, "H", self.__speed, 45, 45)

        # Donkey Kong is currently not moving, which means he is launching a
        # fireball
        else:
            self.__stopDuration -= 1
            if self.__stopDuration == 0:  # Once he finishes launching a fireball, we go back to our normal movement animation
                self.updateWH(self.image, "V", 12, 50, 50)
            if self.__stopDuration >= 10:
                if self.__direction == 0:
                    self.updateWH(self.IMAGES["monsterstill0"], "H", 0, 45, 45)
                else:
                    self.updateWH(
                        self.IMAGES["monsterstill10"], "H", 0, 45, 45)
            elif self.__stopDuration >= 5:
                if self.__direction == 0:
                    self.updateWH(self.IMAGES["monsterstill1"], "H", 0, 45, 45)
                else:
                    self.updateWH(
                        self.IMAGES["monsterstill11"], "H", 0, 45, 45)
            else:
                if self.__direction == 0:
                    self.updateWH(self.IMAGES["monsterstill0"], "H", 0, 45, 45)
                else:
                    self.updateWH(
                        self.IMAGES["monsterstill10"], "H", 0, 45, 45)
