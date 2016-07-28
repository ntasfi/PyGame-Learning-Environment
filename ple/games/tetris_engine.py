# Modified from Tetromino by lusob
# https://github.com/lusob
# Released under the MIT license

import random, time, pygame, sys
from pygame.locals import *

class GameState:
    def __init__(self):
        pygame.init()
        self.BOXSIZE = 20
        self.BOARDWIDTH = 10
        self.BOARDHEIGHT = 20
        self.WINDOWWIDTH = self.BOXSIZE * self.BOARDWIDTH
        self.WINDOWHEIGHT = self.BOXSIZE * self.BOARDHEIGHT
        self.BLANK = '.'
        self.XMARGIN = 0
        self.TOPMARGIN = 0
        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
        self.FPS = 25

#               R    G    B
        WHITE       = (255, 255, 255)
        GRAY        = (185, 185, 185)
        BLACK       = (  0,   0,   0)
        RED         = (155,   0,   0)
        LIGHTRED    = (175,  20,  20)
        GREEN       = (  0, 155,   0)
        LIGHTGREEN  = ( 20, 175,  20)
        BLUE        = (  0,   0, 155)
        LIGHTBLUE   = ( 20,  20, 175)
        YELLOW      = (155, 155,   0)
        LIGHTYELLOW = (175, 175,  20)

        self.BORDERCOLOR = BLUE
        self.BGCOLOR = BLACK
        self.TEXTCOLOR = WHITE
        self.TEXTSHADOWCOLOR = GRAY
        self.COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
        self.LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
        assert len(self.COLORS) == len(self.LIGHTCOLORS) # each color must have light color

        self.TEMPLATEWIDTH = 5
        self.TEMPLATEHEIGHT = 5

        self.S_SHAPE_TEMPLATE = [['..OO.',
                            '.OO..',
                            '.....',
                            '.....',
                            '.....'],
                            ['..O..',
                            '..OO.',
                            '...O.',
                            '.....',
                            '.....']]

        self.Z_SHAPE_TEMPLATE = [['.OO..',
                            '..OO.',
                            '.....',
                            '.....',
                            '.....'],
                            ['..O..',
                            '.OO..',
                            '.O...',
                            '.....',
                            '.....']]

        self.I_SHAPE_TEMPLATE = [['..O..',
                            '..O..',
                            '..O..',
                            '..O..',
                            '.....'],
                            ['OOOO.',
                            '.....',
                            '.....',
                            '.....',
                            '.....']]

        self.O_SHAPE_TEMPLATE = [['.OO..',
                            '.OO..',
                            '.....',
                            '.....',
                            '.....']]

        self.J_SHAPE_TEMPLATE = [['.O...',
                            '.OOO.',
                            '.....',
                            '.....',
                            '.....'],
                            ['..OO.',
                            '..O..',
                            '..O..',
                            '.....',
                            '.....'],
                            ['.OOO.',
                            '...O.',
                            '.....',
                            '.....',
                            '.....'],
                            ['..O..',
                            '..O..',
                            '.OO..',
                            '.....',
                            '.....']]

        self.L_SHAPE_TEMPLATE = [['...O.',
                            '.OOO.',
                            '.....',
                            '.....',
                            '.....'],
                            ['..O..',
                            '..O..',
                            '..OO.',
                            '.....',
                            '.....'],
                            ['.OOO.',
                            '.O...',
                            '.....',
                            '.....',
                            '.....'],
                            ['.OO..',
                            '..O..',
                            '..O..',
                            '.....',
                            '.....']]

        self.T_SHAPE_TEMPLATE = [['..O..',
                            '.OOO.',
                            '.....',
                            '.....',
                            '.....'],
                            ['..O..',
                            '..OO.',
                            '..O..',
                            '.....',
                            '.....'],
                            ['.OOO.',
                            '..O..',
                            '.....',
                            '.....',
                            '.....'],
                            ['..O..',
                            '.OO..',
                            '..O..',
                            '.....',
                            '.....']]

        self.PIECES = {'S': self.S_SHAPE_TEMPLATE,
                       'Z': self.Z_SHAPE_TEMPLATE,
                       'J': self.J_SHAPE_TEMPLATE,
                       'L': self.L_SHAPE_TEMPLATE,
                       'I': self.I_SHAPE_TEMPLATE,
                       'O': self.O_SHAPE_TEMPLATE,
                       'T': self.T_SHAPE_TEMPLATE}


        pygame.display.set_caption('Tetromino')

        # DEBUG
        self.total_lines = 0

        # setup variables for the start of the game
        self.board = self.getBlankBoard()
        self.movingDown = False # note: there is no movingUp variable
        self.movingLeft = False
        self.movingRight = False
        self.score = 0
        self.lines = 0
        self.height = 0
        self.level, self.fallFreq = self.calculateLevelAndFallFreq()

        self.fallingPiece = self.getNewPiece()
        self.nextPiece = self.getNewPiece()

        self.frame_step([1,0,0,0,0,0])


    def reinit(self):
        self.board = self.getBlankBoard()
        self.movingDown = False # note: there is no movingUp variable
        self.movingLeft = False
        self.movingRight = False
        self.score = 0
        self.lines = 0
        self.height = 0
        self.level, self.fallFreq = self.calculateLevelAndFallFreq()

        self.fallingPiece = self.getNewPiece()
        self.nextPiece = self.getNewPiece()

        self.frame_step([1,0,0,0,0,0])



    def frame_step(self,input):
        self.movingLeft = False
        self.movingRight = False

        reward = 0
        terminal = False

        #none is 100000, left is 010000, up is 001000, right is 000100, space is 000010, q is 000001
        if self.fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            self.fallingPiece = self.nextPiece
            self.nextPiece = self.getNewPiece()

            if not self.isValidPosition():
                image_data = pygame.surfarray.array3d(pygame.display.get_surface())
                terminal = True

                self.reinit()
                return image_data, reward, terminal # can't fit a new piece on the self.board, so game over


        # moving the piece sideways
        if (input[1] == 1) and self.isValidPosition(adjX=-1):
            self.fallingPiece['x'] -= 1
            self.movingLeft = True
            self.movingRight = False

        elif (input[3] == 1) and self.isValidPosition(adjX=1):
            self.fallingPiece['x'] += 1
            self.movingRight = True
            self.movingLeft = False

        # rotating the piece (if there is room to rotate)
        elif (input[2] == 1):
            self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] + 1) % len(self.PIECES[self.fallingPiece['shape']])
            if not self.isValidPosition():
                self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] - 1) % len(self.PIECES[self.fallingPiece['shape']])

        elif (input[5] == 1): # rotate the other direction
            self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] - 1) % len(self.PIECES[self.fallingPiece['shape']])
            if not self.isValidPosition():
                self.fallingPiece['rotation'] = (self.fallingPiece['rotation'] + 1) % len(self.PIECES[self.fallingPiece['shape']])

        # move the current piece all the way down
        elif (input[4] == 1):
            self.movingDown = False
            self.movingLeft = False
            self.movingRight = False
            for i in range(1, self.BOARDHEIGHT):
                if not self.isValidPosition(adjY=i):
                    break
            self.fallingPiece['y'] += i - 1

        # handle moving the piece because of user input
        if (self.movingLeft or self.movingRight):
            if self.movingLeft and self.isValidPosition(adjX=-1):
                self.fallingPiece['x'] -= 1
            elif self.movingRight and self.isValidPosition(adjX=1):
                self.fallingPiece['x'] += 1

        if self.movingDown:
            self.fallingPiece['y'] += 1

        # let the piece fall if it is time to fall
        # see if the piece has landed
        cleared = 0
        if not self.isValidPosition(adjY=1):
            # falling piece has landed, set it on the self.board
            self.addToBoard()

            cleared = self.removeCompleteLines()
            if cleared > 0:
                if cleared == 1:
                    self.score += 40 * self.level
                elif cleared == 2:
                    self.score += 100 * self.level
                elif cleared == 3:
                    self.score += 300 * self.level
                elif cleared == 4:
                    self.score += 1200 * self.level

            self.score += self.fallingPiece['y']

            self.lines += cleared
            self.total_lines += cleared

            reward = self.height - self.getBoardHeight()
            self.height = self.getBoardHeight()

            self.level, self.fallFreq = self.calculateLevelAndFallFreq()
            self.fallingPiece = None

        else:
            # piece did not land, just move the piece down
            self.fallingPiece['y'] += 1

        # drawing everything on the screen
        self.DISPLAYSURF.fill(self.BGCOLOR)
        self.drawBoard()
        if self.fallingPiece != None:
           self.drawPiece(self.fallingPiece)

        if cleared > 0:
            reward = 100 * cleared

        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        return image_data, reward, terminal

    def getActionSet(self):
        return range(6)

    def getBoardHeight(self):
        stack_height = 0
        for i in range(0, self.BOARDHEIGHT):
            blank_row = True
            for j in range(0, self.BOARDWIDTH):
                if self.board[j][i] != '.':
                    blank_row = False
            if not blank_row:
                stack_height = self.BOARDHEIGHT - i
                break
        return stack_height

    def getReward(self):
        stack_height = None
        num_blocks = 0
        for i in range(0, self.BOARDHEIGHT):
            blank_row = True
            for j in range(0, self.BOARDWIDTH):
                if self.board[j][i] != '.':
                    num_blocks += 1
                    blank_row = False
            if not blank_row and stack_height is None:
                stack_height = self.BOARDHEIGHT - i

        if stack_height is None:
            return self.BOARDHEIGHT
        else:
            return self.BOARDHEIGHT - stack_height
            return float(num_blocks) / float(stack_height * self.BOARDWIDTH)

    def isGameOver(self):
        # TODO: fix this to return when actually is a game over
        if self.fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            if self.nextPiece == None or not self.isValidPosition(piece=self.nextPiece):
                return True
                 # can't fit a new piece on the self.board, so game over
        return False

    def makeTextObjs(self,text, font, color):
        surf = font.render(text, True, color)
        return surf, surf.get_rect()

    def calculateLevelAndFallFreq(self):
        # Based on the self.score, return the self.level the player is on and
        # how many seconds pass until a falling piece falls one space.
        self.level = min(int(self.lines / 10) + 1, 10)
        self.fallFreq = 0.27 - (self.level * 0.02)
        return self.level, self.fallFreq

    def getNewPiece(self):
        # return a random new piece in a random rotation and color
        shape = random.choice(list(self.PIECES.keys()))
        newPiece = {'shape': shape,
                    'rotation': random.randint(0, len(self.PIECES[shape]) - 1),
                    'x': int(self.BOARDWIDTH / 2) - int(self.TEMPLATEWIDTH / 2),
                    'y': 0, # start it above the self.board (i.e. less than 0)
                    'color': random.randint(0, len(self.COLORS)-1)}
        return newPiece


    def addToBoard(self):
        # fill in the self.board based on piece's location, shape, and rotation
        for x in range(self.TEMPLATEWIDTH):
            for y in range(self.TEMPLATEHEIGHT):
                if self.PIECES[self.fallingPiece['shape']][self.fallingPiece['rotation']][y][x] != self.BLANK:
                    self.board[x + self.fallingPiece['x']][y + self.fallingPiece['y']] = self.fallingPiece['color']


    def getBlankBoard(self):
        # create and return a new blank self.board data structure
        self.board = []
        for i in range(self.BOARDWIDTH):
            self.board.append([self.BLANK] * self.BOARDHEIGHT)
        return self.board


    def isOnBoard(self,x, y):
        return x >= 0 and x < self.BOARDWIDTH and y < self.BOARDHEIGHT


    def isValidPosition(self,adjX=0, adjY=0, piece=None):
        if piece == None:
            piece = self.fallingPiece
        # Return True if the piece is within the self.board and not colliding
        for x in range(self.TEMPLATEWIDTH):
            for y in range(self.TEMPLATEHEIGHT):
                isAboveBoard = y + piece['y'] + adjY < 0
                if isAboveBoard or self.PIECES[piece['shape']][piece['rotation']][y][x] == self.BLANK:
                    continue
                if not self.isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                    return False
                if self.board[x + piece['x'] + adjX][y + piece['y'] + adjY] != self.BLANK:
                    return False
        return True

    def isCompleteLine(self, y):
        # Return True if the line filled with boxes with no gaps.
        for x in range(self.BOARDWIDTH):
            if self.board[x][y] == self.BLANK:
                return False
        return True


    def removeCompleteLines(self):
        # Remove any completed lines on the self.board, move everything above them down, and return the number of complete lines.
        numLinesRemoved = 0
        y = self.BOARDHEIGHT - 1 # start y at the bottom of the self.board
        while y >= 0:
            if self.isCompleteLine(y):
                # Remove the line and pull boxes down by one line.
                for pullDownY in range(y, 0, -1):
                    for x in range(self.BOARDWIDTH):
                        self.board[x][pullDownY] = self.board[x][pullDownY-1]
                # Set very top line to blank.
                for x in range(self.BOARDWIDTH):
                    self.board[x][0] = self.BLANK
                numLinesRemoved += 1
                # Note on the next iteration of the loop, y is the same.
                # This is so that if the line that was pulled down is also
                # complete, it will be removed.
            else:
                y -= 1 # move on to check next row up
        return numLinesRemoved


    def convertToPixelCoords(self,boxx, boxy):
        # Convert the given xy coordinates of the self.board to xy
        # coordinates of the location on the screen.
        return (self.XMARGIN + (boxx * self.BOXSIZE)), (self.TOPMARGIN + (boxy * self.BOXSIZE))


    def drawBox(self,boxx, boxy, color, pixelx=None, pixely=None):
        # draw a single box (each tetromino piece has four boxes)
        # at xy coordinates on the self.board. Or, if pixelx & pixely
        # are specified, draw to the pixel coordinates stored in
        # pixelx & pixely (this is used for the "Next" piece).
        if color == self.BLANK:
            return
        if pixelx == None and pixely == None:
            pixelx, pixely = self.convertToPixelCoords(boxx, boxy)
        pygame.draw.rect(self.DISPLAYSURF, self.COLORS[color], (pixelx + 1, pixely + 1, self.BOXSIZE - 1, self.BOXSIZE - 1))
        pygame.draw.rect(self.DISPLAYSURF, self.LIGHTCOLORS[color], (pixelx + 1, pixely + 1, self.BOXSIZE - 4, self.BOXSIZE - 4))


    def drawBoard(self):
        # draw the border around the self.board
        pygame.draw.rect(self.DISPLAYSURF, self.BORDERCOLOR, (self.XMARGIN - 3, self.TOPMARGIN - 7, (self.BOARDWIDTH * self.BOXSIZE) + 8, (self.BOARDHEIGHT * self.BOXSIZE) + 8), 5)

        # fill the background of the self.board
        pygame.draw.rect(self.DISPLAYSURF, self.BGCOLOR, (self.XMARGIN, self.TOPMARGIN, self.BOXSIZE * self.BOARDWIDTH, self.BOXSIZE * self.BOARDHEIGHT))
        # draw the individual boxes on the self.board
        for x in range(self.BOARDWIDTH):
            for y in range(self.BOARDHEIGHT):
                self.drawBox(x, y, self.board[x][y])



    def drawPiece(self,piece, pixelx=None, pixely=None):
        shapeToDraw = self.PIECES[piece['shape']][piece['rotation']]
        if pixelx == None and pixely == None:
            # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
            pixelx, pixely = self.convertToPixelCoords(piece['x'], piece['y'])

        # draw each of the boxes that make up the piece
        for x in range(self.TEMPLATEWIDTH):
            for y in range(self.TEMPLATEHEIGHT):
                if shapeToDraw[y][x] != self.BLANK:
                    self.drawBox(None, None, piece['color'], pixelx + (x * self.BOXSIZE), pixely + (y * self.BOXSIZE))

