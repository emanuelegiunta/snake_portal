import tgame as tg

@tg.active_object
class credits(object):
	def __init__(self):
		self.h, self.w = tg.screen_size(self._s)

	# Events
	def ev_key(self, keycodes):
		if keycodes:
			self._c.room_goto("Home")

	def ev_draw(self):
		txt = "Emanuele C. G. Giunta"

		x = (self.w - len(txt))//2
		y = (self.h - 1)//2

		self._s.addstr(y, x, txt)