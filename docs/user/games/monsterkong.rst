Monster Kong
=============

.. image:: /_static/monsterkong.gif

A spinoff of the original Donkey Kong game. Objective of the game is to avoid fireballs while collecting coins and rescuing the princess. An additional monster is added each time the princess is rescued.


Valid Actions
-------------
Use w, a, s, d and space keys to move around player around.


Terminal states (game_over)
---------------------------
The game is over when the player hits three fireballs. Touching a monster does not kill cause the agent to lose lives.

Rewards
-------

The player gains +5 for collecting a coin while losing a life and receiving a reward of -25 for hitting a fireball. The player gains +50 points for rescuing a princess.

Note: Images were sourced from various authors. You can find the respective artist listed in the assets directory folder of the game.
