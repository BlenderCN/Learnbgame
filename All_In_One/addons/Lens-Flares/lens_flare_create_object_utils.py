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

def newEmpty(name = "Empty", location = [0, 0, 0], hide = False, type = "PLAIN_AXES"):
	bpy.ops.object.empty_add(location = location, type = type)
	empty = bpy.context.object
	empty.name = getPossibleName(name)
	if hide:
		bpy.ops.object.hide_view_set(unselected = False)
	return empty
	
def newText(name = "Text", location = [0, 0, 0], text = "text"):
	bpy.ops.object.text_add(location = location)
	textObject = bpy.context.object
	textObject.name = getPossibleName(name)
	textObject.data.body = text
	return textObject
	
def newPlane(name = "Plane", location = [0, 0, 0], size = 1):
	bpy.ops.mesh.primitive_plane_add(location = location)
	plane = bpy.context.object
	plane.name = getPossibleName(name)
	plane.scale = [size, size, size]
	bpy.ops.object.transform_apply(scale = True)
	return plane
	
def newCamera(name = "Camera", location = [0, 0, 0]):
	bpy.ops.object.camera_add(location = location)
	camera = bpy.context.object
	camera.name = getPossibleName(name)
	return camera