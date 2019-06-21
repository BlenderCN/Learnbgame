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

## Build the File Loading Operator, and allows for File Selection
# By Matti 'Menithal' Lahtinen

import bpy

import json
import os

from hifi_tools.world.scene import *


def load_file(operator, context, filepath="",
              uv_sphere= False,
              join_children=True, 
              merge_distance = 0.01, 
              delete_interior_faces = True,
              use_boolean_operation = 'NONE'):
                  
    json_data = open(filepath).read()
    data = json.loads(json_data)
    
    scene = HifiScene(data, uv_sphere, join_children, merge_distance, delete_interior_faces, use_boolean_operation)
    return {"FINISHED"}

