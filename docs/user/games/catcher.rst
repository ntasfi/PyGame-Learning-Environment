Catcher
========

.. image:: /_static/catcher.gif

In Catcher the agent must catch falling fruit with its paddle. 


Valid Actions
-------------
Left and right control the direction of the paddle. The paddle has a little velocity added to it to allow smooth movements.


Terminal states (game_over)
---------------------------
The game is over when the agent lose the number of lives set by init_lives parmater.


Rewards
-------
The agent receives a positive reward, of +1, for each successful fruit catch, while it loses a point, -1, if the fruit is not caught.

.. currentmodule:: ple.games.catcher
.. autoclass:: Catcher
   :members: __init__, getGameState
