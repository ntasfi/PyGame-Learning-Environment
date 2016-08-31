import sys
import time
import numpy as np
import pygame

try:
    #ty @ gdb & ppaquette
    import doom_py
    import doom_py.vizdoom as vizdoom
except ImportError:
    raise ImportError("Please install doom_py.")

class DoomWrapper(object):


    def __init__(self, width, height, cfg_file, scenario_file):

        self.doom_game = doom_py.DoomGame() 
        self._loader = doom_py.Loader()

        #make most sense to keep cfg and wads together.
        #which is why we ship them all together
        self.cfg_file = cfg_file 
        self.scenario_file = self._loader.get_scenario_path(scenario_file) 
       
        self.freedom_file = self._loader.get_freedoom_path()
        self.vizdoom_file = self._loader.get_vizdoom_path()

        self.state = None
        self.num_actions = 0
        self.action = None
        self.NOOP = [0]*40

        self.height = height
        self.width = width
        self.screen_dim = (width, height)
        self.allowed_fps = None
        self.rng = None

        self._window = DoomWindow(width, height)

    def _setup(self):
        self.doom_game.set_screen_format(vizdoom.ScreenFormat.BGR24)
        
        #load the cfg
        self.doom_game.load_config(self.cfg_file)
        
        self.doom_game.set_vizdoom_path(self.vizdoom_file)
        self.doom_game.set_doom_game_path(self.freedom_file)
        self.doom_game.set_doom_scenario_path(self.scenario_file)
        self.doom_game.set_window_visible(False) #we use our own window...

        self.doom_game.init()
        
        self.num_actions = self.doom_game.get_available_buttons_size()

        self.actions = []
        for i in range(self.num_actions):
            action = [0]*self.num_actions
            action[i] = 1
            self.actions.append(action)

    def _setAction(self, action, last_action):
        #make the game perform the action
        self.action = action

    def _draw_frame(self, draw_screen):
        if draw_screen:
            self._window.show_frame(self.getScreenRGB())

    def setRNG(self, rng):
        if isinstance(rng, int):
            self.rng = rng
            self.doom_game.set_seed(rng)
        else:
            raise ValueError("ViZDoom needs an int passed as rng")

    def getScreenRGB(self):
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
        self.action = None
        self.doom_game.new_episode()
        self.state = self.doom_game.get_state()

    def reset(self):
        self.init()

    def getScore(self):
        return self.doom_game.get_total_reward()

    def game_over(self):
        return self.doom_game.is_episode_finished()

    def _handle_window_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.doom_game.close() #doom quit
                pygame.quit() #close window
                sys.exit() #close game

    def step(self, dt):
        self._handle_window_events()

        self.state = self.doom_game.get_state()
        
        if self.action is None:
            _ = self.doom_game.make_action(self.NOOP)
        else:
            _ = self.doom_game.make_action(self.action)

class DoomWindow(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height

        pygame.init()
        self.window = pygame.display.set_mode( (self.width, self.height), pygame.DOUBLEBUF, 24 )
        pygame.display.set_caption("PLE ViZDoom")

    def show_frame(self, frame):
        frame = np.rollaxis(frame, 0, 2) #its HEIGHT, WIDTH, 3
        pygame.surfarray.blit_array(self.window, frame)
        pygame.display.update()
