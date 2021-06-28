import tgame as tg
import curses


@tg.active_object
class screen_fill(object):
	def __init__(self, ch = " ", att = curses.A_NORMAL):
		self.layer = -float('inf')
		self.ch = ch
		self.att = att

		self.h, self.w = tg.screen_size(self._s) 

	def ev_draw(self):
		for y in range(self.h):
			self._s.addstr(y, 0, self.ch*self.w, self.att)


