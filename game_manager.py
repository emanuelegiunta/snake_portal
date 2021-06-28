import tgame as tg 
import curses


@tg.active_object
class gm(object):
	def __init__(self, full_view):
		self.permanent = True
		self.full_view = full_view
		self.h, self.w = tg.screen_size(full_view)

	def view_update(self):
		pass

	def ev_key(self, keycodes):
		if curses.KEY_RESIZE in keycodes:
			self.h, self.w = self.full_view.getmaxyx()
			self.view_update()

	def ev_room_start(self):
		self.view_update()
