import tgame as tg
import os

from constants import *
from csv import csv_write, csv_exists, csv_load
from datetime import datetime

#==============================================================================#
# Compatibility with python2.7

def _filter_first(vec):
	try:
		return next(vec)
	except TypeError:
		return vec[0]


#==============================================================================#
# Score
@tg.active_object
class score(object):
	def __init__(self, x, y):

		self._x = x
		self._y = y

		self._score = SNAKE_INITIAL_LENGTH
		self.username = None
		self._levelname = None
		self._highest_score = 0 		# Dummy value before initialization



	# Setters/Getters
	@property
	def score(self):
		# setter
		return self._score

	@score.setter
	def score(self, value):
		self._score = value

		if self._highest_score < value:
			self._highest_score = value

	@property
	def levelname(self):
		# getter
		return self._levelname

	@levelname.setter
	def levelname(self, value):

		self._levelname = value
		self._highscore_load()

	
	# reset function
	def reset(self, l = None):
		# just a rough patch
		self._score = SNAKE_INITIAL_LENGTH
		self.username = None
		
		if l is not None:
			# remove the path from l, but leave the extension
			l = l.split('/')[-1]

		self.levelname = l

		# highscore functions
		# DEPRECATED?
		self._highscore_load()

	# highscore functions
	def highscore_update(self):
		'''Update the highscore adding the current score.

		Note:
		This function is supposed to be called after the snake died - before
		the transition to the highest score room
		'''
		self._highscore_add()
		self._highscore_write()

	def _highscore_load(self):
		'''Set the local highscore from file
		'''
		filename = HIGHSCORE_FILENAME

		if csv_exists(filename):
			# load data from file
			self._data = csv_load(filename)

			# filter data accoding to the current level
			level_data = filter(lambda x : x[3] == self._levelname, \
				self._data)

			# get the highest score as the first entry of the filtered data
			#  assuming that level_data is non empty, otherwise return current
			#  score
			#
			# The try...except is for python2.7 compatibility
			try:
				best = next(level_data, None)
				if best is not None:
					self._highest_score = best[1]
				else:
					self._highest_score = max(0, self._score)
			except TypeError:
				# assuming we are running in a version where filter returns list
				if level_data:
					self._highest_score = _filter_first(level_data)[1]
				else:
					self._highest_score = max(0, self._score)
			
		else:
			self._data = []
			self._highest_score = max(0, self._score)

	def _highscore_write(self):
		'''Write the local highscore to file
		'''
		#
		filename = HIGHSCORE_FILENAME

		csv_write(filename, self._data)

	def _highscore_add(self):
		'''Add a new entry in the local highscore data
		'''
		#
		# data format:
		#  [username, score, date, level]

		self._data.append([
			self.username, 
			self._score,
			datetime.today().strftime(HIGHSCORE_DATE_FORMAT),
			self.levelname])

		# sort according to the score (in position 1)
		self._data.sort(key = lambda x : x[1], reverse = True)

		# drop the last entries if they are more than HIGHSCORE_MAX_SIZE
		#  entries associated to the current level
		this_level_data = filter(lambda x : x[3] == self.levelname, self._data)
		this_level_data = list(this_level_data)
		if len(this_level_data) > HIGHSCORE_MAX_SIZE:

			# remove the last entries 
			last_entry = this_level_data[-1]
			self._data.remove(last_entry)


	# basic manipulation of displayed numbers
	def _display_number(self, n, x, y):
		assert (n >= -1 and n <= 9 and type(n) == int), "Malformed input"

		# set the bit to keep off
		if n == -1:
			cell_off_list = [(k%3, k//3) for k in range(15)]
		if n == 0:
			cell_off_list = ((1, 1), (1, 2), (1, 3))
		elif n == 1:
			cell_off_list = ((0, 0), (0, 2), (0, 3), (2, 0), (2, 1), \
							 (2, 2), (2, 3))
		elif n == 2:
			cell_off_list = ((0, 1), (1, 1), (1, 3), (2, 3))
		elif n == 3:
			cell_off_list = ((0, 1), (0, 2), (0, 3), (1, 1), (1, 3))
		elif n == 4:
			cell_off_list = ((0, 4), (1, 0), (1, 1), (1, 2), (2, 0), \
							 (2, 1), (2, 2), (2, 4))
		elif n == 5:
			cell_off_list = ((0, 3), (1, 1), (1, 3), (2, 1))
		elif n == 6:
			cell_off_list = ((1, 1), (1, 3), (2, 1))
		elif n == 7:
			cell_off_list = ((0, 1), (0, 2), (0, 3), (0, 4), (1, 1), \
							 (1, 2), (1, 3), (1, 4))
		elif n == 8:
			cell_off_list = ((1, 1), (1, 3))
		elif n == 9:
			cell_off_list = ((1, 1), (0, 3), (1, 3))

		# print the number on screen
		for pos_x in range(x, x + 3):
			for pos_y in range(y, y + 5):
				# if the cell is turned off
				if (pos_x - x, pos_y - y) in cell_off_list:
					self._s.addch(pos_y, pos_x, SCORE_CHAR_OFF, SCORE_ATT_OFF)
				else:
					self._s.addch(pos_y, pos_x, SCORE_CHAR_ON, SCORE_ATT_ON)

	def _display_all(self, x, y, n):
		# ugly
		n1 = n%10
		n2 = (n//10)%10
		n3 = (n//100)%10
		n4 = (n//1000)%10

		# don't display most significant zeroes
		if n4 == 0:
			n4 = -1
			if n3 == 0:
				n3 = -1
				if n2 == 0:
					n2 = -1

		self._display_number(n4, x, y)
		self._display_number(n3, x + 4, y)
		self._display_number(n2, x + 8, y)
		self._display_number(n1, x + 12, y)

	# events
	def ev_draw(self):
		#
		self._display_all(self._x + 1, self._y + 2, self._score)

		self._display_all(self._x + 1, self._y + 10, self._highest_score)

		self._s.addstr(self._y, self._x, "Current Score:")
		self._s.addstr(self._y + 8, self._x, "Highest Score:")


#=============================================================================#


# old style object adapted - it probably need more love

@tg.active_object
class highscore(object):
	def __init__(self):

		self.h, self.w = tg.screen_size(self._s)
		self.lcursor = 0
		self.rcursor = 0
		self.rwrapper = 0

		# header of the displayed data
		self.headers = ["Player", "Score", "Date"]

		# position of the separator between left and right menus
		self.sep = 50

		# space from the sep of the right menu
		self.rxoff = 3
		self.ryoff = 1

		self.focus = 'left'

		# load data from file
		self.load_data()


	def load_data(self):
		# load data
		if csv_exists(HIGHSCORE_FILENAME):
			self.data = csv_load(HIGHSCORE_FILENAME)
		else:
			self.data = []

		# convert data to string
		self.data = [[str(x) for x in row] for row in self.data]

		# get the available levels
		self.levels = self._game_get_list()

		# Get filtered_data
		self._filter_data()

	def _filter_data(self):
		level = self.levels[self.rcursor]

		# the third position is the one associated with levels!
		self.filtered_data = filter(lambda row : row[3] == level, self.data)
		self.filtered_data = list(self.filtered_data)

		# reset the left cursor to avoid pointers out of range
		self.lcursor = 0

	def _draw_line(self, y, x, length = None, char = " -" \
		,	att = curses.A_DIM):

		# by default lines are designed to be used on left menu
		if length == None:
			length = self.sep

		self._s.addstr(y, x, char*(length//len(char)), att)

	def _get_displayed_entries(self):
		# Number of entries currently displayed
		#  This equal the numer of filtered elements if there is enough space
		#  on screen, converely equals the maxium number of entries that fits 
		#  into the screen
		return min((self.h - 2)//2, len(self.filtered_data))

	def _game_get_list(self):
		''' return a list of all possible levels

		Note:
		Refers to the folder FILE_PATH. If there is no .EXT_LEVEL raise an
		IOError.
		'''

		file_list = [s for s in os.listdir(FILE_PATH) \
			if tg.extension_get(s) == EXT_LEVEL]

		if not file_list:
			raise IOError("No .{} file found in {}!".format( \
				EXT_LEVEL, FILE_PATH))
		else:
			file_list.sort()
			return file_list


	# key commands
	def _key_up(self):
		if self.focus == "left":
			if self.lcursor > 0:
				self.lcursor -= 1

		elif self.focus == "right":
			if self.rcursor > 0:
				self.rcursor -= 1

				# if i went over the wrapper
				if self.rwrapper > self.rcursor:
					self.rwrapper += 1

			else:
				self.rcursor = len(self.levels) - 1
				self.rwrapper = max(0, len(self.levels) - self.h)

			self._filter_data()

	def _key_down(self):
		if self.focus == "left":
			if self.lcursor < len(self.filtered_data) -\
					self._get_displayed_entries():
				#
				self.lcursor += 1

		elif self.focus == "right":
			if self.rcursor < len(self.levels) - 1:
				self.rcursor += 1

				# if i went over the wrapper
				if self.rwrapper < self.rcursor - self.h + 1:
					self.rwrapper -= 1

			else:
				self.rcursor = 0
				self.rwrapper = 0

			self._filter_data()

	def _key_left(self):
		#
		self.focus = "left"

	def _key_right(self):
		#
		self.focus = "right"

	def _key_swich(self):
		if self.focus == "left":
			self.focus = "right"
		else:
			self.focus = "left"

	# events
	def ev_draw(self):

		### draw left menu ###
		maxw = [16, 4, 19]

		# Update the current max width with the header
		maxw = [max(maxw[i], len(self.headers[i])) for i in range(3)]

		# Get the delta between columns
		delta = (self.sep - sum(maxw))//(len(self.headers) + 2)

		# Get the data printing positions
		posx = [(i + 1)*delta + sum(maxw[:i]) for i in range(3)]

		# Print the header
		for x, entry in zip(posx, self.headers):
			self._s.addstr(0, x, entry, curses.A_BOLD)
		self._draw_line(1, 0, length = self.sep, char = "-")

		# Print data
		entries_number = self._get_displayed_entries()
		for i in range(0, entries_number):

			# set the starting point to the cursor position
			j = i + self.lcursor
			for x, value in zip(posx, self.filtered_data[j]):
				# if not on focus, dim the current values
				att = curses.A_NORMAL
				if self.focus == "right":
					att |= curses.A_DIM

				# print data
				self._s.addstr(2 + 2*i, x, value, att)
				self._draw_line(3 + 2*i, 0, length = self.sep)

		### draw right menu ###
		for y in range(min(self.h, len(self.levels[self.rwrapper:]))):

			i = y + self.rwrapper
			# if on focus, highlight the current choice
			if self.rcursor == i and self.focus == 'right':
				att = curses.A_REVERSE
			else:
				att = curses.A_NORMAL

			if self.focus == "left":
				att |= curses.A_DIM

			self._s.addstr(y + self.ryoff, self.rxoff + self.sep, \
				self.levels[i], att)

	def ev_key(self, keycodes):
		if ord("w") in keycodes or ord("W") in keycodes or \
				curses.KEY_UP in keycodes:
			#
			self._key_up()

		elif ord("s") in keycodes or ord("S") in keycodes or \
				curses.KEY_DOWN in keycodes:
			#
			self._key_down()

		elif ord("d") in keycodes or ord("D") in keycodes or \
				curses.KEY_RIGHT in keycodes:
			#
			self._key_right()

		elif ord("a") in keycodes or ord("A") in keycodes or \
				curses.KEY_LEFT in keycodes:
			#
			self._key_left()

		elif ord('\t') in keycodes:
			#
			self._key_swich()

		elif keycodes:
			self._c.room_goto('Home')
