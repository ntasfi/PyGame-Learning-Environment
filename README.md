#PyGame-Learning-Environment

#### Probably has bugs so proceed with caution.

Wrapper that mimics Arcade Learning Enviroment.


# Why?

You can easily make arbitrary games quickly in PyGame. I attemping to do some work with Reinforcement Learning and found this useful to have!


# Examples
There are some examples of games in the examples folder. WaterWorld and PuckWorld are both inspired/taken from Andrej Karpathy's reinforcejs. Writing both games took a very short amount of time.


# Requirements
* numpy
* pygame


# Getting Started
Pygame-Learning-Enviroment (PLE) expects each game to expose some methods and information to it. The wrapper itself is simple and makes life easier when switching between games.

See `PLE/examples/skeleton_game.py` for the required methods and fields along with comments.

After setting a game up to allow agent inputs:

```python
game = PuckWorld()
p = PLE(game)

frames_per_episode = 3000
for i in range(frames_per_episode):
	idx = np.random.randint(0, 4)
	action = p.getActionSet()[idx]

	reward = p.act(action)

```