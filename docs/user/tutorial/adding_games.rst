Adding Games
=============

We will walk through an implementation of the Catcher game inspired by Eder Santana. As we want to focus on the import aspects related to interfacing games with PLE we will ignore game specific code. 

Note: The full code is not included in each method. The full implementation, which implements scaling based on screen dimensions, is `found here`_.

Catcher is a simple game where the agent must catch 'fruit' dropped at random from the top of the screen with the 'paddle' controlled by the agent.

The main component of the game is enclosed in one class which inherits from :class:`base.Game <ple.games.base.Game>`:

.. code:: python

        from ple.games import base
        from pygame.constants import K_a, K_d

        class Catcher(base.Game):

                def __init__(self, width=48, height=48):
                
                        actions = {
                                "left": K_a,
                                "right": K_d
                        }

                        base.Game.__init__(self, width, height, actions=actions)

                        #game specific
                        self.lives = 0


The crucial porition in the ``__init__`` method is to call the parent class ``__init__`` and pass the width, height and valid actions the game responds too.

.. code:: python

        class Catcher(base.Game):

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

Next we cover four required methods: ``init``, ``getScore``, ``game_over``, and ``step``.

``init`` sets the game to a clean state. This method will perform other actions such as resetting paddle position and cleaning the screen.

``getScore`` returns the current score of the agent. You are free to pull information from the game to decide on a score, such as the number of lives left. Or can be as simple as returning the recorded score, always stored in ``self.score``.

``game_over`` must return True if the game has hit a terminal state. This depends greatly on game. In this case the agent loses a life for each fruit it fails to catch and causes the game to end if it hits 0.

``step`` method is the main logic of the game. It is called everytime we perform an action. It updates the game state by a small amount of time. This method performs actions such as updating player position based on key presses, checking hits between objects and adjusting agent score and lives. If this method is not called the game does not run.

Thats it! You only need a handful of methods defined to be able to interface your game with PLE. It is suggested to look through the different games inside of 

.. _`found here`: https://github.com/ntasfi/PyGame-Learning-Environment/blob/master/ple/games/catcher.py
