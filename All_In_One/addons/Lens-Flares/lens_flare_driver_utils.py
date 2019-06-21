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

def newDriver(object, dataPath, index = -1, type = "SCRIPTED"):
	fcurve = object.driver_add(dataPath, index)
	driver = fcurve.driver
	driver.type = type
	return driver
def createCopyValueDriver(fromObject, fromPath, toObject, toPath):
	driver = newDriver(toObject, toPath)
	linkFloatPropertyToDriver(driver, "var", fromObject, fromPath)
	driver.expression = "var"
def setWorldTransformAsProperty(object, propertyName, transformChannel):
	setCustomProperty(object, propertyName)
	driver = newDriver(object, getDataPath(propertyName), type = "SUM")
	linkTransformChannelToDriver(driver, "var", object, transformChannel)
def setTransformDifferenceAsProperty(target, relative, propertyName, transformChannel, normalized = False):
	setCustomProperty(target, propertyName)
	driver = newDriver(target, getDataPath(propertyName))
	linkTransformChannelToDriver(driver, "a", relative, transformChannel)
	linkTransformChannelToDriver(driver, "b", target, transformChannel)
	if normalized:
		linkDistanceToDriver(driver, "dis", target, relative)
		driver.expression = "(a-b)/(dis+0.0000001)"
	else: driver.expression = "a-b"

def linkFloatPropertyToDriver(driver, name, id, dataPath, idType = "OBJECT"):
	driverVariable = driver.variables.new()
	driverVariable.name = name
	driverVariable.type = "SINGLE_PROP"
	driverVariable.targets[0].id_type = idType
	driverVariable.targets[0].id = id
	driverVariable.targets[0].data_path = dataPath
def linkTransformChannelToDriver(driver, name, id, transformType, space = "WORLD_SPACE"):
	driverVariable = driver.variables.new()
	driverVariable.name = name
	driverVariable.type = "TRANSFORMS"
	driverVariable.targets[0].id = id
	driverVariable.targets[0].transform_type = transformType
	driverVariable.targets[0].transform_space = space
def linkDistanceToDriver(driver, name, object1, object2):
	driverVariable = driver.variables.new()
	driverVariable.name = name
	driverVariable.type = "LOC_DIFF"
	driverVariable.targets[0].id = object1
	driverVariable.targets[1].id = object2