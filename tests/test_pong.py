#!/usr/bin/python
from ple import PLE
from ple.games.pong import Pong, Ball, Player
import pygame, time, sys, pytest

@pytest.mark.parametrize("x1,y1,x2,y2,x3,y3,x4,y4,expected", [
    (0,0,10,10,0,10,10,0,True), #X-like intersection of lines
    (0,0,0,5,0,0,5,0,True), #Shared first end-point (0,0)
    (0,0,0,5.00000000009,10,10,0,5.0000000001,False), #nearly touching end-point
    (0,5,0,0,0,5,0,0,True), #entirely overlapping lines (both end-points shared)
    (1,1,1,6,2,1,2,6,False), #parallel lines (FAILS: Division by zero)
    (1,6,1,1,2,6,2,1,False),  #parallel lines, rotated 90 degrees (FAILS: Division by zero)
    (5,5,10,10,6,6,11,11,False), #parallel lines at a 45 degree angle (FAILS: Division by zero)
    (0,0,0,10,10,5,0,5,True), #T-like intersection, with one end-point meeting another line midway
])

def test_line_intersection(x1,y1,x2,y2,x3,y3,x4,y4,expected):
    game=Ball(10,1,1,(50,50),100,100) #these parameters do not affect the line_intersection function
    answer = game.line_intersection(x1,y1,x2,y2,x3,y3,x4,y4)
    assert answer == expected

def test_movement_up():
    game=Pong()
    p=PLE(game, display_screen=True, fps=20, force_fps=1)
    p.init()
    time.sleep(.5)
    oldState=p.getGameState()
    p.act(game.actions["up"])
    newState=p.getGameState()
    assert oldState["player_velocity"] > newState["player_velocity"]

def test_movement_down():
    game=Pong()
    p=PLE(game, display_screen=True, fps=20, force_fps=1)
    p.init()
    time.sleep(.5)
    oldState=p.getGameState()
    p.act(game.actions["down"])
    newState=p.getGameState()
    assert oldState["player_velocity"] < newState["player_velocity"]

def test_negative_cpu_speed():
    with pytest.raises(Exception):
        game=Pong(cpu_speed_ratio=-1)

def test_negative_player_speed():
    with pytest.raises(Exception):
        game=Pong(players_speed_ratio=-1)

def test_negative_ball_speed():
    with pytest.raises(Exception):
        game=Pong(ball_speed_ratio=-1)

def test_invalid_game_size():
    with pytest.raises(Exception):
        game=Pong(width=-200, height=-200)

def test_invalid_max_score():
    with pytest.raises(Exception):
        game=Pong(MAX_SCORE=-1)

#I'm commenting out this test currently because it is unclear whether the game should 
#       throw an exception for an undefinied action, or do nothing (basically a wait step)
#       Refer to ple.py lines 361-367 in the definition of act(int) for this
#
#def test_invalid_action_input():
#    game=Pong()
#    p=PLE(game, display_screen=True, fps=20, force_fps=1)
#    p.init()
#    time.sleep(.5)
#    with pytest.raises(Exception):
#        p.act(10)

