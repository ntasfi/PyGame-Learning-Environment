Non-Visual State Representation
================================

Sometimes it is useful to have non-visual state representations of games. This could be to try reduced state space, augment visual input, or for troubleshooting purposes. The majority of current games in PLE support non-visual state representations. To use these representations instead of visual inputs one needs to inspect the state structure given in the documentation. You are free to select sub-poritions ofthe state as agent input.

Lets setup an agent to use a non-visual state representation of :class:`Pong <ple.games.pong.Pong>`.

First start by examining the values :class:`Pong <ple.games.pong.Pong>` will return from the ``getGameState()`` method:

.. code-block:: python
        
        def getGameState(self):
            #other code above...

            state = {
                    "player": {
                        "y": self.agentPlayer.pos.y,
                        "velocity": self.agentPlayer.vel.y
                    },
                    "cpu": {
                        "y": self.cpuPlayer.pos.y
                    },
                    "ball": {
                        "x": self.ball.pos.x,
                        "y": self.ball.pos.y,
                        "velocity": {
                            "x": self.ball.pos.x,
                            "y": self.ball.pos.y
                        }
                    }
            }

            return state

We see that ``getGameState()`` of Pong returns several values each time it is called. Using the returned dictonary we can create a numpy vector representating our state.

This can be accomplished using a recursive method or by hand:

.. code-block:: python

        #recursive way
        def get_all_values(d, values):
                if isinstance(d, dict):
                        map(lambda _d: get_all_values(_d, values), d.values())
                else:
                        values.append(d)
        my_state = []
        get_all_values(state, my_state)
        my_state = np.array(my_state)
        
        #by-hand
        my_state = np.array([ state["player"]["x"], state["player"]["velocity"], ... ])

You have control over which values you want to include in the state vector. Training an agent would look like this:

.. code-block:: python

        from ple.games.pong import Pong 
        from ple import PLE
        import numpy as np

        def get_all_values(d, values):
                if isinstance(d, dict):
                        map(lambda _d: get_all_values(_d, values), d.values())
                else:
                        values.append(d)

        def process_state(state):
                _state = []
                get_all_values(state, _state)

                return np.array(_state).reshape((1, len((_state))))

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

To mae this work a state processor must be supplied to PLE's ``state_preprocessor`` initialization method. This function will be called each time we request the games state. We can also let our agent know the dimensions of the vector to expect from PLE. In the main loop just simply replace the call to ``getScreenGrayScale`` with ``getGameState``.
