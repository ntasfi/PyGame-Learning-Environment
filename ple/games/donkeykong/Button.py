__author__ = 'Batchu Vishal'

'''
This class defines all our buttons
A button has an image and a position associated with it
'''


class Button:
    def __init__(self, raw_image, position, nameStr):
        self.image = raw_image
        self.__position = position
        self.rect = self.image.get_rect()
        self.rect.center = self.__position
        self.name = nameStr  # Set the name of the button with a string

    # Update the button's image
    def changeImage(self, raw_image):
        self.image = raw_image

    # Returns the top left corner of our button
    def getTopLeftPosition(self):
        return (self.__position[0] - self.rect.width / 2, self.__position[1] - self.rect.height / 2)

    # Getters and Setters
    def getPosition(self):
        return self.__position

    def setPosition(self, position):
        self.__position = position
