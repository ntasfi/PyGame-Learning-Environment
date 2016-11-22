#!/usr/bin/python


"""

This tests that all the PLE games launch, except for doom; we
explicitly check that it isn't defined.


"""


import nose
import numpy as np
import unittest

NUM_STEPS=150

class NaiveAgent():
    def __init__(self, actions):
        self.actions = actions
    def pickAction(self, reward, obs):
        return self.actions[np.random.randint(0, len(self.actions))]


class MyTestCase(unittest.TestCase):

    def run_a_game(self,game):
        from ple import PLE
        p =  PLE(game,display_screen=True)
        agent = NaiveAgent(p.getActionSet())
        p.init()
        reward = p.act(p.NOOP)
        for i in range(NUM_STEPS):
            obs = p.getScreenRGB()
            reward = p.act(agent.pickAction(reward,obs))

    def test_catcher(self):
        from ple.games.catcher import Catcher
        game = Catcher()
        self.run_a_game(game)

    def test_monsterkong(self):
        from ple.games.monsterkong import MonsterKong
        game = MonsterKong()
        self.run_a_game(game)

    def test_flappybird(self):
        from ple.games.flappybird import FlappyBird
        game = FlappyBird()
        self.run_a_game(game)

    def test_pixelcopter(self):
        from ple.games.pixelcopter import Pixelcopter
        game = Pixelcopter()
        self.run_a_game(game)

    def test_puckworld(self):
        from ple.games.puckworld import PuckWorld
        game = PuckWorld()
        self.run_a_game(game)

    def test_raycastmaze(self):
        from ple.games.raycastmaze import RaycastMaze
        game = RaycastMaze()
        self.run_a_game(game)

    def test_snake(self):
        from ple.games.snake import Snake
        game = Snake()
        self.run_a_game(game)

    def test_waterworld(self):
        from ple.games.waterworld import WaterWorld
        game = WaterWorld()
        self.run_a_game(game)

    def test_pong(self):
        from ple.games.pong import Pong
        game = Pong()
        self.run_a_game(game)

    def test_doom_not_defined(self):
        from nose.tools import assert_raises
        def invoke_doom():
            DoomWrapper
        assert_raises(NameError,invoke_doom)


if __name__ == "__main__":
    nose.runmodule()
