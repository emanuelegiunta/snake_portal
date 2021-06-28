import curses

from constants import *
from class_io import text_field
from option import opt_set

#==============================================================================#
# Entry Definitions

def entry(cls):
	_old___init__ = cls.__init__

	def _new___init__(self, father, *argv, **kwarg):
		#assert False, kwarg
		# get the following keys, through error if not there.
		self.opt = kwarg.pop('o', kwarg.pop('opt', None))
		self.name = kwarg.pop('n', kwarg.pop('name', None))

		if self.opt is None or self.name is None:
			raise ValueError("Malformed Option")

		self.father = father
		self._c = father._c
		self._s = father._s

		# the value of the current variable has to be the one currently stored
		#  in the associated variable name
		self._value = globals()[self.name]

		_old___init__(self, *argv, **kwarg)

	cls.__init__ = _new___init__

	return cls

@entry
class entry_text(object):
	def __init__(self, **kwarg):
		# 'o', 'opt', 'n', 'name' are used above
		# 'f', 'filter'	: filter function
		# 'l', 'len' 	: number of entries in the filter

		self.filter = kwarg.pop('f', kwarg.pop('filter', lambda x : True))
		self.interpret = kwarg.pop('i', kwarg.pop('interpret', lambda x : x))
		self.represent = kwarg.pop('r', kwarg.pop('represent',\
			lambda x : str(x)))
		# the remaining keywords are passed to the prompt function
		self.kwarg = kwarg

		self.text_field = None

	def _store(self, value):
		# interpret the data received (dynamically passed at __init__)
		value = self.interpret(value)

		# update the option file
		opt_set(OPTIONS_FILENAME, self.name, value)

		# update the global value
		globals()[self.name] = value

		# update the local value
		self._value = value


	def key_up(self):
		pass

	def key_down(self):
		pass

	def key_enter(self):
		# if we are not adding anything:
		if self.text_field is None:
			self.text_field = text_field(self._c, s = self._s)

			# take controll of the draw event
			def empty_function():
				pass

			self.text_field.draw = self.text_field.ev_draw
			self.text_field.ev_draw = empty_function

			def fun(value):
				# check that the input string satisfies the given filter
				if self.filter(value):

					# Store the current value
					self._store(value)

				# destroy the dialog window
				self.text_field.destroy()
				self.text_field = None

				# return focus to the left side 
				self.father.return_focus()

			self.text_field.prompt(fun, **self.kwarg)

	def draw(self, y, x):
		if self.text_field is None:

			# draw a representation of the current value:
			self._s.addstr(y, x, self.represent(self._value))

		else:

			# draw the text field
			self.text_field.x = x 
			self.text_field.y = y
			self.text_field.draw()

@entry
class entry_tick(object):
	def __init__(self):
		self.tick = {
			True : "X",
			False : " " 
		}

	def key_up(self):
		pass

	def key_down(self):
		pass

	def key_enter(self):
		# update the local value
		self._value = not self._value

		# update the global value
		globals()[self.name] = self._value

		# update the option file
		opt_set(OPTIONS_FILENAME, self.name, self._value)

		# return the focus
		self.father.return_focus()


	def draw(self, y, x):
		self._s.addstr(y, x, "[{}]".format(self.tick[self._value]))

@entry
class entry_choice(object):
	def __init__(self, **kwarg):

		self.focus = False

		self.choices = kwarg.pop("c", kwarg.pop("choices", []))
		self.values = kwarg.pop("v", kwarg.pop("values", []))

		# assert that all elements in choices and values are different
		assert len(set(self.choices)) == len(self.choices), "Colliding choices"
		assert len(set(self.values)) == len(self.values), "Colliding values"

		# assert than choices and values have the same length
		assert len(self.choices) == len(self.values), "Choices and values number mismatch. Got {:d} choices and {:d} values".format(len(self.choices), len(self.values))

		# assert that the current value is in values
		assert self._value in self.values, "Current value not in list"

		# Get the index of the current value
		self.index = self.values.index(self._value)

	def key_up(self):
		self.index = (self.index - 1) % len(self.values)

	def key_down(self):
		self.index = (self.index + 1) % len(self.values)

	def key_enter(self):
		if self.focus:
			# update local value
			self._value = self.values[self.index]

			# update global value
			globals()[self.name] = self._value

			# update option file
			opt_set(OPTIONS_FILENAME, self.name, self._value)

			# return focus to the parent object
			self.father.return_focus()

			# remove focus from this object
			self.focus = False

		else:
			self.focus = True

	def draw(self, y, x):
		att = curses.A_NORMAL
		if self.focus:
			att |= curses.A_REVERSE	

		self._s.addstr(y, x, self.choices[self.index], att)


#==============================================================================#
# Helper functions and variables

_color_list = [
	"None",
	"White",
	"Black",
	"Blue",
	"Cyan",
	"Green",
	"Magenta",
	"Red",
	"Yellow"
]

_color_values = [
	-1,
	curses.COLOR_WHITE,
	curses.COLOR_BLACK,
	curses.COLOR_BLUE,
	curses.COLOR_CYAN,
	curses.COLOR_GREEN,
	curses.COLOR_MAGENTA,
	curses.COLOR_RED,
	curses.COLOR_YELLOW
]


#==============================================================================#
# Options list
# None objects are used to skip a line

def get_options(self):
	out = [
		entry_text(self,
			o = "Snake speed",
		 	n = 'SNAKE_SPEED',
		 	f = lambda s : s.isdigit() and int(s) <= self._c.speed,
		 	i = lambda s : int(s)),

		entry_text(self,
			o = "Frame per second",
			n = 'CTXT_SPEED',
			f = lambda s : s.isdigit() and int(s) <= 60,
			i = lambda s : int(s)),

		None,

		entry_choice(self,
			o = "Arena background color",
			n = "COLOR_BKG_ARENA",
			c = _color_list,
			v = _color_values),

		entry_choice(self,
			o = "Snake color",
			n = "COLOR_SNAKE",
			c = _color_list,
			v = _color_values),

		entry_choice(self,
			o = "Wall color",
			n = "COLOR_WALL",
			c = _color_list,
			v = _color_values),

		None,

		entry_choice(self,
			o = "Snake texture",
			n = 'SNAKE_FONT',
			c = ('Unicode', 'Ascii'),
			v = ('unicode', 'ascii')),

		entry_choice(self,
			o = "Wall texture",
			n = 'WALL_FONT',
			c = ('Unicode', 'Ascii'),
			v = ('unicode', 'ascii')),
	]

	return out