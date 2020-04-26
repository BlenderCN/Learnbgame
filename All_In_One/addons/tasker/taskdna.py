# Copyright 2015 Bassam Kurdali / urchn.org
# Modified from custom nodes template
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

""" Define the data structures of tasks """

import bpy


class Props():
    """ Just a skeleton and some helper methods """
    description = ("", bpy.props.StringProperty)
    owner = ("", bpy.props.StringProperty)
    reference = ("", bpy.props.StringProperty)
    type = ("", bpy.props.StringProperty)
    time = (0.0, bpy.props.FloatProperty)
    completed = (False, bpy.props.BoolProperty)

    @classmethod
    def get_list(cls):
        return sorted([
            itm for itm in cls.__dict__
            if hasattr(getattr(cls, itm), '__getitem__')
            and not itm.startswith('__')])

    @classmethod
    def get_bpy_type(cls, prop):
        """ return the blender property type of prop """
        return getattr(cls, prop)[1]

    @classmethod
    def get_type(cls, prop):
        """ return the python type of prop """
        return type(getattr(cls, prop)[0])

    @classmethod
    def get_bpy_types(cls):
        """ list of properties and their types """
        return sorted([
            (itm, getattr(cls, itm)[1])
            for itm in cls.__dict__
            if hasattr(getattr(cls, itm), '__getitem__')
            and not itm.startswith('__')])

    @classmethod
    def get_py_types(cls):
        """ list of python properties """
        return sorted([
            (itm, getattr(cls, itm)[0])
            for itm in cls.__dict__
            if hasattr(getattr(cls, itm), '__getitem__')
            and not itm.startswith('__')])
        
    
