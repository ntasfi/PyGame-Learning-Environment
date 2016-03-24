import pygame
import numpy as np
from raycast import RayCastPlayer

class RaycastMaze(RayCastPlayer):


    def __init__(self,
            init_dir=(1.0, 0.0), init_pos=(1,1), resolution=1,
            move_speed=10, turn_speed=7, 
            map_size=10, height=48, width=48):

        assert map_size >= 5, "map_size must be gte 5"


        block_types = {
            0: {
                "pass_through": True,
                "color": None
            },
            1: {
                "pass_through": False,
                "color": (255, 255, 255)
            },
            2: {
                "pass_through": False,
                "color": (255, 100, 100)
            }
        }

        self.init_pos = np.array([init_pos], dtype=np.float32)
        self.init_dir = np.array([init_dir], dtype=np.float32)
        self.init_plane = np.array([(0.0, 0.66)], dtype=np.float32)
        
        RayCastPlayer.__init__(self, None,
                init_pos, init_dir, width, height, resolution, 
                move_speed, turn_speed, self.init_plane, block_types)

        self.height = height
        self.width = width
        self.score = 0.0
        self.screen = None
        self.clock = None
        self.screen_dim = ( self.height, self.width )

        self.obj_loc = None
        self.map_size = map_size

    def _make_maze(self, complexity=0.75, density=0.75):
        """
            ty wikipedia?
        """
        dim = np.floor( self.map_size / 2 )*2+1
        shape = (dim, dim)

        complexity = int(complexity*(5*(shape[0]+shape[1])))
        density = int(density*(shape[0]//2*shape[1]//2))

        # Build actual maze
        Z = np.zeros(shape, dtype=bool)
        # Fill borders
        Z[0,:] = Z[-1,:] = 1
        Z[:,0] = Z[:,-1] = 1
        # Make isles
        for i in range(density):
            x = np.random.random_integers(0,shape[1]//2)*2
            y = np.random.random_integers(0,shape[0]//2)*2

            Z[y,x] = 1
            for j in range(complexity):
                neighbours = []
                if x > 1:           neighbours.append( (y,x-2) )
                if x < shape[1]-2:  neighbours.append( (y,x+2) )
                if y > 1:           neighbours.append( (y-2,x) )
                if y < shape[0]-2:  neighbours.append( (y+2,x) )
                if len(neighbours):
                    y_,x_ = neighbours[np.random.random_integers(0,len(neighbours)-1)]
                    if Z[y_,x_] == 0:
                        Z[y_,x_] = 1
                        Z[y_+(y-y_)//2, x_+(x-x_)//2] = 1
                        x, y = x_, y_

        return Z.astype(int)

    def getScreenDims(self):
        return self.screen_dim

    def getActions(self):
        return self.actions.values()

    def getScore(self):
        return self.score

    def game_over(self):
        obj_loc = self.obj_loc + 0.5
        dist = np.sqrt(np.sum((self.pos - obj_loc)**2.0))
        
        if dist < 1.0:
            self.score += 1.0
            return True
        else:
            return False

    def init(self):
        self.screen.fill((0,0,0))
        self.pos = np.copy(self.init_pos)
        self.dir = np.copy(self.init_dir)
        self.plane = np.copy(self.init_plane)

        self.map_ = self._make_maze()
        
        self.obj_loc = np.random.randint(3, high=self.map_size-1, size=(2))
        self.map_[ self.obj_loc[0], self.obj_loc[1] ] = 2

    def reset(self):
        self.init()

    def step(self, dt):
        self.screen.fill((0,0,0))

        pygame.draw.rect(self.screen, (92,92,92), (0, self.height/2, self.width, self.height))

        self._handle_player_events(dt)

        c, t, b, col = self.draw()

        for i in range(len(c)):
            color = (col[i][0], col[i][1], col[i][2])
            p0 = (c[i], t[i])
            p1 = (c[i], b[i])

            pygame.draw.line(self.screen, color, p0, p1, self.resolution)

if __name__ == "__main__":
    fps = 60
    pygame.init()

    game = RaycastMaze(
        map_size=5
    )

    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(fps)
        
        if game.game_over():
            game.reset()
            print "Game over!"

        game.step(dt)
        
        pygame.display.update()
