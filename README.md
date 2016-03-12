#PyGame-Learning-Environment

#### Probably has bugs so proceed with caution.

Wrapper that mimics Arcade Learning Enviroment.


## Why?

You can easily make arbitrary games quickly in PyGame. I attemping to do some work with Reinforcement Learning and found this useful to have!

## Games (current)
The plan is to eventually build up a games library of different tasks. I'm currently going through and porting games to PyGame. Original games author is in brackets. Current games:

* WaterWorld (Karpathy)
* PuckWorld (Karpathy)
* Pong (marti1125)
* Pixelcopter - Helicopter clone

## Examples
There are some examples of games in the examples folder. WaterWorld and PuckWorld are both inspired/taken from Andrej Karpathy's reinforcejs. Porting both games took a very short amount of time.

## Requirements
* numpy
* pygame
* pillow

## Installation

Clone the repo. 

Install with pip (`pip install -e .`). This will link it to the directory so you can pull new updates.

## Getting Started
Pygame-Learning-Enviroment (PLE) expects each game to expose some methods and information to it. The wrapper itself is simple and makes life easier when switching between games.

### PLE Usage
See `examples/random_agent.py`

### Game creation
See `examples/skeleton_game.py` for the required methods and attributes along with comments.


```
