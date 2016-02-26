import pygame
import numpy as np
from PIL import Image #pillow

from pygame.constants import KEYDOWN, KEYUP, K_F15 #this is our NOOP?

class PLE(object):

	def __init__(self, game, fps=30, frame_skip=1, num_steps=1, force_fps=True, display_screen=True, NOOP=K_F15):
		self.game = game
		self.fps = fps
		self.frame_skip = frame_skip
		self.NOOP = NOOP
		self.num_steps = num_steps
		self.force_fps = force_fps
		self.display_screen = display_screen

		self.last_action = []
		self.action = []
		self.score = 0
		self.previous_score = 0
		self.frame_count = 0

		self.init()
		self.game.init()

	def _tick(self):
		"""
			In physics games the movements are updated based on how much time has elapsed between ticks. 
			Issues occur if there is delay between ticks, such as if an agent needs to calculate the next move.


			To fix this we tell the game to move a consistent amount between ticks by passing it a consistent number
			based on the desired delay per frame.

			If we do not care about this we can set force_fps=False so that it returns to using Clock.tick_busy_loop, 
			which dynamically adjusts the delay between frames.

		"""
		if self.force_fps:
			return 1000.0/self.fps
		else:
			return self.game.clock.tick_busy_loop(self.fps)

	def init(self):
		pygame.init()
		self.game.screen = pygame.display.set_mode( self.getScreenDims(), 0, 32)
		self.game.clock = pygame.time.Clock()

	def getActionSet(self):
		return self.game.actions.values()

	def game_over(self):
		return self.game.game_over()

	def lives(self):
		return self.game.lives

	def reset_game(self):
		self.game.reset()

	def getScreenRGB(self):
		return pygame.surfarray.array3d(pygame.display.get_surface())

	def getScreenGrayscale(self):
		frame = self.getScreenRGB()
		frame = 0.21*frame[:, :, 0] + 0.72*frame[:, :, 1] + 0.07*frame[:, :, 2]
		frame = np.round(frame).astype(np.uint8)

		return frame

	def saveScreen(self, filename):
		frame = Image.fromarray( self.getScreenRGB() )
		frame.save(filename)

	def getScreenDims(self):
		"""
			Returns a tuple that contains (screen_width, screen_height)
		"""
		return self.game.getScreenDims()

	def act(self, action):
		"""
			Perform an action on the game. We lockstep frames with actions. If act is not called the game will not run.
		"""
		sum_rewards = 0
		for i in range(self.frame_skip):
			sum_rewards += self._oneStepAct(action)

		return sum_rewards

	def _draw_frame(self):
		if self.display_screen == True:
			pygame.display.update()

	def _oneStepAct(self, action):
		if self.game_over():
			return 0

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
		reward = self.game.getScore() - self.previous_score
		self.previous_score = self.game.getScore()

		return reward