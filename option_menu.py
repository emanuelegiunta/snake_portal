import tgame as tg

from option_menu_entries import get_options
from constants import *

# an entry is an object with the following methods:
#  key_enter
#  key_up
#  key_down
#  draw(x,y)
# and the following variables:
#  opt:		the option name visualized
#  name: 	the variable name
#  focus:	True/False

@tg.active_object
class options_menu(object):
	def __init__(self):

		# contains information on the options with the following syntax:
		#  .o = displayed option
		#  .n = associated variable name
		#  .s = string representing the current value
		#  .v = variable value (current)
		#  .t = input type
		#
		# E stands for "Entry"
		#

		self.options = get_options(self)

		# cursor functionality
		self.lcursor = 0
		self.lwrapper = 0

		self.rcursos = 0
		self.rwrapper = 0

		self.focus = 'left'

		# geometry
		self.h, self.w = tg.screen_size(self._s)

		self.dx = 3
		self.dy = 2
		self.x = self._get_x()

		# actual height reserved to the menu
		self.mh = self.h - 2*self.dy

	# helpers
	def _get_x(self):
		# generate the width of each column
		x = [
			0,
			max(len(opt.opt) \
				for opt in filter(lambda x : x is not None, self.options)),
			10,
		]
		
		# add the dx
		x = [y + self.dx for y in x]

		# get the positions
		x = [sum(x[:i+1]) for i in range(len(x))]

		return x


	# keys
	def _key_up(self):
		if self.focus == "left":
			# warp + cursor up movement
			if self.lcursor > 0:
				self.lcursor -= 1
				
				if self.lcursor < self.lwrapper:
					self.lwrapper -= 1

			else:
				self.lcursor = len(self.options) - 1
				self.lwrapper = max(0, len(self.options) - self.mh)

			# if we hit a None object, we keep going
			if self.options[self.lcursor] is None:
				self._key_up()

		else:
			self.options[self.lcursor].key_up()

	def _key_down(self):
		if self.focus == "left":
			# wrap + cursor up movement
			if self.lcursor < len(self.options) - 1:
				self.lcursor += 1

				if self.lcursor > self.lwrapper + self.mh - 1:
					self.lwrapper += 1

			else:
				self.lcursor = 0
				self.lwrapper = 0

			# if we hit a None object, we keep going
			if self.options[self.lcursor] is None:
				self._key_down()

		else:
			self.options[self.lcursor].key_down()

	def _key_enter(self):
		if self.focus == "left":
			# give focus to the current entry in the menu
			self.focus = "center"

		self.options[self.lcursor].key_enter()

	def _key_back(self):
		self._c.room_goto("Home")


	# focus handler	
	def return_focus(self):
		self.focus = "left"

	# events
	def ev_key(self, keycodes):
		for key in keycodes:
			if key == curses.KEY_UP:
				self._key_up()

			elif key == curses.KEY_DOWN:
				self._key_down()

			elif key == ord('\n'):
				self._key_enter()

			elif key in (curses.KEY_EXIT, MY_KEY_EXIT):
				self._key_back()

	# draw
	def ev_draw(self):

		# draw left menu and midvalues
		for y in range(0, min(self.mh, len(self.options))):

			i = y + self.lwrapper
			entry = self.options[i]

			if entry is not None:

				att = curses.A_NORMAL
				if i == self.lcursor and self.focus == "left":
					att |= curses.A_REVERSE

				# print the option name
				self._s.addstr(y + self.dy, self.x[0], entry.opt, att)

				# print the option value
				entry.draw(y + self.dy, self.x[1])
