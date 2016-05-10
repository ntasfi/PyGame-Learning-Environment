Wrapping and Adding PyGame Games
=================================

Adding or wrapping games to work with PLE is relatively easy. You must implement a few methods, explained below, to have a game be useable with PLE. We will walk through an implementation of the Catcher game inspired by Eder Santana to examine the required methods for games. As we want to focus on the important aspects related to the game interface we will ignore game specific code. 

Note: The full code is not included in each method. The full implementation, which implements scaling based on screen dimensions, is `found here`_.

Catcher is a simple game where the agent must catch 'fruit' dropped at random from the top of the screen with the 'paddle' controlled by the agent.

The main component of the game is enclosed in one class that inherits from :class:`base.PyGameWrapper <ple.games.base.PyGameWrapper>`:

.. code:: python

        from ple.games import base
        from pygame.constants import K_a, K_d

        class Catcher(base.PyGameWrapper):

                def __init__(self, width=48, height=48):
                
                        actions = {
                                "left": K_a,
                                "right": K_d
                        }

                        base.Game.__init__(self, width, height, actions=actions)

                        #game specific
                        self.lives = 0


The game must inherit from :class:`base.PyGameWrapper <ple.games.base.PyGameWrapper>` as it sets attributes and methods used by PLE to control game flow, scoring and other functions.

The crucial porition in the ``__init__`` method is to call the parent class ``__init__`` and pass the width, height and valid actions the game responds too.

Next we cover four required methods: ``init``, ``getScore``, ``game_over``, and ``step``. These methods are all required to interact with our game.

The code below is within our ``Catcher`` class and has the class definition repeated for clarity:

.. code:: python

        class Catcher(base.PyGameWrapper):

                def init(self):
                        self.score = 0        

                        #game specific
                        self.lives = 3

                def getScore(self):
                        return self.score

                def game_over(self):
                        return self.lives == 0

                def step(self, dt):
                        #move players
                        #check hits
                        #adjust scores
                        #remove lives


The ``init`` method sets the game to a clean state. The minimum this method must do is to reset the ``self.score`` attribute of the game. It is also strongly recommended this method perform other game specific functions such as player position and clearing the screen. This is important as the game might still be in a terminal state if the player and object positions are not reset; which would result in endless resetting of the environment.

``getScore`` returns the current score of the agent. You are free to pull information from the game to decide on a score, such as the number of lives left etc. or you can simply return the ``self.score`` attribute.

``game_over`` must return True if the game has hit a terminal state. This depends greatly on game. In this case the agent loses a life for each fruit it fails to catch and causes the game to end if it hits 0.

``step`` method is responsible for the main logic of the game. It is called everytime our agent performs an action on the game environment. ``step`` performs a step in game time equal to ``dt``. ``dt`` is required to allow the game to run at different frame rates such that the movement speeds of objects are scaled by elapsed time. With that said the game can be locked to a specific frame rate, by setting ``self.allowed_fps``, and written such that ``step`` moves game objects at rates suitable for the locked frame rate. The function signature always expects ``dt`` to be passed, the game logic does not have to use it though. 

Thats it! You only need a handful of methods defined to be able to interface your game with PLE. It is suggested to look through the different games inside of the `games folder`_. 

.. _`found here`: https://github.com/ntasfi/PyGame-Learning-Environment/blob/master/ple/games/catcher.py
.. _`games folder`: https://github.com/ntasfi/PyGame-Learning-Environment/blob/master/ple/games/
