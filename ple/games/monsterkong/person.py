__author__ = 'Batchu Vishal'
import pygame

'''
This class defines all living things in the game, ex.Donkey Kong, Player etc
Each of these objects can move in any direction specified.
'''


class Person(pygame.sprite.Sprite):

    def __init__(self, raw_image, position, width, height):
        super(Person, self).__init__()
        self.width = width
        self.height = height
        self.__position = position
        self.image = raw_image
        self.image = pygame.transform.scale(
            self.image, (width, height)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.__position

    '''
    We set these as abstract methods since this class does not have a speed variable set, but we want all the child classes to
    set a movement speed and they should have setters and getters for this movement speed.
    '''

    def getSpeed(self):  # Abstract method
        raise NotImplementedError("Subclass must implement this")

    def setSpeed(self):  # Abstract method
        raise NotImplementedError("Subclass must implement this")

    # Getters and Setters
    def setCenter(self, position):
        self.rect.center = position

    def getPosition(self):
        return self.__position

    def setPosition(self, position):
        self.__position = position

    # Move the person in the horizontal ("H") or vertical ("V") axis
    def updateWH(self, raw_image, direction, value, width, height):
        if direction == "H":
            self.__position = (self.__position[0] + value, self.__position[1])
        if direction == "V":
            self.__position = (self.__position[0], self.__position[1] + value)
        self.image = raw_image
        # Update the image to the specified width and height
        #self.image = pygame.transform.scale(self.image, (width, height))
        self.rect.center = self.__position

    # When you only need to update vertically
    def updateY(self, value):
        self.__position = (self.__position[0], self.__position[1] + value)
        self.rect.center = self.__position

    # Given a collider list, just check if the person instance collides with
    # any of them
    def checkCollision(self, colliderGroup):
        Colliders = pygame.sprite.spritecollide(self, colliderGroup, False)
        return Colliders

    # This is another abstract function, and it must be implemented in child
    # classes inheriting from this class
    def continuousUpdate(self, GroupList, GroupList2):
        # continuousUpdate that gets called frequently for collision checks,
        # movement etc
        raise NotImplementedError("Subclass must implement this")
