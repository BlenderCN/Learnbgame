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

import bpy, math
from sniper_utils import *

# object names
targetCameraName = "TARGET CAMERA"
movementEmptyName = "MOVEMENT"
dataEmptyName = "TARGET CAMERA CONTAINER"
strongWiggleEmptyName = "STRONG WIGGLE"
wiggleEmptyName = "WIGGLE"
distanceEmptyName = "DISTANCE"
focusEmptyName = "FOCUS"
realTargetPrefix = "REAL TARGET"
animationDataName = "ANIMATION DATA"

# property names
travelPropertyName = "travel"
wiggleStrengthPropertyName = "wiggle strength"
wiggleScalePropertyName = "wiggle scale"
inertiaStrengthPropertyName = "inertia strength"
partOfTargetCamera = "part of target camera"
deleteOnRecalculation = "delete on recalculation"
slowInPropertyName = "slow in"
slowOutPropertyName = "slow out"
loadingTimePropertyName = "loading time"
stayTimePropertyName = "stay time"

# property data paths
travelDataPath = getDataPathFromPropertyName(travelPropertyName)
wiggleStrengthDataPath = getDataPathFromPropertyName(wiggleStrengthPropertyName)
wiggleScaleDataPath = getDataPathFromPropertyName(wiggleScalePropertyName)
slowInDataPath = getDataPathFromPropertyName(slowInPropertyName)
slowOutDataPath = getDataPathFromPropertyName(slowOutPropertyName)
loadingTimeDataPath = getDataPathFromPropertyName(loadingTimePropertyName)
stayTimePropertyName = getDataPathFromPropertyName(stayTimePropertyName)

useListSeparator = False

oldHash = ""


# insert basic camera setup
#################################

def insertTargetCamera():
	oldSelection = getSelectedObjects()
	removeOldTargetCameraObjects()

	camera = newCamera()
	focus = newFocusEmpty()
	movement = newMovementEmpty()
	distanceEmpty = newDistanceEmpty()
	strongWiggle = newStrongWiggleEmpty()
	wiggle = newWiggleEmpty()
	dataEmpty = newDataEmpty()
	animationData = newAnimationDataEmpty()
	
	animationData.parent = dataEmpty
	focus.parent = dataEmpty
	movement.parent = dataEmpty
	distanceEmpty.parent = movement
	strongWiggle.parent = distanceEmpty
	wiggle.parent = distanceEmpty
	camera.parent = wiggle;
	
	distanceEmpty.location.z = 4
	
	setActive(camera)
	bpy.context.object.data.dof_object = focus
	
	insertWiggleConstraint(wiggle, strongWiggle, dataEmpty)
	
	setSelectedObjects(oldSelection)
	newTargetsFromSelection()
	
def removeOldTargetCameraObjects():
	for object in bpy.context.scene.objects:
		if isPartOfTargetCamera(object):
			delete(object)
	
def newCamera():
	bpy.ops.object.camera_add(location = [0, 0, 0])
	camera = bpy.context.object
	camera.name = targetCameraName
	camera.rotation_euler = [0, 0, 0]
	makePartOfTargetCamera(camera)
	bpy.context.scene.camera = camera
	return camera
	
def newFocusEmpty():
	focus = newEmpty(name = focusEmptyName, location = [0, 0, 0])
	focus.empty_draw_size = 0.2
	makePartOfTargetCamera(focus)
	focus.hide = True
	return focus
	
def newMovementEmpty():
	movement = newEmpty(name = movementEmptyName, location = [0, 0, 0])
	movement.empty_draw_size = 0.2
	makePartOfTargetCamera(movement)
	movement.hide = True
	return movement
	
def newDistanceEmpty():
	distanceEmpty = newEmpty(name = distanceEmptyName, location = [0, 0, 0])
	distanceEmpty.empty_draw_size = 0.2
	makePartOfTargetCamera(distanceEmpty)
	distanceEmpty.hide = True
	return distanceEmpty

def newStrongWiggleEmpty():
	strongWiggle = newEmpty(name = strongWiggleEmptyName, location = [0, 0, 0])
	strongWiggle.empty_draw_size = 0.2
	makePartOfTargetCamera(strongWiggle)
	strongWiggle.hide = True
	return strongWiggle
	
def newWiggleEmpty():
	wiggle = newEmpty(name = wiggleEmptyName, location = [0, 0, 0])
	wiggle.empty_draw_size = 0.2
	makePartOfTargetCamera(wiggle)
	wiggle.hide = True
	return wiggle

def newDataEmpty():
	dataEmpty = newEmpty(name = dataEmptyName, location = [0, 0, 0])
	setCustomProperty(dataEmpty, travelPropertyName, 1.0, min = 1.0, description = "Progress of Animation")
	setCustomProperty(dataEmpty, "stops", [], description = "Stores the frames where an target is fully loaded.")
	setCustomProperty(dataEmpty, wiggleStrengthPropertyName, 0.0, min = 0.0, max = 1.0, description = "Higher values result in more wiggle.")
	setCustomProperty(dataEmpty, wiggleScalePropertyName, 5.0, min = 1.0, description = "Higher values result in a slower wiggle.")
	setCustomProperty(dataEmpty, inertiaStrengthPropertyName, 0.0, min = 0.0, description = "Set how far the camera will overshoot the targets.")
	dataEmpty.hide = True
	lockCurrentTransforms(dataEmpty)
	makePartOfTargetCamera(dataEmpty)
	return dataEmpty
	
def newAnimationDataEmpty():
	animationData = newEmpty(name = animationDataName, location = [0, 0, 0])
	animationData.empty_draw_size = 0.1
	setCustomProperty(animationData, travelPropertyName, 1.0, description = "Create your keyframes here. Keyframe handles have no impact in the animation. -> Look into 'Slow In' and 'Slow Out'.")
	makePartOfTargetCamera(animationData)
	return animationData

def insertWiggleConstraint(wiggle, strongWiggle, dataEmpty):
	constraint = wiggle.constraints.new(type = "COPY_TRANSFORMS")
	constraint.target = strongWiggle
	driver = newDriver(wiggle, 'constraints["' + constraint.name + '"].influence')
	linkFloatPropertyToDriver(driver, "var", dataEmpty, wiggleStrengthDataPath)	
	driver.expression = "var**2"
	
# create animation
###########################

def recalculateAnimation():
	createFullAnimation(getTargetList())
	
def createFullAnimation(targetList):
	global oldHash
	getKeyframesFromAnimationDataEmpty(targetList)
	oldSelection = getSelectedObjects()
	cleanupScene(targetList)
	removeAnimation()

	movement = getMovementEmpty()
	focus = getFocusEmpty()
	dataEmpty = getDataEmpty()
	deleteAllConstraints(movement)
	deleteAllConstraints(focus)
	
	createWiggleModifiers()
	
	inertiaBases = []
	
	for i in range(len(targetList)):
		target = targetList[i]
		targetBefore = getObjectFromValidIndex(targetList, i-1)
		
		base = createInertiaEmpties(target, targetBefore)
		inertiaBases.append(base)
		createConstraintSet(movement, base)
		createConstraintSet(focus, getTargetObjectFromBase(base))
		
	createTravelToConstraintDrivers(movement)
	createTravelToConstraintDrivers(focus)	
	createTravelAnimation(targetList)
	createInertiaAnimation(dataEmpty, inertiaBases)
	
	setKeyframesOnAnimationDataEmpty()
	reHideUnneededObjects()
	
	oldHash = getCurrentSettingsHash()
	setSelectedObjects(oldSelection)
	
def cleanupScene(targetList):
	for object in bpy.context.scene.objects:
		if isTargetName(object.name) and object not in targetList or isDeleteOnRecalculation(object):
			delete(object)	
	
	
def removeAnimation():
	clearAnimation(getDataEmpty(), travelDataPath)
	
def createInertiaEmpties(target, targetBefore):
	base = newEmpty(name = "base", type = "SPHERE")
	base.empty_draw_size = 0.15
	emptyAfter = newEmpty(name = "after inertia")
	emptyAfter.empty_draw_size = 0.1
	emptyBefore = newEmpty(name = "before inertia")
	emptyBefore.empty_draw_size = 0.1
	
	setParentWithoutInverse(base, target)
	setParentWithoutInverse(emptyAfter, target)
	setParentWithoutInverse(emptyBefore, target)
	
	makeDeleteOnRecalculation(base)
	makeDeleteOnRecalculation(emptyAfter)
	makeDeleteOnRecalculation(emptyBefore)
	
	createPositionConstraint(emptyAfter, target, targetBefore, negate = False)
	createPositionConstraint(emptyBefore, target, targetBefore, negate = True)
	setBaseBetweenInertiaEmpties(base, emptyAfter, emptyBefore)
	
	base.hide = True
	emptyAfter.hide = True
	emptyBefore.hide = True
	return base
	
def createPositionConstraint(object, target, before, negate = False):
	constraint = object.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	
	driver = newDriver(object, 'constraints["' + constraint.name + '"].min_x')
	linkVariablesToIntertiaDriver(driver, target, before)
	if negate: driver.expression = "-(x1-x2)/(sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)+0.000001)*distance+x1"	
	else: driver.expression = "(x1-x2)/(sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)+0.000001)*distance+x1"	
	createCopyValueDriver(object, 'constraints["' + constraint.name + '"].min_x', object, 'constraints["' + constraint.name + '"].max_x')
	
	driver = newDriver(object, 'constraints["' + constraint.name + '"].min_y')
	linkVariablesToIntertiaDriver(driver, target, before)
	if negate: driver.expression = "-(y1-y2)/(sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)+0.000001)*distance+y1"
	else: driver.expression = "(y1-y2)/(sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)+0.000001)*distance+y1"
	createCopyValueDriver(object, 'constraints["' + constraint.name + '"].min_y', object, 'constraints["' + constraint.name + '"].max_y')
	
	driver = newDriver(object, 'constraints["' + constraint.name + '"].min_z')
	linkVariablesToIntertiaDriver(driver, target, before)
	if negate: driver.expression = "-(z1-z2)/(sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)+0.000001)*distance+z1"
	else: driver.expression = "(z1-z2)/(sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)+0.000001)*distance+z1"
	createCopyValueDriver(object, 'constraints["' + constraint.name + '"].min_z', object, 'constraints["' + constraint.name + '"].max_z')

def linkVariablesToIntertiaDriver(driver, target, before):
	dataEmpty = getDataEmpty()
	linkTransformChannelToDriver(driver, "x1", target, "LOC_X")
	linkTransformChannelToDriver(driver, "x2", before, "LOC_X")
	linkTransformChannelToDriver(driver, "y1", target, "LOC_Y")
	linkTransformChannelToDriver(driver, "y2", before, "LOC_Y")
	linkTransformChannelToDriver(driver, "z1", target, "LOC_Z")
	linkTransformChannelToDriver(driver, "z2", before, "LOC_Z")
	linkFloatPropertyToDriver(driver, "distance", dataEmpty, '["'+ inertiaStrengthPropertyName +'"]')
	
def setBaseBetweenInertiaEmpties(base, emptyAfter, emptyBefore):
	constraint = base.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	createDriversToCopyConstraintValues(emptyAfter, emptyAfter.constraints[0], base, constraint)
	constraint = base.constraints.new(type = "LIMIT_LOCATION")
	constraint.influence = 0.5
	setUseMinMaxToTrue(constraint)
	createDriversToCopyConstraintValues(emptyBefore, emptyBefore.constraints[0], base, constraint)
	
def createDriversToCopyConstraintValues(fromObject, fromConstraint, toObject, toConstraint):
	createCopyValueDriver(fromObject, 'constraints["' + fromConstraint.name + '"].min_x', toObject, 'constraints["' + toConstraint.name + '"].min_x')
	createCopyValueDriver(toObject, 'constraints["' + toConstraint.name + '"].min_x', toObject, 'constraints["' + toConstraint.name + '"].max_x')
	createCopyValueDriver(fromObject, 'constraints["' + fromConstraint.name + '"].min_y', toObject, 'constraints["' + toConstraint.name + '"].min_y')
	createCopyValueDriver(toObject, 'constraints["' + toConstraint.name + '"].min_y', toObject, 'constraints["' + toConstraint.name + '"].max_y')
	createCopyValueDriver(fromObject, 'constraints["' + fromConstraint.name + '"].min_z', toObject, 'constraints["' + toConstraint.name + '"].min_z')
	createCopyValueDriver(toObject, 'constraints["' + toConstraint.name + '"].min_z', toObject, 'constraints["' + toConstraint.name + '"].max_z')
	
def createWiggleModifiers():
	global oldWiggleScale
	strongWiggle = getStrongWiggleEmpty()
	wiggleScale = getWiggleScale()
	clearAnimation(strongWiggle, "location")
	strongWiggle.location = [0, 0, 0]
	insertWiggle(strongWiggle, "location", 6, wiggleScale)
	oldWiggleScale = wiggleScale
	
def createConstraintSet(object, target):
	constraint = object.constraints.new(type = "COPY_TRANSFORMS")
	constraint.target = target
	constraint.influence = 0
	constraint.show_expanded = False
	
def createTravelToConstraintDrivers(object):
	dataEmpty = getDataEmpty()
	constraints = object.constraints
	for i in range(getTargetAmount()):
		constraint = constraints[i]
		driver = newDriver(object, 'constraints["' + constraint.name + '"].influence')
		linkFloatPropertyToDriver(driver, "var", dataEmpty, travelDataPath)
		driver.expression = "var - " + str(i)
		
def createTravelAnimation(targetList):
	dataEmpty = getDataEmpty()
	stops = []
	
	frame = 0
	for i in range(getTargetAmount()):
		frame += getLoadingTime(targetList[i])
		dataEmpty[travelPropertyName] = float(i + 1)
		dataEmpty.keyframe_insert(data_path=travelDataPath, frame = frame)
		stops.append(frame)
		
		frame += getStayTime(targetList[i])
		dataEmpty[travelPropertyName] = float(i + 1)
		dataEmpty.keyframe_insert(data_path=travelDataPath, frame = frame)
	setStops(dataEmpty, stops)
		
	positionKeyframeHandles(targetList)
			
def positionKeyframeHandles(targetList):
	dataEmpty = getDataEmpty()
	changeHandleTypeOfAllKeyframes(dataEmpty, travelDataPath, "FREE")
	keyframes = getKeyframePoints(dataEmpty, travelDataPath)
	if len(keyframes) >= 2:
		for i in range(len(keyframes)):
			keyframe = keyframes[i]
			sourceX = keyframe.co.x
			sourceY = keyframe.co.y
			beforeX = getObjectFromValidIndex(keyframes, i-1).co.x
			beforeY = getObjectFromValidIndex(keyframes, i-1).co.y
			afterX = getObjectFromValidIndex(keyframes, i+1).co.x
			afterY = getObjectFromValidIndex(keyframes, i+1).co.y
				
			(easyIn, strengthIn, easyOut, strengthOut) = getInterpolationParameters(targetList[int(sourceY) - 1])
			keyframe.handle_left.x = (beforeX - sourceX) * easyIn * strengthIn + sourceX
			keyframe.handle_left.y = (beforeY - sourceY) * (1 - easyIn) * strengthIn + sourceY				
			keyframe.handle_right.x = (afterX - sourceX) * easyOut * strengthOut + sourceX
			keyframe.handle_right.y = (afterY - sourceY) * (1 - easyOut) * strengthOut + sourceY
			
		
def getInterpolationParameters(target):
	(easyIn, influenceIn) = getInterpolationParametersFromSingleValue(getSlowIn(target))
	(easyOut, influenceOut) = getInterpolationParametersFromSingleValue(getSlowOut(target))
	return (easyIn, influenceIn, easyOut, influenceOut)
	
def getInterpolationParametersFromSingleValue(easyValue):
	easyValue = clamp(easyValue, 0, 1)
	if easyValue < 0.2:
		easy = 0
		influence = 0.5 + (0.2 - easyValue) * 2.5
	elif easyValue > 0.8:
		easy = 1
		influence = 0.5 + (easyValue - 0.8) * 2.5
	else:
		easy = (easyValue - 0.2) * 5 / 3
		influence = 0.5
	return (easy, influence)
	
def createInertiaAnimation(dataEmpty, inertiaBases):
	travelKeyframes = getKeyframePoints(dataEmpty, travelDataPath)
	
	for i in range(0, len(travelKeyframes), 2):
		travelKeyframe = travelKeyframes[i]
		startFrame = travelKeyframe.co.x
		if i+1 < len(travelKeyframes): endFrame = travelKeyframes[i+1].co.x
		else: endFrame = startFrame
		if int(i/2) < len(inertiaBases):
			base = inertiaBases[int(i/2)]
			dataPath = 'constraints["'+base.constraints[1].name+'"].influence'
			base.keyframe_insert(data_path=dataPath, frame = startFrame)
			base.keyframe_insert(data_path=dataPath, frame = endFrame)
			
			keyframes = getKeyframePoints(base, dataPath)
			keyframe = keyframes[0]
			keyframe.interpolation = "ELASTIC"
			keyframe.amplitude = 0.3
			keyframe.period = 7
			
def reHideUnneededObjects():
	getDataEmpty().hide = True
	getFocusEmpty().hide = True
	getMovementEmpty().hide = True
	getDistanceEmpty().hide = True
	getStrongWiggleEmpty().hide = True
	getWiggleEmpty().hide = True
	
		

# animation extra object		
#############################	

def setKeyframesOnAnimationDataEmpty():
	dataEmpty = getDataEmpty()
	animationData = getAnimationDataEmpty()
	selectedKeyframeFrames = getSelectedKeyframeFrames(getKeyframePoints(animationData, travelDataPath))
	clearAnimation(animationData, travelDataPath)
	keyframes = getKeyframePoints(dataEmpty, travelDataPath)
	for keyframe in keyframes:
		animationData[travelPropertyName] = keyframe.co.y
		animationData.keyframe_insert(data_path = travelDataPath, frame = keyframe.co.x)
	selectKeyframes(getKeyframePoints(animationData, travelDataPath), selectedKeyframeFrames)
		
def getKeyframesFromAnimationDataEmpty(targets):
	animationData = getAnimationDataEmpty()
	keyframes = getKeyframePoints(animationData, travelDataPath)
	
	if isValidKeyframeAmount(keyframes, targets):
		for i in range(len(targets)):
			target = targets[i]
			
			position = max(keyframes[i*2].co.x, 1)
			if i > 0: positionBefore = max(keyframes[i*2-1].co.x, 1)
			else: positionBefore = 0
			if i*2+1 < len(keyframes): positionAfter = max(keyframes[i*2+1].co.x, 1)
			else: positionAfter = position
			
			setLoadingTime(target, position - positionBefore)
			setStayTime(target, positionAfter - position)
	
def isValidKeyframeAmount(keyframes, targetList):
	return len(keyframes) == len(targetList) * 2


	
# target operations
#############################

def newTargetsFromSelection():
	targets = getTargetList()
	selectedObjects = []
	for object in getSelectedObjects():
		if not isPartOfTargetCamera(object):
			selectedObjects.append(object)
		
	selectedObjects.reverse()
	for object in selectedObjects:
		targets.append(newRealTarget(object))
	createFullAnimation(targets)
	
def newRealTarget(target):
	if isValidTarget(target): return target
	
	deselectAll()
	setActive(target)
	bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')

	empty = newEmpty(name = realTargetPrefix, location = [0, 0, 0], type = "SPHERE")
	empty.empty_draw_size = 0.2
	setParentWithoutInverse(empty, target)
	
	setCustomProperty(empty, loadingTimePropertyName, 25, min = 1, description = "Frames needed to move to this target.")
	setCustomProperty(empty, stayTimePropertyName, 20, min = 0, description = "How many frames will the camera hold on this target.")
	setCustomProperty(empty, slowInPropertyName, 0.8, min = 0.0, max = 1.0, description = "Higher values result in a smoother camera stop on this target.")
	setCustomProperty(empty, slowOutPropertyName, 0.8, min = 0.0, max = 1.0, description = "Higher values result in a smoother camera start on this target.")
	
	makePartOfTargetCamera(empty)
	
	return empty
	
def deleteTarget(index):
	targets = getTargetList()
	del targets[index]
	createFullAnimation(targets)
	
def moveTargetUp(index):
	if index > 0:
		targets = getTargetList()
		targets.insert(index-1, targets.pop(index))
		createFullAnimation(targets)
def moveTargetDown(index):
	targets = getTargetList()
	targets.insert(index+1, targets.pop(index))
	createFullAnimation(targets)
	
def goToNextTarget():
	travel = getTravelValue()
	newTravel = math.floor(travel) + 1
	bpy.context.screen.scene.frame_current = getFrameOfTravelValue(newTravel)
def goToPreviousTarget():
	travel = getTravelValue()
	newTravel = math.ceil(travel) - 1
	bpy.context.screen.scene.frame_current = getFrameOfTravelValue(newTravel)
	
def getFrameOfTravelValue(travel):
	travel = max(1, travel)
	stops = getDataEmpty()['stops']
	if len(stops) > 0:
		if travel >= len(stops):
			return stops[-1]
		else:
			return stops[int(travel - 1)]
	else: return 1
	
def copyInterpolationProperties(index):
	targets = getTargetList()
	sourceTarget = targets[index]
	easyIn = getSlowIn(sourceTarget)
	easyOut = getSlowOut(sourceTarget)
	for target in targets:
		setSlowIn(target, easyIn)
		setSlowOut(target, easyOut)
	recalculateAnimation()
	
	
# utilities
#############################

def targetCameraSetupExists():
	if (getTargetCamera() is None or
		getFocusEmpty() is None or
		getMovementEmpty() is None or
		getDataEmpty() is None or
		getStrongWiggleEmpty() is None or
		getAnimationDataEmpty() is None): return False
	else: return True
def isTargetCamera(object):
	return object.name == targetCameraName
	
	
def getTargetCamera():
	return bpy.data.objects.get(targetCameraName)
def getFocusEmpty():
	return bpy.data.objects.get(focusEmptyName)
def getMovementEmpty():
	return bpy.data.objects.get(movementEmptyName)
def getDataEmpty():
	return bpy.data.objects.get(dataEmptyName)
def getDistanceEmpty():
	return bpy.data.objects.get(distanceEmptyName)
def getStrongWiggleEmpty():
	return bpy.data.objects.get(strongWiggleEmptyName)
def getWiggleEmpty():
	return bpy.data.objects.get(wiggleEmptyName)
def getAnimationDataEmpty():
	return bpy.data.objects.get(animationDataName)
	
	
def selectTargetCamera():
	camera = getTargetCamera()
	if camera:
		deselectAll()
		camera.select = True
		setActive(camera)
def selectMovementEmpty():
	deselectAll()
	setActive(getMovementEmpty())
def selectTarget(index):
	deselectAll()
	target = getTargetList()[index]
	setActive(target)
	bpy.context.screen.scene.frame_current = getFrameOfTravelValue(index+1)
		
		
def getTargetAmount():
	return len(getTargetList())
def getTargetList():
	targets = []
	uncleanedTargets = getUncleanedTargetList()
	for target in uncleanedTargets:
		if isValidTarget(target) and target not in targets:
			targets.append(target)
	return targets
def getUncleanedTargetList():
	constraintTargets = getConstraintTargetList()
	uncleanedTargets = []
	for constraintTarget in constraintTargets:
		if hasattr(constraintTarget, "parent"):
			uncleanedTargets.append(constraintTarget.parent)
	return uncleanedTargets
def getConstraintTargetList():
	movement = getMovementEmpty()
	constraintTargets = []
	for constraint in movement.constraints:
		if hasattr(constraint, "target"):
			constraintTargets.append(constraint.target)
	return constraintTargets
def isValidTarget(target):
	if hasattr(target, "name"):
		if isTargetName(target.name):
			if hasattr(target, "parent"):
				if hasattr(target.parent, "name"):
					return True
	return False
def isTargetName(name):
	return name[:len(realTargetPrefix)] == realTargetPrefix
	
def getTargetObjectFromTarget(target):
	return target.parent
def getTargetObjectFromBase(base):
	return base.parent.parent
	
def getSelectedTargets(targetList):
	objects = getSelectedObjects()
	targets = []
	for object in objects:
		targetsOfObject = getTargetsFromObject(object, targetList)
		for target in targetsOfObject:
			if target not in targets:
				targets.append(target)
	return targets
def getTargetsFromObject(object, targetList):
	targets = []
	if isValidTarget(object): targets.append(object)
	for target in targetList:
		if target.parent.name == object.name: targets.append(target)
	return targets
	
	
def makePartOfTargetCamera(object):
	object[partOfTargetCamera] = "1"
def isPartOfTargetCamera(object):
	if object.get(partOfTargetCamera) is None:
		return False
	return True
def makeDeleteOnRecalculation(object):
	object[deleteOnRecalculation] = "1"
def isDeleteOnRecalculation(object):
	if object.get(deleteOnRecalculation) is None:
		return False
	return True
	
	
def setStops(dataEmpty, stops):
	dataEmpty['stops'] = stops

def setLoadingTime(target, value):
	target[loadingTimePropertyName] = value
def setStayTime(target, value):
	target[stayTimePropertyName] = value
def setSlowIn(target, value):
	target[slowInPropertyName] = value
def setSlowOut(target, value):
	target[slowOutPropertyName] = value

def getLoadingTime(target):
	return target[loadingTimePropertyName]
def getStayTime(target):
	return target[stayTimePropertyName]
def getSlowIn(target):
	return target[slowInPropertyName]
def getSlowOut(target):
	return target[slowOutPropertyName]
	
def setWiggleScale(value):
	getDataEmpty()[wiggleScalePropertyName] = value
def getWiggleScale():
	return getDataEmpty()[wiggleScalePropertyName]
def getTravelValue():
	return round(getDataEmpty().get(travelPropertyName), 3)
	

def getCurrentSettingsHash():
	hash = getHashFromTargets()
	hash += getAnimationKeyframesHash()
	hash += str(getWiggleScale())
	return hash
def getHashFromTargets():
	hash = ""
	targets = getTargetList()
	for target in targets:
		hash += getHashFromTarget(target)
	return hash
def getAnimationKeyframesHash():
	hash = ""
	keyframes = getKeyframePoints(getAnimationDataEmpty(), travelDataPath)
	for keyframe in keyframes:
		hash += str(keyframe.co.x)
	return hash
def getHashFromTarget(target):
	hash = str(getLoadingTime(target))
	hash += str(getStayTime(target))
	hash += str(getSlowIn(target))
	hash += str(getSlowOut(target))
	return hash
	
	
def openDopeSheet():
	area1 = bpy.context.area
	area1.type = "DOPESHEET_EDITOR"
	bpy.ops.screen.area_split(direction = "HORIZONTAL", factor = 0.86)
	area1.type = "VIEW_3D"
	area2 = getAreaByType("DOPESHEET_EDITOR")
	

		
# interface
#############################

class TargetCameraPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Sniper"
	bl_label = "Sniper"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return targetCameraSetupExists()
	
	def draw(self, context):		
		layout = self.layout
		
		camera = getTargetCamera()
		movement = getMovementEmpty()
		dataEmpty = getDataEmpty()
		targetList = getTargetList()
		
		col = layout.column(align = True)
		col.operator("sniper.recalculate_animation", text = "Recalculate", icon = "ACTION_TWEAK")
		col.operator("sniper.open_dope_sheet", text = "Manipulate Timing", icon = "ACTION")
			
		row = layout.row(align = True)
		row.operator("sniper.go_to_previous_target", icon = 'TRIA_LEFT', text = "")
		row.label("Travel: " + str(getTravelValue()))
		row.operator("sniper.go_to_next_target", icon = 'TRIA_RIGHT', text = "")
		
		box = layout.box()
		col = box.column(align = True)
		
		for i in range(len(targetList)):
			row = col.split(percentage=0.6, align = True)
			row.scale_y = 1.35
			name = row.operator("sniper.select_target", getTargetObjectFromTarget(targetList[i]).name)
			name.currentIndex = i
			up = row.operator("sniper.move_target_up", icon = 'TRIA_UP', text = "")
			up.currentIndex = i
			down = row.operator("sniper.move_target_down", icon = 'TRIA_DOWN', text = "")
			down.currentIndex = i
			delete = row.operator("sniper.delete_target", icon = 'X', text = "")
			delete.currentIndex = i
			if useListSeparator: col.separator()
		box.operator("sniper.new_target_object", icon = 'PLUS')
		
		selectedTargets = getSelectedTargets(targetList)
		selectedTargets.reverse()
		for target in selectedTargets:
			box = layout.box()
			box.label(target.parent.name + "  (" + str(targetList.index(target) + 1) + ")")
			
			col = box.column(align = True)
			col.prop(target, slowInDataPath, slider = False, text = "Ease In")
			col.prop(target, slowOutDataPath, slider = False, text = "Ease Out")
			copyToAll = col.operator("sniper.copy_interpolation_properties_to_all", text = "Copy to All", icon = "COPYDOWN")
			copyToAll.currentIndex = targetList.index(target)			
			
		col = layout.column(align = True)
		col.label("Camera Wiggle")
		col.prop(dataEmpty, wiggleStrengthDataPath, text = "Strength")
		col.prop(dataEmpty, wiggleScaleDataPath, text = "Time Scale")
		
		layout.prop(dataEmpty, '["'+ inertiaStrengthPropertyName +'"]', text = "Inertia Strength")
		
		if getCurrentSettingsHash() != oldHash:
			layout.label("You should recalculate the animation", icon = 'ERROR')
		
	
# operators
#############################
		
class AddTargetCamera(bpy.types.Operator):
	bl_idname = "sniper.insert_target_camera"
	bl_label = "Add Target Camera"
	bl_description = "Create new active camera and create targets from selection."
	
	@classmethod
	def poll(self, context):
		return not targetCameraSetupExists()
		
	def execute(self, context):
		insertTargetCamera()
		return{"FINISHED"}
		
class SetupTargetObject(bpy.types.Operator):
	bl_idname = "sniper.new_target_object"
	bl_label = "New Targets From Selection"
	bl_description = "Use selected objects as targets."
	
	def execute(self, context):
		newTargetsFromSelection()
		return{"FINISHED"}
		
class DeleteTargetOperator(bpy.types.Operator):
	bl_idname = "sniper.delete_target"
	bl_label = "Delete Target"
	bl_description = "Delete the target from the list."
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		deleteTarget(self.currentIndex)
		return{"FINISHED"}
		
class RecalculateAnimationOperator(bpy.types.Operator):
	bl_idname = "sniper.recalculate_animation"
	bl_label = "Recalculate Animation"
	bl_description = "Regenerates most of the constraints, drivers and keyframes."
	
	def execute(self, context):
		createFullAnimation(getTargetList())
		return{"FINISHED"}
		
class MoveTargetUp(bpy.types.Operator):
	bl_idname = "sniper.move_target_up"
	bl_label = "Move Target Up"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		moveTargetUp(self.currentIndex)
		return{"FINISHED"}
		
class MoveTargetDown(bpy.types.Operator):
	bl_idname = "sniper.move_target_down"
	bl_label = "Move Target Down"
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		moveTargetDown(self.currentIndex)
		return{"FINISHED"}		
		
class SelectTarget(bpy.types.Operator):
	bl_idname = "sniper.select_target"
	bl_label = "Select Target"
	bl_description = "Select that target."
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		selectTarget(self.currentIndex)
		return{"FINISHED"}

class GoToNextTarget(bpy.types.Operator):		
	bl_idname = "sniper.go_to_next_target"
	bl_label = "Go To Next Target"
	bl_description = "Change frame to show next target."
	
	def execute(self, context):
		goToNextTarget()
		return{"FINISHED"}
		
class GoToPreviousTarget(bpy.types.Operator):		
	bl_idname = "sniper.go_to_previous_target"
	bl_label = "Go To Previous Target"
	bl_description = "Change frame to show previous target."
	
	def execute(self, context):
		goToPreviousTarget()
		return{"FINISHED"}
		
class CopyInterpolationPropertiesToAll(bpy.types.Operator):
	bl_idname = "sniper.copy_interpolation_properties_to_all"
	bl_label = "Copy Interpolation Properties"
	bl_description = "All targets will have these interpolation values."
	currentIndex = bpy.props.IntProperty()
	
	def execute(self, context):
		copyInterpolationProperties(self.currentIndex)
		return{"FINISHED"}
		
class OpenDopeSheet(bpy.types.Operator):
	bl_idname = "sniper.open_dope_sheet"
	bl_label = "Open Dope Sheet"
	bl_description = "Open dope sheet to manipulate the timing."
	
	@classmethod
	def poll(self, context):
		return not areaTypeExists("DOPESHEET_EDITOR")
	
	def execute(self, context):
		openDopeSheet()
		return{"FINISHED"}

		
# register
#############################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)
