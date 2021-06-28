import tgame as tg
import sys

from constants import *
from option import opt_load
from class_rm import rm_main, rm_select
from class_menu import menu_pause, menu_main
from class_snake import snake
from class_score import score, highscore
from class_food import food
from class_message import dialog
from other_object import portal, wall
from class_editor import cursor, editor_info
from option_menu import options_menu
from class_graphics import screen_fill
from class_credits import credits
from game_manager import gm


def main(ctxt):
	# settings
	ctxt.speed = CTXT_SPEED

	# initialise colors
	COLOR_SET()

	# create views and abort if something fail

	h, w = tg.screen_size(ctxt.screen)

	if h < 24 or w < 80:
		sys.exit("Please, resize your terminal to be at leat 80x24")

	view_full = ctxt.screen
	view_main = ctxt.view_new(x = 0, y = 0, w = 80, h = 24)

	# this is not the right way, yet it seems to be the only reasonable one
	#  anyway, it make the smaller centered view as the one that object
	#  inherit by default
	ctxt._screen = view_main
		
	# create the other views
	view_tl = ctxt.view_new(x = 0,  y = 0,  w = 50, h = 20)
	view_tr = ctxt.view_new(x = 50, y = 0,  w = 30, h = 20)
	view_bl = ctxt.view_new(x = 0,  y = 20, w = 50, h = 4)

	# set background colors
	view_tl.bkgd(curses.color_pair(COLOR_NO_ARENA))

	#==========================================================================#
	### Main room
	ctxt.room_new('Main')


	ctxt.view_add(view_tl)
	ctxt.view_add(view_tr)
	ctxt.view_add(view_bl)

	inst = rm_main(ctxt)
	inst.view_tl = view_tl

	wall(ctxt, s = view_tl)
	score(ctxt, 6, 2, s = view_tr)
	menu_pause(ctxt)
	dialog(ctxt, 2, 1, 2, 2, screen = view_bl)

	screen_fill(ctxt, s = view_tl)


	#==========================================================================#
	### Select room
	ctxt.room_new('Select')

	ctxt.view_add(view_tl)
	ctxt.view_add(view_tr)
	ctxt.view_add(view_bl)

	rm_select(ctxt, views = (view_tl, view_tr, view_bl))
	screen_fill(ctxt, s = view_tl)


	#==========================================================================#
	### Highscore room
	ctxt.room_new('Highscore')

	highscore(ctxt)


	#==========================================================================#
	### Home room
	ctxt.room_new('Home')

	#ctxt.view_add(view_full)

	ctxt.background_new(FILE_PATH + "home")
	menu_main(ctxt, )


	#==========================================================================#
	### Editor room
	ctxt.room_new('Editor')

	ctxt.view_add(view_tl)
	ctxt.view_add(view_tr)
	ctxt.view_add(view_bl)

	dialog(ctxt, 2, 1, 2, 2, s = view_bl)
	crs = cursor(ctxt, s = view_tl)
	editor_info(ctxt, crs, s = view_tr)

	screen_fill(ctxt, s = view_tl)


	#==========================================================================#
	### Options room
	ctxt.room_new('Options')

	options_menu(ctxt)


	#==========================================================================#
	### Credit Room
	ctxt.room_new('Credits')

	credits(ctxt)


	#==========================================================================#




	

	# goto to the initial room
	ctxt.room_goto('Home')

	gm(ctxt, view_full)




tg.wrapper(main)
