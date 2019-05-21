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
from lens_flare_driver_utils import *

def setTrackTo(child, trackTo):
	deselectAll()
	child.select = True
	setActive(trackTo)
	bpy.ops.object.track_set(type = "TRACKTO")   

def setParent(child, parent):
	child.parent = parent
	
def setParentWithoutInverse(child, parent):
	hide = (child.hide, parent.hide)
	child.hide = parent.hide = False
	deselectAll()
	child.select = True
	setActive(parent)
	bpy.ops.object.parent_no_inverse_set()
	(child.hide, parent.hide) = hide

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
		
def appendObjectReference(object, target):
	constraint = object.constraints.new(type = "CHILD_OF")
	constraint.influence = 0
	constraint.target = target
	constraint.show_expanded = False
	
def getObjectReferences(object):
	references = []
	for constraint in object.constraints:
		if constraint.type == "CHILD_OF":
			target = constraint.target
			if target is not None: references.append(target)
	return references
	
def cleanReferenceList(object):
	for constraint in object.constraints:
		if constraint.type == "CHILD_OF":
			if constraint.target is None: object.constraints.remove(constraint)
		
def getObjectReference(object, name):
	if isObjectReferenceSet(object, name):
		return object.constraints[name].target
	return None

def removeObjectReference(object, name):
	if name in object.constraints:
		object.constraints.remove(object.constraints[name])
	
def newLinkedLimitLocationConstraint(object):
	constraint = object.constraints.new(type = "LIMIT_LOCATION")
	setUseMinMaxToTrue(constraint)
	constraintPath = getConstraintPath(constraint)
	createCopyValueDriver(object, constraintPath + ".min_x", object, constraintPath + ".max_x")
	createCopyValueDriver(object, constraintPath + ".min_y", object, constraintPath + ".max_y")
	createCopyValueDriver(object, constraintPath + ".min_z", object, constraintPath + ".max_z")
	return constraint
	
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
		
def getConstraintPath(constraint):
	return 'constraints["' + constraint.name + '"]'