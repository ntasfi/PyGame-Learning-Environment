Pixelcopter
=============

.. image:: /_static/pixelcopter.gif

Pixelcopter is a side-scrolling game where the agent must successfully nagivate through a cavern. This is a clone of the popular helicopter game but where the player is a humble pixel. 

Valid Actions
-------------
Up which causes the pixel to accelerate upwards. 

Terminal states (game_over)
---------------------------
If the pixel makes contact with anything green the game is over.

Rewards
-------
For each vertical block it passes through it gains a positive reward of +1. Each time a terminal state reached it receives a negative reward of -1.

.. currentmodule:: ple.games.pixelcopter
.. autoclass:: Pixelcopter
   :members: __init__, getGameState
