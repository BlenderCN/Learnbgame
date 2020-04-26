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

import bpy

def newEmpty(name = "Empty", location = [0, 0, 0], hide = False, type = "PLAIN_AXES"):
	bpy.ops.object.empty_add(location = location, type = type)
	empty = bpy.context.object
	empty.name = name
	if hide:
		bpy.ops.object.hide_view_set(unselected = False)
	return empty
	
def newText(name = "Text", location = [0, 0, 0], text = "text"):
	bpy.ops.object.text_add(location = location)
	textObject = bpy.context.object
	textObject.name = name
	textObject.data.body = text
	return textObject

def setTrackTo(child, trackTo):
	deselectAll()
	child.select = True
	setActive(trackTo)
	bpy.ops.object.track_set(type = "TRACKTO")   

def setParent(child, parent):
	deselectAll()
	child.select = True
	setActive(parent)
	bpy.ops.object.parent_set(type = "OBJECT", keep_transform = True)
	
def setParentWithoutInverse(child, parent):
	deselectAll()
	child.select = True
	setActive(parent)
	bpy.ops.object.parent_no_inverse_set()
	
def setCustomProperty(object, propertyName, value, min = -1000000.0, max = 1000000.0, description = ""):
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
	
def newDriver(object, dataPath, index = -1, type = "SCRIPTED"):
	fcurve = object.driver_add(dataPath, index)
	driver = fcurve.driver
	driver.type = type
	return driver
def createCopyValueDriver(fromObject, fromPath, toObject, toPath):
	driver = newDriver(toObject, toPath)
	linkFloatPropertyToDriver(driver, "var", fromObject, fromPath)
	driver.expression = "var"

def linkFloatPropertyToDriver(driver, name, id, dataPath):
	driverVariable = driver.variables.new()
	driverVariable.name = name
	driverVariable.type = "SINGLE_PROP"
	driverVariable.targets[0].id = id
	driverVariable.targets[0].data_path = dataPath
def linkTransformChannelToDriver(driver, name, id, transformType):
	driverVariable = driver.variables.new()
	driverVariable.name = name
	driverVariable.type = "TRANSFORMS"
	driverVariable.targets[0].id = id
	driverVariable.targets[0].transform_type = transformType
	
def deselectAll():
	bpy.ops.object.select_all(action = "DESELECT")
	
def getActive():
	return bpy.context.scene.objects.active
	
def setActive(object):
	object.select = True
	bpy.context.scene.objects.active = object
	
def deleteSelectedObjects():
	bpy.ops.object.delete(use_global=False)
	
def isObjectReferenceSet(object, name):
	if name in object.constraints:
		constraint = object.constraints[name]
		if constraint.name == name:
			if constraint.target:
				return True
	return False

def getChildOfConstraintWithName(object, name):
	if name not in object.constraints:
		constraint = object.constraints.new(type = "CHILD_OF")
		constraint.name = name
	return object.constraints[name]

def setObjectReference(object, name, target):
	if isObjectReferenceSet(object, name):
		object.constraints[name].target = target
	else:
		constraint = getChildOfConstraintWithName(object, name)
		constraint.influence = 0
		constraint.target = target
		constraint.show_expanded = False
		
def getObjectReference(object, name):
	if isObjectReferenceSet(object, name):
		return object.constraints[name].target
	return None

def removeObjectReference(object, name):
	if name in object.constraints:
		object.constraints.remove(object.constraints[name])
		
def lockCurrentTransforms(object):
	lockCurrentLocalLocation(object)
	lockCurrentLocalRotation(object)
	lockCurrentLocalScale(object)
		
def lockCurrentLocalLocation(object, xAxes = True, yAxes = True, zAxes = True):
	setActive(object)
	constraint = object.constraints.new(type = "LIMIT_LOCATION")
	constraint.owner_space = "LOCAL"
	
	setConstraintLimitData(constraint, object.location)
	
	constraint.use_min_x = xAxes
	constraint.use_max_x = xAxes
	constraint.use_min_y = yAxes
	constraint.use_max_y = yAxes
	constraint.use_min_z = zAxes
	constraint.use_max_z = zAxes
	
def lockCurrentLocalRotation(object, xAxes = True, yAxes = True, zAxes = True):
	setActive(object)
	constraint = object.constraints.new(type = "LIMIT_ROTATION")
	constraint.owner_space = "LOCAL"
	
	setConstraintLimitData(constraint, object.rotation_euler)
	
	constraint.use_limit_x = xAxes
	constraint.use_limit_y = yAxes
	constraint.use_limit_z = zAxes
	
def lockCurrentLocalScale(object, xAxes = True, yAxes = True, zAxes = True):
	setActive(object)
	constraint = object.constraints.new(type = "LIMIT_SCALE")
	constraint.owner_space = "LOCAL"
	
	setConstraintLimitData(constraint, object.scale)
	
	constraint.use_min_x = xAxes
	constraint.use_max_x = xAxes
	constraint.use_min_y = yAxes
	constraint.use_max_y = yAxes
	constraint.use_min_z = zAxes
	constraint.use_max_z = zAxes
	
def setConstraintLimitData(constraint, vector):
	(x, y, z) = vector
	constraint.min_x = x
	constraint.max_x = x
	constraint.min_y = y
	constraint.max_y = y
	constraint.min_z = z
	constraint.max_z = z
	
def setUseMinMaxToTrue(constraint):
	constraint.use_min_x = True
	constraint.use_max_x = True
	constraint.use_min_y = True
	constraint.use_max_y = True
	constraint.use_min_z = True
	constraint.use_max_z = True
	
def deleteAllConstraints(object):
	for constraint in object.constraints:
		object.constraints.remove(constraint)
		
def textToName():
	for object in bpy.data.objects:
		if hasattr(object.data, "body"):
			object.name = object.data.body
			
def seperateTextObject(textObject, seperator = "\n"):
	textList = textObject.data.body.split(seperator)
	for i in range(len(textList)):
		newText(name = textList[i], location = [0, -i, 0], text = textList[i])
	
def clearAnimation(object, dataPath):
	fcurves = getFCurvesWithDataPath(object, dataPath)
	for fcurve in fcurves:
		deleteKeyframesInFCurve(object, fcurve)
		
def slowAnimationOnEachKeyframe(object, dataPath):
	fcurves = getFCurvesWithDataPath(object, dataPath)
	for fcurve in fcurves:
		for keyframe in fcurve.keyframe_points:
			keyframe.handle_left.y = keyframe.co.y
			keyframe.handle_right.y = keyframe.co.y
		
def hasAnimationData(object):
	if object.animation_data is not None:
		if object.animation_data.action is not None:
			return True
	return False

def getFCurvesWithDataPath(object, dataPath):
	fcurves = []
	if hasAnimationData(object):
		for fcurve in object.animation_data.action.fcurves:
			if fcurve.data_path == dataPath:
				fcurves.append(fcurve)
	return fcurves
	
def deleteKeyframesInFCurve(object, fcurve):
	object.animation_data.action.fcurves.remove(fcurve)

def changeHandleTypeOfAllKeyframes(object, dataPath, type):
	fcurves = getFCurvesWithDataPath(object, dataPath)
	for fcurve in fcurves:
		for keyframe in fcurve.keyframe_points:
			setKeyframeHandleType(keyframe, type)
			
def setKeyframeHandleType(keyframe, type):
	keyframe.handle_left_type = type
	keyframe.handle_right_type = type
	
def getKeyframePoints(object, dataPath, index = 0):
	fcurves = getFCurvesWithDataPath(object, dataPath)
	if len(fcurves) > index: return fcurves[index].keyframe_points
	return []
		
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
	
def delete(object):
	deselectAll()	
	object.layers[getActiveSceneLayer()] = True
	object.select = True
	object.hide = False
	object.name = "DELETED" + object.name
	bpy.ops.object.delete()
	
def getCurrentFrame():
	return bpy.context.screen.scene.frame_current
	
def insertWiggle(object, dataPath, strength, scale):
	object.keyframe_insert(data_path = dataPath, frame = getCurrentFrame())
	fcurves = []
	for fcurve in object.animation_data.action.fcurves:
		if fcurve.data_path == "location":
			fcurves.append(fcurve)
	for i in range(len(fcurves)):
		modifier = fcurves[i].modifiers.new(type = 'NOISE')
		modifier.phase = i * 10
		modifier.strength = strength
		modifier.scale = scale
		
def clamp(value, minValue, maxValue):
	return max(min(value, maxValue), minValue)
	
def getSelectedKeyframeFrames(keyframes):
	selectedFrames = []
	for keyframe in keyframes:
		if keyframe.select_control_point: selectedFrames.append(keyframe.co.x)
	return selectedFrames
def selectKeyframes(keyframes, keyframeFrames):
	for keyframe in keyframes:
		if keyframe.co.x in keyframeFrames: setKeyframeSelection(keyframe, True)
		else: setKeyframeSelection(keyframe, False)
def setKeyframeSelection(keyframe, select):
	keyframe.select_control_point = select
	keyframe.select_left_handle = select
	keyframe.select_right_handle = select
	
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
	
def getDataPathFromPropertyName(name):
	return '["' + name + '"]'
	
def getObjectFromValidIndex(list, index):
	return list[clamp(index, 0, len(list) - 1)]
	
def getActiveSceneLayer():
	return bpy.context.scene.active_layer
					