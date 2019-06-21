# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####

def read_parameters(f):
	parameters = {}
	file = open(f, "r")

	if not "{" in file.readline():
		print("Not a valid parameters file: File doesn't start with {")
		return 1

	block = None # used to store current context block
	lines = file.readlines()

	i = 0
	while i < len(lines):
		line = lines[i]

		# skips line if it's a comment
		if line[0] == ';':
			if line[1] == ')': # escaped 1.2/rvgl comment
				line = line[2:]
			else:
				i += 1
				continue
		
		# split comments from lines and remove tabs
		line = line.split(";")[0].replace('\t', ' ')

		# skips an empty line
		if not line.strip():
			i += 1
			continue

		# detects start of a block
		if '{' in line:
			block = line.split('{')[0].strip().lower()
			print("Block:", block)
		
		# reads block entries
		elif block:
			if '}' in line:
				block = None
			else:
				if not "inertia" in line[:7].lower():
					pline = parse_line(line)
				else: # read inertia matrix
					pline = parse_line(' '.join([line, lines[i+1], lines[i+2]]))
					i += 2
				if not block in parameters:
					parameters[block] = {}
				parameters[block][pline[0]] = pline[1]

		# detects when the file is over
		elif '}' in line:
			print("FILE END")
			break

		# regular entries outside of blocks
		else:
			# print("Value", line.strip())
			pline = parse_line(line)
			parameters[pline[0]] = pline[1]
		i += 1
	return parameters

def parse_line(line):
	
	line = line.replace(',', ' ') # get rid of commas, they're not needed (e.g. offset)
	line = line.strip() # remove whitespace
	line = ' '.join(line.split()) # remove whitespace between words (make it just one space)

	entry = line.split(' ')[0].lower()

	# correct the model entries to include their number
	if entry == "model":
		entry = ' '.join(line.split(' ')[:2]).lower()
		value = line.split(' ')[2:]
	else:
		value = line.split(' ')[1:]
	
	# for the name, only split once and remove the ""
	if entry == "name":
		value = line.split(' ', 1)[1].replace('"', '')

	else:

		if type(value) is list:
			for i in range(len(value)):
				if '.' in value[i] and value[i].replace('.', '').replace('-', '').isdigit():
					value[i] = float(value[i])
				elif value[i].isdigit():
					value[i] = int(value[i])
				elif value[i].lower() == "true":
					value[i] = True
				elif value[i].lower() == "false":
					value[i] = False
				elif value[i].lower() == "none":
					value[i] = None
				else:
					value[i] = value[i].replace('"', '')
		# convert single-element lists into a simple variable
		if len(value) == 1:
			value = value[0]

	print(entry, value)
	return (entry, value)