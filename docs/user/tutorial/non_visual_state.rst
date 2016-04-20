Non-Visual State Representation
================================

Sometimes it is useful to have non-visual state representations of games. This could be to try reduced state space, augment visual input, or for troubleshooting purposes. The majority of current games in PLE support non-visual state representations. To use these representations instead of visual inputs one needs to inspect the state structure given in the documentation. You are free to select sub-poritions ofthe state as agent input.

Lets setup an agent to use a non-visual state representation of :class:`Pong <ple.games.pong.Pong>`.

First start by examining the values :class:`Pong <ple.games.pong.Pong>` will return from the ``getGameState()`` method:

.. code-block:: python
        
        def getGameState(self):
            #other code above...

            state = {
                "player_y": self.agentPlayer.pos.y,
                "player_velocity": self.agentPlayer.vel.y,
                "cpu_y": self.cpuPlayer.pos.y,
                "ball_x": self.ball.pos.x,
                "ball_y": self.ball.pos.y,
                "ball_velocity_x": self.ball.pos.x,
                "ball_velocity_y": self.ball.pos.y
            }

            return state

We see that ``getGameState()`` of Pong returns several values each time it is called. Using the returned dictonary we can create a numpy vector representating our state.

This can be accomplished in the following ways:

.. code-block:: python

        #easiest
        my_state = np.array([ state.values() ])

        #by-hand
        my_state = np.array([ state["player"]["x"], state["player"]["velocity"], ... ])

You have control over which values you want to include in the state vector. Training an agent would look like this:

.. code-block:: python

        from ple.games.pong import Pong 
        from ple import PLE
        import numpy as np

        def process_state(state):
                return np.array([ state.values() ])

        game = Pong()
        p = PLE(game, display_screen=True, state_preprocessor=process_state)
        agent = myAgentHere(input_shape=p.getGameStateDims(), allowed_actions=p.getActionSet())

        p.init()
        nb_frames = 10000
        reward = 0.0
        for i in range(nb_frames):
           if p.game_over():
                   p.reset_game()

           state = p.getGameState()
           action = agent.pickAction(reward, state)
           reward = p.act(action)

To make this work a state processor must be supplied to PLE's ``state_preprocessor`` initialization method. This function will be called each time we request the games state. We can also let our agent know the dimensions of the vector to expect from PLE. In the main loop just simply replace the call to ``getScreenGrayScale`` with ``getGameState``.

Be aware different games will have different dictonary structures. The majority of games will return back a flat dictory structure but others will have lists inside of them. In particular games with variable objects to track, such as the number of segments in snake, require usage of lists within the dictonary.


.. code-block:: python

        state = {
            "snake_head_x": self.player.head.pos.x, 
            "snake_head_y": self.player.head.pos.y,
            "food_x": self.food.pos.x, 
            "food_y": self.food.pos.y,
            "snake_body": []
        }

The ``"snake_body"`` field contains a dynamic number of values. It must be taken into consideration when creating your state preprocessor.
