import ipdb

import os
import sys
import itertools
import time
import numpy as np

sys.path.append("/home/ntasfi/ViZDoom/bin/python/")

try:
    import vizdoom
except ImportError:
    raise ImportError("Please install ViZDoom.")

class DoomWrapper(object):


    def __init__(self, doom_game, width, height, 
            cfg_file, scenario_file):

        self.doom_game = doom_game
        
        self.cfg_file = cfg_file 
        self.scenario_file = scenario_file 
       
        _root = os.environ["VIZDOOM_ROOT"]
        self.freedom_file = os.path.join( _root, "scenarios/freedoom2.wad" )
        self.vizdoom_file = os.path.join( _root, "bin/vizdoom" )
        print self.vizdoom_file

        self.state = None
        self.actions = []
        self.num_actions = 0
        self.action = None
        self.last_action = None

        self.height = height
        self.width = width
        self.screen_dim = (width, height)
        self.allowed_fps = None
        self.rng = None

    def _init(self):
        #load the cfg
        self.doom_game.load_config(self.cfg_file)
        
        self.doom_game.set_vizdoom_path(self.vizdoom_file)
        self.doom_game.set_doom_game_path(self.freedom_file)
        self.doom_game.set_doom_scenario_path(self.scenario_file)

        #overwrite with sane defaults. we expect RGB values
        self.doom_game.set_screen_format(vizdoom.ScreenFormat.RGB24)

        self.doom_game.init()
        
        ipdb.set_trace()

        self.num_actions = self.doom_game.get_available_buttons_size()
        for perm in itertools.product([True, False], repeat=self.num_actions):
            self.actions.append(list(perm))


    def _setAction(self, action, last_action):
        #make the game perform the action
        self.last_action = self.action
        self.action = action

    def _draw_frame(self, draw_screen):
        #devices if the screen will be drawn
        pass

    def setRNG(self, rng):
        if isinstance(rng, int):
            self.rng = rng
            self.doom_game.set_seed(rng)
        else:
            raise ValueError("ViZDoom needs an int passed as rng")

    def getScreenRGB(self):
        #return a RGB of the screen
        return self.state.image_buffer.copy()

    def tick(self, fps):
        time.sleep(1.0/fps) #sleep a bit here (in seconds)
        return fps

    def adjustRewards(self, rewards):
        if "tick" in rewards:
            self.doom_game.set_living_reward(rewards["tick"])

        if "loss" in rewards:
            self.doom_game.set_death_penalty(rewards["loss"])

    def getGameState(self):
        return self.doom_game.get_state().game_variables

    def getScreenDims(self):
        return self.screen_dim

    def getActions(self):
        return self.actions

    def init(self):
        #used to init the game.
        self.doom_game.new_episode()
        self.state = self.doom_game.get_state()

    def reset(self):
        self.init()

    def getScore(self):
        return self.doom_game.get_total_reward()

    def game_over(self):
        return self.doom_game.is_episode_finished()

    def step(self, dt):
        self.state = self.doom_game.get_state()
        
        action = self.action
        if action is None:
            action = [False]*self.num_actions

        _ = self.doom_game.make_action(action)
