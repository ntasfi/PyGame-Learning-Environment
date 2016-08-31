import numpy as np
from ple import PLE
from ple.games import Doom

class NaiveAgent():
	"""
		This is our naive agent. It picks actions at random!
	"""
	def __init__(self, actions):
		self.actions = actions

	def pickAction(self, reward, obs):
		return self.actions[np.random.randint(0, len(self.actions))]

###################################
game = Doom(scenario="take_cover")

env = PLE(game)
agent = NaiveAgent(env.getActionSet())
env.init()

reward = 0.0
for f in range(15000):
	#if the game is over
        if env.game_over():
            env.reset_game()
            
        action = agent.pickAction(reward, env.getScreenRGB())
        reward = env.act(action)

        if f > 2000:
            env.display_screen = True 
            env.force_fps = False
        
        if f > 2250:
            env.display_screen = True 
            env.force_fps = True
