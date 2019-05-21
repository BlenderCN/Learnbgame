# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          18-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import os
import bpy
import copy
# Framework libs
from extensions_framework import util as efutil

from ..outputs import sunflowLog

def mix(MasterDict, InputDict , TargetName):
    for keys in InputDict.keys():
        if keys not in MasterDict.keys():
            MasterDict[keys] = {}
        if InputDict[keys] != []:
            MasterDict[keys][TargetName] = InputDict[keys]


def tr_color_str(_color):
    colors = [ "%+0.4f" % channel for channel in _color ]
    return '  '.join(colors)

        
def make_path_real(path):
    xfac = efutil.filesystem_path(path)
    return os.path.abspath(xfac)


def file_exists(filepath):
    path = make_path_real(filepath)
    if os.path.exists(path):
        return True
    else:
        return False
    

def getObjectPos(obj, as_matrix=True):
    obj_mat = obj.matrix_world.copy()
    if not as_matrix :
        obj_mat.transpose()
        eye = obj_mat[3]
        dir = obj_mat[2]
        up = obj_mat[1]
        target = eye - dir        
        points = [ eye.to_tuple()[:3], target.to_tuple()[:3], up.to_tuple()[:3] ]        
        pos = [ "%+0.4f %+0.4f %+0.4f" % elm for elm in points ]
        return (pos)
    else:
        matrix_rows = [ "%+0.4f" % element for rows in obj_mat for element in rows ]
        return (matrix_rows)
            
def dict_merge(*dictionaries):
    cp = {}
    for dic in dictionaries:
        cp.update(copy.deepcopy(dic))
    return cp

def dmix(MasterDict, InputDict , TargetName):
    if TargetName not in MasterDict.keys():
        MasterDict[TargetName] = {}        
    for keys in InputDict.keys():
        MasterDict[TargetName][keys] = InputDict[keys]


def is_dupli_child(object_name):
    if not bpy.context.scene.render.use_instances:
        return False
    if object_name in [ obj.name for obj in  bpy.context.scene.objects]:
        obj = bpy.context.scene.objects[object_name]
        # sunflowLog(" %s parent %s " % (object_name, obj.parent.name))    
        if  hasattr(obj , 'dupli_type') and obj.dupli_type in ['GROUP' , 'FRAMES'] :
            return True
        if  hasattr(obj.parent , 'dupli_type'):
            return obj.parent.dupli_type not in ['NONE']
        else:
            return False
    else:
        return False
    


# def is_dupli_child(object_name):
#     if not bpy.context.scene.render.use_instances:
#         return False
#     if object_name in [ obj.name for obj in  bpy.context.scene.objects]:
#         obj = bpy.context.scene.objects[object_name]
#         # sunflowLog(" %s parent %s " % (object_name, obj.parent.name))    
#         if  hasattr(obj , 'dupli_type') and obj.dupli_type in ['GROUP' , 'FRAMES'] :
#             return True
#         if  hasattr(obj.parent , 'dupli_type'):
#             return obj.parent.dupli_type not in ['NONE']
#         else:
#             return False
#     else:
#         return False


def resolution(scene):
    '''
    scene        bpy.types.scene
    Calculate the output render resolution
    Returns        tuple(2) (floats)
    '''
    xr = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
    yr = scene.render.resolution_y * scene.render.resolution_percentage / 100.0
    
    return int(xr), int(yr)


def get_instance_materials(ob):
    obmats = []
    # Grab materials attached to object instances ...
    if hasattr(ob, 'material_slots'):
        for ms in ob.material_slots:
            obmats.append(ms.material)
    # ... and to the object's mesh data
#     if hasattr(ob.data, 'materials'):
#         for m in ob.data.materials:
#             obmats.append(m)
    return obmats
