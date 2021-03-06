# Game options
TITLE = "Jump High (aka JumPy)"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'Arial'
HS_FILE = 'highscores.txt'
SPRITESHEET = 'spritesheet_jumper.png'
PLAY_MUSIC = 'mushroom dance_0.ogg'
SCREEN_MUSIC = 'jump and run - tropics.ogg'

# Player properties
PLAYER_ACC = 0.8
PLAYER_FRICTION = -0.19
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = 20

# Game properties
BOOST_POWER = 60
POW_SPWAN_PCT = 10
MOB_FREQ = 7000
PLAYER_LAYER = 3
PLATFORM_LAYER = 1
POW_LAYER = PLATFORM_LAYER
MOB_LAYER = 2
MOB_MIN_SPEED = 1
MOB_MAX_SPEED = 4

# starting platforms
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (173, 230, 255)
BGCOLOR = LIGHTBLUE
