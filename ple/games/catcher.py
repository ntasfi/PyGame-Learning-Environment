import sys
import pygame
from .utils import percent_round_int

from ple.games import base
from pygame.constants import K_a, K_d


class Paddle(pygame.sprite.Sprite):

    def __init__(self, speed, width, height, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.speed = speed
        self.width = width

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.vel = 0.0

        pygame.sprite.Sprite.__init__(self)

        image = pygame.Surface((width, height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 255, 255),
            (0, 0, width, height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (
            SCREEN_WIDTH / 2 - self.width / 2,
            SCREEN_HEIGHT - height - 3)

    def update(self, dx, dt):
        self.vel += dx
        self.vel *= 0.9

        x, y = self.rect.center
        n_x = x + self.vel

        if n_x <= 0:
            self.vel = 0.0
            n_x = 0

        if n_x + self.width >= self.SCREEN_WIDTH:
            self.vel = 0.0
            n_x = self.SCREEN_WIDTH - self.width

        self.rect.center = (n_x, y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


class Fruit(pygame.sprite.Sprite):

    def __init__(self, speed, size, SCREEN_WIDTH, SCREEN_HEIGHT, rng):
        self.speed = speed
        self.size = size

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.rng = rng

        pygame.sprite.Sprite.__init__(self)

        image = pygame.Surface((size, size))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 120, 120),
            (0, 0, size, size),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (-30, -30)

    def update(self, dt):
        x, y = self.rect.center
        n_y = y + self.speed * dt

        self.rect.center = (x, n_y)

    def reset(self):
        x = self.rng.choice(
            range(
                self.size *
                2,
                self.SCREEN_WIDTH -
                self.size *
                2,
                self.size))
        y = self.rng.choice(
            range(
                self.size,
                int(self.SCREEN_HEIGHT / 2),
                self.size))

        self.rect.center = (x, -1 * y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)


class Catcher(base.PyGameWrapper):
    """
    Based on `Eder Santana`_'s game idea.

    .. _`Eder Santana`: https://github.com/EderSantana

    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    init_lives : int (default: 3)
        The number lives the agent has.

    """

    def __init__(self, width=64, height=64, init_lives=3):

        actions = {
            "left": K_a,
            "right": K_d
        }

        base.PyGameWrapper.__init__(self, width, height, actions=actions)

        self.fruit_size = percent_round_int(height, 0.06)
        self.fruit_fall_speed = 0.00095 * height

        self.player_speed = 0.021 * width
        self.paddle_width = percent_round_int(width, 0.2)
        self.paddle_height = percent_round_int(height, 0.04)

        self.dx = 0.0
        self.init_lives = init_lives

    def _handle_player_events(self):
        self.dx = 0.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.key

                if key == self.actions['left']:
                    self.dx -= self.player_speed

                if key == self.actions['right']:
                    self.dx += self.player_speed

    def init(self):
        self.score = 0
        self.lives = self.init_lives

        self.player = Paddle(self.player_speed, self.paddle_width,
                             self.paddle_height, self.width, self.height)

        self.fruit = Fruit(self.fruit_fall_speed, self.fruit_size,
                           self.width, self.height, self.rng)

        self.fruit.reset()

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player x position.
            * players velocity.
            * fruits x position.
            * fruits y position.

            See code for structure.

        """
        state = {
            "player_x": self.player.rect.center[0],
            "player_vel": self.player.vel,
            "fruit_x": self.fruit.rect.center[0],
            "fruit_y": self.fruit.rect.center[1]
        }

        return state

    def getScore(self):
        return self.score

    def game_over(self):
        return self.lives == 0

    def step(self, dt):
        self.screen.fill((0, 0, 0))
        self._handle_player_events()

        self.score += self.rewards["tick"]

        if self.fruit.rect.center[1] >= self.height:
            self.score += self.rewards["negative"]
            self.lives -= 1
            self.fruit.reset()

        if pygame.sprite.collide_rect(self.player, self.fruit):
            self.score += self.rewards["positive"]
            self.fruit.reset()

        self.player.update(self.dx, dt)
        self.fruit.update(dt)

        if self.lives == 0:
            self.score += self.rewards["loss"]

        self.player.draw(self.screen)
        self.fruit.draw(self.screen)

if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = Catcher(width=256, height=256)
    game.rng = np.random.RandomState(24)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.init()

    while True:
        dt = game.clock.tick_busy_loop(30)
        if game.game_over():
            game.reset()

        game.step(dt)
        pygame.display.update()
