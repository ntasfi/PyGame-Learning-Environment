class Game(object):
    """Game base class

    ple.games.base.Game(width, height, actions={})
    
    This :class:`Game` class sets methods all games require. It should be subclassed when creating new games.

    Parameters
    ----------
    width: int
        The width of the game screen.

    height: int
        The height of the game screen.

    actions: dict
        Contains possible actions that the game responds too. The dict keys are used by the game, while the values are `pygame.constants` referring the keys. 
        
        Possible actions dict:

        >>> from pygame.constants import K_w, K_s
        >>> actions = {
        >>>     "up": K_w,
        >>>     "down": K_s
        >>> }
    """
    def __init__(self, width, height, actions={}):

        #Required fields
        self.actions = actions #holds actions

        self.score = 0.0 #required.
        self.lives = 0 #required. Can be 0 or -1 if not required.
        self.screen = None #must be set to None
        self.clock = None #must be set to None
        self.height = height
        self.width = width
        self.screen_dim = (width, height) #width and height
        self.allowed_fps = None #fps that the game is allowed to run at.


    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------
        dict or None
            dict if the game supports it and None otherwise.

        """
        return None

    def getScreenDims(self):
        """
        Gets the screen dimensions of the game in tuple form.

        Returns
        -------
        tuple of int
            Returns tuple as follows (width, height).

        """
        return self.screen_dim

    def getActions(self):
        """
        Gets the actions used within the game.

        Returns
        -------
        list of `pygame.constants`

        """
        return self.actions.values()

    def init(self):
        """
        This is used to initialize the game, such reseting the score, lives, and player position. 

        This is game dependent.

        """
        raise NotImplementedError("Please override this method")

    def reset(self):
        """
        Wraps the init() function, can be setup to reset certain poritions of the game only if needed. 
        """
        self.init()

    def getScore(self):
        """
        Return the current score of the game.


        Returns
        -------
        int 
            The current reward the agent has received since the last init() or reset() call. 
        """
        raise NotImplementedError("Please override this method")

    def game_over(self):
        """
        Gets the status of the game, returns True if game has hit a terminal state. False otherwise. 

        This is game dependent.

        Returns
        -------
        bool

        """
        raise NotImplementedError("Please override this method")

    def step(self, dt):
        """
        This method steps the game forward one step in time equal to the dt parameter. The game does not run unless this method is called.

        Parameters
        ----------
        dt : integer
            This is the amount of time elapsed since the last frame in milliseconds.
        
        """
        raise NotImplementedError("Please override this method")
