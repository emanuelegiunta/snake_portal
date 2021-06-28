import os.path
import tgame as tg

def csv_load(filename, sep = ',', nl = '\n', ext = "csv"):
	''' load a .csv file

	Input:
	filename: the name of the file to read
	[sep] : separator
	[nl]

	Output:
	A list of list whose elements are the rows of [filename].csv

	Note:
	Current implementation uses eval() to interpret data, meaning that data in
	the .csv file has to be stored using repr()
	'''

	filename = tg.extension_set(filename, ext)

	with open(filename, "r") as f:
		data = f.read() # the file is usually very small
	
	data = data.split(nl)
	data = data[:-1]

	for i in range(len(data)):
		data[i] = data[i].split(sep)
		data[i] = [eval(x) for x in data[i]]

	return data

def csv_write(filename, data):
	''' store data in a .csv file

	Input:
	filename: the name of the file to write
	data: 2D list containing the data to write

	Note:
	The function transform data in a comma separated string whose rows are
	separated with linebreaks (\\n)	
	'''

	data = ''.join([",".join([repr(x) for x in row]) + "\n" for row in data])
	
	with open(filename + ".csv", "w") as f:
		f.write(data)

def csv_exists(filename):
	''' check is the given csv file exists
	'''

	return os.path.isfile(filename + ".csv")
