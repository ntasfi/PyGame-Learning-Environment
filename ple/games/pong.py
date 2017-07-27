import math
import sys

import pygame
from pygame.constants import K_w, K_s
from ple.games.utils.vec2d import vec2d
from ple.games.utils import percent_round_int

#import base
from ple.games.base.pygamewrapper import PyGameWrapper

class Ball(pygame.sprite.Sprite):

    def __init__(self, radius, speed, rng,
                 pos_init, SCREEN_WIDTH, SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)

        self.rng = rng
        self.radius = radius
        self.speed = speed
        self.pos = vec2d(pos_init)
        self.pos_before = vec2d(pos_init)
        self.vel = vec2d((speed, -1.0 * speed))

        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH

        image = pygame.Surface((radius * 2, radius * 2))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            image,
            (255, 255, 255),
            (radius, radius),
            radius,
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def line_intersection(self, p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):

        s1_x = p1_x - p0_x
        s1_y = p1_y - p0_y
        s2_x = p3_x - p2_x
        s2_y = p3_y - p2_y

        s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
        t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)

        return (s >= 0 and s <= 1 and t >= 0 and t <= 1)

    def update(self, agentPlayer, cpuPlayer, dt):

        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt

        is_pad_hit = False

        if self.pos.x <= agentPlayer.pos.x + agentPlayer.rect_width:
            if self.line_intersection(self.pos_before.x, self.pos_before.y, self.pos.x, self.pos.y, agentPlayer.pos.x + agentPlayer.rect_width / 2, agentPlayer.pos.y - agentPlayer.rect_height / 2, agentPlayer.pos.x + agentPlayer.rect_width / 2, agentPlayer.pos.y + agentPlayer.rect_height / 2):
                self.pos.x = max(0, self.pos.x)
                self.vel.x = -1 * (self.vel.x + self.speed * 0.05)
                self.vel.y += agentPlayer.vel.y * 2.0
                self.pos.x += self.radius
                is_pad_hit = True

        if self.pos.x >= cpuPlayer.pos.x - cpuPlayer.rect_width:
            if self.line_intersection(self.pos_before.x, self.pos_before.y, self.pos.x, self.pos.y, cpuPlayer.pos.x - cpuPlayer.rect_width / 2, cpuPlayer.pos.y - cpuPlayer.rect_height / 2, cpuPlayer.pos.x - cpuPlayer.rect_width / 2, cpuPlayer.pos.y + cpuPlayer.rect_height / 2):
                self.pos.x = min(self.SCREEN_WIDTH, self.pos.x)
                self.vel.x = -1 * (self.vel.x + self.speed * 0.05)
                self.vel.y += cpuPlayer.vel.y * 0.006
                self.pos.x -= self.radius
                is_pad_hit = True

        # Little randomness in order not to stuck in a static loop
        if is_pad_hit:
            self.vel.y += self.rng.random_sample() * 0.001 - 0.0005

        if self.pos.y - self.radius <= 0:
            self.vel.y *= -0.99
            self.pos.y += 1.0

        if self.pos.y + self.radius >= self.SCREEN_HEIGHT:
            self.vel.y *= -0.99
            self.pos.y -= 1.0

        self.pos_before.x = self.pos.x
        self.pos_before.y = self.pos.y

        self.rect.center = (self.pos.x, self.pos.y)


class Player(pygame.sprite.Sprite):

    def __init__(self, speed, rect_width, rect_height,
                 pos_init, SCREEN_WIDTH, SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)

        self.speed = speed
        self.pos = vec2d(pos_init)
        self.vel = vec2d((0, 0))

        self.rect_height = rect_height
        self.rect_width = rect_width
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH

        image = pygame.Surface((rect_width, rect_height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 255, 255),
            (0, 0, rect_width, rect_height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dy, dt):
        self.vel.y += dy * dt
        self.vel.y *= 0.9

        self.pos.y += self.vel.y

        if self.pos.y - self.rect_height / 2 <= 0:
            self.pos.y = self.rect_height / 2
            self.vel.y = 0.0

        if self.pos.y + self.rect_height / 2 >= self.SCREEN_HEIGHT:
            self.pos.y = self.SCREEN_HEIGHT - self.rect_height / 2
            self.vel.y = 0.0

        self.rect.center = (self.pos.x, self.pos.y)

    def updateCpu(self, ball, dt):
        dy = 0.0
        if ball.vel.x >= 0 and ball.pos.x >= self.SCREEN_WIDTH / 2:
            dy = self.speed
            if self.pos.y > ball.pos.y:
                dy = -1.0 * dy
        else:
            dy = 1.0 * self.speed / 4.0

            if self.pos.y > self.SCREEN_HEIGHT / 2.0:
                dy = -1.0 * self.speed / 4.0

        if self.pos.y - self.rect_height / 2 <= 0:
            self.pos.y = self.rect_height / 2
            self.vel.y = 0.0

        if self.pos.y + self.rect_height / 2 >= self.SCREEN_HEIGHT:
            self.pos.y = self.SCREEN_HEIGHT - self.rect_height / 2
            self.vel.y = 0.0

        self.pos.y += dy * dt
        self.rect.center = (self.pos.x, self.pos.y)


class Pong(PyGameWrapper):
    """
    Loosely based on code from marti1125's `pong game`_.

    .. _pong game: https://github.com/marti1125/pong/

    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    MAX_SCORE : int (default: 11)
        The max number of points the agent or cpu need to score to cause a terminal state.
        
    cpu_speed_ratio: float (default: 0.5)
        Speed of opponent (useful for curriculum learning)
        
    players_speed_ratio: float (default: 0.25)
        Speed of player (useful for curriculum learning)

    ball_speed_ratio: float (default: 0.75)
        Speed of ball (useful for curriculum learning)

    """

    def __init__(self, width=64, height=48, cpu_speed_ratio=0.6, players_speed_ratio = 0.4, ball_speed_ratio=0.75,  MAX_SCORE=11):

        actions = {
            "up": K_w,
            "down": K_s
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)

        # the %'s come from original values, wanted to keep same ratio when you
        # increase the resolution.
        self.ball_radius = percent_round_int(height, 0.03)

        self.cpu_speed_ratio = cpu_speed_ratio
        self.ball_speed_ratio = ball_speed_ratio
        self.players_speed_ratio = players_speed_ratio

        self.paddle_width = percent_round_int(width, 0.023)
        self.paddle_height = percent_round_int(height, 0.15)
        self.paddle_dist_to_wall = percent_round_int(width, 0.0625)
        self.MAX_SCORE = MAX_SCORE

        self.dy = 0.0
        self.score_sum = 0.0  # need to deal with 11 on either side winning
        self.score_counts = {
            "agent": 0.0,
            "cpu": 0.0
        }

    def _handle_player_events(self):
        self.dy = 0

        if __name__ == "__main__":
            # for debugging mode
            pygame.event.get()
            keys = pygame.key.get_pressed()
            if keys[self.actions['up']]:
                self.dy = -self.agentPlayer.speed
            elif keys[self.actions['down']]:
                self.dy = self.agentPlayer.speed

            if keys[pygame.QUIT]:
                pygame.quit()
                sys.exit()
            pygame.event.pump()
        else:
            # consume events from act
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == self.actions['up']:
                        self.dy = -self.agentPlayer.speed

                    if key == self.actions['down']:
                        self.dy = self.agentPlayer.speed



    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player y position.
            * players velocity.
            * cpu y position.
            * ball x position.
            * ball y position.
            * ball x velocity.
            * ball y velocity.

            See code for structure.

        """
        state = {
            "player_y": self.agentPlayer.pos.y,
            "player_velocity": self.agentPlayer.vel.y,
            "cpu_y": self.cpuPlayer.pos.y,
            "ball_x": self.ball.pos.x,
            "ball_y": self.ball.pos.y,
            "ball_velocity_x": self.ball.vel.x,
            "ball_velocity_y": self.ball.vel.y
        }

        return state

    def getScore(self):
        return self.score_sum

    def game_over(self):
        # pong used 11 as max score
        return (self.score_counts['agent'] == self.MAX_SCORE) or (
            self.score_counts['cpu'] == self.MAX_SCORE)

    def init(self):
        self.score_counts = {
            "agent": 0.0,
            "cpu": 0.0
        }

        self.score_sum = 0.0
        self.ball = Ball(
            self.ball_radius,
            self.ball_speed_ratio * self.height,
            self.rng,
            (self.width / 2, self.height / 2),
            self.width,
            self.height
        )

        self.agentPlayer = Player(
            self.players_speed_ratio * self.height,
            self.paddle_width,
            self.paddle_height,
            (self.paddle_dist_to_wall, self.height / 2),
            self.width,
            self.height)

        self.cpuPlayer = Player(
            self.cpu_speed_ratio * self.height,
            self.paddle_width,
            self.paddle_height,
            (self.width - self.paddle_dist_to_wall, self.height / 2),
            self.width,
            self.height)

        self.players_group = pygame.sprite.Group()
        self.players_group.add(self.agentPlayer)
        self.players_group.add(self.cpuPlayer)

        self.ball_group = pygame.sprite.Group()
        self.ball_group.add(self.ball)


    def reset(self):
        self.init()
        # after game over set random direction of ball otherwise it will always be the same
        self._reset_ball(1 if self.rng.random_sample() > 0.5 else -1)


    def _reset_ball(self, direction):
        self.ball.pos.x = self.width / 2  # move it to the center

        # we go in the same direction that they lost in but at starting vel.
        self.ball.vel.x = self.ball.speed * direction
        self.ball.vel.y = (self.rng.random_sample() *
                           self.ball.speed) - self.ball.speed * 0.5

    def step(self, dt):
        dt /= 1000.0
        self.screen.fill((0, 0, 0))

        self.agentPlayer.speed = self.players_speed_ratio * self.height
        self.cpuPlayer.speed = self.cpu_speed_ratio * self.height
        self.ball.speed = self.ball_speed_ratio * self.height

        self._handle_player_events()

        # doesnt make sense to have this, but include if needed.
        self.score_sum += self.rewards["tick"]

        self.ball.update(self.agentPlayer, self.cpuPlayer, dt)

        is_terminal_state = False

        # logic
        if self.ball.pos.x <= 0:
            self.score_sum += self.rewards["negative"]
            self.score_counts["cpu"] += 1.0
            self._reset_ball(-1)
            is_terminal_state = True

        if self.ball.pos.x >= self.width:
            self.score_sum += self.rewards["positive"]
            self.score_counts["agent"] += 1.0
            self._reset_ball(1)
            is_terminal_state = True

        if is_terminal_state:
            # winning
            if self.score_counts['agent'] == self.MAX_SCORE:
                self.score_sum += self.rewards["win"]

            # losing
            if self.score_counts['cpu'] == self.MAX_SCORE:
                self.score_sum += self.rewards["loss"]
        else:
            self.agentPlayer.update(self.dy, dt)
            self.cpuPlayer.updateCpu(self.ball, dt)

        self.players_group.draw(self.screen)
        self.ball_group.draw(self.screen)

if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = Pong(width=256, height=200)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(60)
        game.step(dt)
        pygame.display.update()
