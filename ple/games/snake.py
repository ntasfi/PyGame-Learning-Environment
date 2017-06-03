import pygame
import sys
import math

#import .base
from .base.pygamewrapper import PyGameWrapper

from pygame.constants import K_w, K_a, K_s, K_d
from .utils.vec2d import vec2d
from .utils import percent_round_int


class Food(pygame.sprite.Sprite):

    def __init__(self, pos_init, width, color,
                 SCREEN_WIDTH, SCREEN_HEIGHT, rng):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.color = color

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.width = width
        self.rng = rng

        image = pygame.Surface((width, width))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))
        pygame.draw.rect(
            image,
            color,
            (0, 0, self.width, self.width),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def new_position(self, snake):
        new_pos = snake.body[0].pos
        snake_body = [s.pos for s in snake.body]

        while (new_pos in snake_body):
            _x = self.rng.choice(range(
                self.width * 2, self.SCREEN_WIDTH - self.width * 2, self.width
            ))

            _y = self.rng.choice(range(
                self.width * 2, self.SCREEN_HEIGHT - self.width * 2, self.width
            ))

            new_pos = vec2d((_x, _y))

        self.pos = new_pos
        self.rect.center = (self.pos.x, self.pos.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


class SnakeSegment(pygame.sprite.Sprite):

    def __init__(self, pos_init, width, height, color):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.color = color
        self.width = width
        self.height = height

        image = pygame.Surface((width, height))
        image.fill((0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            color,
            (0, 0, self.width, self.height),
            0
        )

        self.image = image
        # use half the size
        self.rect = pygame.Rect(pos_init, (self.width / 2, self.height / 2))
        self.rect.center = pos_init

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


# basically just holds onto all of them
class SnakePlayer():

    def __init__(self, speed, length, pos_init, width,
                 color, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.dir = vec2d((1, 0))
        self.speed = speed
        self.pos = vec2d(pos_init)
        self.color = color
        self.width = width
        self.length = length
        self.body = []
        self.update_head = True

        # build our body up
        for i in range(self.length):
            self.body.append(
                # makes a neat "zapping" in effect
                SnakeSegment(
                            (self.pos.x - (width) * i, self.pos.y),
                    self.width,
                    self.width,
                    tuple([c - 100 for c in self.color]
                          ) if i == 0 else self.color
                )
            )
        # we dont add the first few because it cause never actually hit it
        self.body_group = pygame.sprite.Group()
        self.head = self.body[0]

    def update(self, dt):
        for i in range(self.length - 1, 0, -1):
            scale = 0.1

            self.body[i].pos = vec2d((
                ((1.0 - scale) *
                 self.body[i - 1].pos.x + scale * self.body[i].pos.x),
                ((1.0 - scale) *
                 self.body[i - 1].pos.y + scale * self.body[i].pos.y)
            ))

            self.body[i].rect.center = (self.body[i].pos.x, self.body[i].pos.y)

        self.head.pos.x += self.dir.x * self.speed * dt
        self.head.pos.y += self.dir.y * self.speed * dt
        self.update_hitbox()

    def update_hitbox(self):
        # need to make a small rect pointing the direction the snake is
        # instead of counting the entire head square as a hit box, since
        # the head touchs the body on turns and causes game overs.

        x = self.head.pos.x
        y = self.head.pos.y

        if self.dir.x == 0:
            w = self.width
            h = percent_round_int(self.width, 0.25)

            if self.dir.y == 1:
                y += percent_round_int(self.width, 1.0)

            if self.dir.y == -1:
                y -= percent_round_int(self.width, 0.25)

        if self.dir.y == 0:
            w = percent_round_int(self.width, 0.25)
            h = self.width

            if self.dir.x == 1:
                x += percent_round_int(self.width, 1.0)

            if self.dir.x == -1:
                x -= percent_round_int(self.width, 0.25)

        if self.update_head:
            image = pygame.Surface((w, h))
            image.fill((0, 0, 0))
            image.set_colorkey((0, 0, 0))

            pygame.draw.rect(
                image,
                (255, 0, 0),
                (0, 0, w, h),
                0
            )

            self.head.image = image
            self.head.rect = self.head.image.get_rect()
            self.update_head = False

        self.head.rect.center = (x, y)

    def grow(self):
        self.length += 1
        add = 100 if self.length % 2 == 0 else -100
        color = (self.color[0] + add, self.color[1], self.color[2] + add)
        last = self.body[-1].pos

        self.body.append(
            SnakeSegment(
                        (last.x, last.y),  # initially off screen?
                self.width,
                self.width,
                color
            )
        )
        if self.length > 3:  # we cant actually hit another segment until this point.
            self.body_group.add(self.body[-1])

    def draw(self, screen):
        for b in self.body[::-1]:
            b.draw(screen)


class Snake(PyGameWrapper):
    """
    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    init_length : int (default: 3)
        The starting number of segments the snake has. Do not set below 3 segments. Has issues with hitbox detection with the body for lower values.

    """

    def __init__(self,
                 width=64,
                 height=64,
                 init_length=3):

        actions = {
            "up": K_w,
            "left": K_a,
            "right": K_d,
            "down": K_s
        }

        PyGameWrapper.__init__(self, width, height, actions=actions)

        self.speed = percent_round_int(width, 0.45)

        self.player_width = percent_round_int(width, 0.05)
        self.food_width = percent_round_int(width, 0.09)
        self.player_color = (100, 255, 100)
        self.food_color = (255, 100, 100)

        self.INIT_POS = (width / 2, height / 2)
        self.init_length = init_length

        self.BG_COLOR = (25, 25, 25)

    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key

                #left = -1
                #right = 1
                #up = -1
                #down = 1

                if key == self.actions["left"] and self.player.dir.x != 1:
                    self.player.dir = vec2d((-1, 0))

                if key == self.actions["right"] and self.player.dir.x != -1:
                    self.player.dir = vec2d((1, 0))

                if key == self.actions["up"] and self.player.dir.y != 1:
                    self.player.dir = vec2d((0, -1))

                if key == self.actions["down"] and self.player.dir.y != -1:
                    self.player.dir = vec2d((0, 1))

                self.player.update_head = True

    def getGameState(self):
        """

        Returns
        -------

        dict
            * snake head x position.
            * snake head y position.
            * food x position.
            * food y position.
            * distance from head to each snake segment.

            See code for structure.

        """

        state = {
            "snake_head_x": self.player.head.pos.x,
            "snake_head_y": self.player.head.pos.y,
            "food_x": self.food.pos.x,
            "food_y": self.food.pos.y,
            "snake_body": [],
            "snake_body_pos": [],
        }

        for s in self.player.body:
            dist = math.sqrt((self.player.head.pos.x - s.pos.x)
                             ** 2 + (self.player.head.pos.y - s.pos.y)**2)
            state["snake_body"].append(dist)
            state["snake_body_pos"].append([s.pos.x, s.pos.y])

        return state

    def getScore(self):
        return self.score

    def game_over(self):
        return self.lives == -1

    def init(self):
        """
            Starts/Resets the game to its inital state
        """

        self.player = SnakePlayer(
            self.speed,
            self.init_length,
            self.INIT_POS,
            self.player_width,
            self.player_color,
            self.width,
            self.height
        )

        self.food = Food((0, 0),
                         self.food_width,
                         self.food_color,
                         self.width,
                         self.height,
                         self.rng
                         )

        self.food.new_position(self.player)

        self.score = 0
        self.ticks = 0
        self.lives = 1

    def step(self, dt):
        """
            Perform one step of game emulation.
        """
        dt /= 1000.0

        self.ticks += 1
        self.screen.fill(self.BG_COLOR)
        self._handle_player_events()
        self.score += self.rewards["tick"]

        hit = pygame.sprite.collide_rect(self.player.head, self.food)
        if hit:  # it hit
            self.score += self.rewards["positive"]
            self.player.grow()
            self.food.new_position(self.player)

        hits = pygame.sprite.spritecollide(
            self.player.head, self.player.body_group, False)
        if len(hits) > 0:
            self.lives = -1

        x_check = (
            self.player.head.pos.x < 0) or (
            self.player.head.pos.x +
            self.player_width /
            2 > self.width)
        y_check = (
            self.player.head.pos.y < 0) or (
            self.player.head.pos.y +
            self.player_width /
            2 > self.height)

        if x_check or y_check:
            self.lives = -1

        if self.lives <= 0.0:
            self.score += self.rewards["loss"]

        self.player.update(dt)

        self.player.draw(self.screen)
        self.food.draw(self.screen)


if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = Snake(width=128, height=128)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        if game.game_over():
            game.init()

        dt = game.clock.tick_busy_loop(30)
        game.step(dt)
        pygame.display.update()
