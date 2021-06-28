import tgame as tg
import curses

from constants import *
from texture import *

#==============================================================================#
# Compatibility functions

def _filter_first(vec):
	try:
		return next(vec)
	except TypeError:
		return vec[0]


@tg.timer
@tg.active_object
class cursor(object):
	def __init__(self):
		self.h, self.w = tg.screen_size(self._s)
		self.x = 0
		self.y = 0

		# normal/portal/wall/del
		self._mode = "normal"

		self.snake = None		
		self.walls = set()
		self.portals = []
		self._new_portal = None

		self.dialog = _filter_first(self._c.instance_of("dialog"))

		self.timer['c'] = int(EDITOR_BLINK_TIME*self._c.speed)
		self.cursor_visible = True

		self._focus = True

	# focus setter and getter
	@property
	def focus(self):
		return self._focus

	@focus.setter
	def focus(self, value):
		self._focus = value

		if value:
			self._cursor_reset()

		else:
			# deactivate the timer
			self.timer['c'] = -1
			self.cursor_visible = True

	# helper
	def _portal_other(self, x, y):
		i = self.portals.index((x, y))
		j = i + 1 - 2*(i % 2)
		return self.portals[j]

	def _cursor_reset(self):
		self.timer['c'] = int(EDITOR_BLINK_TIME*self._c.speed)
		self.cursor_visible = True

	def _message(self, msg):
		self.dialog.message = msg 
		self.timer['m'] = int(EDITOR_MESSAGE_TIME*self._c.speed)


	# save functions
	def save_ready(self):
		# return true if the level is ready to be saved, otherwise return false
		#  and print a message

		if self.snake is None:
			self._message("Cannot save a game without a Snake")
			return False

		return True

	def save(self, filename):
		# save the current level
		filename = tg.extension_set(FILE_PATH + filename, EXT_LEVEL)

		with open(filename, 'w') as f:

			# add the snake's head
			f.write('"snake";{:d};{:d}\n'.format(*self.snake))

			# add portals
			for i in range(len(self.portals)//2):
				x1, y1 = self.portals[2*i]
				x2, y2 = self.portals[2*i + 1]
				f.write('"portal";{:d};{:d};{:d};{:d}\n'.format(x1, y1, x2, y2))

			# add walls
			for w in self.walls:
				f.write('"wall";{}\n'.format(w))
		
	def close(self):
		self.x = 0
		self.y = 0

		# normal/portal/wall/del
		self._mode = "normal"

		self.snake = None		
		self.walls = set()
		self.portals = []
		self._new_portal = None

		# dialog message might need a refresh
		self.dialog.message = ""

		self.timer['c'] = int(EDITOR_BLINK_TIME*self._c.speed)
		self.cursor_visible = True

		self._c.room_goto("Home")

	def save_and_close(self, filename):
		# reset everything and leave
		self.save(filename)
		self.close()


	# key functions
	def key_arrow(self):
		# reset the blinking cursor
		self._cursor_reset()

		x, y = self.x, self.y
		if self._mode == 'wall':

			# if not on snake/portal
			if self.snake == (x, y):
				self._mode = "normal"
				self._message("Cannot build walls on Snake's Head")

			elif (x, y) in self.portals:
				self._mode = "normal"
				self._message("Cannot build walls on portals")

			else:
				self.walls = self.walls | {(x, y)}

		if self._mode == 'del':

			if self.snake == (x, y):
				self.snake = None

			if (x, y) in self.portals:
				other = self._portal_other(x, y)
				self.portals.remove((x, y))
				self.portals.remove(other)

			self.walls = self.walls - {(x, y)}

	def key_snake(self):
		# the snake shall not be removed once placed
		if self._mode == "normal":
			x, y = self.x, self.y
			if (x,y) in self.portals:
				self._message("Cannot place a Snake's head in a Portal")

			elif (x, y) in self.walls:
				self._message("Cannot place a Snake's head inside a wall")
			else:
				self.snake = (x, y)	

	def key_wall_mode(self):
		#
		if self._mode != "wall":
			self._new_portal = None
			self._mode = "wall"
		else:
			self._mode = "normal"

		# pretend that we pressed an arrow key to build a wall now
		self.key_arrow()
		
	def key_portal(self):
		x, y = self.x, self.y

		# pressing p over a wall - throw a warning
		if (x, y) in self.walls:
			self._message("Cannot build portals on walls")
			return

		# pressing p over the snake cause a warning
		if (x, y) == self.snake:
			self._message("Cannot build portals on Snake's head")

		# else ...
		if self._new_portal is None:

			# pressing p over a portal will remove it
			if (x, y) in self.portals:

				# remove the portal
				other = self._portal_other(x, y)
				self.portals.remove(other)
				self.portals.remove((x, y))

			# pressing p on empty space create a new portal
			else:
				self._new_portal = (x, y)
				self._mode = 'portal'

		# if I'm already building a new portal
		else:
			# if pressing p on other portal - do nothing
			if (x, y) in self.portals:

				# throw a warning
				self._message("Portals cannot overlap")

			# if pressing p on same new portal - do nothing
			elif (x, y) == self._new_portal:

				# throw a warning
				self._message("Linked portals have to be on different places")

			# if pressing p on open space
			else:
				self.portals.append(self._new_portal)
				self.portals.append((x, y))

				self._new_portal = None
				self._mode = "normal"

	def key_esc(self):
		# quit from current special state
		self._new_portal = None
		self._mode = "normal"

	def key_del(self):
		if self._mode != "del":
			self._mode = "del"
			self._new_portal = None

		else:
			self._mode = "normal"

		# pretend we pressed an arrow key so we can destory things now
		self.key_arrow()


	# drawing methods
	def draw_snake(self):
		if self.snake is not None:
			x, y = self.snake

			# print head
			self._s.addstr(y, x, *SNAKE_CHRATT['rh'])

			# print body
			for i in range(1, 4):
				self._s.addstr(y, (x - i)%self.w, *SNAKE_CHRATT['rr'])

			# print tail	
			self._s.addstr(y, (x - 4)%self.w, *SNAKE_CHRATT['tr'])

	def draw_portals(self):
		c = []
		c += [chr(ord('A') + i) for i in range(26)]
		c += [chr(ord('a') + i) for i in range(26)]

		for i, (x, y) in enumerate(self.portals):
			self._s.addstr(y, x, c[i//2], curses.A_REVERSE)

		# draw new portal
		if self._new_portal is not None:
			x, y = self._new_portal
			self._s.addstr(y, x, c[len(self.portals)//2])

	def draw_walls(self):
		for (x, y) in self.walls:
			key = WALL_KEY_NONE

			if (x + 1, y) in self.walls:
				key |= WALL_KEY_RIGHT

			if (x - 1, y) in self.walls:
				key |= WALL_KEY_LEFT

			if (x, y + 1) in self.walls:
				key |= WALL_KEY_DOWN

			if (x, y - 1) in self.walls:
				key |= WALL_KEY_UP

			self._s.addstr(y, x, *WALL_CHRATT[key])

	def draw_cursor(self):
		#
		if self.cursor_visible:
			a = curses.A_BOLD

			if not self._focus:
				a |= curses.A_DIM

			if self._mode == "normal":
				c = '0'
			elif self._mode == "portal":
				c = 'P'
			elif self._mode == "wall":
				c = 'W'
			elif self._mode == "del":
				c = 'X'
			self._s.addstr(self.y, self.x, c, a)


	# events
	def ev_step(self):
		# check the timer
		if self.timer['c'] == 0:
			self.timer['c'] = int(EDITOR_BLINK_TIME*self._c.speed)
			self.cursor_visible = not self.cursor_visible

		if self.timer['m'] == 0:
			self.dialog.message = ''

	def ev_key(self, keycodes):
		if self._focus:
			for key in keycodes:
				if key == curses.KEY_UP:
					self.y = (self.y - 1) % self.h
					self.key_arrow()

				elif key == curses.KEY_LEFT:
					self.x = (self.x - 1) % self.w
					self.key_arrow()

				elif key == curses.KEY_DOWN:
					self.y = (self.y + 1) % self.h
					self.key_arrow()

				elif key == curses.KEY_RIGHT:
					self.x = (self.x + 1) % self.w
					self.key_arrow()	

				elif key in ():
					self.key_wall()

				elif key in (ord('s'), ord('S')):
					self.key_snake()

				elif key in (ord('a'), ord('A')):
					self.key_portal()

				elif key in (ord('w'), ord('W')):
					self.key_wall_mode()

				elif key in (ord('d'), ord('D')):
					self.key_del()

				elif key in (ord('o'), ord('O')):
					self.key_options()

				elif key in (curses.KEY_DC, curses.KEY_BACKSPACE, ord(' ')):
					self.key_esc()

	def ev_draw(self):
		self.draw_snake()

		self.draw_portals()

		self.draw_walls()

		self.draw_cursor()

#==============================================================================#

@tg.menu_object
class editor_info(object):
	def __init__(self, cursor):

		self.editor_cursor = cursor

		self.x = 3
		self.y = 1
		self.yoff = 8
	
		self.options = [["Save and Quit", "Discard"]]

		self.focus = False

	def _str_mode(self):
		# normal/portal/wall/del
		if self.editor_cursor._mode == 'normal':
			return "Normal"
		elif self.editor_cursor._mode == 'portal':
			return "Making Portal"
		elif self.editor_cursor._mode == 'wall':
			return "Making Wall"
		elif self.editor_cursor._mode == 'del':
			return "Erase"

	# Keys
	def _key_switch(self):
		# Change the current focus
		self.focus = not self.focus
		self.editor_cursor.focus = not self.editor_cursor.focus

	def opt_Discard(self):
		# switch the focus, so next time it will be on the cursor
		self._key_switch()

		# quit
		self.editor_cursor.close()
		
	def opt_Save_and_Quit(self):
		if self.editor_cursor.save_ready():
			for inst in self._c.instance_of("dialog"):

				def fun(value):
					# switch the focus
					self._key_switch()

					# save and quit
					self.editor_cursor.save_and_close(value)

				inst.prompt(fun, l = 20, m = "Enter level name:")

	# events
	def ev_draw(self):
		x = self.editor_cursor.x 
		y = self.editor_cursor.y

		# Informaiton - keys
		self._s.addstr(self.y + 0, self.x, "W : build a wall")
		self._s.addstr(self.y + 1, self.x, "A : add portal")
		self._s.addstr(self.y + 2, self.x, "S : place snake head")
		self._s.addstr(self.y + 3, self.x, "D : erase")

		# Informations - position
		self._s.addstr(self.y + 5, self.x, "Position: ({:2d},{:2d})".format(x, y))

		# Information - current mode
		self._s.addstr(self.y + 6, self.x, \
			"Mode: {:s}".format(self._str_mode()))

	def ev_key(self, keycodes):
		for key in keycodes:
			if key == ord('\t'):
				self._key_switch()




