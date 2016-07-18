import numpy as np
from ple import PLE
from ple.games.waterworld import WaterWorld


# lets adjust the rewards our agent recieves
rewards = {
    "tick": -0.01,  # each time the game steps forward in time the agent gets -0.1
    "positive": 1.0,  # each time the agent collects a green circle
    "negative": -5.0,  # each time the agent bumps into a red circle
}

# make a PLE instance.
# use lower fps so we can see whats happening a little easier
game = WaterWorld(width=256, height=256, num_creeps=8)
p = PLE(game, fps=15, force_fps=False, display_screen=True,
        reward_values=rewards)
# we pass in the rewards and PLE will adjust the game for us

p.init()
actions = p.getActionSet()
for i in range(1000):
    if p.game_over():
        p.reset_game()

    action = actions[np.random.randint(0, len(actions))]  # random actions
    reward = p.act(action)

    print "Score: {:0.3f} | Reward: {:0.3f} ".format(p.score(), reward)
