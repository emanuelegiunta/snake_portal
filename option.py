import tgame as tg
import curses
import os

from constants_path import EXT_OPTIONS

'''
Contains functions that deals with the options (reading/writing)
'''

# helpers
def _get_var(s):
	# variable names cannot contain a space
	return s.split('=')[0].replace(' ', '')

def _get_val(s):
	return eval(s.replace(' ', '').split('=')[1])

def _check_comment(s):
	# a comment is a line starting with "#"
	return s[0] == "#"

def _check_emptyline(s):
	# an empty line is any number of spaces and a newline character
	return s.replace(' ','') == '\n'

# opt functions
def opt_load(filename, d):
	''' load all the options stored in filename.EXT_OPTIONS in the dictionary
	d. Usually d = globals() to store new variables as global one. Otherwise
	one could locally import variables or in custom dictionaries.
	'''

	filename = tg.extension_set(filename, EXT_OPTIONS)

	DEBUG = ""
	# execute all commands in f
	with open(filename, 'r') as f:
		for cmd in f:

			if not _check_comment(cmd) and not _check_emptyline(cmd):
				# only not so bad way to generate global variables
				#  dynamically:
				#  add a global variable in the globals dictionary

				d[_get_var(cmd)] = _get_val(cmd)

def opt_load_single(filename, var):
	'''load a single variable from filename.EXT_OPTIONS
	'''

	flag = True
	filename = tg.extension_set(filename, EXT_OPTIONS)


	with open(filename, 'r') as f:
		for line in f:

			# strip comments and empty lines.
			if not _check_comment(line) and not _check_emptyline(line) \
					and var == _get_var(line):
				#

				return _get_val(line)

	raise ValueError("variable {} not found in {}".format(v, filename))

def opt_set(filename, var, val):
	'''set a single varible var in the filename.EXT_OPTIONS to val
	Note that the variable has to already exists in the options menu
	'''

	filename = tg.extension_set(filename, EXT_OPTIONS)
	flag = True

	# look for a free tmp name
	tmpname = "TEMP._$tmp"
	while os.path.isfile(tmpname):
		tmpname = "_" + tmpname

	# modify and store in a tmp file
	with open(filename, 'r') as f:
		with open(tmpname, 'w') as g:
			for line in f:

				# look for a line that defines the current variable
				if not _check_comment(line) and not _check_emptyline(line) \
						and var == _get_var(line):
					#
					line = "{:s} = {:s}\n".format(var, repr(val))

				g.write(line)

	# copy back to the original file
	with open(filename, 'w') as f:
		with open(tmpname, 'r') as g:
			for line in g:
				f.write(line)

	# remove the tmp file
	os.remove(tmpname)