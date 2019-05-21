# Rig Description Structure
# Copyright (C) 2015  Bassam Kurdali
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

class Foot():
    """
    Simple foot structure:
        name (str) is the name of the foot bone
        tracks list_of_strings is the number of 'children' of the foot
        deps is a list of feet that the foot depends on
        up string in (X,Y,Z,-X,-Y,-Z)
        forward string in (X,Y,Z,-X,-Y,-Z)
    """

    def __init__(self, name, tracks, deps, up, forward):
        self.name = name
        self.tracks = tracks
        self.deps = deps
        self.up = up
        self.forward = forward
        self.steps = []
        

class ParameterEffect():
    """
    Structure that describes how a parameter effects a bone:
        bone (str) name of bone that is effected
        mutiplier (boolean) if true multiply the value, otherwise add
        transform (str) in transformation type (location, rotation_*, scale)
        'w': (boolean) do we affect this axis
        'w_mul': (float) multiplier for effect
        'x': (boolean)
        'x_mul': (float)        
        'y': (boolean)
        'y_mul': (float)
        'z': (boolean)
        'z_mul': (float)    
    """

    def __init__(
            self, bone, multiplier, w, w_mul, x, x_mul, y, y_mul, z, z_mul):
        self.bone = bone
        self.multiplier = multiplier
        self.w = w
        self.w_mul = w_mul
        self.x = x
        self.x_mul = x_mul
        self.y = y
        self.y_mul = y_mul
        self.z = z
        self.z_mul = z_mul


class Rig():
    """
    Simple rig descriptor:
    feet: a list of feet
    stride: (str) name of the stride bone or None
    parent: (str) name of the parent bone or None
    properties: (str) name of property holder bone for params or None
    params: (dict) keys are names of properties, values are lists of 
            parameter effects
    """

    def __init__(
            self, rig, feet, params, properties=None, stride=None, parent=None):
        self.rig = rig
        self.feet = feet
        self.stride = stride
        self.parent = parent
        self.properties = properties
        self.params = params
       
        
