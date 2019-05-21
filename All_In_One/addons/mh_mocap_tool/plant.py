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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
from . import simplify
from .utils import MocapError

#
#    plantKeys(context)
#

def plantKeys(context):
    rig = context.object
    scn = context.scene
    if not rig.animation_data:
        raise MocapError("Cannot plant: no animation data")
    act = rig.animation_data.action
    if not act:
        raise MocapError("Cannot plant: no action")
    bone = rig.data.bones.active
    if not bone:
        raise MocapError("Cannot plant: no active bone")

    fromIndex = int(scn.McpPlantFrom)
    pb = rig.pose.bones[bone.name]
    locPath = 'pose.bones["%s"].location' % bone.name
    locPlants = [scn.McpPlantLocX, scn.McpPlantLocY, scn.McpPlantLocZ]
    if pb.rotation_mode == 'QUATERNION':
        rotPath = 'pose.bones["%s"].rotation_quaternion' % bone.name
        rotPlants = [False, scn.McpPlantRotX, scn.McpPlantRotY, scn.McpPlantRotZ]
        pbRot = pb.rotation_quaternion
    else:
        rotPath = 'pose.bones["%s"].rotation_euler' % bone.name
        rotPlants = [scn.McpPlantRotX, scn.McpPlantRotY, scn.McpPlantRotZ]
        pbRot = pb.rotation_euler
        
    targets = []
    for fcu in act.fcurves:
        if fcu.data_path == locPath:   
            if locPlants[fcu.array_index]:        
                targets.append(fcu)
            if fcu.array_index == fromIndex:
                fromFcu = fcu
        if fcu.data_path == rotPath:
            if rotPlants[fcu.array_index]:
                targets.append(fcu)

    plantTimes = []
    for kp in fromFcu.keyframe_points:
        if kp.select_control_point:
            plantTimes.append(int(kp.co[0]))
            
    for fcu in targets:
        block = []            
        t0 = -1000
        for kp in fcu.keyframe_points:
            t = int(kp.co[0])
            if t in plantTimes:
                if t == t0+1:
                    block.append(kp)
                else:
                    plantBlock(block)
                    block = [kp]
                t0 = t
            plantBlock(block)
            

def plantBlock(block):            
    if block == []:
        return
    sum = 0
    for kp in block:
        sum += kp.co[1]
    ave = sum/len(block)
    for kp in block:
        kp.co[1] = ave
    return
        

########################################################################
#
#   class VIEW3D_OT_McpPlantButton(bpy.types.Operator):
#

class VIEW3D_OT_McpPlantButton(bpy.types.Operator):
    bl_idname = "mcp.plant"
    bl_label = "Plant"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            plantKeys(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Keys planted")
        return{'FINISHED'}    

