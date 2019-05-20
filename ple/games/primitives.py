from math import tan, radians, degrees

import pygame
from pygame.math import Vector2

from .utils.vec2d import vec2d


class Creep(pygame.sprite.Sprite):

    def __init__(self,
                 color,
                 radius,
                 pos_init,
                 dir_init,
                 speed,
                 reward,
                 TYPE,
                 SCREEN_WIDTH,
                 SCREEN_HEIGHT,
                 jitter_speed):

        pygame.sprite.Sprite.__init__(self)

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.TYPE = TYPE
        self.jitter_speed = jitter_speed
        self.speed = speed
        self.reward = reward
        self.radius = radius
        self.pos = vec2d(pos_init)

        self.direction = vec2d(dir_init)
        self.direction.normalize()  # normalized

        image = pygame.Surface((radius * 2, radius * 2))
        image.fill((0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            image,
            color,
            (radius, radius),
            radius,
            0
        )

        self.image = image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):

        dx = self.direction.x * self.speed * dt
        dy = self.direction.y * self.speed * dt

        if self.pos.x + dx > self.SCREEN_WIDTH - self.radius:
            self.pos.x = self.SCREEN_WIDTH - self.radius
            self.direction.x = -1 * self.direction.x * \
                (1 + 0.5 * self.jitter_speed)  # a little jitter
        elif self.pos.x + dx <= self.radius:
            self.pos.x = self.radius
            self.direction.x = -1 * self.direction.x * \
                (1 + 0.5 * self.jitter_speed)  # a little jitter
        else:
            self.pos.x = self.pos.x + dx

        if self.pos.y + dy > self.SCREEN_HEIGHT - self.radius:
            self.pos.y = self.SCREEN_HEIGHT - self.radius
            self.direction.y = -1 * self.direction.y * \
                (1 + 0.5 * self.jitter_speed)  # a little jitter
        elif self.pos.y + dy <= self.radius:
            self.pos.y = self.radius
            self.direction.y = -1 * self.direction.y * \
                (1 + 0.5 * self.jitter_speed)  # a little jitter
        else:
            self.pos.y = self.pos.y + dy

        self.direction.normalize()

        self.rect.center = ((self.pos.x, self.pos.y))


class Wall(pygame.sprite.Sprite):

    def __init__(self, pos, w, h):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos)
        self.w = w
        self.h = h

        image = pygame.Surface([w, h])
        image.fill((10, 10, 10))
        self.image = image.convert()

        self.rect = self.image.get_rect()
        self.rect.center = pos

    def draw(self, screen):
        pygame.draw.rect(
            screen, (10, 10, 10), [
                self.pos.x, self.pos.y, self.w, self.h], 0)


class Player(pygame.sprite.Sprite):

    def __init__(self,
                 radius,
                 color,
                 speed,
                 pos_init,
                 SCREEN_WIDTH,
                 SCREEN_HEIGHT, angle=0.0, length=4, max_steering=30, max_acceleration=10.0):

        pygame.sprite.Sprite.__init__(self)

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        self.pos = vec2d(pos_init)
        self.position = Vector2(0.0, 0.0)
        self.vel = vec2d((0, 0))
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 40
        self.brake_deceleration = 10
        self.free_deceleration = 2

        self.acceleration = 0.0
        self.steering = 0.0

        image = pygame.Surface([radius * 2, radius * 2])
        image.set_colorkey((0, 0, 0))

        pygame.draw.circle(
            image,
            color,
            (radius, radius),
            radius,
            0
        )

        self.image = image.convert()
        self.rect = self.image.get_rect()
        self.radius = radius

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

        self.vel = self.velocity.rotate(-self.angle)

        print(self.angle)

        new_x = self.pos.x + self.vel.x * dt
        new_y = self.pos.y + self.vel.y * dt

        # if its not against a wall we want a total decay of 50
        if new_x >= self.SCREEN_WIDTH - self.radius * 2:
            self.pos.x = self.SCREEN_WIDTH - self.radius * 2
            self.vel.x = 0.0
        elif new_x < 0.0:
            self.pos.x = 0.0
            self.vel.x = 0.0
        else:
            self.pos.x = new_x
            self.vel.x = self.vel.x * 0.975

        if new_y > self.SCREEN_HEIGHT - self.radius * 2:
            self.pos.y = self.SCREEN_HEIGHT - self.radius * 2
            self.vel.y = 0.0
        elif new_y < 0.0:
            self.pos.y = 0.0
            self.vel.y = 0.0
        else:
            self.pos.y = new_y
            self.vel.y = self.vel.y * 0.975

        self.rect.center = (self.pos.x, self.pos.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)
