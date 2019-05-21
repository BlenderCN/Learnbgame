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
# Created on                          14-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import math
import mathutils

from ..outputs import sunflowLog

def getPos(obj , as_matrix=True , grp=False):
    obj_mat = obj.matrix.copy()
    #----------------- this is to correct some wierdness in group dupli problem.
    if grp:  
        obj_mat = obj_mat * obj.matrix_original.inverted()
    matrix_rows = [ "%+0.4f" % element for rows in obj_mat for element in rows ]
    return (matrix_rows)
    
def InstanceExporter(scene , objname, turn_on_motion_blur, steps=0):
    if not turn_on_motion_blur:
        obj_parent = scene.objects[objname]
        obj_parent.dupli_list_create(scene)
        dupli_list = {}
        index = 0
        for obj in obj_parent.dupli_list :
            ins = {}
            pos = getPos(obj, as_matrix=True , grp=(obj_parent.dupli_type == 'GROUP')) 
            ins['iname'] = "%s.inst.%03d" % (obj_parent.name, index)
            ins['index'] = index  # obj.index
            ins['pname'] = obj.object.name
            ins['trans'] = [pos]
            dupli_list[ ins['iname'] ] = ins
            index += 1
        obj_parent.dupli_list_clear()
        return dupli_list
    else:
        obj_parent = scene.objects[objname]
        obj_parent.dupli_list_create(scene)
        num_dupli = len(obj_parent.dupli_list)
        dupli_list = {}
        index = 0
        for obj in obj_parent.dupli_list :
            ins = {}  
            ins['iname'] = "%s.inst.%03d" % (obj_parent.name, index)
            ins['index'] = index  # obj.index
            ins['pname'] = obj.object.name
            ins['trans'] = None
            dupli_list[ ins['iname'] ] = ins
            index += 1
        obj_parent.dupli_list_clear()
        
        current_frame , current_subframe = (scene.frame_current, scene.frame_subframe)
        mb_start = current_frame - math.ceil(steps / 2) + 1
        frame_steps = [ mb_start + n for n in range(0, steps) ]
        transform = [ [] for dummy_i in range(num_dupli)] 
        for sub_frame in frame_steps:
            scene.frame_set(sub_frame, current_subframe) 
            obj_parent.dupli_list_create(scene)
            for objindx in range(num_dupli) :
                xpos = getPos(obj_parent.dupli_list[objindx], as_matrix=True , grp=(obj_parent.dupli_type == 'GROUP'))
                transform[objindx].append(xpos)
            obj_parent.dupli_list_clear()
        scene.frame_set(current_frame, current_subframe)
        
        for dup in dupli_list.values():
            if obj_parent.dupli_type == 'FRAMES':
                dup['trans'] = transform[dup['index'] - obj_parent.dupli_frames_start ]
            else:
                dup['trans'] = transform[dup['index']]            
        return dupli_list
