import math
import random
import sys

import pygame
from pygame.constants import K_w, K_s
from creepCommon.primitives import vec2d

class Ball(pygame.sprite.Sprite):

	def __init__(self, radius, speed,
		pos_init, SCREEN_WIDTH, SCREEN_HEIGHT):
                
                pygame.sprite.Sprite.__init__(self)

		self.radius = radius
		self.speed = speed
		self.pos = vec2d(pos_init)
		self.vel = vec2d((speed, -1.0*speed))

		self.SCREEN_HEIGHT = SCREEN_HEIGHT
		self.SCREEN_WIDTH = SCREEN_WIDTH

		image = pygame.Surface((radius*2, radius*2))
		image.fill((0, 0, 0, 0))
		image.set_colorkey((0,0,0))

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

	def update(self, agentPlayer, cpuPlayer, time_elapsed):
		
                if self.pos.y-self.radius <= 0: 
                        self.vel.y *= -1.0
                        self.pos.y += 1.0

                if self.pos.y+self.radius >= self.SCREEN_HEIGHT:
			self.vel.y *= -1.0
                        self.pos.y -= 1.0

                if pygame.sprite.collide_rect(self, agentPlayer):
                        self.vel.x = (-1*self.vel.x + self.speed*0.1)
                        self.pos.x += 1.0

                if pygame.sprite.collide_rect(self, cpuPlayer):
			self.vel.x = -1*(self.vel.x + self.speed*0.1)
                        self.pos.x -= 1.0

                self.pos.x += self.vel.x * time_elapsed
		self.pos.y += self.vel.y * time_elapsed

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
		image.set_colorkey((0,0,0))

		pygame.draw.rect(
			image,
			(255, 255, 255),
			(0, 0, rect_width, rect_height),
			0
		)

		self.image = image
		self.rect = self.image.get_rect()
		self.rect.center = pos_init

	def updateAgent(self, dy, time_elapsed):
                self.vel.y += dy
                self.vel.y *= 0.9
                
                self.pos.y += self.vel.y

                if self.pos.y-self.rect_height/2 <= 0:
                    self.pos.y = self.rect_height/2
                    self.vel.y = 0.0

                if self.pos.y+self.rect_height/2 >= self.SCREEN_HEIGHT:
                    self.pos.y = self.SCREEN_HEIGHT-self.rect_height/2
                    self.vel.y = 0.0

		self.rect.center = (self.pos.x, self.pos.y)

	def updateCpu(self, ball, time_elapsed):
		if ball.vel.x >= 0 and ball.pos.x >= self.SCREEN_WIDTH/2:
			if self.pos.y < ball.pos.y:
				self.pos.y += self.speed * time_elapsed

			if self.pos.y > ball.pos.y:
				self.pos.y -= self.speed * time_elapsed

		self.rect.center = (self.pos.x, self.pos.y)

class Pong():
        """
            loosely based on code from marti1125s pong lib.
            https://github.com/marti1125/pong/
        """
	def __init__(self, players_speed=0.05, 
                ball_speed=0.05, ball_radius=3, paddle_width=3, 
                paddle_height=11, paddle_dist_to_wall=4):

		actions = {
			"up": K_w,
			"down": K_s
		}

                SCREEN_WIDTH = 64
                SCREEN_HEIGHT = 48

		#required fields
		self.actions = actions

		self.screen = None
		self.clock = None
		self.lives = -1
		self.screen_dim = (SCREEN_WIDTH, SCREEN_HEIGHT)

                self.ball_radius = ball_radius
		self.ball_speed = ball_speed
                self.players_speed = players_speed
                self.paddle_width = paddle_width
                self.paddle_height = paddle_height
                self.paddle_dist_to_wall = paddle_dist_to_wall

                self.dy = 0.0
		self.score_sum = 0.0 #need to deal with 11 on either side winning
		self.score_counts = {
			"agent": 0.0,
			"cpu": 0.0
		}

                self.SCREEN_WIDTH = SCREEN_WIDTH
                self.SCREEN_HEIGHT = SCREEN_HEIGHT

	def _handle_player_events(self):
		self.dy = 0
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			if event.type == pygame.KEYDOWN:
				key = event.key
				if key == self.actions['up']:
                                        self.dy -= self.players_speed

				if key == self.actions['down']:
					self.dy += self.players_speed

	def getScreenDims(self):
		return self.screen_dim

	def getActions(self):
		return self.actions.values()

	def getScore(self):
		return self.score_sum

	def game_over(self):
		#pong used 11 as max score
		return (self.score_counts['agent'] == 11.0) or (self.score_counts['cpu'] == 11.0)

	def init(self):
            self.score_counts = {
                    "agent": 0.0,
                    "cpu": 0.0
            }

            self.score_sum = 0.0
            self.ball = Ball(
        	self.ball_radius,
		self.ball_speed,
		(self.SCREEN_WIDTH/2, self.SCREEN_HEIGHT/2),
                self.SCREEN_WIDTH,
                self.SCREEN_HEIGHT
            )
            
            self.agentPlayer = Player(
		self.players_speed,
		self.paddle_width,
		self.paddle_height,
		(self.paddle_dist_to_wall, self.SCREEN_HEIGHT/2),
		self.SCREEN_WIDTH,
		self.SCREEN_HEIGHT)

            self.cpuPlayer = Player(
		self.players_speed,
		self.paddle_width,
		self.paddle_height,
		(self.SCREEN_WIDTH-self.paddle_dist_to_wall, self.SCREEN_HEIGHT/2),
		self.SCREEN_WIDTH,
		self.SCREEN_HEIGHT)

            self.players_group = pygame.sprite.Group()
            self.players_group.add( self.agentPlayer )
            self.players_group.add( self.cpuPlayer )

            self.ball_group = pygame.sprite.Group()
            self.ball_group.add( self.ball )
	
        def reset(self):
		self.init()

	def _reset_ball(self, direction):
            self.ball.pos.x = self.SCREEN_WIDTH/2 #move it to the center
            
            #we go in the same direction that they lost in but at starting vel.
            self.ball.vel.x = self.ball_speed*direction
            self.ball.vel.y = (random.random()*self.ball_speed)-self.ball_speed

	def step(self, time_elapsed):

		self.screen.fill((0,0,0))

		self._handle_player_events()

		#logic
		if self.ball.pos.x <= 0:
			self.score_sum -= 1.0
			self.score_counts["cpu"] += 1.0
			self._reset_ball(-1)

		if self.ball.pos.x >= self.SCREEN_WIDTH:
			self.score_sum += 1.0
			self.score_counts["agent"] += 1.0
			self._reset_ball(1)

                self.ball.update(self.agentPlayer, self.cpuPlayer, time_elapsed)
		self.agentPlayer.updateAgent(self.dy, time_elapsed)
		self.cpuPlayer.updateCpu(self.ball, time_elapsed)
		
		self.players_group.draw(self.screen)
		self.ball_group.draw(self.screen)

if __name__ == "__main__":
    pygame.init()
    game = Pong()
    game.screen = pygame.display.set_mode( game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.init()

    while True:
        time_elapsed = game.clock.tick_busy_loop(60)
        game.step(time_elapsed)
        pygame.display.update()
