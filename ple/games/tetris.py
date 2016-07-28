import base
import pygame
import numpy as np
import tetris_engine as game_engine

class Tetris(base.PyGameWrapper):
    def __init__(self, width=200, height=400):
        self.game_state = game_engine.GameState()
        actions = {}
        for i,v in enumerate(self.game_state.getActionSet()):
            actions[str(i)]=v
        base.PyGameWrapper.__init__(self, width, height, actions=actions)
        self.last_action = None

    def getGameState(self):
        """

        Returns
        -------

        None
            Does not have a non-visual representation of game state.

        """
        return None

    def getScore(self):
        return self.game_state.getReward()

    def game_over(self):
        return self.game_state.isGameOver()

    def init(self):
        return self.game_state.reinit()

    def reset(self):
        self.init()

    def step(self, dt):
        self._action_set = np.zeros([len(self.game_state.getActionSet())])
        self._action_set[self.last_action] = 1
        reward = 0.0
        state, reward, terminal = self.game_state.frame_step(self._action_set)
        return reward

    def _setAction(self, action, last_action):
        self.last_action = action

if __name__ == "__main__":
    fps = 60
    pygame.init()
    game = Tetris()
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(fps)

        if game.game_over():
            print "Game over!"
            print "Resetting!"
            game.reset()

        game.step(dt)

        pygame.display.update()
