import pygame
import sys
import math

import base

from pygame.constants import K_w, K_a, K_d, K_LEFT, K_UP, K_RIGHT
from utils.vec2d import vec2d
from utils import percent_round_int


class Ball(pygame.sprite.Sprite):

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, rng):
        pygame.sprite.Sprite.__init__(self)

        self.pos_init = (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.525)
        self.radius = percent_round_int(SCREEN_WIDTH, 0.02)

        self.color = (255, 200, 20)

        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH

        self.rng = rng

        image = pygame.Surface((2 * self.radius, 2 * self.radius))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            image,
            self.color,
            (self.radius, self.radius),
            self.radius,
            0
        )

        self.image = image
        self.rect = self.image.get_rect()

        self.max_speed = percent_round_int(SCREEN_HEIGHT, 0.35)
        self.min_speed = 0.0
        self.wind_drag = 1.0
        self.fraction = 1.0
        self.nudge = self.radius * 0.1
        self.gravity = percent_round_int(SCREEN_HEIGHT, 0.2)

        self.reset()

    def update(self, dt):
        #applyAccel ( grav )
        self.vel.y = self.vel.y + self.gravity * dt

        #limitSpeed ( 0, maxBallSpeed )
        mag2 = self.vel.magSq()
        if mag2 > (self.max_speed * self.max_speed):
            self.vel.normalize()
            self.vel = self.vel.multScalar(self.max_speed)

        if mag2 < 0:
            self.vel.normalize()
            self.vel = self.vel.multScalar(self.min_speed)

        # move
        self.pos = self.pos + self.vel.multScalar(dt)
        self.vel = self.vel.multScalar(1.0 - (1.0 - self.wind_drag) * dt)
        self.rect.center = (self.pos.x, self.pos.y)

    def isColliding(self, other):
        # p is the point
        # r is the radius from p's center to its edge
        return self.pos.dist(other.pos) < (other.radius + self.radius)

    def bounce(self, other):
        op = other.pos
        ov = other.vel
        r = other.radius
        op.x = op.x + other.radius

        # other is another object with {pos, vel, radius} set
        # bounce off this and that.

        pos = self.pos
        pos = pos - op
        pos.normalize()
        pos = pos.multScalar(self.nudge)
        while self.isColliding(op, r):
            self.pos = self.pos + pos

        n = self.pos - other.pos
        n.normalize()

        u = self.vel - other.vel
        un = n.multScalar(u.dot(u) * 2)
        u = u - un
        self.vel = u + other.vel

    def reset(self):
        x_speed = self.max_speed * \
            self.rng.choice([-1.0, 1.0]) * (0.65 * self.rng.rand() + 0.5)
        # always going to be up in the air
        y_speed = self.max_speed * (0.85 * self.rng.rand() + 0.65)
        self.vel = vec2d((x_speed, y_speed))
        self.pos = vec2d(self.pos_init)
        self.rect.center = self.pos_init

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


class Fence(pygame.sprite.Sprite):

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        self.width = percent_round_int(SCREEN_WIDTH, 0.04)
        self.height = percent_round_int(SCREEN_HEIGHT, 0.09)
        self.color = (240, 210, 130)

        image = pygame.Surface((self.width, self.height + self.width))
        image.fill((0, 0, 0))
        image.set_colorkey((0, 0, 0))

        # rect of post
        pygame.draw.rect(
            image,
            self.color,
            (0, self.width, self.width, self.height),
            0
        )

        # circle of post
        pygame.draw.circle(
            image,
            self.color,
            (self.width / 2, self.width),
            self.width / 2,
            0
        )

        self.image = image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH / 2,
                            percent_round_int(SCREEN_HEIGHT,
                                              0.95) - (self.height + self.width))

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


class Backdrop():

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        backdrop_color = (251, 252, 255)
        sun_color = (248, 240, 167)
        floor_color = (127, 227, 152)
        shrub_small_color = (207, 254, 208)
        shrub_large_color = (239, 252, 243)

        image.fill((0, 0, 0, 0))

        # backdrop
        pygame.draw.rect(
            image,
            backdrop_color,
            (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            0
        )

        # sun
        pygame.draw.circle(
            image,
            sun_color,
            (percent_round_int(SCREEN_WIDTH, 0.325),
             percent_round_int(SCREEN_HEIGHT, 0.55)),
            percent_round_int(SCREEN_WIDTH, 0.05),
            0
        )

        # shrubs
        pygame.draw.circle(
            image,
            shrub_large_color,
            (percent_round_int(SCREEN_WIDTH, 0.6),
             percent_round_int(SCREEN_HEIGHT, 1.15)),
            percent_round_int(SCREEN_WIDTH, 0.275),
            0
        )

        pygame.draw.circle(
            image,
            shrub_small_color,
            (percent_round_int(SCREEN_WIDTH, 0.8),
             percent_round_int(SCREEN_HEIGHT, 1.15)),
            percent_round_int(SCREEN_WIDTH, 0.2),
            0
        )

        # floor
        pygame.draw.rect(
            image,
            floor_color,
            (0, SCREEN_HEIGHT * 0.95, SCREEN_WIDTH, SCREEN_HEIGHT * 0.1),
            0
        )

        self.image = image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


class Slime(pygame.sprite.Sprite):

    def __init__(self, pos_init, color, SCREEN_WIDTH,
                 SCREEN_HEIGHT, flipped=False):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.vel = vec2d((0, 0))

        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.speed_x = percent_round_int(SCREEN_WIDTH, 0.35)
        self.speed_y = percent_round_int(SCREEN_WIDTH, 0.09)

        self.radius = percent_round_int(SCREEN_WIDTH, 0.05)
        self.color = color
        self.gravity = percent_round_int(SCREEN_HEIGHT, 0.2)
        self.nudge = self.radius * 0.1
        self.flipped = flipped

        image = pygame.Surface((self.radius * 2, self.radius))
        image.fill((1, 1, 1))
        image.set_colorkey((1, 1, 1))

        # body
        pygame.draw.circle(
            image,
            self.color,
            (self.radius, percent_round_int(self.radius, 1.15)),
            self.radius,
            0
        )

        # white eye
        pygame.draw.circle(
            image,
            (255, 255, 255),
            (percent_round_int(self.radius * 2, 0.65),
             percent_round_int(self.radius, 0.7)),
            percent_round_int(self.radius, 0.25),
            0
        )

        pygame.draw.circle(
            image,
            (0, 0, 0),
            (percent_round_int(self.radius * 2, 0.7),
             percent_round_int(self.radius, 0.7)),
            percent_round_int(self.radius, 0.09),
            0
        )

        if self.flipped:
            image = pygame.transform.flip(image, True, False)

        self.image = image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def circle_center(self):
        return (self.rect.center[0] + self.radius, self.rect.center[1])

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

    def update(self, dx, dy, dt):
        self.vel.x = self.vel.x * 0.75
        # proccess actions is taken care of
        dx *= -1.0 if self.flipped else 1.0

        floor = self.SCREEN_HEIGHT * 0.95

        self.vel.y = self.vel.y + self.gravity * dt

        if self.pos.y + self.radius >= floor + self.nudge * dt:
            self.vel.y = dy * self.speed_y

        self.vel.x = self.vel.x + dx * self.speed_x

        # move
        # set the loc += vel*dt
        # this double multiplies y
        self.pos = self.pos + self.vel.multScalar(dt)

        if self.pos.y >= floor:
            self.pos.y = floor
            self.vel.y = 0.0

        self.rect.center = (self.pos.x, self.pos.y)


class Player(Slime):

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        pos_init = (SCREEN_WIDTH * 0.40, SCREEN_HEIGHT * 0.85)
        color = (240, 75, 0)

        Slime.__init__(self, pos_init, color, SCREEN_WIDTH, SCREEN_HEIGHT)


class Computer(Slime):

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        pos_init = (SCREEN_WIDTH * 0.60, SCREEN_HEIGHT * 0.85)
        color = (0, 150, 255)

        Slime.__init__(
            self,
            pos_init,
            color,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            flipped=True)


class SlimeVolley(base.Game):

    def __init__(self, width=64, height=32):

        actions = {
            "left": K_a,
            "up": K_w,
            "right": K_d
        }

        base.Game.__init__(self, width, height, actions=actions)

        self.score = {
            "player": 0,
            "computer": 0
        }

        self.MAX_SCORE = 11
        self.ticks = 0
        self.start_delay = 45

    def init(self):
        self.score = {
            "player": 0,
            "computer": 0
        }

        # add background
        self.backdrop = Backdrop(self.width, self.height)
        self.fence = Fence(self.width, self.height)
        self.ball = Ball(self.width, self.height, self.rng)
        # add cpu player
        # add player
        self.player = Player(self.width, self.height)
        #self.computer = Computer(self.width, self.height)

    def getScore(self):
        return self.score["player"] - self.score["computer"]

    def game_over(self):
        return self.score["player"] == self.MAX_SCORE or self.score[
            "computer"] == self.MAX_SCORE

    def _handle_player_events(self):
        self.dx = 0.0
        self.dy = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key

                if key == self.actions["right"]:
                    self.dx = 1.0

                if key == self.actions["left"]:
                    self.dx = -1.0

                if key == self.actions["up"]:
                    self.dy = -1.0

    def step(self, dt):
        dt /= 1000.0
        self.ticks += 1
        self.screen.fill((200, 200, 200))

        self._handle_player_events()

        self.player.update(self.dx, self.dy, dt)
        #self.computer.update(self.ball, dt)

        self.ball.update(dt)

        if self.ball.isColliding(self.player):
            self.ball.bounce(self.player)

            # do the fence check here...

        # player is on left and computer is right
        if self.ball.pos.y + 2 * self.ball.radius > self.height * 0.95:  # floor
            if self.ball.pos.x > self.width / 2:  # player score
                self.score["player"] += 1
            else:
                self.score["computer"] += 1

            self.ball.reset()

        self.backdrop.draw(self.screen)
        self.fence.draw(self.screen)
        self.ball.draw(self.screen)
        # self.computer.draw(self.screen)
        self.player.draw(self.screen)

if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = SlimeVolley(width=512, height=256)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState()
    game.init()

    while True:
        if game.game_over():
            game.init()

        dt = game.clock.tick_busy_loop(60)
        game.step(dt)
        pygame.display.update()
