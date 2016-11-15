#!/usr/bin/python

import nose


import nose
import numpy as np
import unittest


class NaiveAgent():
    def __init__(self, actions):
        self.actions = actions
    def pickAction(self, reward, obs):
        return self.actions[np.random.randint(0, len(self.actions))]


class MyTestCase(unittest.TestCase):

    def run_a_game(self,game):

        from ple import PLE
        p =  PLE(game)
        agent = NaiveAgent(p.getActionSet())
        p.init()
        reward = p.act(p.NOOP)
        for i in range(50):
            obs = p.getScreenRGB()
            reward = p.act(agent.pickAction(reward,obs))

    def test_doom(self):
        from ple.games.doom import Doom
        game = Doom()
        self.run_a_game(game)

if __name__ == "__main__":
    nose.runmodule()


