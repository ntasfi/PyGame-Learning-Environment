__author__ = 'Batchu Vishal'
import pygame
import math
import sys
import os

from .person import Person
from .onBoard import OnBoard
from .coin import Coin
from .player import Player
from .fireball import Fireball
from .monsterPerson import MonsterPerson


class Board(object):
    '''
    This class defines our gameboard.
    A gameboard contains everthing related to our game on it like our characters, walls, ladders, coins etc
    The generation of the level also happens in this class.
    '''

    def __init__(self, width, height, rewards, rng, _dir):
        self.__width = width
        self.__actHeight = height
        self.__height = self.__actHeight + 10
        self.score = 0
        self.rng = rng
        self.rewards = rewards
        self.cycles = 0  # For the characters animation
        self.direction = 0
        self._dir = _dir

        self.IMAGES = {
            "still": pygame.image.load(os.path.join(_dir, 'assets/still.png')).convert_alpha(),
            "monster0": pygame.image.load(os.path.join(_dir, 'assets/monster0.png')).convert_alpha(),
            "princess": pygame.image.load(os.path.join(_dir, 'assets/princess.png')).convert_alpha(),
            "fireballright": pygame.image.load(os.path.join(_dir, 'assets/fireballright.png')).convert_alpha(),
            "coin1": pygame.image.load(os.path.join(_dir, 'assets/coin1.png')).convert_alpha(),
            "wood_block": pygame.image.load(os.path.join(_dir, 'assets/wood_block.png')).convert_alpha(),
            "ladder": pygame.image.load(os.path.join(_dir, 'assets/ladder.png')).convert_alpha()
        }

        self.white = (255, 255, 255)

        '''
        The map is essentially an array of 30x80 in which we store what each block on our map is.
        1 represents a wall, 2 for a ladder and 3 for a coin.
        '''
        self.map = []
        # These are the arrays in which we store our instances of different
        # classes
        self.Players = []
        self.Enemies = []
        self.Allies = []
        self.Coins = []
        self.Walls = []
        self.Ladders = []
        self.Fireballs = []
        self.Boards = []
        self.FireballEndpoints = []

        # Resets the above groups and initializes the game for us
        self.resetGroups()

        # Initialize the instance groups which we use to display our instances
        # on the screen
        self.fireballGroup = pygame.sprite.RenderPlain(self.Fireballs)
        self.playerGroup = pygame.sprite.RenderPlain(self.Players)
        self.enemyGroup = pygame.sprite.RenderPlain(self.Enemies)
        self.wallGroup = pygame.sprite.RenderPlain(self.Walls)
        self.ladderGroup = pygame.sprite.RenderPlain(self.Ladders)
        self.coinGroup = pygame.sprite.RenderPlain(self.Coins)
        self.allyGroup = pygame.sprite.RenderPlain(self.Allies)
        self.fireballEndpointsGroup = pygame.sprite.RenderPlain(
            self.FireballEndpoints)

    def resetGroups(self):
        self.score = 0
        self.lives = 3
        self.map = []  # We will create the map again when we reset the game
        self.Players = [
            Player(
                self.IMAGES["still"],
                (self.__width / 2,
                 435),
                15,
                15)]
        self.Enemies = [
            MonsterPerson(
                self.IMAGES["monster0"],
                (100,
                 117),
                self.rng,
                self._dir)]
        self.Allies = [Person(self.IMAGES["princess"], (50, 48), 18, 25)]
        self.Allies[0].updateWH(self.Allies[0].image, "H", 0, 25, 25)
        self.Coins = []
        self.Walls = []
        self.Ladders = []
        self.Fireballs = []
        self.FireballEndpoints = [OnBoard(self.IMAGES["still"], (50, 440))]
        self.initializeGame()  # This initializes the game and generates our map
        self.createGroups()  # This creates the instance groups

    # Checks to destroy a fireball when it reaches its terminal point
    def checkFireballDestroy(self, fireball):
        if pygame.sprite.spritecollide(
                fireball, self.fireballEndpointsGroup, False):
            # We use indices on fireballs to uniquely identify each fireball
            self.DestroyFireball(fireball.index)

    # Creates a new fireball and adds it to our fireball group
    def CreateFireball(self, location, monsterIndex):
        if len(self.Fireballs) < len(self.Enemies) * 5:
            self.Fireballs.append(
                Fireball(self.IMAGES["fireballright"], (location[0], location[1] + 15), len(self.Fireballs),
                         2 + len(self.Enemies) / 2, self.rng, self._dir))
            # Starts monster's animation
            self.Enemies[monsterIndex].setStopDuration(15)
            self.Enemies[monsterIndex].setPosition(
                (self.Enemies[monsterIndex].getPosition()[0], self.Enemies[monsterIndex].getPosition()[1] - 12))
            self.Enemies[monsterIndex].setCenter(
                self.Enemies[monsterIndex].getPosition())
            self.createGroups()  # We recreate the groups so the fireball is added

    # Destroy a fireball if it has collided with a player or reached its
    # endpoint
    def DestroyFireball(self, index):
        for fireBall in range(len(self.Fireballs)):
            if self.Fireballs[fireBall].index == index:
                self.Fireballs.remove(self.Fireballs[fireBall])
                for fireBallrem in range(
                        len(self.Fireballs)):  # We need to reduce the indices of all fireballs greater than this
                    if self.Fireballs[fireBallrem].index > index:
                        self.Fireballs[fireBallrem].index -= 1
                self.createGroups()  # Recreate the groups so the fireball is removed
                break

    # Randomly Generate coins in the level where there is a wall below the
    # coin so the player can reach it
    def GenerateCoins(self):
        for i in range(6, len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == 0 and ((i + 1 < len(self.map) and self.map[i + 1][j] == 1) or (
                        i + 2 < len(self.map) and self.map[i + 2][j] == 1)):
                    randNumber = math.floor(self.rng.rand() * 1000)
                    if randNumber % 35 == 0 and len(
                            self.Coins) <= 25:  # At max there will be 26 coins in the map
                        self.map[i][j] = 3
                        if j - 1 >= 0 and self.map[i][j - 1] == 3:
                            self.map[i][j] = 0
                        if self.map[i][j] == 3:
                            # Add the coin to our coin list
                            self.Coins.append(
                                Coin(
                                    self.IMAGES["coin1"],
                                    (j * 15 + 15 / 2,
                                     i * 15 + 15 / 2),
                                    self._dir))
        if len(
                self.Coins) <= 15:  # If there are less than 21 coins, we call the function again
            self.GenerateCoins()

    # Given a position and checkNo ( 1 for wall, 2 for ladder, 3 for coin) the
    # function tells us if its a valid position to place or not
    def checkMapForMatch(self, placePosition, floor, checkNo, offset):
        if floor < 1:
            return 0
        for i in range(
                0, 5):  # We will get things placed atleast 5-1 blocks away from each other
            if self.map[floor * 5 - offset][placePosition + i] == checkNo:
                return 1
            if self.map[floor * 5 - offset][placePosition - i] == checkNo:
                return 1
        return 0

    # Create an empty 2D map of 30x80 size
    def makeMap(self):
        for point in range(0, int(self.__height / 15 + 1)):
            row = []
            for point2 in range(0, int(self.__width / 15)):
                row.append(0)
            self.map.append(row)

    # Add walls to our map boundaries and also the floors
    def makeWalls(self):
        for i in range(0, int(self.__height / 15)):
            self.map[i][0] = self.map[i][int(self.__width / 15 - 1)] = 1
        for i in range(2, int(self.__height / (15 * 4))):
            for j in range(0, int(self.__width / 15)):
                self.map[i * 5][j] = 1

    # Make a small chamber on the top where the princess resides
    def makePrincessChamber(self):
        for j in range(0, 4):
            self.map[j][9] = 1

        for j in range(0, 10):
            self.map[4][j] = 1

        for j in range(0, 6):
            self.map[1 * 4 + j][7] = self.map[1 * 4 + j][8] = 2

    # Generate ladders randomly, 1 for each floor such that they are not too
    # close to each other
    def makeLadders(self):
        for i in range(2, int(self.__height / (15 * 4) - 1)):
            ladderPos = math.floor(self.rng.rand() * (self.__width / 15 - 20))
            ladderPos = int(7 + ladderPos)
            while self.checkMapForMatch(ladderPos, i - 1, 2, 0) == 1:
                ladderPos = math.floor(
                    self.rng.rand() * (self.__width / 15 - 20))
                ladderPos = int(7 + ladderPos)
            for k in range(0, 5):
                self.map[i * 5 + k][ladderPos] = self.map[i *
                                                          5 + k][ladderPos + 1] = 2

    # Create the holes on each floor (extreme right and extreme left)
    def makeHoles(self):
        for i in range(3, int(self.__height / (15 * 4) - 1)):
            for k in range(
                    1, 6):  # Ladders wont interfere since they leave 10 blocks on either side
                if i % 2 == 0:
                    self.map[i * 5][k] = 0
                else:
                    self.map[i * 5][int(self.__width / 15 - 1 - k)] = 0

    '''
    This is called once you have finished making holes, ladders, walls etc
    You use the 2D map to add instances to the groups
    '''

    def populateMap(self):
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if self.map[x][y] == 1:
                    # Add a wall at that position
                    self.Walls.append(
                        OnBoard(
                            self.IMAGES["wood_block"],
                            (y * 15 + 15 / 2,
                             x * 15 + 15 / 2)))
                elif self.map[x][y] == 2:
                    # Add a ladder at that position
                    self.Ladders.append(
                        OnBoard(
                            self.IMAGES["ladder"],
                            (y * 15 + 15 / 2,
                             x * 15 + 15 / 2)))

    # Check if the player is on a ladder or not
    def ladderCheck(self, laddersCollidedBelow,
                    wallsCollidedBelow, wallsCollidedAbove):
        if laddersCollidedBelow and len(wallsCollidedBelow) == 0:
            for ladder in laddersCollidedBelow:
                if ladder.getPosition()[1] >= self.Players[0].getPosition()[1]:
                    self.Players[0].onLadder = 1
                    self.Players[0].isJumping = 0
                    # Move the player down if he collides a wall above
                    if wallsCollidedAbove:
                        self.Players[0].updateY(3)
        else:
            self.Players[0].onLadder = 0

    # Update all the fireball positions and check for collisions with player
    def fireballCheck(self):
        for fireball in self.fireballGroup:
            fireball.continuousUpdate(self.wallGroup, self.ladderGroup)
            if fireball.checkCollision(self.playerGroup, "V"):
                self.Fireballs.remove(fireball)
                self.Players[0].setPosition((50, 440))
                self.score += self.rewards["negative"]
                self.lives += -1
                self.createGroups()
            self.checkFireballDestroy(fireball)

    # Check for coins collided and add the appropriate score
    def coinCheck(self, coinsCollected):
        for coin in coinsCollected:
            self.score += self.rewards["positive"]
            # We also remove the coin entry from our map
            self.map[int((coin.getPosition()[1] - 15 / 2) /
                     15)][int((coin.getPosition()[0] - 15 / 2) / 15)] = 0
            # Remove the coin entry from our list
            self.Coins.remove(coin)
            # Update the coin group since we modified the coin list
            self.createGroups()

    # Check if the player wins
    def checkVictory(self):
        # If you touch the princess or reach the floor with the princess you
        # win!
        if self.Players[0].checkCollision(self.allyGroup) or self.Players[
                0].getPosition()[1] < 4 * 15:

            self.score += self.rewards["win"]

            # This is just the next level so we only clear the fireballs and
            # regenerate the coins
            self.Fireballs = []
            self.Players[0].setPosition((50, 440))
            self.Coins = []
            self.GenerateCoins()

            # Add monsters
            if len(self.Enemies) == 1:
                self.Enemies.append(
                    MonsterPerson(
                        self.IMAGES["monster0"], (700, 117), self.rng, self._dir))
            elif len(self.Enemies) == 2:
                self.Enemies.append(
                    MonsterPerson(
                        self.IMAGES["monster0"], (400, 117), self.rng, self._dir))
            # Create the groups again so the enemies are effected
            self.createGroups()

    # Redraws the entire game screen for us
    def redrawScreen(self, screen, width, height):
        screen.fill((40, 20, 0))  # Fill it with black
        # Draw all our groups on the background
        self.ladderGroup.draw(screen)
        self.playerGroup.draw(screen)
        self.coinGroup.draw(screen)
        self.wallGroup.draw(screen)
        self.fireballGroup.draw(screen)
        self.enemyGroup.draw(screen)
        self.allyGroup.draw(screen)

    # Update all the groups from their corresponding lists
    def createGroups(self):
        self.fireballGroup = pygame.sprite.RenderPlain(self.Fireballs)
        self.playerGroup = pygame.sprite.RenderPlain(self.Players)
        self.enemyGroup = pygame.sprite.RenderPlain(self.Enemies)
        self.wallGroup = pygame.sprite.RenderPlain(self.Walls)
        self.ladderGroup = pygame.sprite.RenderPlain(self.Ladders)
        self.coinGroup = pygame.sprite.RenderPlain(self.Coins)
        self.allyGroup = pygame.sprite.RenderPlain(self.Allies)
        self.fireballEndpointsGroup = pygame.sprite.RenderPlain(
            self.FireballEndpoints)

    '''
    Initialize the game by making the map, generating walls, generating princess chamber, generating ladders randomly,
    generating broken ladders randomly, generating holes, generating coins randomly, adding the ladders and walls to our lists
    and finally updating the groups.
    '''

    def initializeGame(self):
        self.makeMap()
        self.makeWalls()
        self.makePrincessChamber()
        self.makeLadders()
        self.makeHoles()
        self.GenerateCoins()
        self.populateMap()
        self.createGroups()
