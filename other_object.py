import tgame as tg

from constants import *
from texture import *

@tg.active_object
class portal(object):
	def __init__(self, x1, y1, x2, y2):

		for inst in self._c.instance_of('snake'):

			# get the number of teleport currently used
			n = inst.teleport_num()

			# add a new teleport in the snake object
			inst.teleport_add(x1, y1, x2, y2)

		# choose a character to display the current portal
		if n < 26:
			self._char = chr(ord('A') + n)
		
		elif n < 52:
			self._char = chr(ord('a') + n - 26)

		else:
			raise ValueError("Game currently supports up to 56 portals")

		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

	def ev_draw(self):
		self._s.addch(self.y1, self.x1, self._char, PORTAL_ATT)
		self._s.addch(self.y2, self.x2, self._char, PORTAL_ATT)


@tg.active_object
class wall(object):
	def __init__(self, *argv):
		# an element of wall list is of the form:
		#  [y, x, chr, att, key]
		#  so that one can always pass them to screen.addch(*item[:4]) for
		#  item in self._wall_list

		self._wall_dict = {}
		self.add(*argv)

	# adding walls

	def _neighbour_update(self, x, y, key):
		# get the list position
		wall_piece = self._wall_dict[x, y]

		# update the key
		wall_piece[2] |= key

		# update the characted and its attribute
		wall_piece[0], wall_piece[1] = WALL_CHRATT[wall_piece[2]]
		
	def _single_add(self, x, y):
		''' return the char of the wall in x, y
		'''

		key = WALL_KEY_NONE

		if (x + 1, y) in self._wall_dict:
			key |= WALL_KEY_RIGHT

			self._neighbour_update(x + 1, y, WALL_KEY_LEFT)


		if (x, y + 1) in self._wall_dict:
			key |= WALL_KEY_DOWN

			self._neighbour_update(x, y + 1, WALL_KEY_UP)

		if (x - 1, y) in self._wall_dict:
			key |= WALL_KEY_LEFT

			self._neighbour_update(x - 1, y, WALL_KEY_RIGHT)

		if (x, y - 1) in self._wall_dict:
			key |= WALL_KEY_UP

			self._neighbour_update(x, y - 1, WALL_KEY_DOWN)

		# set the new wall piece, appending in the end the chratt key
		new_wall_piece = list(WALL_CHRATT[key])
		new_wall_piece.append(key)
		self._wall_dict[x, y] = new_wall_piece

	def add(self, *vec):
		# vec has to have the form
		#  (x1, y1), (x2, y2), ...

		for wall_place in vec:
			if wall_place not in self._wall_dict:
				self._single_add(*wall_place)

	def add_line(self, p1, p2):
		#
		(x1, y1) = p1
		(x2, y2) = p2


		if x1 == x2:
			x = x1
			for y in range(min(y1, y2), max(y1, y2) + 1):
				self.add((x, y))

		elif y1 == y2:
			y = y1
			for x in range(min(x1, x2), max(x1, x2) + 1):
				self.add((x, y))

		else:
			raise ValueError("Adding wall in a non horizontal/vertical line! Please don't modify the .lvl or I'll have to call the police")


	# check

	def check(self, x, y):

		return (x, y) in self._wall_dict


	# reset

	def reset(self):
		#
		self._wall_dict = {}

	# events

	def ev_draw(self):

		# the elements of _wall_dict are tuples of the form [c, a, k]
		for (x, y), (c, a, k) in self._wall_dict.items():
			self._s.addstr(y, x, c, a)

		