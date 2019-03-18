from ple import PLE
from ple.games.pong import Pong
import pygame
import time
import sys

game = Pong(width=300, height=200)

p = PLE(game, fps=30, display_screen=True, force_fps=True)
p.init()

print(p.getActionSet())

nb_frames = 1000
action = None

for f in range(nb_frames):
    if p.game_over():
        p.reset_game()
    obs = p.getScreenRGB()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key:
                action = event.key
                print(action)
        elif event.type == pygame.KEYUP:
            action = None
    p.act(action)
    time.sleep(.05)

#This is a change