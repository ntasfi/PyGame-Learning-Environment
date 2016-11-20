from .. import base
import numpy as np
import pygame
import sys
import tetris_engine as game_engine
from pygame.constants import K_SPACE, K_LEFT, K_RIGHT, K_r, K_l

class Tetris(base.PyGameWrapper):
    def __init__(self, width=200, height=400):
        self.game_state = game_engine.GameState()
        self.allowed_fps = 30  # restrict the fps

        self.actions = {
            "None": '',
            "left": K_LEFT,
            "rotate left": K_l,
            "right": K_RIGHT,
            "rotate right": K_r,
            "drop": K_SPACE,
        }
        base.PyGameWrapper.__init__(self, width, height, actions=self.actions)
        self.last_act = None

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

    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key in self.actions.values():
                    self.last_act = self.actions.values().index(key)

    def step(self, dt):
        self._action_set = np.zeros([len(self.actions)])
        self._handle_player_events()
        if self.last_act:
            self._action_set[self.last_act] = 1
        reward = 0.0
        state, reward, terminal = self.game_state.frame_step(self._action_set)
        return reward

if __name__ == "__main__":
    fps = 30
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
