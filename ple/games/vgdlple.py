import sys
import pygame
import base
import vgdl.core as core

# Hacked together VLE wrapper for py-VGDL. Potentially extremely buggy - use with caution.
# This allows you to use VGDL (see http://people.idsia.ch/~tom/publications/pyvgdl.pdf , thanks to Tom Schaul) with the PLE.

# Example VGDL description text
# The game dynamics are specified as a paragraph of text
aliens_game = """
BasicGame
    SpriteSet
        base    > Immovable    color=WHITE
        avatar  > FlakAvatar   stype=sam
        missile > Missile
            sam  > orientation=UP    color=BLUE singleton=True
            bomb > orientation=DOWN  color=RED  speed=0.5
        alien   > Bomber       stype=bomb   prob=0.01  cooldown=3 speed=0.75
        portal  > SpawnPoint   stype=alien  cooldown=16   total=20
    
    LevelMapping
        0 > base
        1 > portal

    TerminationSet
        SpriteCounter      stype=avatar               limit=0 win=False
        MultiSpriteCounter stype1=portal stype2=alien limit=0 win=True
        
    InteractionSet
        avatar  EOS  > stepBack
        alien   EOS  > turnAround        
        missile EOS  > killSprite
        missile base > killSprite
        base missile > killSprite
        base   alien > killSprite
        avatar alien > killSprite
        avatar bomb  > killSprite
        alien  sam   > killSprite         
"""

# the (initial) level as a block of characters 
aliens_level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w1                             w
w000                           w
w000                           w
w                              w
w                              w
w                              w
w                              w
w    000      000000     000   w
w   00000    00000000   00000  w
w   0   0    00    00   00000  w
w                A             w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


class vgdlPLE(base.PyGameWrapper):


    def __init__(self, game_str = aliens_game, map_str = aliens_level):

	# GVG-AI competition allows 40ms per move, which equates to 25fps
        self.allowed_fps = 25

        self.game_desc = game_str
        self.level_desc = map_str
        
        # Need to build a sample level to get the available actions and screensize....
        self.g = core.VGDLParser().parseGame(self.game_desc)
        self.g.buildLevel(self.level_desc)

        actions = self.g.getPossibleActions()
        base.PyGameWrapper.__init__(self, self.g.screensize[0], self.g.screensize[1], actions=actions)


    def getGameState(self):
        # Using the VGDL State Representation for now
        return self.g.getFullState()

    def getScore(self):
        return self.g.score

    def game_over(self):
        return self.g.ended

    def init(self):
        # Need to reset Env here, current py-vgdl doesn't allow this so this is a complete hack
        del self.g
        self.g = core.VGDLParser().parseGame(self.game_desc)
        self.g.buildLevel(self.level_desc)

        # Sprites rely on BasicGame.screen 
        self.g.screen = self.screen

        # Sprites rely on BasicGame.background
        self.g.background = pygame.Surface(self.g.screensize)
        


    def step(self, dt):

	# This update code is lifted straight from BasicGame.Startgame (since BasicGame.tick is a bit funky).
	# In the interest of transparency with the current VGDL library I've tried to work with the existing interfaces, but it might be better to wrap these into routines in vgdl itself.

        # Clean up dead sprites
        self.g._clearAll()

        # Clear Screen - This is only really needed at the start of each game so there are some efficiency savings to be had here
        self.screen.fill((0, 0, 0))

        # This is required for game-updates to work properly
        self.g.time += 1

        # Update Keypresses
        # Agents are updated during the update routine in their ontology files, this demends on BasicGame.keystate
        # N.B: actions will only happen on keypress, I don't know how the PLE handles this with RL agents
        self.g.keystate = [0]*323 #323 seems to be the magic number..... (try len(pygame.key.get_pressed()))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.g.keystate[event.key] = True

	# Iterate Over Termination Criteria
	for t in self.g.terminations:
	    self.g.ended, win = t.isDone(self.g)
	    if self.g.ended:
	        break
	# Update Sprites
	for s in self.g:
	    s.update(self.g)
	# Handle Collision Effects
	self.g._eventHandling()

	self.g._drawAll()
        #pygame.display.update(core.VGDLSprite.dirtyrects)
        #core.VGDLSprite.dirtyrects = []


if __name__ == "__main__":
    import numpy as np

    if len(sys.argv)<2:
        game_desc = aliens_game
        level_desc = aliens_level
    else:
        with open (sys.argv[1], "r") as myfile:
            game_desc = myfile.read()
        with open (sys.argv[2], "r") as myfile:
            game_level = myfile.read()

    pygame.init()
    game = vgdlPLE(game_desc,game_level)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)

    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(60)
        game.step(dt)
        pygame.display.update()
