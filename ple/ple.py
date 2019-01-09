import numpy as np
from PIL import Image  # pillow
import sys

import pygame
from .games.base.pygamewrapper import PyGameWrapper

class PLE(object):
    """
    ple.PLE(
        game, fps=30,
        frame_skip=1, num_steps=1,
        reward_values={}, force_fps=True,
        display_screen=False, add_noop_action=True,
        NOOP=K_F15, state_preprocessor=None,
        rng=24
    )

    Main wrapper that interacts with games.
    Provides a similar interface to Arcade Learning Environment.

    Parameters
    ----------
    game: Class from ple.games.base
        The game the PLE environment manipulates and maintains.

    fps: int (default: 30)
        The desired frames per second we want to run our game at.
            Typical settings are 30 and 60 fps.

    frame_skip: int (default: 1)
        The number of times we skip getting observations while
        repeat an action.

    num_steps: int (default: 1)
        The number of times we repeat an action.

    reward_values: dict
        This contains the rewards we wish to set give our agent based on
        different actions in game. The current defaults are as follows:

        .. code-block:: python

            rewards = {
                "positive": 1.0,
                "negative": -1.0,
                "tick": 0.0,
                "loss": -5.0,
                "win": 5.0
            }

        Tick is given to the agent at each game step. You can selectively
        adjust the rewards by passing a dictonary with the key you want to
        change. Eg. If we want to adjust the negative reward and the tick
        reward we would pass in the following:

        .. code-block:: python

            rewards = {
                "negative": -2.0,
                "tick": -0.01
            }

        Keep in mind that the tick is applied at each frame. If the game is
        running at 60fps the agent will get a reward of 60*tick.

    force_fps: bool (default: True)
        If False PLE delays between game.step() calls to ensure the fps is
        specified. If not PLE passes an elapsed time delta to ensure the
        game steps by an amount of time consistent with the specified fps.
        This is usally set to True as it allows the game to run as fast as
        possible which speeds up training.

    display_screen: bool (default: False)
        If we draw updates to the screen. Disabling this speeds up
        interation speed. This can be toggled to True during testing phases
        so you can observe the agents progress.

    add_noop_action: bool (default: True)
        This inserts the NOOP action specified as a valid move the agent
        can make.

    state_preprocessor: python function (default: None)
        Python function which takes a dict representing game state and
        returns a numpy array.

    rng: numpy.random.RandomState, int, array_like or None. (default: 24)
        Number generator which is used by PLE and the games.

    """

    def __init__(self,
                 game, fps=30, frame_skip=1, num_steps=1,
                 reward_values={}, force_fps=True, display_screen=False,
                 add_noop_action=True, state_preprocessor=None, rng=24):

        self.game = game
        self.fps = fps
        self.frame_skip = frame_skip
        self.NOOP = None
        self.num_steps = num_steps
        self.force_fps = force_fps
        self.display_screen = display_screen
        self.add_noop_action = add_noop_action

        self.last_action = []
        self.action = []
        self.previous_score = 0
        self.frame_count = 0

        # update the scores of games with values we pick
        if reward_values:
            self.game.adjustRewards(reward_values)


        if isinstance(self.game, PyGameWrapper):
            if isinstance(rng, np.random.RandomState):
                self.rng = rng
            else:
                self.rng = np.random.RandomState(rng)

            # some pygame games preload the images
            # to speed resetting and inits up.
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        else:
            # in order to use doom, install following https://github.com/openai/doom-py
            from .games.base.doomwrapper import DoomWrapper
            if isinstance(self.game, DoomWrapper):
                self.rng = rng
        
        self.game.setRNG(self.rng)
        self.init()

        self.state_preprocessor = state_preprocessor
        self.state_dim = None

        if self.state_preprocessor is not None:
            self.state_dim = self.game.getGameState()

            if self.state_dim is None:
                raise ValueError(
                    "Asked to return non-visual state on game that does not support it!")
            else:
                self.state_dim = self.state_preprocessor(self.state_dim).shape

        if game.allowed_fps is not None and self.fps != game.allowed_fps:
            raise ValueError("Game requires %dfps, was given %d." %
                             (game.allowed_fps, game.allowed_fps))

    def _tick(self):
        """
        Calculates the elapsed time between frames or ticks.
        """
        if self.force_fps:
            return 1000.0 / self.fps
        else:
            return self.game.tick(self.fps)

    def init(self):
        """
        Initializes the game. This depends on the game and could include
        doing things such as setting up the display, clock etc.

        This method should be explicitly called.
        """
        self.game._setup()
        self.game.init() #this is the games setup/init

    def getActionSet(self):
        """
        Gets the actions the game supports. Optionally inserts the NOOP
        action if PLE has add_noop_action set to True.

        Returns
        --------

        list of pygame.constants
            The agent can simply select the index of the action
            to perform.

        """
        actions = self.game.actions

        if (sys.version_info > (3, 0)): #python ver. 3
            if isinstance(actions, dict) or isinstance(actions, dict_values):
                actions = actions.values()
        else:
            if isinstance(actions, dict):
                actions = actions.values()

        actions = list(actions) #.values()
        #print (actions)
        #assert isinstance(actions, list), "actions is not a list"

        if self.add_noop_action:
            actions.append(self.NOOP)

        return actions

    def getFrameNumber(self):
        """
        Gets the current number of frames the agent has seen
        since PLE was initialized.

        Returns
        --------

        int

        """

        return self.frame_count

    def game_over(self):
        """
        Returns True if the game has reached a terminal state and
        False otherwise.

        This state is game dependent.

        Returns
        -------

        bool

        """

        return self.game.game_over()

    def score(self):
        """
        Gets the score the agent currently has in game.

        Returns
        -------

        int

        """

        return self.game.getScore()

    def lives(self):
        """
        Gets the number of lives the agent has left. Not all games have
        the concept of lives.

        Returns
        -------

        int

        """

        return self.game.lives

    def reset_game(self):
        """
        Performs a reset of the games to a clean initial state.
        """
        self.last_action = []
        self.action = []
        self.previous_score = 0.0
        self.game.reset()

    def getScreenRGB(self):
        """
        Gets the current game screen in RGB format.

        Returns
        --------
        numpy uint8 array
            Returns a numpy array with the shape (width, height, 3).


        """

        return self.game.getScreenRGB()

    def getScreenGrayscale(self):
        """
        Gets the current game screen in Grayscale format. Converts from RGB using relative lumiance.

        Returns
        --------
        numpy uint8 array
                Returns a numpy array with the shape (width, height).


        """
        frame = self.getScreenRGB()
        frame = 0.21 * frame[:, :, 0] + 0.72 * \
            frame[:, :, 1] + 0.07 * frame[:, :, 2]
        frame = np.round(frame).astype(np.uint8)

        return frame

    def saveScreen(self, filename):
        """
        Saves the current screen to png file.

        Parameters
        ----------

        filename : string
            The path with filename to where we want the image saved.

        """
        frame = Image.fromarray(self.getScreenRGB())
        frame.save(filename)

    def getScreenDims(self):
        """
        Gets the games screen dimensions.

        Returns
        -------

        tuple of int
            Returns a tuple of the following format (screen_width, screen_height).
        """
        return self.game.getScreenDims()

    def getGameStateDims(self):
        """
        Gets the games non-visual state dimensions.

        Returns
        -------

        tuple of int or None
            Returns a tuple of the state vectors shape or None if the game does not support it.
        """
        return self.state_dim

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        This can include items such as player position, velocity, ball location and velocity etc.

        Returns
        -------

        dict or None
            It returns a dict of game information. This greatly depends on the game in question and must be referenced against each game.
            If no state is available or supported None will be returned back.

        """
        state = self.game.getGameState()
        if state is not None:
            if self.state_preprocessor is not None:
                return self.state_preprocessor(state)
            return state
        else:
            raise ValueError(
                "Was asked to return state vector for game that does not support it!")

    def act(self, action):
        """
        Perform an action on the game. We lockstep frames with actions. If act is not called the game will not run.

        Parameters
        ----------

        action : int
            The index of the action we wish to perform. The index usually corresponds to the index item returned by getActionSet().

        Returns
        -------

        int
            Returns the reward that the agent has accumlated while performing the action.

        """
        return sum(self._oneStepAct(action) for i in range(self.frame_skip))

    def _draw_frame(self):
        """
        Decides if the screen will be drawn too
        """

        self.game._draw_frame(self.display_screen)

    def _oneStepAct(self, action):
        """
        Performs an action on the game. Checks if the game is over or if the provided action is valid based on the allowed action set.
        """
        if self.game_over():
            return 0.0

        if action not in self.getActionSet():
            action = self.NOOP

        self._setAction(action)
        for i in range(self.num_steps):
            time_elapsed = self._tick()
            self.game.step(time_elapsed)
            self._draw_frame()

        self.frame_count += self.num_steps

        return self._getReward()

    def _setAction(self, action):
        """
            Instructs the game to perform an action if its not a NOOP
        """

        if action is not None:
            self.game._setAction(action, self.last_action)

        self.last_action = action

    def _getReward(self):
        """
        Returns the reward the agent has gained as the difference between the last action and the current one.
        """
        reward = self.game.getScore() - self.previous_score
        self.previous_score = self.game.getScore()

        return reward
