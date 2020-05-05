import os
import sys
import numpy as np
import random

from collections import namedtuple

import pygame
from ple.games import base
from pygame.constants import K_SPACE, K_DOWN, K_UP

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 150

FPS = 60
gravity = 0.6

black = (0, 0, 0)
white = (255, 255, 255)
background_col = (235, 235, 235)


class Dino(pygame.sprite.Sprite):

    def __init__(self, images, images_rect, ducking_images, ducking_images_rect):
        self.images, self.rect = images, images_rect
        self.images1, self.rect1 = ducking_images, ducking_images_rect
        self.reset()

    def reset(self):
        self.rect.bottom = int(0.98 * SCREEN_HEIGHT)
        self.rect.left = SCREEN_WIDTH / 15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0, 0]
        self.jumpSpeed = 11.5
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def check_bounds(self):
        if self.rect.bottom > int(0.98 * self.screen_height):
            self.rect.bottom = int(0.98 * self.screen_height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.isDead:
            self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[self.index % 2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.check_bounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking is False:
            self.score += 1
        self.counter = (self.counter + 1)


class Cactus(pygame.sprite.Sprite):
    def __init__(self, images, rect, speed=5):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = images, rect
        self.rect.bottom = int(0.98 * SCREEN_HEIGHT)
        self.rect.left = SCREEN_WIDTH + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.movement = [-1 * speed, 0]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()


class Ptera(pygame.sprite.Sprite):
    def __init__(self, images, rect, speed=5):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = images, rect
        self.ptera_height = [SCREEN_WIDTH * 0.82, SCREEN_HEIGHT * 0.75, SCREEN_HEIGHT * 0.60]
        self.rect.centery = self.ptera_height[random.randrange(0, 3)]
        self.rect.left = SCREEN_WIDTH + self.rect.width
        self.image = self.images[0]
        self.movement = [-1 * speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index + 1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground(pygame.sprite.Sprite):
    def __init__(self, image, rect, image_swap, rect_swap, speed=-5):
        self.image, self.rect = image, rect
        self.image1, self.rect1 = image_swap, rect_swap
        self.speed = speed
        self.reset()

    def reset(self):
        self.rect.bottom = SCREEN_HEIGHT
        self.rect1.bottom = SCREEN_HEIGHT
        self.rect1.left = self.rect.right

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


class Scoreboard(pygame.sprite.Sprite):
    def __init__(self, numbers_images, numbers_rect):
        self.score = 0
        self.tempimages, self.temprect = numbers_images, numbers_rect
        self.reset()

    def reset(self):
        self.image = pygame.Surface((55, int(11 * 6 / 5)))
        self.rect = self.image.get_rect()
        self.rect.left = SCREEN_WIDTH * 0.89
        self.rect.top = SCREEN_HEIGHT * 0.1

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, score):
        score_digits = self.extract_digits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s], self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

    def extract_digits(self, number):
        if number > -1:
            digits = []
            i = 0
            while number / 10 != 0:
                digits.append(number % 10)
                number = int(number / 10)

            digits.append(number % 10)
            for i in range(len(digits), 5):
                digits.append(0)
            digits.reverse()
            return digits


SpriteAsset = namedtuple('SpriteAsset', ['images', 'rect'])


class TRex(base.PyGameWrapper):
    """
    Based on code from shivamshekhar's Chrome-T-Rex-Rush.

    Original game repo: https://github.com/shivamshekhar/Chrome-T-Rex-Rush

    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height.
    """

    def __init__(self, max_score=150):
        actions = {
            'jump': K_SPACE,
            'duck': K_DOWN,
            'stand': K_UP,
        }

        base.PyGameWrapper.__init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, actions=actions)

        self.score = 0.0
        self.game_tick = 0
        self.game_speed = 4
        self.max_score = max_score

        self.dino = None
        self.ground = None
        self.scoreboard = None
        self.counter = 0

        self.cacti = None
        self.pteras = None
        self.last_obstacle = None

        # so we can preload images
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

        self.cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.asset_dir = os.path.join(self.cur_dir, 'sprites')

        # Preload images for performance
        self.images = {}

        dino, dino_rect = self.load_sprite_sheet('dino.png', 5, 1, 44, 47, -1)
        dino_ducking, dino_ducking_rect = self.load_sprite_sheet('dino_ducking.png', 2, 1, 59, 47, -1)
        self.images['dino'] = SpriteAsset(images=dino, rect=dino_rect)
        self.images['dino_ducking'] = SpriteAsset(images=dino_ducking, rect=dino_ducking_rect)

        bg, bg_rect = self.load_image('ground.png', -1, -1, -1)
        self.images['background'] = SpriteAsset(images=bg, rect=bg_rect)
        self.images['background_swap'] = SpriteAsset(images=bg, rect=bg_rect)

        numbers, numbers_rect = self.load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
        self.images['numbers'] = SpriteAsset(images=numbers, rect=numbers_rect)

        pteras, pteras_rect = self.load_sprite_sheet('ptera.png', 3, 1, 46, 40, -1)
        self.images['ptera'] = SpriteAsset(images=pteras, rect=pteras_rect)

        cactus, cactus_rect = self.load_sprite_sheet('cacti-small.png', 3, 1, 40, 40, -1)
        self.images['cactus'] = SpriteAsset(images=cactus, rect=cactus_rect)

    def init(self):
        self.game_speed = 4

        if self.dino is None:
            dino_asset = self.images['dino']
            dino_ducking_asset = self.images['dino_ducking']
            self.dino = Dino(dino_asset.images,
                             dino_asset.rect,
                             dino_ducking_asset.images,
                             dino_ducking_asset.rect)
        self.dino.reset()

        if self.ground is None:
            ground_asset = self.images['background']
            ground_swap_asset = self.images['background_swap']
            self.ground = Ground(ground_asset.images,
                                 ground_asset.rect,
                                 ground_swap_asset.images,
                                 ground_swap_asset.rect,
                                 -1 * self.game_speed)
        self.ground.reset()

        if self.scoreboard is None:
            numbers_asset = self.images['numbers']
            self.scoreboard = Scoreboard(numbers_asset.images, numbers_asset.rect)
        self.scoreboard.reset()

        self.cacti = pygame.sprite.Group()
        self.pteras = pygame.sprite.Group()
        self.last_obstacle = pygame.sprite.Group()

        Cactus.containers = self.cacti
        Ptera.containers = self.pteras

        self.score = 0.0
        self.lives = 1
        self.game_tick = 0
        self.counter = 0

    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.dino.rect.bottom == int(0.98 * SCREEN_HEIGHT):
                        self.dino.isJumping = True
                        self.dino.movement[1] = -1 * self.dino.jumpSpeed

                if event.key == pygame.K_DOWN:
                    if not (self.dino.isJumping and self.dino.isDead):
                        self.dino.isDucking = True

                if event.key == pygame.K_UP:
                    if not self.dino.isDead:
                        self.dino.isDucking = False

    def step(self, dt):
        self.game_tick += 1

        self.score += self.rewards['tick']

        self._handle_player_events()

        for c in self.cacti:
            c.movement[0] = -1 * self.game_speed
            if pygame.sprite.collide_mask(self.dino, c):
                self.dino.isDead = True
            if c.rect.right <= self.dino.rect.left < c.rect.right + 4:
                self.score += self.rewards["positive"]

        for p in self.pteras:
            p.movement[0] = -1 * self.game_speed
            if pygame.sprite.collide_mask(self.dino, p):
                self.dino.isDead = True
            if (p.x - p.width / 2) <= self.player.pos_x < (p.x - p.width / 2 + 4):
                self.score += self.rewards["positive"]

        if len(self.cacti) < 2:
            cactus_asset = self.images['cactus']
            if len(self.cacti) == 0:
                self.last_obstacle.empty()
                self.last_obstacle.add(Cactus(cactus_asset.images, cactus_asset.rect, self.game_speed))
            else:
                for l in self.last_obstacle:
                    if l.rect.right < SCREEN_WIDTH * 0.7 and random.randrange(0, 50) == 10:
                        self.last_obstacle.empty()
                        self.last_obstacle.add(Cactus(cactus_asset.images, cactus_asset.rect, self.game_speed))

        if len(self.pteras) == 0 and random.randrange(0, 200) == 10 and self.counter > 500:
            pteras_asset = self.images['pteras']
            for l in self.last_obstacle:
                if l.rect.right < SCREEN_WIDTH * 0.8:
                    self.last_obstacle.empty()
                    self.last_obstacle.add(Ptera(pteras_asset.images, pteras_asset.rect, self.game_speed))

        if self.dino.isDead:
            self.score += self.rewards['loss']

        self.dino.update()
        self.cacti.update()
        self.pteras.update()
        self.ground.update()
        self.scoreboard.update(self.dino.score)

        self.screen.fill(background_col)
        self.ground.draw(self.screen)
        self.scoreboard.draw(self.screen)
        self.cacti.draw(self.screen)
        self.pteras.draw(self.screen)
        self.dino.draw(self.screen)

    def getScore(self):
        return self.score

    def game_over(self):
        return self.dino.isDead or self.score >= self.max_score

    def getGameState(self):
        return {}

    # Helper methods
    def load_sprite_sheet(
            self,
            sheet_name,
            nx,
            ny,
            scale_x=-1,
            scale_y=-1,
            color_key=None,
    ):
        fullname = os.path.join(self.asset_dir, sheet_name)
        sheet = pygame.image.load(fullname)
        sheet = sheet.convert()

        sheet_rect = sheet.get_rect()

        sprites = []

        size_x = sheet_rect.width / nx
        size_y = sheet_rect.height / ny

        for i in range(0, ny):
            for j in range(0, nx):
                rect = pygame.Rect((j * size_x, i * size_y, size_x, size_y))
                image = pygame.Surface(rect.size)
                image = image.convert()
                image.blit(sheet, (0, 0), rect)

                if color_key is not None:
                    if color_key is -1:
                        color_key = image.get_at((0, 0))
                    image.set_colorkey(color_key, pygame.RLEACCEL)

                if scale_x != -1 or scale_y != -1:
                    image = pygame.transform.scale(image, (scale_x, scale_y))

                sprites.append(image)

        sprite_rect = sprites[0].get_rect()

        return sprites, sprite_rect

    def load_image(
            self,
            name,
            size_x=-1,
            size_y=-1,
            color_key=None,
    ):
        fullname = os.path.join(self.asset_dir, name)
        image = pygame.image.load(fullname)
        image = image.convert()
        if color_key is not None:
            if color_key is -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key, pygame.RLEACCEL)

        if size_x != -1 or size_y != -1:
            image = pygame.transform.scale(image, (size_x, size_y))

        return image, image.get_rect()
