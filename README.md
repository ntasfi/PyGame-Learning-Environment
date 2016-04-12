#PyGame-Learning-Environment

![Games](ple_games.jpg?raw=True "Games!")

**PyGame Learning Environment (PLE)** is a learning environment, mimicking the [Arcade Learning Environment](https://github.com/mgbellemare/Arcade-Learning-Environment) interface, allowing a quick start to Reinforcement Learning in Python. The goal of PLE is allow practitioners to focus design of models and experiments instead of environment design.

PLE hopes to eventually build an expansive library of games.

## Documentation

Docs for the project can be [found here](http://pygame-learning-environment.readthedocs.org/). They are current a WIP.

## Games
Original games author in brackets:

* WaterWorld (Karpathy)
* PuckWorld (Karpathy)
* Pong (marti1125)
* Pixelcopter - Helicopter clone
* Raycast Maze
* FlappyBird 
* Snake
* Catcher (EderSantana)

## Getting started

A `PLE` instance requires a game exposing a set of control methods. To see the required methods look at `ple/games/base.py`. 

Here's an example of importing Pong from the games library within PLE:

```python
from ple.games.pong import Pong

game = Pong()
```

Next we configure and initialize PLE:

```python
from ple import PLE

p = PLE(game, fps=30, display_screen=True, force_fps=False)
p.init()
```

The options above instruct PLE to display the game screen, with `display_screen`, while allowing PyGame to select the appropriate delay timing between frames to ensure 30fps with `force_fps`.

You are free to use any agent with the PLE. Below we create a fictional agent and grab the valid actions:

```python
myAgent = MyAgent(p.getActionSet())
```

We can now have our agent, with the help of PLE, interact with the game over a certain number of frames:

```python

nb_frames = 1000
reward = 0.0

for f in range(nb_frames):
	if p.game_over(): #check if the game is over
		p.reset_game()

	obs = p.getScreenRGB()
	action = myAgent.pickAction(reward, obs)
	reward = p.act(action)

```

Just like that we have our agent interacting with our game environment.

## Installation

PLE requires the following dependencies:
* numpy
* pygame
* pillow

Clone the repo and install with pip.

```bash
git clone https://github.com/ntasfi/PyGame-Learning-Environment.git
cd PyGame-Learning-Environment/
pip install -e .
``` 

## Updating

`cd` into the `PyGame-Learning-Environment` directory and run the following:

```bash
git pull
```

## Todos
 * Documentation is currently in progress.
 * Tests
 * Parallel Learning (One agent, many game copies)
 * Add games
 * Generalize the library (eg. add Pyglet support)

