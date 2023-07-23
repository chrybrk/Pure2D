#############################################################
#                           Imports                         #
#############################################################
import pygame, sys, math, random, time, os, json
import numpy as np
from pygame.locals import *
from enum import Enum
from PIL import Image

true = True; false = False; nil = None
clock = pygame.time.Clock()

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone', 'floor'}

def fpsLock(fps): return clock.tick(fps)

def err(msg):
    print(msg)
    exit(1)

def sine_wave(time, period, amplitude, midpoint):
    return math.sin(time * 2 * math.pi / period) * amplitude + midpoint
