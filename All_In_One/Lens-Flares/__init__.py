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

import sys, os, bpy, mathutils, inspect
import xml.etree.ElementTree as ET
from bpy.app.handlers import persistent
sys.path.append(os.path.dirname(__file__))
from lens_flare_utils import *
from lens_flare_create_object_utils import *
from lens_flare_constraint_utils import *
from lens_flare_driver_utils import *
from lens_flare_animation_utils import *
from lens_flare_material_and_node_utils import *


bl_info = {
	"name":        "Lens Flares",
	"description": "",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 80, 0),
	"location":    "View 3D > Tool Shelf",
	"category": "Learnbgame",
	"warning":	   "alpha"
	}
	
activeFlareName = ""
activeElementName = ""

addonFolder = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")]
elementsFolder = addonFolder + "elements\\"
presetsFolder = addonFolder + "presets\\"
	
flareControlerPrefix = "flare controler"
angleCalculatorPrefix = "angle calculator"
startDistanceCalculatorPrefix = "start distance calculator"
flareElementPrefix = "flare element"
cameraCenterPrefix = "center of camera"
cameraDirectionCalculatorPrefix = "camera direction calculator"
startElementPrefix = "start element"
endElementPrefix = "end element"
flareElementEmptyPrefix = "flare element data"
elementNamesContainerPrefix = "element data names container"
targetEmptyPrefix = "target empty"

dofDistanceName = "dof distance"
plainDistanceName = "plane distance"
directionXName = "direction x"
directionYName = "direction y"
directionZName = "direction z"
angleName = "angle"
startDistanceName = "start distance"
avoidArtefactsOffsetName = "offset to avoid artefacts"
currentElementOffsetName = "current offset"
elementPositionName = "element position"
planeWidthFactorName = "width factor"
scaleXName = "scale x"
scaleYName = "scale y"
offsetXName = "offset x"
offsetYName = "offset y"
imagePathName = "image path"
colorMultiplyName = "multiply color"
additionalRotationName = "additional rotation"
trackToCenterInfluenceName = "track to center influence"
intensityName = "intensity"
imageNodeName = "image node"
colorMultiplyNodeName = "color multiply node"
emissionNodeName = "emission node"
childOfFlarePropertyName = "child of flare"
targetPropertyName = "flare target"
cameraOfFlarePropertyName = "camera of this flare"
startElementPropertyName = "start element"
endElementPropertyName = "end element"
elementNamePropertyName = "corresponding element"
elementNamesContainerPropertyName = "element data names container"
elementNamePropertyName = "element data name"
elementPlainNamePropertyName = "element plane name"
flareNamePropertyName = "flare name"
linkToFlareControlerPropertyName = "flare link from target"
targetNamePropertyName = "target empty"
angleNamePropertyName = "angle calculator"

anglePath = getDataPath(angleName)
startDistancePath = getDataPath(startDistanceName)
directionXPath = getDataPath(directionXName)
directionYPath = getDataPath(directionYName)
directionZPath = getDataPath(directionZName)
dofDistancePath = getDataPath(dofDistanceName)
avoidArtefactsOffsetPath = getDataPath(avoidArtefactsOffsetName)
elementPositionPath = getDataPath(elementPositionName)
planeWidthFactorPath = getDataPath(planeWidthFactorName)
scaleXPath = getDataPath(scaleXName)
scaleYPath = getDataPath(scaleYName)
offsetXPath = getDataPath(offsetXName)
offsetYPath = getDataPath(offsetYName)
additionalRotationPath = getDataPath(additionalRotationName)
trackToCenterInfluencePath = getDataPath(trackToCenterInfluenceName)
intensityPath = getDataPath(intensityName)
elementNamePropertyPath = getDataPath(elementNamePropertyName)
flareNamePropertyPath = getDataPath(flareNamePropertyName)


# new lens flare
###################################

def newLensFlareFromData(camera, target, flareData):
	flareControler = newLensFlare(camera, target)
	flareData.setDataOnFlareControler(flareControler)
	return flareControler

def newLensFlare(camera, target):
	setCurrentOffsetPropertyOnCamera(camera)
	center = getCenterEmpty(camera)
	targetEmpty = newTargetEmpty(target)
	flareControler = newFlareControler(camera, targetEmpty, center)	
	setCustomProperty(targetEmpty, linkToFlareControlerPropertyName, flareControler.name)
	angleCalculator = newAngleCalculator(flareControler, camera, targetEmpty, center)
	startDistanceCalculator = newStartDistanceCalculator(flareControler, angleCalculator, center, camera)
	
	startElement = newStartElement(flareControler, camera, startDistanceCalculator)
	endElement = newEndElement(flareControler, startElement, center, camera)
	
	elementNamesContainer = newElementEmptyNamesContainer(flareControler)
	
	setCustomProperty(flareControler, startElementPropertyName, startElement.name)
	setCustomProperty(flareControler, endElementPropertyName, endElement.name)
	setCustomProperty(flareControler, elementNamesContainerPropertyName, elementNamesContainer.name)
	setCustomProperty(flareControler, targetNamePropertyName, targetEmpty.name)
	setCustomProperty(flareControler, angleNamePropertyName, angleCalculator.name)
	setParentWithoutInverse(targetEmpty, camera)
	makePartOfFlareControler(targetEmpty, flareControler)
	
	flareControler.hide =  True
	angleCalculator.hide = True
	startDistanceCalculator.hide = True
	startElement.hide = True
	endElement.hide = True
	elementNamesContainer.hide = True
	targetEmpty.hide = True
	
	setMinMaxTransparentBounces(512)
	return flareControler
	
def setCurrentOffsetPropertyOnCamera(camera):
	if currentElementOffsetName not in camera:
		setCustomProperty(camera, currentElementOffsetName, -0.002)
		
def newTargetEmpty(target):
	targetEmpty = newEmpty(name = targetEmptyPrefix)
	constraint = targetEmpty.constraints.new(type = "COPY_LOCATION")
	constraint.target = target
	return targetEmpty

# camera direction calculator

def getCameraDirectionCalculator(camera):
	directionCalculators = getCameraDirectionCalculators()
	for calculator in directionCalculators:
		if calculator.parent == camera:
			return calculator
	return newCameraDirectionCalculator(camera)
	
def getCameraDirectionCalculators():
	calculators = []
	for object in bpy.data.objects:
		if hasPrefix(object.name, cameraDirectionCalculatorPrefix):
			calculators.append(object)
	return calculators
	
def newCameraDirectionCalculator(camera):
	calculator = newEmpty(name = cameraDirectionCalculatorPrefix)
	setParentWithoutInverse(calculator, camera)
	calculator.location.z = -1
	lockCurrentLocalLocation(calculator)
	setCameraDirectionProperties(calculator, camera)
	calculator.hide = True
	return calculator
	
def setCameraDirectionProperties(directionCalculator, camera):
	setTransformDifferenceAsProperty(directionCalculator, camera, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(directionCalculator, camera, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(directionCalculator, camera, directionZName, "LOC_Z", normalized = True)
	
# center creation	

def getCenterEmpty(camera):
	centers = getCenterEmpties()
	for center in centers:
		if center.parent == camera:
			return center
	return newCenterEmpty(camera)
	
def getCenterEmpties():
	centers = []
	for object in bpy.data.objects:
		if hasPrefix(object.name, cameraCenterPrefix):
			centers.append(object)
	return centers
	
def newCenterEmpty(camera):
	center = newEmpty(name = cameraCenterPrefix, type = "SPHERE")
	setParentWithoutInverse(center, camera)
	center.empty_draw_size = 0.1
	center.hide = True
	setCenterDistance(center, camera)
	lockCurrentLocalLocation(center, zAxes = False)
	return center
	
def setCenterDistance(center, camera):
	directionCalculator = getCameraDirectionCalculator(camera)
	
	driver = newDriver(center, "location", index = 2)
	linkFloatPropertyToDriver(driver, "distance", getCameraFromObject(camera), "dof_distance", idType = "CAMERA")
	linkTransformChannelToDriver(driver, "scale", camera, "SCALE_Z")
	driver.expression = "-max(distance, 1)/scale"
	
# flare controler creation	

def newFlareControler(camera, target, center):
	flareControler = newEmpty(name = flareControlerPrefix)
	makePartOfFlareControler(flareControler, flareControler)
	setCustomProperty(flareControler, flareNamePropertyName, "Lens Flare")
	setCustomProperty(flareControler, intensityName, 1.0, min = 0.0)
	setObjectReference(flareControler, cameraOfFlarePropertyName, camera)
	setObjectReference(flareControler, targetPropertyName, target)
	setParentWithoutInverse(flareControler, camera)	
	lockCurrentLocalLocation(flareControler)
	setTargetDirectionProperties(flareControler, target)
	return flareControler
	
def setTargetDirectionProperties(flareControler, target):
	setTransformDifferenceAsProperty(flareControler, target, directionXName, "LOC_X", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionYName, "LOC_Y", normalized = True)
	setTransformDifferenceAsProperty(flareControler, target, directionZName, "LOC_Z", normalized = True)
	
# angle calculator

def newAngleCalculator(flareControler, camera, target, center):
	angleCalculator = newEmpty(name = angleCalculatorPrefix)
	makePartOfFlareControler(angleCalculator, flareControler)
	setParentWithoutInverse(angleCalculator, flareControler)
	setTargetAngleProperty(angleCalculator, flareControler, getCameraDirectionCalculator(camera))
	return angleCalculator
	
def setTargetAngleProperty(angleCalculator, flareControler, cameraDirectionCalculator):
	setCustomProperty(angleCalculator, angleName)
	driver = newDriver(angleCalculator, anglePath)
	linkFloatPropertyToDriver(driver, "x1", flareControler, directionXPath)
	linkFloatPropertyToDriver(driver, "y1", flareControler, directionYPath)
	linkFloatPropertyToDriver(driver, "z1", flareControler, directionZPath)	
	linkFloatPropertyToDriver(driver, "x2", cameraDirectionCalculator, directionXPath)
	linkFloatPropertyToDriver(driver, "y2", cameraDirectionCalculator, directionYPath)
	linkFloatPropertyToDriver(driver, "z2", cameraDirectionCalculator, directionZPath)
	driver.expression = "degrees(acos(x1*x2+y1*y2+z1*z2))"
	
# start distance calculator
	
def newStartDistanceCalculator(flareControler, angleCalculator, center, camera):
	startDistanceCalculator = newEmpty(name = startDistanceCalculatorPrefix)
	makePartOfFlareControler(startDistanceCalculator, flareControler)
	setParentWithoutInverse(startDistanceCalculator, flareControler)
	setStartDistanceProperty(startDistanceCalculator, angleCalculator, center, camera)
	return startDistanceCalculator
	
def setStartDistanceProperty(startDistanceCalculator, angleCalculator, center, camera):
	setCustomProperty(startDistanceCalculator, startDistanceName)
	driver = newDriver(startDistanceCalculator, startDistancePath)
	linkDistanceToDriver(driver, "distance", center, camera)
	linkFloatPropertyToDriver(driver, "angle", angleCalculator, anglePath)
	driver.expression = "-distance/cos(radians(angle))"

# start element creation
	
def newStartElement(flareControler, camera, startDistanceCalculator):
	startElement = newEmpty(name = startElementPrefix)
	makePartOfFlareControler(startElement, flareControler)
	setParentWithoutInverse(startElement, flareControler)
	setStartLocationDrivers(startElement, camera, flareControler, startDistanceCalculator)
	return startElement
	
def setStartLocationDrivers(startElement, camera, flareControler, startDistanceCalculator):
	constraint = startElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)
	
	for val in [".min", ".max"]:
		driver = newDriver(startElement, constraintPath + val + "_x")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionXPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_X")
		driver.expression = "direction*distance+cam"
		
		driver = newDriver(startElement, constraintPath + val + "_y")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionYPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_Y")
		driver.expression = "direction*distance+cam"
		
		driver = newDriver(startElement, constraintPath + val + "_z")
		linkFloatPropertyToDriver(driver, "direction", flareControler, directionZPath)
		linkFloatPropertyToDriver(driver, "distance", startDistanceCalculator, startDistancePath)
		linkTransformChannelToDriver(driver, "cam", camera, "LOC_Z")
		driver.expression = "direction*distance+cam"
	
# end element creation

def newEndElement(flareControler, startElement, center, camera):
	endElement = newEmpty(name = endElementPrefix)
	makePartOfFlareControler(endElement, flareControler)
	setParentWithoutInverse(endElement, flareControler)
	setEndLocationDrivers(endElement, startElement, center)
	return endElement
	
def setEndLocationDrivers(endElement, startElement, center):
	constraint = endElement.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)

	for val in [".min", ".max"]:
		driver = newDriver(endElement, constraintPath + val + "_x")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_X")
		linkTransformChannelToDriver(driver, "center", center, "LOC_X")
		driver.expression = "2*center - start"
		
		driver = newDriver(endElement, constraintPath + val + "_y")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Y")
		linkTransformChannelToDriver(driver, "center", center, "LOC_Y")
		driver.expression = "2*center - start"
		
		driver = newDriver(endElement, constraintPath + val + "_z")
		linkTransformChannelToDriver(driver, "start", startElement, "LOC_Z")
		linkTransformChannelToDriver(driver, "center", center, "LOC_Z")
		driver.expression = "2*center - start"
	
# element data names container
	
def newElementEmptyNamesContainer(flareControler):
	elementNamesContainer = newEmpty(name = elementNamesContainerPrefix)
	makePartOfFlareControler(elementNamesContainer, flareControler)
	setParentWithoutInverse(elementNamesContainer, flareControler)
	return elementNamesContainer
	

	
	
# new element
#########################################

def newFlareElementFromData(flareControler, elementData):
	name = elementData.name
	image = getImage(elementData.getImagePath())
	(element, plane) = newFlareElement(flareControler, image, name)
	elementData.setDataOnElement(element)
	return element
	
def newFlareElement(flareControler, image, name = "element"):
	camera = getCameraFromFlareControler(flareControler)
	camera[currentElementOffsetName] += 0.0003
	startElement = getStartElement(flareControler)
	endElement = getEndElement(flareControler)
	
	element = newFlareElementEmpty(flareControler, startElement, endElement, camera)
	flareElement = newFlareElementPlane(image, element, flareControler, camera)	
	
	setCustomProperty(element, elementPlainNamePropertyName, flareElement.name)
	
	makePartOfFlareElement(element, element)
	makePartOfFlareElement(flareElement, element)
	
	elementNamesContainer = getElementEmptyNamesContainer(flareControler)
	appendObjectReference(elementNamesContainer, element)
	
	setCustomProperty(element, elementNamePropertyName, name)
	
	setDisplayTypeToWire(flareElement)
	
	return (element, flareElement)
	
def newFlareElementEmpty(flareControler, startElement, endElement, camera):
	element = newEmpty(name = flareElementEmptyPrefix)
	makePartOfFlareControler(element, flareControler)
	element.empty_draw_size = 0.01
	
	setParentWithoutInverse(element, flareControler)
	setCustomPropertiesOnFlareElement(element, camera)
	setPositionConstraintOnFlareElement(element, startElement, endElement)
	return element
	
def setCustomPropertiesOnFlareElement(element, camera):
	setCustomProperty(element, elementNamePropertyName, "Glow", description = "This name shows up in the element list.")
	setCustomProperty(element, avoidArtefactsOffsetName, camera[currentElementOffsetName], description = "Random offset of every object to avoid overlapping.")
	setCustomProperty(element, elementPositionName, 0.0, description = "Relative element position. 0: element is on target; 1: opposite side")
	setCustomProperty(element, scaleXName, 1.0, min = 0.0, description = "Width of this element.")
	setCustomProperty(element, scaleYName, 1.0, min = 0.0, description = "Height of this element.")
	setCustomProperty(element, trackToCenterInfluenceName, 0.0, min = 0.0, max = 1.0, description = "0: normal; 1: rotate element to center")
	setCustomProperty(element, intensityName, 1.0, min = 0.0, description = "Brightness of this element.")
	setCustomProperty(element, additionalRotationName, 0, description = "Rotation in camera direction.")
	setCustomProperty(element, offsetXName, 0.0, description = "Horizontal movement of this element.")
	setCustomProperty(element, offsetYName, 0.0, description = "Vertical movement of this element.")
	
def setPositionConstraintOnFlareElement(element, startElement, endElement):
	constraint = element.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)
	for val in [".min", ".max"]:
		setPositionDriverOnFlareElementConstraint(element, startElement, endElement, constraintPath + val + "_x", "LOC_X")
		setPositionDriverOnFlareElementConstraint(element, startElement, endElement, constraintPath + val + "_y", "LOC_Y")
		setPositionDriverOnFlareElementConstraint(element, startElement, endElement, constraintPath + val + "_z", "LOC_Z")
		
def setPositionDriverOnFlareElementConstraint(element, startElement, endElement, pathToValue, channel):
	driver = newDriver(element, pathToValue)
	linkTransformChannelToDriver(driver, "start", startElement, channel)
	linkTransformChannelToDriver(driver, "end", endElement, channel)
	linkFloatPropertyToDriver(driver, "position", element, elementPositionPath)
	driver.expression = "start * (1-position) + end * position"

def newFlareElementPlane(image, element, flareControler, camera):
	plane = newPlane(name = flareElementPrefix, size = 0.1)
	makePartOfFlareControler(plane, flareControler)
	setCustomProperty(plane, planeWidthFactorName, image.size[0] / image.size[1])
	makeOnlyVisibleToCamera(plane)
	material = newCyclesFlareMaterial(image)
	setMaterialOnObject(plane, material)
	
	setParentWithoutInverse(plane, element)
	setScaleConstraintOnElementPlane(plane, element, camera)
	setTrackToCenterConstraintOnElementPlane(plane, element, camera)
	limitXYRotationOnElementPlane(plane)
	setLimitLocationConstraintOnElementPlane(plane, element, camera)
	setIntensityDriverOnElementPlane(plane, element, flareControler)
	setAdditionalRotationDriverOnElementPlane(plane, element)
	
	return plane
	
def newCyclesFlareMaterial(image):
	material = newCyclesMaterial()
	cleanMaterial(material)
	
	nodeTree = material.node_tree
	textureCoordinatesNode = newTextureCoordinatesNode(nodeTree)
	imageNode = newImageTextureNode(nodeTree)
	colorRamp = newColorRampNode(nodeTree)
	colorMultiply = newColorMixNode(nodeTree, type = "MULTIPLY", factor = 1.0, default2 = [1.0, 1.0, 1.0, 1.0])
	emission = newEmissionNode(nodeTree)
	transparent = newTransparentNode(nodeTree)
	addShader = newAddShader(nodeTree)
	output = newOutputNode(nodeTree)
	
	imageNode.image = image
	imageNode.name = imageNodeName
	colorMultiply.name = colorMultiplyNodeName
	emission.name = emissionNodeName
	
	newNodeLink(nodeTree, textureCoordinatesNode.outputs["Generated"], imageNode.inputs[0])
	newNodeLink(nodeTree, imageNode.outputs[0], colorRamp.inputs[0])
	newNodeLink(nodeTree, colorRamp.outputs[0], colorMultiply.inputs[1])
	newNodeLink(nodeTree, colorMultiply.outputs[0], emission.inputs[0])
	linkToAddShader(nodeTree, emission.outputs[0], transparent.outputs[0], addShader)
	newNodeLink(nodeTree, addShader.outputs[0], output.inputs[0])
	return material
	
def setScaleConstraintOnElementPlane(plane, element, camera):
	constraint = plane.constraints.new(type = "LIMIT_SCALE")
	constraintPath = getConstraintPath(constraint)
	setUseMinMaxToTrue(constraint)
	for val in [".min", ".max"]:
		driver = newDriver(plane, constraintPath + val + "_x")
		linkDistanceToDriver(driver, "distance", plane, camera)
		linkFloatPropertyToDriver(driver, "factor", plane, planeWidthFactorPath)
		linkFloatPropertyToDriver(driver, "scale", element, scaleXPath)
		driver.expression = "factor * scale * distance / 1"
		
		driver = newDriver(plane, constraintPath + val + "_y")
		linkDistanceToDriver(driver, "distance", plane, camera)
		linkFloatPropertyToDriver(driver, "scale", element, scaleYPath)
		driver.expression = "scale * distance / 1"
		
		driver = newDriver(plane, constraintPath + val + "_z")
		linkDistanceToDriver(driver, "distance", plane, camera)
		driver.expression = "distance / 1"
	
def setTrackToCenterConstraintOnElementPlane(plane, element, camera):
	constraint = plane.constraints.new(type = "TRACK_TO")
	constraint.target = getCenterEmpty(camera)
	constraint.track_axis = "TRACK_X"
	constraint.use_target_z = True
	constraintPath = getConstraintPath(constraint)
	driver = newDriver(plane, constraintPath + ".influence", type = "SUM")
	linkFloatPropertyToDriver(driver, "var", element, trackToCenterInfluencePath)
	
def limitXYRotationOnElementPlane(plane):
	constraint = plane.constraints.new(type = "LIMIT_ROTATION")
	constraint.owner_space = "LOCAL"
	constraint.use_limit_x = True
	constraint.use_limit_y = True
	
def setLimitLocationConstraintOnElementPlane(plane, element, camera):
	constraint = plane.constraints.new(type = "LIMIT_LOCATION")
	constraint.owner_space = "LOCAL"
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)
	for channel in [".min_", ".max_"]:
		driver = newDriver(plane, constraintPath + channel + "x")
		linkFloatPropertyToDriver(driver, "offset", element, offsetXPath)
		linkDistanceToDriver(driver, "distance", element, camera)
		driver.expression = "offset*distance"
		
		driver = newDriver(plane, constraintPath + channel + "y")
		linkFloatPropertyToDriver(driver, "offset", element, offsetYPath)
		linkDistanceToDriver(driver, "distance", element, camera)
		driver.expression = "offset*distance"
	
		driver = newDriver(plane, constraintPath + channel + "z")
		linkFloatPropertyToDriver(driver, "offset", element, avoidArtefactsOffsetPath)
		linkDistanceToDriver(driver, "distance", element, camera)
		driver.expression = "offset*distance"
		
def setIntensityDriverOnElementPlane(plane, element, flareControler):
	driver = newDriver(getNodeWithNameInObject(plane, emissionNodeName).inputs[1], "default_value")
	linkFloatPropertyToDriver(driver, "objectIntensity", element, intensityPath)
	linkFloatPropertyToDriver(driver, "flareIntensity", flareControler, intensityPath)
	driver.expression = "(objectIntensity * flareIntensity)**2"
	
def setAdditionalRotationDriverOnElementPlane(plane, element):
	driver = newDriver(plane, "rotation_euler", index = 2)
	linkFloatPropertyToDriver(driver, "var", element, additionalRotationPath)
	driver.expression = "radians(var)"
	
	
	
# utils
################################

def getAllFlares():
	flareControlers = []
	for object in bpy.data.objects:
		if hasFlareControlerAttribute(object) or hasLinkToFlareControler(object):
			flareControler = getCorrespondingFlareControler(object)
			if flareControler not in flareControlers and flareControler is not None:
				flareControlers.append(flareControler)
	return flareControlers

def getSelectedFlares():
	flareControlers = []
	selection = getSelectedObjects()
	selection.append(getActive())
	for object in selection:
		if hasFlareControlerAttribute(object) or hasLinkToFlareControler(object):
			flareControler = getCorrespondingFlareControler(object)
			if flareControler not in flareControlers and flareControler is not None:
				flareControlers.append(flareControler)
	return flareControlers
	
def getSelectedFlareElementEmpties():	
	flareElementEmpties = []
	selection = getSelectedObjects()
	for object in selection:
		if hasFlareElementAttribute(object):
			element = getCorrespondingElement(object)
			if element not in flareElementEmpties and element is not None:
				flareElementEmpties.append(element)
	return flareElementEmpties
	
def getDataElementsFromFlare(flareControler):
	elementNamesContainer = getElementEmptyNamesContainer(flareControler)
	elementEmpties = getObjectReferences(elementNamesContainer)
	return elementEmpties
	
def getCameraFromFlareControler(flareControler):
	return flareControler.parent
	
def getStartElement(flareControler):
	return bpy.data.objects[flareControler[startElementPropertyName]]
def getEndElement(flareControler):
	return bpy.data.objects[flareControler[endElementPropertyName]]
def getAngleCalculator(flareControler):
	return bpy.data.objects[flareControler[angleNamePropertyName]]
def getElementEmptyObjects(flareControler):
	container = getElementEmptyNamesContainer(flareControler)
	return getObjectReferences(container)
def getElementEmptyNamesContainer(flareControler):
	return bpy.data.objects[flareControler[elementNamesContainerPropertyName]]

def isPartOfAnyFlareControler(object):
	return getCorrespondingFlareControler(object) is not None
def makePartOfFlareControler(object, flareControler):
	setCustomProperty(object, childOfFlarePropertyName, flareControler.name)
def isPartOfFlareControler(object, flareControler):
	if object is None or flareControler is None: return False
	return object.get(childOfFlarePropertyName) == flareControler.name
def getCorrespondingFlareControler(object):
	if hasFlareControlerAttribute(object): return bpy.data.objects.get(object[childOfFlarePropertyName])
	if hasLinkToFlareControler(object): return bpy.data.objects.get(object[linkToFlareControlerPropertyName])
def hasFlareControlerAttribute(object):
	if object is None: return False
	return childOfFlarePropertyName in object
def hasLinkToFlareControler(object):
	if object is None: return False
	return linkToFlareControlerPropertyName in object
	
def makePartOfFlareElement(object, dataElement):
	setCustomProperty(object, elementNamePropertyName, dataElement.name)
def getCorrespondingElement(object):
	if hasFlareElementAttribute(object): return bpy.data.objects.get(object[elementNamePropertyName])
def hasFlareElementAttribute(object):
	if object is None: return False
	return elementNamePropertyName in object
	
def getTargetEmpty(flareControler):
	return bpy.data.objects[flareControler[targetNamePropertyName]]
	
def getPlaneFromElement(element):
	return bpy.data.objects[element[elementPlainNamePropertyName]]
	
def getImageFromElementEmpty(data):
	plane = getPlaneFromElement(data)
	node = getNodeWithNameInObject(plane, imageNodeName)
	return node.image
	
def setImagePathOnElementPlane(plane, imagePath):
	image = getImage(imagePath)
	getNodeWithNameInObject(plane, imageNodeName).image = image
	plane[planeWidthFactorName] = image.size[0] / image.size[1]
	
def setMultiplyColorOnElementPlane(plane, color):
	getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2].default_value = color
	
def deleteFlare(flareControler):
	for object in bpy.data.objects:
		if isPartOfFlareControler(object, flareControler) and object != flareControler:
			delete(object)
	delete(flareControler)
	
def deleteFlareElement(element):
	flareControler = getCorrespondingFlareControler(element)
	delete(getPlaneFromElement(element))
	delete(element)
	cleanReferenceList(getElementEmptyNamesContainer(flareControler))
	
def duplicateFlareElement(element):
	flareControler = getCorrespondingFlareControler(element)
	elementData = FlareElementData.FromElement(element)
	newElement = newFlareElementFromData(flareControler, elementData)
	return newElement
	
def duplicateLensFlare(flareControler):
	flareData = LensFlareData.FromFlareControler(flareControler)
	elements = getElementEmptyObjects(flareControler)
	elementDatas = []
	for element in elements:
		elementDatas.append(FlareElementData.FromElement(element))
	generateLensFlare(getActiveCamera(), getActive(), flareData, elementDatas)
	
def generateLensFlare(camera, target, flareData, elementDatas):
	flareControler = newLensFlareFromData(camera, target, flareData)
	for elementData in elementDatas:
		newFlareElementFromData(flareControler, elementData)
	
def saveLensFlare(flareControler, path):
	flare = ET.Element("Flare")
	flare.set("name", flareControler[flareNamePropertyName])
	flare.set("intensity", str(flareControler[intensityName]))
	
	elements = getElementEmptyObjects(flareControler)
	for element in elements:
		elementData = FlareElementData.FromElement(element)
		
		el = ET.SubElement(flare, "Element")
		el.set("imageName", str(elementData.imageName))
		el.set("name", str(elementData.name))
		
		el.set("position", str(elementData.position))
		el.set("intensity", str(elementData.intensity))
		el.set("rotation", str(elementData.rotation))
		el.set("centerRotation", str(elementData.centerRotation))
		el.set("width", str(elementData.width))
		el.set("height", str(elementData.height))
		el.set("horizontal", str(elementData.xOffset))
		el.set("vertical", str(elementData.yOffset))
		
		multiplyColor = ET.SubElement(el, "multiplyColor")
		multiplyColor.set("red", str(elementData.color[0]))
		multiplyColor.set("green", str(elementData.color[1]))
		multiplyColor.set("blue", str(elementData.color[2]))
	
	ET.ElementTree(flare).write(path)	
	
def loadLensFlare(path):
	tree = ET.parse(path)
	flareET = tree.getroot()
	
	flareData = LensFlareData()
	flareData.name = getStringProperty(flareET, "name", "Lens Flare")
	flareData.intensity = getFloatProperty(flareET, "intensity", 1.0)
	
	elementDatas = []
	for elementET in flareET:
		elementData = FlareElementData()
		elementData.name = getStringProperty(elementET, "name", "Flare Element")
		elementData.imageName = getStringProperty(elementET, "imageName", "circle.jpg")
		elementData.position = getFloatProperty(elementET, "position", 0.0)
		elementData.intensity = getFloatProperty(elementET, "intensity", 1.0)
		elementData.rotation = getIntProperty(elementET, "rotation", 0)
		elementData.centerRotation = getFloatProperty(elementET, "centerRotation", 0.0)
		elementData.width = getFloatProperty(elementET, "width", 1.0)
		elementData.height = getFloatProperty(elementET, "height", 1.0)
		elementData.xOffset = getFloatProperty(elementET, "horizontal", 0.0)
		elementData.yOffset = getFloatProperty(elementET, "vertical", 0.0)
		
		multiplyColorET = elementET.find("multiplyColor")
		color = [1, 1, 1, 1]
		color[0] = getFloatProperty(multiplyColorET, "red", 1.0)
		color[1] = getFloatProperty(multiplyColorET, "green", 1.0)
		color[2] = getFloatProperty(multiplyColorET, "blue", 1.0)
		
		elementData.color = color
		
		elementDatas.append(elementData)
		

	generateLensFlare(getActiveCamera(), getActive(), flareData, elementDatas)

def updateActiveFlareName():
	flareControler = getCorrespondingFlareControler(getActive())
	if flareControler is not None: setActiveFlareName(flareControler.name)
def setActiveFlareName(flareControlerName):
	global activeFlareName
	activeFlareName = flareControlerName
def isFlareActive():
	return getActiveFlare() is not None
def getActiveFlare():
	return bpy.data.objects.get(activeFlareName)
	
def updateActiveElementName():
	element = getCorrespondingElement(getActive())
	if element is not None: setActiveElementName(element.name)
def setActiveElementName(elementName):
	global activeElementName
	activeElementName = elementName
def isElementActive():
	return getActiveElement() is not None
def getActiveElement():
	activeFlare = getActiveFlare()
	activeElement = bpy.data.objects.get(activeElementName)
	if isPartOfFlareControler(activeElement, activeFlare): return activeElement
	return None
	
	
class LensFlareData:
	def __init__(self, 	name = "lens flare",
						intensity = 1.0):
		self.name = name
		self.intensity = intensity
		
	def setDataOnFlareControler(self, flareControler):
		flareControler[flareNamePropertyName] = self.name
		flareControler[intensityName] = self.intensity
		
	def fromFlareControler(flareControler):
		flareData = LensFlareData()
		flareData.name = flareControler[flareNamePropertyName]
		flareData.intensity = flareControler[intensityName]
		return flareData
	FromFlareControler = staticmethod(fromFlareControler)
	
class FlareElementData:
	def __init__(self, 	name = "flare element", 
						imageName = "circle.jpg",
						position = 0.0, 
						intensity = 1.0,
						rotation = 0.0,
						centerRotation = 0.0,
						width = 1.0,
						height = 1.0,
						xOffset = 0.0,
						yOffset = 0.0,
						color = [1, 1, 1, 1]):
		self.name = name
		self.imageName = imageName
		self.position = position
		self.intensity = intensity
		self.rotation = rotation
		self.centerRotation = centerRotation
		self.width = width
		self.height = height
		self.xOffset = xOffset
		self.yOffset = yOffset
		self.color = color
	
	def getImagePath(self):
		return elementsFolder + self.imageName
		
	def setDataOnElement(self, element):
		plane = getPlaneFromElement(element)
		
		element[elementNamePropertyName] = self.name
		element[elementPositionName] = self.position
		element[scaleXName] = self.width
		element[scaleYName] = self.height
		element[offsetXName] = self.xOffset
		element[offsetYName] = self.yOffset
		element[trackToCenterInfluenceName] = self.centerRotation
		element[intensityName] = self.intensity
		element[additionalRotationName] = self.rotation
		setImagePathOnElementPlane(plane, self.getImagePath())
		setMultiplyColorOnElementPlane(plane, self.color)
		
	def fromElement(element):
		plane = getPlaneFromElement(element)
	
		elementData = FlareElementData()
		elementData.name = element[elementNamePropertyName]
		elementData.imageName = getImageFromElementEmpty(element).name
		elementData.position = element[elementPositionName]
		elementData.intensity = element[intensityName]
		elementData.rotation = element[additionalRotationName]
		elementData.centerRotation = element[trackToCenterInfluenceName]
		elementData.width = element[scaleXName]
		elementData.height = element[scaleYName]
		elementData.xOffset = element[offsetXName]
		elementData.yOffset = element[offsetYName]
		elementData.color = getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2].default_value
		
		return elementData
	FromElement = staticmethod(fromElement)


	
	
# interface
##################################

class LensFlaresPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Lens Flares"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout	

		updateActiveFlareName()
		updateActiveElementName()
		
		flares = getAllFlares()
		activeFlare = getActiveFlare()
		if len(flares) == 0: layout.label("no flares in this scene", icon = "INFO")
		else:
			col = layout.column(align = True)
			for flare in flares:
				row = col.row(align = True)
				row.scale_y = 1.35
				if activeFlare == flare: 
					selectFlare = row.operator("lens_flares.select_flare", text = flare[flareNamePropertyName], icon = "PINNED")
				else: selectFlare = row.operator("lens_flares.select_flare", text = flare[flareNamePropertyName])
				selectFlare.flareName = flare.name
				
				saveFlare = row.operator("lens_flares.save_lens_flare", text = "", icon = "SAVE_COPY")
				saveFlare.flareName = flare.name
				deleteFlare = row.operator("lens_flares.delete_lens_flare", text = "", icon = "X")
				deleteFlare.flareName = flare.name
				
		row = layout.row(align = True)
		row.operator("lens_flares.new_lens_flare", icon = 'NEW', text = "New")
		row.operator("lens_flares.load_lens_flare", icon = 'FILE_FOLDER', text = "Load")
				
class LensFlareSettingsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Lens Flares Settings"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return isFlareActive()
	
	def draw(self, context):
		layout = self.layout
		
		flare = getActiveFlare()
		if flare is None: return
		target = getTargetEmpty(flare)
		self.bl_label = "Settings: " + flare[flareNamePropertyName]
		
		row = layout.row(align = True)
		row.prop(flare, flareNamePropertyPath, text = "Name")
		duplicateFlare = row.operator("lens_flares.duplicate_lens_flare", text = "", icon = "NEW")
		duplicateFlare.flareName = flare.name
		
		layout.prop(target.constraints[0], 'target', text = "Target")
		layout.prop(flare, intensityPath, text = "Intensity")
				
		elements = getDataElementsFromFlare(flare)
		activeElement = getActiveElement()
		box = layout.box()
		if len(elements) == 0: box.label("no elements on this flare", icon = "INFO")
		else:
			col = box.column(align = True)
			for element in elements:
				row = col.row(align = True)
				row.scale_y = 1.35
				if element == activeElement: 
					selectElement = row.operator("lens_flares.select_flare_element", text = element[elementNamePropertyName], icon = "PINNED")
				else: selectElement = row.operator("lens_flares.select_flare_element", text = element[elementNamePropertyName])
				selectElement.elementName = element.name
				deleteElement = row.operator("lens_flares.delete_flare_element", text = "", icon = "X")
				deleteElement.elementName = element.name
		newElement = box.operator("lens_flares.new_flare_element", icon = 'PLUS')
		newElement.flareName = flare.name
				
class LensFlareElementSettingsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Lens Flares"
	bl_label = "Element Settings"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return isElementActive()
	
	def draw(self, context):
		layout = self.layout
		
		element = getActiveElement()
		if element is None: return
		plane = getPlaneFromElement(element)
		
		row = layout.row(align = True)
		row.prop(element, elementNamePropertyPath, text = "Name")
		duplicateElement = row.operator("lens_flares.duplicate_flare_element", text = "", icon = "NEW")
		duplicateElement.elementName = element.name
		
		col = layout.column(align = True)
		col.prop(element, elementPositionPath, text = "Position")
		row = col.row(align = True)
		row.prop(element, offsetXPath, text = "X Offset")
		row.prop(element, offsetYPath, text = "Y Offset")
		layout.prop(element, intensityPath, text = "Intensity")
		
		col = layout.column(align = True)
		col.prop(element, additionalRotationPath, text = "Rotation")
		col.prop(element, trackToCenterInfluencePath, text = "Center Influence")
		
		col = layout.column(align = True)
		col.prop(element, scaleXPath, text = "Width")
		col.prop(element, scaleYPath, text = "Height")
		
		layout.prop(getNodeWithNameInObject(plane, colorMultiplyNodeName).inputs[2], "default_value", text = "Color")
		
		
# operators
###################################
		
class NewLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.new_lens_flare"
	bl_label = "New Lens Flare"
	bl_description = "Create a new Lens Flare on active object."
	
	def execute(self, context):
		activeObject = getActive()
		if activeObject is not None:
			if not (isPartOfAnyFlareControler(activeObject) or isCameraObject(activeObject)):
				flareControler = newLensFlare(getActiveCamera(), activeObject)
				setActiveFlareName(flareControler.name)
		return{"FINISHED"}
		
class NewFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.new_flare_element"
	bl_label = "New Flare Element"
	bl_description = "Create a new Element in active Lens Flare."

	flareName = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")

	def execute(self, context):
		(element, flareElement) = newFlareElement(bpy.data.objects[self.flareName], getImage(self.filepath), getFileName(self.filepath))
		setActiveElementName(element.name)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.filepath = elementsFolder
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class SaveLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.save_lens_flare"
	bl_label = "Save Lens Flare"
	bl_description = "Save this Lens Flare."
	
	flareName = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	def execute(self, context):
		saveLensFlare(bpy.data.objects[self.flareName], self.filepath)
		return{"FINISHED"}
		
	def invoke(self, context, event):
		self.filepath = presetsFolder
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class LoadLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.load_lens_flare"
	bl_label = "Load Lens Flare"
	bl_description = "Load Lens Flare from file."
	
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	def execute(self, context):
		loadLensFlare(self.filepath)
		return{"FINISHED"}
		
	def invoke(self, context, event):
		self.filepath = presetsFolder
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class SelectFlare(bpy.types.Operator):
	bl_idname = "lens_flares.select_flare"
	bl_label = "Select Flare"
	bl_description = "Select this flare to see its elements."
	
	flareName = bpy.props.StringProperty()
	
	def execute(self, context):
		setActiveFlareName(self.flareName)
		onlySelect(bpy.data.objects.get(self.flareName))
		return{"FINISHED"}
		
class SelectFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.select_flare_element"
	bl_label = "Select Flare Element"
	bl_description = "Select this element to change its settings."
	
	elementName = bpy.props.StringProperty()
	
	def execute(self, context):
		setActiveElementName(self.elementName)
		onlySelect(bpy.data.objects.get(self.elementName))
		return{"FINISHED"}
		
class DeleteLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.delete_lens_flare"
	bl_label = "Delete Lens Flare"
	bl_description = "Delete this Lens Flare."
	
	flareName = bpy.props.StringProperty()
	
	def execute(self, context):
		selectionBefore = getSelectedObjects()
		deleteFlare(bpy.data.objects[self.flareName])
		setSelectedObjects(selectionBefore)
		return{"FINISHED"}
		
class DeleteFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.delete_flare_element"
	bl_label = "Delete Flare Element"
	bl_description = "Delete this Element."
	
	elementName = bpy.props.StringProperty()
	
	def execute(self, context):
		selectionBefore = getSelectedObjects()
		deleteFlareElement(bpy.data.objects[self.elementName])
		setSelectedObjects(selectionBefore)
		return{"FINISHED"}

class DuplicateFlareElement(bpy.types.Operator):
	bl_idname = "lens_flares.duplicate_flare_element"
	bl_label = "Duplicate Flare Element"
	bl_description = "Duplicate this Element."
	
	elementName = bpy.props.StringProperty()
	
	def execute(self, context):
		element = duplicateFlareElement(bpy.data.objects[self.elementName])
		setActiveElementName(element.name)
		return{"FINISHED"}
		
class DuplicateLensFlare(bpy.types.Operator):
	bl_idname = "lens_flares.duplicate_lens_flare"
	bl_label = "Duplicate Lens Flare"
	bl_description = "Duplicate this Lens Flare."
	
	flareName = bpy.props.StringProperty()
	
	def execute(self, context):
		duplicateLensFlare(bpy.data.objects[self.flareName])
		return{"FINISHED"}
		
		
		
# register
##################################

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()