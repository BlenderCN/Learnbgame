import os

#class Camera():
#    def __init__(self, name,f, k1, k2, rotation, translation):
#        self.name = name
#        self.focal = f
#        self.k1 = k1
#        self.k2 = k2
#        self.rotation = rotation
#        self.translation = translation
#
#class Point():
#    def __init__(self, pos, color, viewList):
#        self.pos = pos
#        self.color = color
#        self.viewList = viewList
#
#class Feature():
#    def __init__(self,camId, key, sx, sy):
#        self.camId = camId
#        self.key = key
#        self.sx = sx
#        self.sy = sy

from collections import namedtuple
Camera = namedtuple('Camera', ['name','focal','k1','k2','rotation','translation'])
Point  = namedtuple('Point',  ['pos','color','viewList'])
Feature= namedtuple('Feature',['camId','key','sx','sy'])

def gen_lines(f):
#	lineNumber = 0
	for line in iter(lambda: f.readline(), ''):
#		lineNumber += 1
#		print(lineNumber)
		if line.startswith('#') or line.startswith('\n'): continue
		yield line.strip(' \t\n')

def readlisti(s):
	return list(map(int,s.split(' ')))

def readlistf(s):
	return list(map(float, s.split(' ')))

def getCamNameFromFileName( imageName ):
    return os.path.basename(imageName).split('_')[1]
