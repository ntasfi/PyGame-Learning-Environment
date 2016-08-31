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
* doom-py (if using doom)

PyGame
#######

PyGame can be installed using this `tutorial`_ (Ubuntu). For mac you can use these following instructions;

.. code-block:: bash

   brew install sdl sdl_ttf sdl_image sdl_mixer portmidi  # brew or use equivalent means
   conda install -c https://conda.binstar.org/quasiben pygame  # using Anaconda

.. _tutorial: http://www.pygame.org/wiki/CompileUbuntu

ViZDoom (optional)
##################

If you are on mac you can install the dependicies as follows:

.. code-block:: bash

   brew install cmake boost boost-python

If you are on Ubuntu (only test on 14.04) type:

.. code-block:: bash

   apt-get install -y cmake zlib1g-dev libjpeg-dev libboost-all-dev gcc libsdl2-dev wget unzip

Finally install OpenAI's excellent wrapper `doom-py` with the following command:

.. code-block:: bash

   sudo pip install doom-py

Or you can clone the `repo here`_ and install with pip.

PLE
###

To install PLE first clone the repo:

.. code-block:: bash

   git clone https://github.com/ntasfi/PyGame-Learning-Environment

Then use the ``cd`` command to enter the ``PyGame-Learning-Environment`` directory and run the command:

.. code-block:: bash
        
   sudo pip install -e .

This will install PLE as an editable library with pip.

.. _repo here: https://github.com/openai/doom-py

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
