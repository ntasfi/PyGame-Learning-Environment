import os
from ..base import DoomWrapper

class Doom(DoomWrapper):
    
    def __init__(self, scenario="basic"):
        cfg_file = "assets/cfg/%s.cfg" % scenario
        scenario_file = "assets/wad/%s.wad" % scenario
        width = 320 
        height = 240
        
        package_directory = os.path.dirname(os.path.abspath(__file__))
        cfg_file = os.path.join( package_directory, cfg_file )
        scenario_file = os.path.join( package_directory, scenario_file )
        
        DoomWrapper.__init__(self, width, height, 
                cfg_file, scenario_file)
