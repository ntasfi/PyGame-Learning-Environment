.. _home:

=====
Home
=====

Installation
---------------

PLE requires the following libraries to be installed:

* numpy
* pillow
* pygame

PyGame can be installed using this `tutorial`_.

.. _tutorial: http://www.pygame.org/wiki/CompileUbuntu

To install PLE first clone the repo:

.. code-block:: bash

   git clone https://github.com/ntasfi/PyGame-Learning-Environment

Then use the ``cd`` command to enter the ``PyGame-Learning-Environment`` directory and run the command:

.. code-block:: bash
        
   sudo pip install -e .

This will install PLE as an editable library with pip.

Quickstart
---------------

PLE allows agents to train against games through a standard model supplied by :class:`ple.PLE <ple.PLE>`, which interacts and manipulates games on behalf of your agent. PLE mimics the `Arcade Learning Environment`_ (ALE) interface as closely as possible. This means projects using the ALE interface can easily be adjusted to use PLE with minimal effort.

If you do not wish to perform such modifications you can write your own code that interacts with PLE or use libraries with PLE support such as `General Deep Q RL`_.

Here is an example of having an agent run against :class:`FlappyBird <ple.games.flappybird>`.

.. code-block:: python

        from ple.games.flappybird import FlappyBird
        from ple import PLE


        game = FlappyBird()
        p = PLE(game, fps=30, display_screen=True)
        agent = myAgentHere(allowed_actions=p.getActionSet())

        p.init()
        reward = 0.0

        for i in range(nb_frames):
           if p.game_over():
                   p.reset_game()

           observation = p.getScreenRGB()
           action = agent.pickAction(reward, observation)
           reward = p.act(action)

.. _Arcade Learning Environment: https://github.com/mgbellemare/Arcade-Learning-Environment
.. _General Deep Q RL: https://github.com/VinF/General_Deep_Q_RL
