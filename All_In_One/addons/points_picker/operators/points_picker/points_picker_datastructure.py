# Copyright (C) 2018 Christopher Gearhart
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
from bpy.types import Object
from mathutils import Vector

# Addon imports
# NONE!


class D3Point(object):
    ''' Point object '''

    def __init__(self, location:Vector, surface_normal:Vector, view_direction:Vector, label:str="", source_object:Object=None):
        self.label = label
        self.location = location
        self.surface_normal = surface_normal
        self.view_direction = view_direction
        self.source_object = source_object

    def __str__(self):
        return "<D3Point (%0.4f, %0.4f, %0.4f)>" % (self.location.x, self.location.y, self.location.z)

    def __repr__(self):
        return self.__str__()
