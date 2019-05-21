'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy, random, math, mathutils, os.path
from bpy_extras.image_utils import load_image
import xml.etree.ElementTree as ET
	
def getActiveCamera():
	if bpy.context.scene.camera is None: return newCamera()
	else: return bpy.context.scene.camera
	
def setCustomProperty(object, propertyName, value = 0.0, min = -1000000.0, max = 1000000.0, description = ""):
	object[propertyName] = value
	insertPropertyParameters(object, propertyName, min, max, description)
def insertPropertyParameters(object, propertyName, min, max, description):
	rna = { "min": min,
			"max": max,
			"description": description }
	if "_RNA_UI" in object: 
		object["_RNA_UI"][propertyName] = rna
	else: 
		object["_RNA_UI"] = {propertyName: rna}
	
	
def deselectAll():
	bpy.ops.object.select_all(action = "DESELECT")
	
def getActive():
	return bpy.context.scene.objects.active
	
def setActive(object):
	object.select = True
	bpy.context.scene.objects.active = object
	
def onlySelect(object):
	deselectAll()
	if object is not None: setActive(object)
	
def deleteSelectedObjects():
	bpy.ops.object.delete(use_global=False)
	
def getDofObject(camera):
	return bpy.data.cameras[camera.name].dof_object
		
def textToName():
	for object in bpy.data.objects:
		if hasattr(object.data, "body"):
			object.name = object.data.body
			
def seperateTextObject(textObject, seperator = "\n"):
	textList = textObject.data.body.split(seperator)
	for i in range(len(textList)):
		newText(name = textList[i], location = [0, -i, 0], text = textList[i])
		
def getSelectedObjects():
	return bpy.context.selected_objects
def setSelectedObjects(selection):
	deselectAll()
	for object in selection:
		object.select = True
		setActive(object)
		
def isTextObject(object):
	if hasattr(object, "data"):
		if hasattr(object.data, "body"):
			return True
	return False
	
def isCameraObject(object):
	return bpy.data.cameras.get(object.name) is not None
def getCameraFromObject(object):
	return bpy.data.cameras[object.name]
	
def delete(object):
	deselectAll()
	object.select = True
	object.hide = False
	object.name = "DELETED" + object.name
	bpy.ops.object.delete()
	
def getCurrentFrame():
	return bpy.context.screen.scene.frame_current

		
def clamp(value, minValue, maxValue):
	return max(min(value, maxValue), minValue)
	
def areaTypeExists(type):
	return getAreaByType(type) is not None
def getAreaByType(type):
	for area in bpy.context.screen.areas:
		if area.type == type: return area
	return None
def swapAreaTypes(area1, area2):
	type1 = area1.type
	area1.type = area2.type
	area2.type = type1
	
def getDataPath(name):
	return '["' + name + '"]'
	
def getObjectFromValidIndex(list, index):
	return list[clamp(index, 0, len(list) - 1)]

def getImage(path):
	for image in bpy.data.images:
		if path == image.filepath: return image
	return loadImage(path)
def loadImage(path):
	return load_image(path)
	
def getRandom(min, max):
	return random.random() * (max - min) + min
	
def hasPrefix(name, prefix):
	return name[:len(prefix)] == prefix
	
def getPossibleName(prefix):
	if bpy.data.objects.get(prefix) is None: return prefix
	i = 1
	while bpy.data.objects.get(prefix + str(i)) is not None:
		i += 1
	return prefix + str(i)
	
def getFileName(path):
	return os.path.splitext(os.path.basename(path))[0]
	
def setMinMaxTransparentBounces(amount):
	bpy.context.scene.cycles.transparent_min_bounces = amount
	bpy.context.scene.cycles.transparent_max_bounces = amount
	
def setDisplayTypeToWire(object):
	object.draw_type = "WIRE"
	
def getStringProperty(tree, name, fallback = ""):
	return str(getProperty(tree, name, fallback))
def getFloatProperty(tree, name, fallback = 0.0):
	return float(getProperty(tree, name, fallback))
def getIntProperty(tree, name, fallback = 0):
	return int(getProperty(tree, name, fallback))
def getProperty(tree, name, fallback = 0):
	object = tree.get(name)
	if object is None: object = fallback
	return object
					