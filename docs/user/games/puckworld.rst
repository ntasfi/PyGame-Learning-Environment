PuckWorld
==========

.. image:: /_static/puckworld.gif

In PuckWorld the agent, a blue circle, must navigate towards the green dot while avoiding the larger red puck.

The green dot randomly moves around the screen while the red puck slowly follows the agent.

Valid Actions
-------------
Up, down, left and right apply thrusters to the agent. It adds velocity to the agent which decays over time.

Terminal states (game_over)
---------------------------
None. This is a continuous game.

Rewards
-------
The agent is rewarded based on its distance to the green dot, where lower values are good. If the agent is within the large red radius it receives a negative reward. The negative reward is proportional to the agents distance from the pucks center. 

.. currentmodule:: ple.games.puckworld
.. autoclass:: PuckWorld
   :members: __init__, getGameState
