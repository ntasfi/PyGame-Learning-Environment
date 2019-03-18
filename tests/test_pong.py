#!/usr/bin/python
from ple import PLE
from ple.games.pong import Pong, Ball, Player
import pygame, time, sys, pytest

#This test passes if a positive difference in movement speed is detected
def test_movement_up():
    game=Pong()
    p=PLE(game, display_screen=True, fps=20, force_fps=1)
    p.init()
    time.sleep(.5)
    oldState=p.getGameState()
    p.act(game.actions["up"])
    newState=p.getGameState()
    assert oldState["player_velocity"] > newState["player_velocity"]

#This tests passes is a negative difference in movement speed is detected
def test_movement_down():
    game=Pong()
    p=PLE(game, display_screen=True, fps=20, force_fps=1)
    p.init()
    time.sleep(.5)
    oldState=p.getGameState()
    p.act(game.actions["down"])
    newState=p.getGameState()
    assert oldState["player_velocity"] < newState["player_velocity"]

#This test passes if an exception is thrown when a negative cpu speed is specified
def test_negative_cpu_speed():
    with pytest.raises(Exception):
        game=Pong(cpu_speed_ratio=-1)

#This test passes if an exception is thrown when a negative player speed is specified
def test_negative_player_speed():
    with pytest.raises(Exception):
        game=Pong(players_speed_ratio=-1)

#This test passes if an exception is thrown when a negative ball speed is specified
def test_negative_ball_speed():
    with pytest.raises(Exception):
        game=Pong(ball_speed_ratio=-1)

#This test passes if an exception is thrown when a negative game size is specified
def test_invalid_game_size():
    with pytest.raises(Exception):
        game=Pong(width=-200, height=-200)

#This test passes if an exception is thrown when a negative max score is specified
def test_invalid_max_score():
    with pytest.raises(Exception):
        game=Pong(MAX_SCORE=-1)