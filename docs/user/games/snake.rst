Snake
======

.. image:: /_static/snake.gif

Snake is a game where the agent must maneuver a line which grows in length each time food is touched by the head of the segment. The line follows the previous paths taken which eventually become obstacles for the agent to avoid.

The food is randomly spawned inside of the valid window while checking it does not make contact with the snake body.

Valid Actions
-------------
Up, down, left, and right. It cannot turn back on itself. Eg. if its moving downwards it cannot move up.

Terminal states (game_over)
---------------------------
If the head of the snake comes in contact with any of the walls or its own body (can occur after only 7 segments) the game is over.

Rewards
-------
It recieves a positive reward, +1, for each red square the head comes in contact with. While getting -1 for each terminal state it reaches.

.. currentmodule:: ple.games.snake
.. autoclass:: Snake
   :members: __init__, getGameState
