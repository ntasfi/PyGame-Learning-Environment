#!/usr/bin/python
from ple import PLE
from ple.games.raycastmaze import RaycastMaze
import pygame, time, sys, pytest


def test_oob_init_pos():
    with pytest.raises(Exception):
        game=RaycastMaze(init_pos=(-1,-1))

def test_below_min_map_size():
    with pytest.raises(Exception):
        game=RaycastMaze(map_size=3)

def test_beyond_max_map_size():
    with pytest.raises(Exception):
        game=RaycastMaze(map_size=400)

def test_negative_move_speed():
    with pytest.raises(Exception):
        game=RaycastMaze(move_speed=-1)

def test_negative_turn_speed():
    with pytest.raises(Exception):
        game=RaycastMaze(turn_speed=-1)

def test_beyond_max_turn_speed():
    with pytest.raises(Exception):
        game=RaycastMaze(turn_speed=400)

def test_negative_game_size():
    with pytest.raises(Exception):
        game=RaycastMaze(width=-100,height=-100)
