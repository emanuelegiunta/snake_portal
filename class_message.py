import curses
import tgame as tg

from constants import CURSOR_INS, CURSOR_OWR, CURSOR_BLINK_TIME

@tg.active_object
class dialog(object):
	def __init__(self, message_x, message_y, input_x, input_y \
	,		message_att = None):
		#
		if message_att is None:
			message_att = curses.A_NORMAL

		self.message = ""	# publicly settable

		self._input = "" 	# Read only

		self._mx = message_x
		self._my = message_y
		self._matt = message_att

		self._ix = input_x
		self._iy = input_y
		self._imax = float('inf')
		self._if = None
		self._iflag = False
		self._ireset()


	# Interface
	@property
	def input(self):
		if not self._iflag:
			return self._input

	@input.setter
	def input(self):
		#
		raise TypeError("Assignment to a protected variable")
	
	# Initialise the Input
	def _ireset(self):
		self._input = ""

		self._ic = 0				# cursor position
		self._icblink = True
		self._icblink_timer = 0
		self._iins = True

	def prompt(self, *argv, **kwarg):
		# Ugly - if both message and m are passed only m is considered.
		#  should chech for both and raise an error in case both are used
		self.message = kwarg.pop('m', kwarg.pop('message', ''))
		self._imax = kwarg.pop('l', kwarg.pop('input_len', float('inf')))

		self._ireset()
		self._iflag = True
		self._if = argv			# list of functions/methods to pass "input" to

	# Internal action acording to the key pressed
	def _reset_blink(self):
		self._icblink = True
		self._icblink_timer = 0

	def _ch(self, c):
		if self._iins and len(self._input) < self._imax:
			# insert the char at cursor position and move the cursor forward
			self._input = self._input[:self._ic] + c + self._input[self._ic:]
			self._ic += 1

		if not self._iins and self._ic < self._imax:
			self._input = self._input[:self._ic] + c + self._input[1+self._ic:]
			self._ic += 1

		self._reset_blink()

	def _backspace(self):
		# act indepently from insert or overwrite
		#  if the cursor is at position 0, do nothing
		if self._ic != 0:
			self._input = self._input[:self._ic - 1] + self._input[self._ic:]
			self._ic -= 1
		
		self._reset_blink()

	def _cancel(self):
		self._input = self._input[:self._ic] + self._input[1 + self._ic:]

		self._reset_blink()

	def _left(self):
		if self._ic > 0:
			self._ic -= 1

		self._reset_blink()

	def _right(self):
		# the cursor can exceed the max input len by 1
		if self._ic < min(self._imax, len(self._input)):
			self._ic += 1

		self._reset_blink()

	def _ins(self):
		#
		self._iins = not self._iins

	def _enter(self):
		#
		self._iflag = False

		for f in self._if:
			f(self._input)

	# events
	def ev_step(self):
		self._icblink_timer += 1
		if self._icblink_timer >= CURSOR_BLINK_TIME*self._c.speed:
			self._icblink = not self._icblink
			self._icblink_timer = 0

	def ev_key(self, keycodes):
		for c in keycodes:
			if self._iflag:
				# look for characters
				if (126 >= c and c >= 32):
					self._ch(chr(c))

				# lok for backspace
				elif c == curses.KEY_BACKSPACE:
					self._backspace()

				elif c == curses.KEY_DC:
					self._cancel()

				elif c == curses.KEY_ENTER or c == ord('\n'):
					self._enter()

				elif c == curses.KEY_LEFT:
					self._left()

				elif c == curses.KEY_RIGHT:
					self._right()

				elif c == curses.KEY_IC:
					self._ins()

		# DEBUG
		if curses.KEY_BACKSPACE in keycodes:
			for inst in self._c.instance_of('debug'):
				inst.flag = True

		if keycodes:
			for inst in self._c.instance_of('debug'):
				inst.keys = keycodes

	def ev_draw(self):
		self._s.addstr(self._my, self._mx, self.message, self._matt)

		if self._iflag:
			self._s.addstr(self._iy, self._ix, self._input)

			# draw the cursor
			if self._icblink:
				# get the attribute and character to write at cursor position
				if self._iins:
					att = CURSOR_INS
				else:
					att = CURSOR_OWR
				ch = (self._input + " ")[self._ic]

				self._s.addch(self._iy, self._ix + self._ic, ch, att)
