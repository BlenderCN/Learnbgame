# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
import bpy
from mathutils import Vector, Euler

# Addon imports
from .common import confirmIter
from .general import *


def storeTransformData(cm, obj, offsetBy=None):
    """ store transform data from obj into cm.modelLoc/Rot/Scale """
    if obj:
        loc = obj.location
        if offsetBy is not None:
            loc += Vector(offsetBy)
        cm.modelLoc = listToStr(loc.to_tuple())
        # cm.modelLoc = listToStr(obj.matrix_world.to_translation().to_tuple())
        lastMode = obj.rotation_mode
        obj.rotation_mode = "XYZ"
        cm.modelRot = listToStr(tuple(obj.rotation_euler))
        cm.modelScale = listToStr(obj.scale.to_tuple())
        obj.rotation_mode = lastMode
    elif obj is None:
        cm.modelLoc = "0,0,0"
        cm.modelRot = "0,0,0"
        cm.modelScale = "1,1,1"


def getTransformData(cm):
    """ return transform data from cm.modelLoc/Rot/Scale """
    l = strToTuple(cm.modelLoc, float)
    r = strToTuple(cm.modelRot, float)
    s = strToTuple(cm.modelScale, float)
    return l, r, s


def clearTransformData(cm):
    cm.modelLoc = "0,0,0"
    cm.modelRot = "0,0,0"
    cm.modelScale = "1,1,1"


def applyTransformData(cm, objs):
    """ apply transform data from cm.modelLoc/Rot/Scale to objects in passed iterable """
    objs = confirmIter(objs)
    # apply matrix to objs
    for obj in objs:
        # LOCATION
        l, r, s = getTransformData(cm)
        obj.location = obj.location + Vector(l)
        # ROTATION
        lastMode = obj.rotation_mode
        obj.rotation_mode = "XYZ"
        obj.rotation_euler.rotate(Euler(r))
        obj.rotation_mode = lastMode
        # SCALE
        osx, osy, osz = obj.scale
        obj.scale = vec_mult(obj.scale, s)
