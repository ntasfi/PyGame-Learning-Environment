
#import .base
from .base.pygamewrapper import PyGameWrapper
import pygame
import numpy as np
import math
from .raycast import RayCastPlayer
from pygame.constants import K_w, K_a, K_d, K_s


class RaycastMaze(PyGameWrapper, RayCastPlayer):
    """
    Parameters
    ----------
    init_pos : tuple of int (default: (1,1))
        The position the player starts on in the grid. The grid is zero indexed.

    resolution : int (default: 1)
        This instructs the Raycast engine on how many vertical lines to use when drawing the screen. The number is equal to the width / resolution.

    move_speed : int (default: 20)
        How fast the agent moves forwards or backwards.

    turn_speed : int (default: 13)
        The speed at which the agent turns left or right.

    map_size : int (default: 10)
        The size of the maze that is generated. Must be greater then 5. Can be incremented to increase difficulty by adjusting the attribute between game resets.

    width : int (default: 48)
        Screen width.

    height : int (default: 48)
        Screen height, recommended to be same dimension as width.
        
    init_pos_distance_to_target : int (default None aka. map_size)
        Useful for curriculum learning, slowly move target away from init position to improve learning

    """

    def __init__(self,
                 init_pos=(1, 1), resolution=1,
                 move_speed=20, turn_speed=13,
                 map_size=10, height=48, width=48,
                 init_pos_distance_to_target=None):

        assert map_size > 5, "map_size must be gte 5"

        # do not change
        init_dir = (1.0, 0.0)
        init_plane = (0.0, 0.66)

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
        actions = {
            "forward": K_w,
            "left": K_a,
            "right": K_d,
            "backward": K_s
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)

        RayCastPlayer.__init__(self, None,
                               init_pos, init_dir, width, height, resolution,
                               move_speed, turn_speed, init_plane, actions, block_types)

        self.init_pos = np.array([init_pos], dtype=np.float32)
        self.init_dir = np.array([init_dir], dtype=np.float32)
        self.init_plane = np.array([init_plane], dtype=np.float32)

        self.obj_loc = None
        if init_pos_distance_to_target is None:
            init_pos_distance_to_target = map_size
        init_pos_distance_to_target = max(2, init_pos_distance_to_target)
        self.init_pos_distance_to_target = init_pos_distance_to_target
        self.map_size = map_size
        self.is_game_over = False

    def _make_maze(self, complexity=0.75, density=0.75):
        """
            ty wikipedia?
        """
        dim = int(np.floor(self.map_size / 2) * 2 + 1)
        shape = (dim, dim)

        complexity = int(complexity * (5 * (shape[0] + shape[1])))
        density = int(density * (shape[0] // 2 * shape[1] // 2))

        # Build actual maze
        Z = np.zeros(shape, dtype=bool)
        # Fill borders
        Z[0, :] = Z[-1, :] = 1
        Z[:, 0] = Z[:, -1] = 1
        # Make isles
        for i in range(density):
            x = self.rng.random_integers(0, shape[1] // 2) * 2
            y = self.rng.random_integers(0, shape[0] // 2) * 2

            Z[y, x] = 1
            for j in range(complexity):
                neighbours = []
                if x > 1:
                    neighbours.append((y, x - 2))
                if x < shape[1] - 2:
                    neighbours.append((y, x + 2))
                if y > 1:
                    neighbours.append((y - 2, x))
                if y < shape[0] - 2:
                    neighbours.append((y + 2, x))
                if len(neighbours):
                    y_, x_ = neighbours[
                        self.rng.random_integers(
                            0, len(neighbours) - 1)]
                    if Z[y_, x_] == 0:
                        Z[y_, x_] = 1
                        Z[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 1
                        x, y = x_, y_

        return Z.astype(int)

    def getGameState(self):
        """

        Returns
        -------

        None
            Does not have a non-visual representation of game state.
            Would be possible to return the location of the maze end.

        """
        return None

    def getScore(self):
        return self.score

    def game_over(self):
        return self.is_game_over

    def init(self):
        self.score = 0 #reset score
        self.is_game_over = False
        self.pos = np.copy(self.init_pos)
        self.dir = np.copy(self.init_dir)
        self.plane = np.copy(self.init_plane)

        self.map_ = self._make_maze()
        sqr_dist = self.init_pos_distance_to_target ** 2

        available_positions = []
        for y in range(self.map_size):
            for x in range(self.map_size):
                # in a distance of curriculum learning
                dist = (x - self.pos[0][0]) ** 2 + (y - self.pos[0][1]) ** 2
                if dist < sqr_dist:
                    # in a wall
                    if self.map_[y, x] == 1:
                        # by the wall access to this point
                        if self.map_[y-1, x] == 0 or self.map_[y+1, x] == 0 or self.map_[y, x-1] == 0 or self.map_[y, x-1] == 0:
                            available_positions.append([y,x])


        self.obj_loc = np.array(available_positions[self.rng.randint(0, high=len(available_positions))])
        self.map_[self.obj_loc[0], self.obj_loc[1]] = 2

    def reset(self):
        self.init()

    def normalize(self, vector):
        norm = math.sqrt(vector[0][0] ** 2 + vector[0][1] ** 2)
        vector[0][0] /= norm
        vector[0][1] /= norm
        return vector

    def step(self, dt):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (92, 92, 92),
                         (0, self.height / 2, self.width, self.height))

        if not self.is_game_over:
            self.score += self.rewards["tick"]

            self._handle_player_events(dt)

            c, t, b, col = self.draw()

            for i in range(len(c)):
                color = (col[i][0], col[i][1], col[i][2])
                p0 = (c[i], t[i])
                p1 = (c[i], b[i])

                pygame.draw.line(self.screen, color, p0, p1, self.resolution)

            dist = np.sqrt(np.sum((self.pos - self.obj_loc)**2.0))

            dir_to_loc = self.obj_loc - self.pos
            dir_to_loc = self.normalize(dir_to_loc)
            dir_norm = self.normalize(np.copy(self.dir))
            angle_rad = np.arccos(np.dot(dir_to_loc[0], dir_norm[0]))

            # Close to target object and in sight
            if dist < 1.6 and angle_rad < 1.2:
                self.score += self.rewards["win"]
                self.is_game_over = True

if __name__ == "__main__":
    import numpy as np

    fps = 60
    pygame.init()

    game = RaycastMaze(
        height=256,
        width=256,
        map_size=10
    )

    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(fps)

        if game.game_over():
            print("Game over!")
            print("Resetting!")
            game.reset()

        game.step(dt)

        pygame.display.update()
