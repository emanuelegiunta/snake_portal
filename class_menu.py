import tgame as tg
import sys
import curses

@tg.menu_object
class menu_pause(object):
	def __init__(self):
		self.visible = False

		# we define the shape of the menu
		self.xoff = 4	# space from the canvas
		self.yoff = 2	# "
		self.yskip = 1
		self.options = [["Continue", "Main menu", "Exit"]]

		h, w = tg.screen_size(self._s)

		# position the menu
		self.x = (w - 2*self.xoff - self.w)//2
		self.y = (h - 2*self.yoff - self.h)//2

		# local variables
		self.previous_instances = []
		self.previous_background = None

	# options
	def option_Main_menu(self):
		# un-pause
		self.pause()

		# reset the game
		for inst in self._c.instance_of('rm_main'):
			inst.game_reset()

		# change room
		self._c.room_goto('Home')

	def Opt_Continue(self):
		self.pause()

	def Opt_Exit(self):
		sys.exit(0)

	# Other methods
	def pause(self):
		# when the menu is visible the game is in pause and viceversa
		if self.visible:
			self.visible = False

			# undo the next case
			for inst in self.previous_instances:
				inst.activate()

			self._c.background = self.previous_background

			self.previous_instances = []
			self.previous_background = None

		else:
			self.visible = True

			# deactivate all objects
			for inst in self._c.instance_all('menu_pause'):
				if inst.active:
					inst.deactivate()
					self.previous_instances.append(inst)

			# get the current screen in a background object
			self.previous_background = self._c.background
			self._c.background = tg.background_screenshot(self._c)
			self._c.background.eff_add(curses.A_DIM)

	# Events
	def ev_key(self, keycodes):
		if ord('p') in keycodes or ord('P') in keycodes:
			self.pause()

	def ev_draw(self):
		tg.draw_rectangle(self._s, self.x + 1, self.y + 1, \
			self.w + 2*(self.xoff - 1), self.h + 2*(self.yoff - 1), c = ' ')

		tg.draw_canvas(self._s, self.x, self.y, \
			self.w + 2*self.xoff, self.h + 2*self.yoff, c = ':',\
			a = curses.A_REVERSE)

#==============================================================================#
# Main Menu

@tg.menu_object
class menu_main(object):
	def __init__(self):

		# define the shape of the options
		self.yskip = 1
		self.xskip = 6
		self.options = [["New Game", "Options"],
						["Create Level", "Credits"],
						["Highscore", "Quit Game"]]

		h, w = tg.screen_size(self._s)
		
		self.y = 20
		self.x = (w - 2*self.xoff - self.w)//2

	def opt_New_Game(self):
		self._c.room_goto('Select')

	def opt_Create_Level(self):
		self._c.room_goto('Editor')

	def opt_Highscore(self):
		self._c.room_goto('Highscore')

	def opt_Options(self):
		self._c.room_goto('Options')

	def opt_Credits(self):
		self._c.room_goto('Credits')

	def opt_Quit_Game(self):
		sys.exit(0)

#==============================================================================#