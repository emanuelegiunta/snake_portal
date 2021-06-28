import tgame as tg

from constants import FOOD_CHAR

@tg.active_object
class food(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	# Events
	def ev_draw(self):
		self._s.addstr(self.y, self.x, FOOD_CHAR)