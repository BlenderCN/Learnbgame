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
from lens_flare_utils import *

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