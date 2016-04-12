Pong
=====

.. image:: /_static/pong.gif

Pong simulates 2D table tennis. The agent controls an in-game paddle which is used to hit the ball back to the other side. 

The agent controls the left paddle while the CPU controls the right paddle.

Valid Actions
-------------
Up and down control the direction of the paddle. The paddle has a little velocity added to it to allow smooth movements.


Terminal states (game_over)
---------------------------
The game is over if either the agent or CPU reach the number of points set by MAX_SCORE.


Rewards
-------
The agent receives a positive reward, of +1, for each successful ball placed behind the opponents paddle, while it loses a point, -1, if the ball goes behind its paddle.

.. currentmodule:: ple.games.pong
.. autoclass:: Pong
   :members: __init__, getGameState
