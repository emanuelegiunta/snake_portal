import curses
import tgame as tg

import numpy.random as rnd

from class_food import food
from constants import *

def _filter_first(vec):
	try:
		return next(vec)
	except TypeError:
		return vec[0]

@tg.timer
@tg.active_object
class snake(object):
	def __init__(self, x, y):
		''' initialise the snake
	
		Input:
		x: initial head position, x-coordinate
		y: initial head position, y-coordinate
		context: the context
		screen: a curses.window object
		length: initial length of the snake
		'''
		
		self.screen_h, self.screen_w = tg.screen_size(self._s)

		self.speed_x = 1
		self.speed_y = 0
		self.next_speed_x = None
		self.next_speed_y = None
		self.direction = (self.speed_x, self.speed_y)
		
		# list of (x, y) coordinates of body components
		self.body = [(x - i, y) for i in range(SNAKE_INITIAL_LENGTH-1, -1, -1)]

		# flag denoting if the snake is still alive
		self.dead = False

		# flag indicting if the snake will grow in this step
		self.grow = False

		# list of portal in the game
		self.portal_list = []

		# flag indicating if the snake is teleporting in this step
		self.teleporting = False

		# link with the wall object
		self.wall = self.wall_get()

		# current food piece - setted in the ev_room_start event (as all obj will be created by then)
		self.food = None

		# set the timer to make a new step forward
		self.step_time = self._c.speed // SNAKE_SPEED
		self.timer[0] = self.step_time
		self._keycodes_buffer = []


	# Creation function
	def end_setup(self):
		'''to call after all the object in the room have been created and setted

		Perform action that in theory belong to __init__ but cannot be placed there as they also depends on other object that might not be ready yet.
		'''
		self.food = self.food_place()


	# Teleport Function
	def teleport_add(self, x1, y1, x2, y2):
		'''Add a teleport to the snake
		
		Input:
		x1: x-coordinate of the first portal
		y1: y-coordinate of the first portal
		x2: x-coordinate of the second portal
		y2: y-coordinate of the second portal

		Note:
		Does not check if the portal lies in the given window
		'''
		self.portal_list.append((x1, y1))
		self.portal_list.append((x2, y2))

	def teleport_other(self, x, y):
		'''Return the other portal, given the coordinate of the first one

		Input:
		x: x-coordinate of the first portal
		y: y-coordinate of the first portal

		Output (x, y):
		x: x-coordinate of the other portal
		y: y-coordinate of the other portal

		Note:
		Will rise an error if no portal was initialised at (x, y)
		'''

		assert (x, y) in self.portal_list

		# uses the fact portal are added in pairs to self.portal_list
		# we need a fuction that returns given the indices i of the given
		# portal, i+1 if i is even and i-1 if i is odd 

		i = self.portal_list.index((x, y))
		j = i + 1 - 2*(i % 2)
		return self.portal_list[j]

	def teleport_check(self, x, y):
		''' check if there is a portal in the given position

		Input:
		x: x-coordinate of the supposed portal
		y: y-coordinate of the supposed portal

		Output:
		a boolean
		'''

		return (x, y) in self.portal_list

	def teleport_num(self):
		'''Return the number of teleports currently used
		'''

		return len(self.portal_list)//2

	
	# Wall Function
	def wall_get(self):
		''' return the first wall object in the room
		'''
		try:
			return _filter_first(self._c.instance_of('wall'))
		except:
			if not list(self._c.instance_of('wall')):
				raise RuntimeError("The snake looked for a wall object in the room, but none was found - maybe you are creating that after this snake?")
			else:
				raise

	def wall_check(self, x, y):
		''' return True if there is a wall in position x, y
		'''
		return self.wall.check(x, y)


	# Food function
	def food_place(self): # Warning : inefficient
		'''Place a piece of food in the map
		'''

		while True:
			# look for a free (x, y) position to place food in
			x = rnd.randint(self.screen_w)
			y = rnd.randint(self.screen_h)

			if ((x, y) not in self.body) and (not self.wall_check(x, y)):
				break

		# place food
		new_food = food(self._c, x, y, screen = self._s)
		return new_food

	def food_check(self, x, y):
		''' check if there is food in the given position

		Input:
		x: x-coordinate of the supposed food piece
		y: y-coordinate of the supposed food piece
		'''

		return (x == self.food.x) and (y == self.food.y)

	def food_eat(self):
		'''Wrapper for the actions performed while eating a piece of food
		'''

		# move the piece of food eaten
		self.food.destroy()
		self.food = self.food_place()

		# after eating the snake grow of one piece
		self.grow = True

		# increase the score by one
		for inst in self._c.instance_of("score"):
			inst.score += 1


	# Death
	def die(self):
		'''Wrapper for action performed after death.
		'''
		# the snake become inactive (the room will
		#  actually destroy him) and tell the room that the game ended
		self.dead = True

		# remove the menu as it will cause troubles with the input
		#  afterall we are dead - no more need to pause
		for inst in self._c.instance_of("menu_pause"):
			inst.deactivate()

		# ask the dialog to prompt for input
		for inst in self._c.instance_of("dialog"):

			# we need to tell dialog how to use its input
			score_obj = _filter_first(self._c.instance_of("score"))
			rm_obj = _filter_first(self._c.instance_of("rm_main"))

			# this will be executed by the dialog window once the input is take
			def fun(value):
				# give the value to the score
				score_obj.username = value

				# tell the room that the game is over
				rm_obj.game_end()

				# reactivate the menu
				for inst in self._c.instance_of("menu_pause"):
					inst.activate()

			# start the input prompt
			inst.prompt(fun, l = 16, \
				m = "Game Over! Insert your username:")

	def death_check(self, x, y):
		'''check if the snake will die next step

		Input:
		x: x-coordinate of the next head position
		y: y-coordinate of the next head position

		Note:
		Death may occur due to self intersection or by hitting a wall
		'''

		return ((x, y) in self.body) or (self.wall_check(x, y))


	# Draw helper
	def _get_dir(self, p, d):

		# hard coded bynary search
		#  observe that one among delta_x or delta_y is non-zero
		#  so we first ask which one and then ask the right direction
		#
		x, y = p 
		xnext, ynext = d

		# first check if the piece is in a portal
		if (x, y) in self.portal_list:
			if (xnext, ynext) == self.teleport_other(x, y):
				return 'p'

		# otherwise we did not teleport, so our next body piece is nearby
		if (xnext - x) == 0:
			if (ynext - y) % self.screen_h == 1:
				return 'd'
			else:
				return 'u'
		else:
			if (xnext - x) % self.screen_w == 1:
				return 'r'
			else:
				return 'l'

	def _chratt_list(self):
		out = []

		prev_body = self.body[0]		# we start from the tail
		next_body = self.body[1] 
		prev_dir = self._get_dir(prev_body, next_body)

		# if the tail is over a portal, mark it
		if prev_dir != 'p' and prev_body in self.portal_list:
			out.append(SNAKE_CHRATT["pt" + prev_dir])
		else:
			out.append(SNAKE_CHRATT["t" + prev_dir])

		# continue the process
		for i in range(2, len(self.body)):

			# get the next piece of the body
			prev_body, next_body = next_body, self.body[i]

			# determine the new direction
			next_dir = self._get_dir(prev_body, next_body)

			# append the chratt
			out.append(SNAKE_CHRATT[prev_dir + next_dir])

			# update prev_dir e prev_body
			prev_dir = next_dir
			prev_body = next_body

		# finally deal with the head. Remind "h" stands for head.
		#  Remark if the previous piece was on a portal we need to find our current direction
		if next_dir != "p":

			# check if we enter a new portal now (next_boy is the head position)
			if next_body in self.portal_list:
				out.append(SNAKE_CHRATT[next_dir + 'hp'])
			else:
				out.append(SNAKE_CHRATT[next_dir + "h"])
		else:
			out.append(SNAKE_CHRATT[next_dir + "h" +
				self._get_dir((0,0), (self.speed_x, self.speed_y))])

		return out


	# Events
	def ev_key(self, keycodes):
		self._keycodes_buffer += keycodes
		
		if self.timer[0] == 0:
			# detect if the snake will change direction
			speed_change_flag = False

			# detect if the snake will change direction agin
			next_speed_change_flag = False

			# dictionary of direction - hard codes the wasd keys
			direction = {'w':(0, -1), 'd':(1, 0), 's':(0, 1), 'a':(-1, 0)}

			# orders of the wasd keys - upper case is included to avoid issues
			# with capsLock on (otherwise the input is not captured)
			wasd_keys = [ord(c) for c in "wasdWASD"]

			# current direction
			dx, dy = self.direction

			for key_code in self._keycodes_buffer:
				if key_code in wasd_keys:

					c = chr(key_code).lower()
					if speed_change_flag and not next_speed_change_flag and \
						(-self.speed_x, -self.speed_y) != direction[c] and \
						(self.speed_x, self.speed_y) != direction[c]:

						# set the new direction (will be applied next step)
						self.next_speed_x, self.next_speed_y = direction[c]

						# prevent from further change
						next_speed_change_flag = True

					if not speed_change_flag and \
						(-dx, -dy) != direction[c] and \
						(dx, dy) != direction[c]:

						# set the new direction
						self.speed_x, self.speed_y = direction[c]

						# prevent from further changes in the direction and enble
						#  the possibility to store the next direction
						speed_change_flag = True

			# when the buffer is fully read
			self._keycodes_buffer = []

	def ev_step(self):
		if not self.dead and self.timer[0] == 0:
			# update the timer
			self.timer[0] = self.step_time

			# current head position
			x, y = self.body[-1]

			# find the new head position
			#  if the snake is teleporting move to the other portal
			if self.teleporting == True:
				x, y = self.teleport_other(x, y)
				self.teleporting = False
			#  otherwise move according to the current speed
			else:
				x = (x + self.speed_x) % self.screen_w
				y = (y + self.speed_y) % self.screen_h

				# if we landed on a portal BY MOVING, mark it
				if self.teleport_check(x, y):
					self.teleporting = True

			# update the current direction
			self.direction = (self.speed_x, self.speed_y)

			# if we find food in the next position
			#  
			if self.food_check(x, y):
				self.food_eat() 

			# remove the tail if not eating
			#  AFTER - eat
			if not self.grow:
				self.body = self.body[1:]
			else:
				self.grow = False

			# if we eat our own body
			#  AFTER - grow (tail bug)
			if self.death_check(x, y):
				self.die()

			# update the head position
			#  AFTER - death check (head bug)
			self.body.append((x, y))

			# update speed
			if self.next_speed_x is not None and self.next_speed_y is not None:
				self.speed_x = self.next_speed_x
				self.speed_y = self.next_speed_y
				self.next_speed_x = None
				self.next_speed_y = None

	def ev_draw(self):
		''' print the whole body of the snake
		'''
		for (x, y), (c, a) in zip(self.body, self._chratt_list()):

			if self.dead:
				# we take the or as we don't know what att really is
				a = a | SNAKE_DEAD_ATT

			self._s.addstr(y, x, c, a)
			
	def ev_destroy(self):
		if self.food in self._c.instance_all():
			self.food.destroy()