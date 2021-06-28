import curses

from constants_path import *
from texture import SNAKE_CHRATT, WALL_CHRATT
from option import opt_load

# load other variables
opt_load(OPTIONS_FILENAME, globals())	

# game settings
CTXT_SPEED # imported from settings

#==============================================================================#
# Colors

# Give Semantic Value to the color pair identifier
COLOR_NO_ARENA = 2
COLOR_NO_SNAKE = 3
COLOR_NO_WALL = 4

# Define the color pairs
#  Arena's color
def COLOR_SET():
	curses.init_pair(COLOR_NO_ARENA, -1, COLOR_BKG_ARENA)
	curses.init_pair(COLOR_NO_SNAKE, COLOR_SNAKE, COLOR_BKG_ARENA)
	curses.init_pair(COLOR_NO_WALL, COLOR_WALL, COLOR_BKG_ARENA)

	# set this colors in the snake/wall dictionary:
	for key, (ch, att) in SNAKE_CHRATT.items():
		SNAKE_CHRATT[key] = (ch, att | curses.color_pair(COLOR_NO_SNAKE))

	for key, (ch, att) in WALL_CHRATT.items():
		WALL_CHRATT[key] = (ch, att | curses.color_pair(COLOR_NO_WALL))

#==============================================================================#

# character used to draw food
FOOD_CHAR = '@'

# snake values
SNAKE_INITIAL_LENGTH = 5
SNAKE_SPEED # From Setting

# dead snake effect
SNAKE_DEAD_ATT = curses.A_BLINK

# dialog attributes
CURSOR_INS = curses.A_REVERSE
CURSOR_OWR = curses.A_UNDERLINE
CURSOR_BLINK_TIME = 0.5				# time in seconds
EDITOR_BLINK_TIME = 0.5				# time in seconds
EDITOR_MESSAGE_TIME = 4				# time for which a message is shown

# character used to display score. Remark that colors are stored in the settings
SCORE_CHAR_ON = ":"
SCORE_ATT_ON = curses.A_REVERSE
SCORE_CHAR_OFF = ":"
SCORE_ATT_OFF = curses.A_NORMAL

# attribute of portals
PORTAL_ATT = curses.A_REVERSE

# max number of entries in the highscore database
HIGHSCORE_MAX_SIZE = 100

# format of the date in the highscore entries
HIGHSCORE_DATE_FORMAT = '%d-%m-%Y %H:%M:%S'

# missing/wrong key from curses
MY_KEY_EXIT = 27

