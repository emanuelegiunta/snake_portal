import os
import curses
import tgame as tg


from csv import csv_load
from constants import EXT_LEVEL, FILE_PATH, MY_KEY_EXIT
from class_snake import snake
from other_object import portal, wall

# General information on the encoding
#  string of comma separated values. The first argument specifies the object to
#  create. The others are evaluated and passed as arguments. (it is important
#  to use the `repr()` function when saving a level for the output argument.
# 


@tg.active_object
class rm_main(object):
	def __init__(self):
		self.wall_obj = None

		# the only view required - you have to manually set it right now
		self.view_tl = None

		# list of object created - so that they can then be removed
		self.instances = []

	def game_start(self, filename):
		# reset the message displayed
		for inst in self._c.instance_of('dialog'):
			inst.message = "wasd : movement    p : pause menu"

		# reset the wall
		for inst in self._c.instance_of('wall'):
			self.wall_obj = inst

		self.wall_obj.reset()

		# reset the score
		for inst in self._c.instance_of('score'):
			inst.reset(l = filename)

		# load the game
		self._game_load(filename)

	def game_reset(self):
		''' Reset the current game

		Ususally called before changing room by this or other object
		'''

		# destroy all the object created in this level
		for inst in self.instances:
			inst.destroy()

		self.instances = []

	def game_end(self):
		self.game_reset()

		# update the highscore with the current score
		for inst in self._c.instance_of("score"):
			inst.highscore_update()

		# peeking function
		def peek():
			for inst in self._c.instance_of("highscore"):
				inst.load_data()	

		# change room
		self._c.room_goto("Highscore", p = peek)

	def _game_load(self, filename):
		with open(filename, 'r') as f:
			for line in f:
				cmd = line.replace('\n', '')
				cmd = cmd.split(';')
				cmd = [eval(x) for x in cmd]

				if cmd[0] == "snake":
					inst = snake(self._c, *cmd[1:], s = self.view_tl)
					self.instances.append(inst)

				elif cmd[0] == "portal":
					inst = portal(self._c, *cmd[1:], l = -1, s = self.view_tl)
					self.instances.append(inst)

				elif cmd[0] == "wall":
					self.wall_obj.add(*cmd[1:])

				elif cmd[0] == "wall_line":
					self.wall_obj.add_line(*cmd[1:])

		# complete the snake setup
		for inst in self._c.instance_of("snake"):
			inst.end_setup()


#==============================================================================#

@tg.active_object
class rm_select(object):
	def __init__(self, views = None):
		self.name_list = self._game_get_list()
		self.game_list = [FILE_PATH + s for s in self.name_list]

		# does not return error as self.game_list is guaranteed to not be empty
		self.index = 0  # index of the currently selected element
		self.current = self.game_list[0]

		# fake instances created just to give a preview
		self.instances = []

		# create other useful objects and views
		if views is None:
			self.view_tl = self._c.view_new(x = 0,  y = 0,  w = 50, h = 20)
			self.view_tr = self._c.view_new(x = 50, y = 0,  w = 30, h = 20)
			self.view_bl = self._c.view_new(x = 0,  y = 20, w = 50, h = 4)
		else:
			self.view_tl = views[0]
			self.view_tr = views[1]
			self.view_bl = views[2]

		# pointer to wall. Needed to add new wall pieces
		self.wall_obj = wall(self._c, s = self.view_tl)

		# sub-menu [sm] options
		self.sm_h, self.sm_w = tg.screen_size(self.view_tr)
		self.sm_xoff = 1
		self.sm_yoff = 1
		self.sm_i = 0 	# index of the first displayed option
		self.sm_max_opt = self.sm_h - 2*self.sm_yoff

		# start:
		#  load the descryption of the game
		self._game_load()

	
	def _sm_move(self):
		if self.sm_i > self.index:
			self.sm_i = self.index

		if self.sm_i < self.index - self.sm_max_opt:
			self.sm_i = self.index - self.sm_max_opt

	def _instance_add(self, inst):
		self.instances.append(inst)
		inst.deactivate()

	def _game_get_list(self):
		''' return a list of all possible levels

		Note:
		Refers to the folder FILE_PATH. If there is no .EXT_LEVEL raise an
		IOError.
		'''

		file_list = [s for s in os.listdir(FILE_PATH) \
			if tg.extension_get(s) == EXT_LEVEL]

		if not file_list:
			raise IOError("No .{} file found in {}!".format( \
				EXT_LEVEL, FILE_PATH))
		else:
			file_list.sort()
			return file_list

	def _game_load(self):
		with open(self.game_list[self.index], 'r') as f:
			for line in f:
				cmd = line.replace('\n', '')
				cmd = cmd.split(';')
				cmd = [eval(x) for x in cmd]

				if cmd[0] == "snake":
					inst = snake(self._c, *cmd[1:], s = self.view_tl)
					self._instance_add(inst)

					# remove food
					for other_inst in self._c.instance_of("food"):
						other_inst.destroy()

				elif cmd[0] == "portal":
					inst = portal(self._c, *cmd[1:], l = -1, s = self.view_tl)
					self._instance_add(inst)

				elif cmd[0] == "wall":
					self.wall_obj.add(*cmd[1:])

				elif cmd[0] == "wall_line":
					self.wall_obj.add_line(*cmd[1:])


	def _game_reset(self):
		# destroy all the fake instances
		for inst in self.instances:
			inst.destroy()

		# reset the walls
		for inst in self._c.instance_of('wall'):
			inst.reset()

		# empty the list of instance created so far
		self.instances = []

	def ev_key(self, keycodes):

		if curses.KEY_UP in keycodes:
			
			# reduce the index by 1
			self.index = (self.index - 1) % len(self.game_list)
			self.current = self.game_list[self.index]

			self._game_reset()
			self._game_load()
			self._sm_move()

		if curses.KEY_DOWN in keycodes:

			# reduce the index by 1
			self.index = (self.index + 1) % len(self.game_list)
			self.current = self.game_list[self.index]

			self._game_reset()
			self._game_load()	
			self._sm_move()

		if ord('\n') in keycodes:

			# peek
			def peek():
				for inst in self._c.instance_of("rm_main"):
					inst.game_start(self.current)

			# start the game by changing room
			self._c.room_goto('Main', p = peek)

		if curses.KEY_EXIT in keycodes or MY_KEY_EXIT in keycodes:
			self._c.room_goto("Home")


	def ev_draw(self):
		# forziamo il draw event
		for inst in self.instances:
			inst.ev_draw()

		# draw on view_tr a list of available games
		for i in range(min( \
			self.sm_max_opt, len(self.name_list[self.sm_i:]))):

			if self.index == i:
				a = curses.A_REVERSE
			else:
				a = curses.A_NORMAL

			self.view_tr.addstr(self.sm_yoff + i, self.sm_xoff, \
				self.name_list[i], a)

