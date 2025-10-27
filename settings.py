# settings.py

import pygame
import os

# display settings
TITLE = "Tank War"
TILE_SIZE = 32
MAP_WIDTH_TILES = 26
MAP_HEIGHT_TILES = 26
SCREEN_WIDTH = MAP_WIDTH_TILES * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT_TILES * TILE_SIZE
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60

# color define for UI
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# path of resources
BASE_DIR = os.path.dirname(__file__)
RESOURCE_DIR = os.path.join(BASE_DIR, 'resources')
IMAGE_DIR = os.path.join(RESOURCE_DIR, 'images')
SOUND_DIR = os.path.join(RESOURCE_DIR, 'musics')

# filename of images
IMG_P1_UP = 'hero/hero1U.gif'
IMG_P1_DOWN = 'hero/hero1D.gif'
IMG_P1_LEFT = 'hero/hero1L.gif'
IMG_P1_RIGHT = 'hero/hero1R.gif'
IMG_P2_UP = 'hero/hero1U.gif' 
IMG_P2_DOWN = 'hero/hero1D.gif'
IMG_P2_LEFT = 'hero/hero1L.gif'
IMG_P2_RIGHT = 'hero/hero1R.gif'
IMG_ENEMY_WHITE_UP = 'enemy/enemy1U.gif'
IMG_ENEMY_WHITE_DOWN = 'enemy/enemy1D.gif'
IMG_ENEMY_WHITE_LEFT = 'enemy/enemy1L.gif'
IMG_ENEMY_WHITE_RIGHT = 'enemy/enemy1R.gif'
IMG_ENEMY_GREEN_UP = 'enemy/enemy2U.gif'
IMG_ENEMY_GREEN_DOWN = 'enemy/enemy2D.gif'
IMG_ENEMY_GREEN_LEFT = 'enemy/enemy2L.gif'
IMG_ENEMY_GREEN_RIGHT = 'enemy/enemy2R.gif'
IMG_BULLET = 'bullet/bullet.gif'
IMG_WALL_RED = 'walls/1.png'
IMG_WALL_IRON = 'walls/2.png'
IMG_BUSH = 'walls/3.png'
IMG_BOSS = 'walls/5.png'

SND_FIRE = 'fire.wav'
SND_BANG_ENEMY = 'boom.wav'
SND_BANG_PLAYER = 'boom.wav'
SND_HIT_IRON = 'boom.wav'

# player and enemy tank information
PLAYER_HP = 3
PLAYER_SPEED = 3
PLAYER_HEAL_ON_KILL = 1 

ENEMY_TOTAL_COUNT = 20  # total 20 enemies
ENEMY_START_COUNT = 8   # begin with 8 on screen
ENEMY_MAX_ON_SCREEN = 8 # max 8 on screen

ENEMY_HP_WHITE = 1
ENEMY_HP_GREEN = 2
ENEMY_SPEED = 2
ENEMY_SHOOT_COOLDOWN = 1500
BULLET_SPEED = 7
BULLET_COOLDOWN = 500

# for map.py
MAP_TILE_EMPTY = 0
MAP_TILE_RED_WALL = 1
MAP_TILE_IRON_WALL = 2
MAP_TILE_BUSH = 3
MAP_TILE_BOSS = 5

# define input keys
P1_UP = pygame.K_w
P1_DOWN = pygame.K_s
P1_LEFT = pygame.K_a
P1_RIGHT = pygame.K_d
P1_SHOOT = pygame.K_SPACE
P2_UP = pygame.K_UP
P2_DOWN = pygame.K_DOWN
P2_LEFT = pygame.K_LEFT
P2_RIGHT = pygame.K_RIGHT

P2_SHOOT = pygame.K_RETURN

