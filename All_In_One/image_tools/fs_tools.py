# v0.1

import os
import bpy
# cross platform paths
# maybe add utf8 replace to old ascii blender builtin
def clean(path) :
	return path.strip().replace('\\','/')

## test for existence of a file or a dir
def exist(path) :
	if isfile(path) or isdir(path) : return True
	return False

## test for existence of a file
def isfile(path) :
	if os.path.isfile(path) : return True
	# could be blender relative
	path = bpy.path.abspath(path)
	if os.path.isfile(path) : return True
	return False

## test for existence of a dir
def isdir(path) :
	if os.path.isdir(path) : return True
	# could be blender relative
	path = bpy.path.abspath(path)
	if os.path.isdir(path) : return True
	return False

## returns a list of every absolute filepath
# to each file within the 'ext' extensions
# from a folder and its subfolders
def scanDir(path,ext='all') :
	files = []
	fields = os.listdir(path)
	if ext != 'all' and type(ext) != list : ext = [ext]
	for item in fields :
		if os.path.isfile(path + '/' + item) and (ext == 'all' or item.split('.')[-1] in ext) :
			#print('  file %s'%item)
			files.append(path + '/' + item)
		elif os.path.isdir(path + '/' + item) :
			print('folder %s/%s :'%(path,item))
			files.extend(scanDir(path + '/' + item))
	return files