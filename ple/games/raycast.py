import pdb
import time
import os
import sys

import pygame
import numpy as np
from pygame.constants import K_w, K_a, K_d, K_s

import copy

class RayCastPlayer():
    """
    Loosely based on code from Lode's `Computer Graphics Tutorial`_.

    .. _Computer Graphics Tutorial: http://lodev.org/cgtutor/raycasting.html

    Takes input from key presses and traverses a map
    """

    def __init__(self, map_, init_pos, init_dir,
                 width, height, resolution, move_speed,
                 turn_speed, plane, actions, block_types):

        self.actions = actions

        self.map_ = map_
        self.width = width
        self.height = height

        self.pos = np.array([init_pos], dtype=np.float32)
        self.dir = np.array([init_dir], dtype=np.float32)
        self.plane = np.array([plane], dtype=np.float32)

        self.resolution = resolution
        self.move_speed = move_speed
        self.turn_speed = turn_speed

        self.eps = 1e-7

        self.block_types = block_types

    def _handle_player_events(self, dt):
        dt = dt / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key

                new_location = self.pos

                if key == self.actions["forward"]:
                    new_location = self.pos + self.dir * self.move_speed * dt

                if key == self.actions["backward"]:
                    new_location = self.pos - self.dir * self.move_speed * dt

                new_location = new_location.astype(int)

                newX, newY = new_location[0, :]

                if newX < self.map_.shape[0] and newY < self.map_.shape[1]:
                    new_map = self.map_[newX, newY]

                    if self.block_types[new_map]["pass_through"]:

                        if key == self.actions["forward"]:
                            self.pos[0, 0] += self.dir[0, 0] * \
                                self.move_speed * dt
                            self.pos[0, 1] += self.dir[0, 1] * \
                                self.move_speed * dt

                        if key == self.actions["backward"]:
                            self.pos[0, 0] -= self.dir[0, 0] * \
                                self.move_speed * dt
                            self.pos[0, 1] -= self.dir[0, 1] * \
                                self.move_speed * dt

                if key == self.actions["right"]:
                    X_TURN = np.cos(self.turn_speed * dt)
                    Y_TURN = np.sin(self.turn_speed * dt)

                    _dirX = self.dir[0, 0] * X_TURN - self.dir[0, 1] * Y_TURN
                    _dirY = self.dir[0, 0] * Y_TURN + self.dir[0, 1] * X_TURN

                    _planeX = self.plane[0, 0] * \
                        X_TURN - self.plane[0, 1] * Y_TURN
                    _planeY = self.plane[0, 0] * \
                        Y_TURN + self.plane[0, 1] * X_TURN

                    self.dir[0, 0] = _dirX
                    self.dir[0, 1] = _dirY

                    self.plane[0, 0] = _planeX
                    self.plane[0, 1] = _planeY

                if key == self.actions["left"]:
                    X_INV_TURN = np.cos(-self.turn_speed * dt)
                    Y_INV_TURN = np.sin(-self.turn_speed * dt)

                    _dirX = self.dir[0, 0] * X_INV_TURN - \
                        self.dir[0, 1] * Y_INV_TURN
                    _dirY = self.dir[0, 0] * Y_INV_TURN + \
                        self.dir[0, 1] * X_INV_TURN

                    _planeX = self.plane[0, 0] * X_INV_TURN - \
                        self.plane[0, 1] * Y_INV_TURN
                    _planeY = self.plane[0, 0] * Y_INV_TURN + \
                        self.plane[0, 1] * X_INV_TURN

                    self.dir[0, 0] = _dirX
                    self.dir[0, 1] = _dirY

                    self.plane[0, 0] = _planeX
                    self.plane[0, 1] = _planeY


    def draw(self):
        #N = width/resolution
        # N,2
        cameraX = np.arange(
            0.0,
            self.width,
            self.resolution).astype(
            np.float32)[
            :,
            np.newaxis]
        cameraX = 2.0 * cameraX / float(self.width) - 1.0

        # set the rayPos to the players current position
        ray_pos = np.tile(self.pos, [cameraX.shape[0], 1])  # N,2

        # ray direction
        ray_dir = self.dir + self.plane * cameraX  # N,2

        # which box of the map we're in
        map_ = ray_pos.astype(int)

        ray_pow = np.power(ray_dir, 2.0) + self.eps
        ray_div = ray_pow[:, 0] / (ray_pow[:, 1])
        delta_dist = np.sqrt(
            1.0 + np.array([1.0 / (ray_div), ray_div])).T  # N,2

        # N,2
        step = np.ones(ray_dir.shape).astype(int)
        step[ray_dir[:, 0] < 0, 0] = -1
        step[ray_dir[:, 1] < 0, 1] = -1

        # N,2
        side_dist = (map_ + 1.0 - ray_pos) * delta_dist
        _value = (ray_pos - map_) * delta_dist

        side_dist[ray_dir[:, 0] < 0, 0] = _value[ray_dir[:, 0] < 0, 0]
        side_dist[ray_dir[:, 1] < 0, 1] = _value[ray_dir[:, 1] < 0, 1]

        side_dist, delta_dist, map_, side = self._DDA(
            side_dist, delta_dist, map_, step)

        perpWallDistX = (map_[:, 0] - ray_pos[:, 0] + (1.0 - step[:, 0]) / 2.0)
        perpWallDistX = perpWallDistX / (ray_dir[:, 0] + self.eps)
        perpWallDistX = perpWallDistX[:, np.newaxis]

        perpWallDistY = (map_[:, 1] - ray_pos[:, 1] + (1.0 - step[:, 1]) / 2.0)
        perpWallDistY = perpWallDistY / (ray_dir[:, 1] + self.eps)
        perpWallDistY = perpWallDistY[:, np.newaxis]

        perpWallDist = perpWallDistY
        perpWallDist[side == 0] = perpWallDistX[side == 0]

        lineHeights = (self.height / (perpWallDist + self.eps)).astype(int)

        tops = -(lineHeights) / 2.0 + self.height / 2.0
        tops[tops < 0] = 0.0
        tops = tops.astype(int)

        bottoms = lineHeights / 2.0 + self.height / 2.0
        bottoms[bottoms >= self.height] = self.height - 1
        bottoms = bottoms.astype(int)

        visible_blocks = self.map_[map_[:, 0], map_[:, 1]]
        coloring = np.ones((bottoms.shape[0], 3)) * 255.0

        for k in self.block_types.keys():
            if self.block_types[k] is not None:
                c = self.block_types[k]["color"]
                sel = visible_blocks == k
                coloring[sel] = np.tile(c, [bottoms.shape[0], 1])[sel]

        shading = np.abs(perpWallDist * 15) * 1.5
        coloring = coloring - shading
        coloring = np.clip(coloring, 0, 255)
        coloring[(side == 1.0).flatten(), :] *= 0.65  # lighting apparently

        cameraX = np.arange(0, self.width, self.resolution)
        returns = [cameraX, tops, bottoms, coloring]

        return [r.astype(int) for r in returns]

    def _DDA(self, side_dist, delta_dist, map_, step):
        # tested against for-loop version using line_profiler
        # for-loop take about 0.005968s per call
        # this version takes 0.000416s per call
        hits = np.zeros((map_.shape[0], 1))
        side = np.zeros((map_.shape[0], 1))

        while np.sum(hits) < side_dist.shape[0]:
            # only update values that havent hit a wall. So are 0 still.

            update_mask = np.logical_not(hits).astype(np.bool)

            # 1 => 1, 0
            # 0 => 0, 1
            mask = (side_dist[:, 0] < side_dist[:, 1])[:, np.newaxis]

            sel = (update_mask & (mask == True)).flatten()
            side_dist[sel, 0] += delta_dist[sel, 0]
            map_[sel, 0] += step[sel, 0]
            side[sel] = np.zeros(side.shape)[sel]

            sel = (update_mask & (mask == False)).flatten()
            side_dist[sel, 1] += delta_dist[sel, 1]
            map_[sel, 1] += step[sel, 1]
            side[sel] = np.ones(side.shape)[sel]

            # once it becomes 1 it never goes back to 0.
            hits = np.logical_or(
                hits, (self.map_[
                    map_[
                        :, 0], map_[
                        :, 1]] > 0)[
                    :, np.newaxis])

        return side_dist, delta_dist, map_, side


def make_map(dim):
    map_grid = np.zeros((dim, dim))
    map_grid[0, :] = 1.0
    map_grid[:, 0] = 1.0
    map_grid[:, -1] = 1.0
    map_grid[-1, :] = 1.0

    return map_grid


def make_box(grid, p0, p1, fill=0, isFilled=True):
    x0, y0 = p0
    x1, y1 = p1

    if isFilled:
        grid[x0:x1, y0:y1] = fill
    else:
        grid[x0, y0:y1 + 1] = fill
        grid[x1, y0:y1 + 1] = fill
        grid[x0:x1, y0] = fill
        grid[x0:x1, y1] = fill

    return grid

if __name__ == "__main__":
    map_grid = make_map(15)

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
            "color": (220, 100, 100)
        },

        3: {
            "pass_through": False,
            "color": (100, 220, 100)
        },

        4: {
            "pass_through": False,
            "color": (100, 100, 220)
        }
    }

    map_grid = make_box(map_grid, (5, 5), (9, 9), fill=2, isFilled=False)
    map_grid = make_box(map_grid, (8, 8), (14, 14), fill=3, isFilled=True)
    map_grid = make_box(map_grid, (1, 2), (3, 9), fill=4, isFilled=False)
    map_grid = make_box(map_grid, (11, 6), (12, 11), fill=0, isFilled=True)
    map_grid = make_box(map_grid, (6, 11), (12, 12), fill=0, isFilled=True)
    map_grid = make_box(map_grid, (2, 6), (7, 7), fill=0, isFilled=True)

    map_grid[map_grid > 0] = np.random.randint(
        2, high=5, size=map_grid[map_grid > 0].shape)

    init_dir = (1.0, 0.0)
    init_pos = (1, 1)
    width = 128
    height = 128
    resolution = 1
    move_speed = 15
    turn_speed = 10.5
    plane = (0.0, 0.66)

    actions = {
        "forward": K_w,
        "left": K_a,
        "right": K_d,
        "backward": K_s
    }

    rc = RayCastPlayer(
        map_grid,
        init_pos,
        init_dir,
        width,
        height,
        resolution,
        move_speed,
        turn_speed,
        plane,
        actions,
        block_types
    )
    pygame.init()

    screen = pygame.display.set_mode((width, height), 0, 24)
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60)
        screen.fill((0, 0, 0))

        pygame.draw.rect(screen, (92, 92, 92), (0, height / 2, width, height))

        rc._handle_player_events(dt)

        c, t, b, col = rc.draw()

        for i in range(len(c)):
            pygame.draw.line(screen, (col[i][0], col[i][1], col[i][2]), (c[
                             i], t[i]), (c[i], b[i]), rc.resolution)

        pygame.display.update()
