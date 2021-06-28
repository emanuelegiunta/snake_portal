# import script
import locale
import curses

from option import opt_load_single
from constants_path import OPTIONS_FILENAME

locale.setlocale(locale.LC_ALL, '')
_LC_ENC = locale.getpreferredencoding()

## some internal constants that should be later setted by some "setting" file
_SNAKE_FONT = opt_load_single(OPTIONS_FILENAME, 'SNAKE_FONT') 
_WALL_FONT = opt_load_single(OPTIONS_FILENAME, 'WALL_FONT')


## helper functions

def _try_encode(unicode_obj, otherwise):
	try:
		out = {}
		for key, value in unicode_obj.items():
			out[key] = value.encode(_LC_ENC)

		return out

	except UnicodeError:
		return otherwise

def _zip_dict(*argv):
	out = {}
	if argv:
		for key in argv[0].keys():
			out[key] = tuple(d[key] for d in argv)

	return out


#==============================================================================#
### Internal encoding database - should probably be replaced by a file read
#
# legend:
#  u/l/d/r = up / left / down / right
#  h/t = head / tail
#  p = portal
#
#  so "ul" means the character used for a piece entering from above and leaving
#  on the left. "dp" means entering from below and leaving through a portal
#  "phd" means entering from a portal as head directed below

# - - snake - - #
_SNAKE_KEYS = ['dd', 'dh', 'dhp', 'dl', 'dp', 'dr', 'ld', 'lh', 'lhp', 'll', 
	'lp', 'lu', 'pd', 'phd', 'phl', 'phr', 'phu', 'pl', 'pr', 'ptd', 'ptl',
	'ptr', 'ptu', 'pu', 'rd', 'rh', 'rhp', 'rp', 'rr', 'ru', 'td', 'tl', 'tp',
	'tr', 'tu', 'uh', 'uhp', 'ul', 'up', 'ur', 'uu']

_SNAKE_CHAR_UNICODE = {
	# from up to ...
	"uu" : u'\N{box drawings double vertical}', 
	"ul" : u'\N{box drawings double down and left}', 
	"ur" : u'\N{box drawings double down and right}',

	# from left to ...
	"lu" : u'\N{box drawings double up and right}',
	"ll" : u'\N{box drawings double horizontal}',
	"ld" : u'\N{box drawings double down and right}',

	# from down to ...
	"dl" : u'\N{box drawings double up and left}',
	"dd" : u'\N{box drawings double vertical}',
	"dr" : u'\N{box drawings double up and right}',

	# from right to ...
	"ru" : u'\N{box drawings double up and left}',
	"rd" : u'\N{box drawings double down and left}',
	"rr" : u'\N{box drawings double horizontal}',

	# from tail to ...
	"tu" : u'\N{box drawings light up}',
	"tl" : u'\N{box drawings light left}',
	"td" : u'\N{box drawings light down}',
	"tr" : u'\N{box drawings light right}',
	"tp" : u'\N{middle dot}',

	# from portal, tail to ...
	"ptu" : u'\N{box drawings light up}',
	"ptl" : u'\N{box drawings light left}',
	"ptd" : u'\N{box drawings light down}',
	"ptr" : u'\N{box drawings light right}',
	"tp" : u'\N{middle dot}',

	# from ... to head
	"uh" : u'\N{black up-pointing small triangle}',
	"lh" : u'\N{black left-pointing small triangle}',
	"dh" : u'\N{black down-pointing small triangle}', 
	"rh" : u'\N{black right-pointing small triangle}',

	# from ... to portal
	"up" : u'\N{box drawings light down}', 
	"lp" : u'\N{box drawings light right}', 
	"rp" : u'\N{box drawings light left}', 
	"dp" : u'\N{box drawings light up}',

	# from portal to ...
	"pu" : u'\N{box drawings light up}',
	"pl" : u'\N{box drawings light left}', 
	"pr" : u'\N{box drawings light right}',
	"pd" : u'\N{box drawings light down}',

	# from portal to head toward
	"phu" : u'\N{black up-pointing small triangle}',
	"phl" : u'\N{black left-pointing small triangle}',
	"phr" : u'\N{black right-pointing small triangle}',
	"phd" : u'\N{black down-pointing small triangle}',

	# from ... to head toward portal
	"uhp" : u'\N{black up-pointing small triangle}',
	"lhp" : u'\N{black left-pointing small triangle}',
	"rhp" : u'\N{black right-pointing small triangle}',
	"dhp" : u'\N{black down-pointing small triangle}',
}

_SNAKE_CHAR_ASCII = {}
for key in _SNAKE_KEYS:
	if 'h' in key:
		_SNAKE_CHAR_ASCII[key] = 'Q'

	elif 't' in key:
		_SNAKE_CHAR_ASCII[key] = 'o'

	else:
		_SNAKE_CHAR_ASCII[key] = '0'

_SNAKE_ATT_UNICODE = {}
for key in _SNAKE_KEYS:
	if 'p' in key:
		_SNAKE_ATT_UNICODE[key] = curses.A_REVERSE
	else:
		_SNAKE_ATT_UNICODE[key] = curses.A_NORMAL

_SNAKE_ATT_ASCII = {}
for key in _SNAKE_KEYS:
	_SNAKE_ATT_ASCII[key] = curses.A_BOLD

# - - wall - - #
_NONE = 0
_U = 1
_L = 2
_D = 4
_R = 8

_WALL_KEYS = range(0, 16)

_WALL_CHAR_UNICODE = {
	_NONE : u'\N{black small square}',

	_U : u'\N{box drawings heavy up}',
	_L : u'\N{box drawings heavy left}',
	_D : u'\N{box drawings heavy down}',
	_R : u'\N{box drawings heavy right}',

	_U|_L : u'\N{box drawings heavy up and left}',
	_U|_D : u'\N{box drawings heavy vertical}',
	_U|_R : u'\N{box drawings heavy up and right}',
	_L|_D : u'\N{box drawings heavy down and left}',
	_L|_R : u'\N{box drawings heavy horizontal}',
	_D|_R : u'\N{box drawings heavy down and right}',

	_U|_L|_D : u'\N{box drawings heavy vertical and left}',
	_U|_L|_R : u'\N{box drawings heavy up and horizontal}',
	_U|_D|_R : u'\N{box drawings heavy vertical and right}',
	_L|_D|_R : u'\N{box drawings heavy down and horizontal}',

	_U|_L|_D|_R : u'\N{box drawings heavy vertical and horizontal}',
}

_WALL_CHAR_ASCII = {}
for key in _WALL_KEYS:
	_WALL_CHAR_ASCII[key] = '#'

_WALL_ATT_UNICODE = {}
for key in _WALL_KEYS:
	_WALL_ATT_UNICODE[key] = curses.A_NORMAL

_WALL_ATT_ASCII = _WALL_ATT_UNICODE


#==============================================================================#
### Intermediate dictionaries

# setup the SNAKE
if _SNAKE_FONT == "unicode":
	_SNAKE_CHAR = _try_encode(_SNAKE_CHAR_UNICODE, None)

	if _SNAKE_CHAR is None:
		# if the encoding failed
		_SNAKE_FONT = "ascii"
	else:
		# if the encoding succeded
		_SNAKE_ATT = _SNAKE_ATT_UNICODE

# back up condition - or a setting
if _SNAKE_FONT == "ascii":
	_SNAKE_CHAR = _SNAKE_CHAR_ASCII
	_SNAKE_ATT = _SNAKE_ATT_ASCII


# setup the WALL
if _WALL_FONT == "unicode":
	_WALL_CHAR = _try_encode(_WALL_CHAR_UNICODE, None)

	if _WALL_CHAR is None:
		# if the encoding failed
		_WALL_FONT = "ascii"

	else:
		# if the encoding suceede
		_WALL_ATT = _WALL_ATT_UNICODE

# back up condition - or a setting
if _WALL_FONT == "ascii":
	_WALL_CHAR = _WALL_CHAR_ASCII
	_WALL_ATT = _WALL_ATT_ASCII


#==============================================================================#
### External dictionaries (this stuff is actually imported)

SNAKE_CHRATT = _zip_dict(_SNAKE_CHAR, _SNAKE_ATT)
WALL_CHRATT = _zip_dict(_WALL_CHAR, _WALL_ATT)

# constant for key refence
WALL_KEY_NONE = 0
WALL_KEY_UP = _U
WALL_KEY_LEFT = _L
WALL_KEY_DOWN = _D
WALL_KEY_RIGHT = _R