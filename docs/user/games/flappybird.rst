FlappyBird
===========

.. image:: /_static/flappybird.gif

Flappybird is a side-scrolling game where the agent must successfully nagivate through gaps between pipes. 

FPS Restrictions
----------------
This game is restricted to 30fps as the physics at higher and lower framerates feels slightly off. You can remove this by setting the `allowed_fps` parameter to `None`.

Valid Actions
-------------
Up causes the bird to accelerate upwards. 

Terminal states (game_over)
---------------------------
If the bird makes contact with the ground, pipes or goes above the top of the screen the game is over.

Rewards
-------
For each pipe it passes through it gains a positive reward of +1. Each time a terminal state is reached it receives a negative reward of -1.

.. currentmodule:: ple.games.flappybird
.. autoclass:: FlappyBird
   :members: __init__, getGameState
