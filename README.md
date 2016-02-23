#PyGame-Learning-Environment

### Probably as bugs and issues so proceed with caution.

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

See `examples/skeleton_game.py` for the required methods and fields along with comments.

After its as simple as this to get the game running with agent inputs:

```python
game = PuckWorld()
p = PLE(game)

frames_per_episode = 3000
for i in range(frames_per_episode):
	idx = np.random.randint(0, 4)
	action = p.getActionSet()[idx]

	reward = p.act(action)

```


#Potential caveats & considerations.
We currently perform one step of game emulation (draw/update), more if frame_skip is enabled, per `.act(_action_)` call. 

Which means if your agent requires alot of work between each `.act(_action_)` call it can slow down the fps. The delay only becomes an issue at high fps (above 40) and high delay (75 - 100 ms). This can be mitigated in many ways such as setting a `frame_skip` or increasing `fps`. 

Currently unsure if this is a big issue since we generally care about number of frames seen rather than the time per frame or true fps.