WaterWorld
===========

.. image:: /_static/waterworld.gif

In WaterWorld the agent, a blue circle, must navigate around the world capturing green circles while avoiding red ones. 

After capture a circle it will respawn in a random location as either red or green. The game is over if all the green circles have been captured.

Valid Actions
-------------
Up, down, left and right apply thrusters to the agent. It adds velocity to the agent which decays over time.

Terminal states (game_over)
---------------------------
The game ends when all the green circles have been captured by the agent.

Rewards
-------
For each green circle captured the agent receives a positive reward of +1; while hitting a red circle causes a negative reward of -1.

.. currentmodule:: ple.games.waterworld
.. autoclass:: WaterWorld
   :members: __init__, getGameState
