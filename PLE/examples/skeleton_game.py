class Game(object):

    def __init__(self, actions={}, fps=30):

        #Required fields
        self.actions = actions #holds actions
        self.score = 0.0 #required.
        self.lives = 0 #required. Can be 0 or -1 if not required.
        self.screen = None #must be set to None
        self.clock = None #must be set to None
        self.screen_dim = (0, 0) #width and height

    def getScreenDims(self):
        """
            Return a tuple of screen_dim
        """
        return self.screen_dim

    def getActions(self):
        return self.actions

    def init(self):
        """
            Set the games initial state.
            Reset score, player/enemy positions etc.
        """
        raise NotImplementedError("Please override this method")

    def reset(self):
        """
            Resets the game. Can usually just wrap init() in here.
            Unless the game has some notion of check points
        """
        raise NotImplementedError("Please override this method")

    def getScore(self):
        """
            Return the score
        """
        return self.score

    def game_over(self):
        """
            Return bool if the game has 'finished'
        """
        raise NotImplementedError("Please override this method")

    def step(self, time_elapsed):
        """
            Perform one step of game emulation.
        """
        raise NotImplementedError("Please override this method")