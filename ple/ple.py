import pygame
import numpy as np
from PIL import Image #pillow

from pygame.constants import KEYDOWN, KEYUP, K_F15 #this is our NOOP?

class PLE(object):
        """
        ple.PLE(game, fps=30, frame_skip=1, num_steps=1, force_fps=True, display_screen=False, add_noop_action=True, NOOP=K_15)

        Main wrapper that interacts with games. Provides a similar interface to Arcade Learning Environment.

        Parameters
        ----------
        game: ple.game.base
            The game the PLE environment manipulates and maintains.

        fps: int (default: 30)
            The desired frames per second we want to run our game at. Typical settings are 30 and 60 fps.

        frame_skip: int (default: 1)
            The number of times we skip getting observations while repeat an action.

        num_steps: int (default: 1)
            The number of times we repeat an action.

        force_fps: bool (default: True)
            If False PLE delays between game.step() calls to ensure the fps is specified. If not PLE passes an elapsed time delta to ensure the game steps by an amount of time consistent with the specified fps. This is usally set to True as it allows the game to run as fast as possible which speeds up training.

        display_screen: bool (default: False)
            If we draw updates to the screen. Disabling this speeds up interation speed. This can be toggled to True during testing phases so you can observe the agents progress.

        add_noop_action: bool (default: True)
            This inserts the NOOP action specified as a valid move the agent can make.

        NOOP: pygame.constants (default: K_F15)
            The key we want our agent to send that represents a NOOP. This is currently set to F15.

        state_preprocessor: python function (default: None)
            Python function which takes a dict representing game state and returns a numpy array.

        """
	def __init__(self, 
                game, fps=30, frame_skip=1, num_steps=1, force_fps=True, 
                display_screen=False, add_noop_action=True, 
                NOOP=K_F15, state_preprocessor=None):

		self.game = game
		self.fps = fps
		self.frame_skip = frame_skip
		self.NOOP = NOOP
		self.num_steps = num_steps
		self.force_fps = force_fps
		self.display_screen = display_screen
                self.add_noop_action = add_noop_action

		self.last_action = []
		self.action = []
		self.score = 0
		self.previous_score = 0
		self.frame_count = 0
                
                #some games need a screen setup for convert images
                pygame.display.set_mode((1,1), pygame.NOFRAME)

		self.game.init()

                self.state_preprocessor = state_preprocessor
                self.state_dim = None

                if self.state_preprocessor != None:
                    self.state_dim = self.game.getGameState()

                    if self.state_dim == None:
                        raise ValueError("Asked to return non-visual state on game that does not support it!")
                    else:
                        self.state_dim = self.state_preprocessor(self.state_dim).shape

                if game.allowed_fps != None and self.fps != game.allowed_fps:
                    raise ValueError("Game requires %dfps, was given %d." % (game.allowed_fps, game.allowed_fps))

	def _tick(self):
		"""
                Calculates the elapsed time between frames or ticks.
		"""
		if self.force_fps:
			return 1000.0/self.fps
		else:
			return self.game.clock.tick_busy_loop(self.fps)

	def init(self):
                """
                Initializes the pygame environement, setup the display, and game clock.

                This method should be explicitly called.
                """
		pygame.init()
		self.game.screen = pygame.display.set_mode( self.getScreenDims(), 0, 32)
		self.game.clock = pygame.time.Clock()

	def getActionSet(self):
                """
                Gets the actions the game supports. Optionally inserts the NOOP action if PLE has add_noop_action set to True.

                Returns
                --------
                
                list of pygame.constants
                    The agent can simply select the index of the action to perform.

                """
		actions = self.game.actions.values()

                if self.add_noop_action:
                    actions.append(self.NOOP)

                return actions

	def getFrameNumber(self):
                """
                Gets the current number of frames the agent has seen since PLE was initialized.

                Returns
                --------

                int

                """

		return self.frame_count

	def game_over(self):
                """
                Returns True if the game has reached a terminal state and False otherwise.

                This state is game dependent.

                Returns
                -------

                bool

                """

		return self.game.game_over()

	def lives(self):
                """
                Gets the number of lives the agent has left. Not all games have the concept of lives.

                Returns
                -------

                int

                """

		return self.game.lives

	def reset_game(self):
                """ 
                Performs a reset of the games to a clean initial state.
                """
                self.previous_score = 0.0
		self.game.reset()

	def getScreenRGB(self):
                """
                Gets the current game screen in RGB format.
                
                Returns
                --------
                numpy uint8 array
                    Returns a numpy array with the shape (width, height, 3).


                """

		return pygame.surfarray.array3d(pygame.display.get_surface()).astype(np.uint8)

	def getScreenGrayscale(self):
                """
                Gets the current game screen in Grayscale format. Converts from RGB using relative lumiance.

                Returns
                --------
                numpy uint8 array
                    Returns a numpy array with the shape (width, height).


                """
		frame = self.getScreenRGB()
		frame = 0.21*frame[:, :, 0] + 0.72*frame[:, :, 1] + 0.07*frame[:, :, 2]
		frame = np.round(frame).astype(np.uint8)

		return frame

	def saveScreen(self, filename):
		"""
                Saves the current screen to png file.

                Parameters
                ----------

                filename : string
                    The path with filename to where we want the image saved.

                """
                frame = Image.fromarray( self.getScreenRGB() )
		frame.save(filename)

	def getScreenDims(self):
		"""
		Gets the games screen dimensions.
                
                Returns
                -------
                
                tuple of int
                    Returns a tuple of the following format (screen_width, screen_height).
		"""
		return self.game.getScreenDims()

	def getGameStateDims(self):
		"""
		Gets the games non-visual state dimensions.
                
                Returns
                -------
                
                tuple of int or None
                    Returns a tuple of the state vectors shape or None if the game does not support it.
		"""
		return self.state_dim

        def getGameState(self):
                """
                Gets a non-visual state representation of the game.

                This can include items such as player position, velocity, ball location and velocity etc.
                
                Returns
                -------

                dict or None
                    It returns a dict of game information. This greatly depends on the game in question and must be referenced against each game.
                    If no state is available or supported None will be returned back.

                """
                state = self.game.getGameState()
                if state != None and self.state_preprocessor != None:
                    return self.state_preprocessor(state)
                else: 
                    raise ValueError("Was asked to return state vector for game that does not support it!")

	def act(self, action):
		"""
		Perform an action on the game. We lockstep frames with actions. If act is not called the game will not run.

                Parameters
                ----------

                action : int
                    The index of the action we wish to perform. The index usually corresponds to the index item returned by getActionSet().

                Returns
                -------

                int
                    Returns the reward that the agent has accumlated while performing the action.

		"""
		sum_rewards = 0.0
		for i in range(self.frame_skip):
			sum_rewards += self._oneStepAct(action)

		return sum_rewards

	def _draw_frame(self):
                """
                Decides if the screen will be drawn too
                """

		if self.display_screen == True:
			pygame.display.update()

	def _oneStepAct(self, action):
                """
                Performs an action on the game. Checks if the game is over or if the provided action is valid based on the allowed action set.
                """
		if self.game_over():
			return 0.0

		if action not in self.getActionSet():
			action = self.NOOP

		self._setAction(action)
		for i in range(self.num_steps):
			time_elapsed = self._tick()
			self.game.step(time_elapsed)
			self._draw_frame()

		self.frame_count += self.num_steps

		return self._getReward()

	def _setAction(self, action):
		"""
			Pushes the action to pygame event queue.
		"""

		kd = pygame.event.Event(KEYDOWN, {"key": action})
		ku = pygame.event.Event(KEYUP, {"key": self.last_action})

		self.last_action = action
		
		#send it to the event stack
		pygame.event.post(kd) 
		pygame.event.post(ku)

	def _getReward(self):
                """
                Returns the reward the agent has gained as the difference between the last action and the current one.
                """
		reward = self.game.getScore() - self.previous_score
		self.previous_score = self.game.getScore()

		return reward
