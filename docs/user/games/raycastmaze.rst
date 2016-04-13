RaycastMaze
============

.. image:: /_static/raycastmaze.gif

In RaycastMaze the agent must navigate a 3D environment searching for the exit denoted with a bright red square.

It is possible to increase the map size by 1 each time it successfully solves the maze. As seen below.

Example
-------
>>> #init and setup etc.
>>> while True:
>>>   if game.game_over():
>>>     game.map_size += 1
>>>   game.step(dt) #assume dt is given

**Not valid code above.** 

Valid Actions
-------------
Forwards, backwards, turn left and turn right.

Terminal states (game_over)
---------------------------
When the agent is a short distance, nearly touching the red square, the game is considered over.

Rewards
-------
Currently it receives a postive reward of +1 when it finds the red block.

.. currentmodule:: ple.games.raycastmaze
.. autoclass:: RaycastMaze
   :members: __init__, getGameState
