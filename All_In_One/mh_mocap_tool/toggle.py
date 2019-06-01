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
from bpy.props import *

#
#   class VIEW3D_OT_McpToggleLimitButton(bpy.types.Operator):
#

def toggleConstraints(rig, types, mute):
    for pb in rig.pose.bones:
        for cns in pb.constraints:
            if cns.type in types:
                cns.mute = mute
    bpy.ops.object.mode_set(mode='OBJECT')                
    bpy.ops.object.mode_set(mode='POSE')                
    return                


class VIEW3D_OT_McpToggleLimitButton(bpy.types.Operator):
    bl_idname = "mcp.toggle_limits"
    bl_label = "Limit"
    bl_options = {'UNDO'}
    mute = BoolProperty()

    def execute(self, context):
        ob = context.object
        toggleConstraints(ob, 
            ['LIMIT_LOCATION', 'LIMIT_ROTATION', 'LIMIT_DISTANCE', 'LIMIT_SCALE'],
            self.mute)
        ob.McpLimitsOn = not self.mute
        return{'FINISHED'}    

class VIEW3D_OT_McpToggleChildofButton(bpy.types.Operator):
    bl_idname = "mcp.toggle_childofs"
    bl_label = "Childofs"
    bl_options = {'UNDO'}
    mute = BoolProperty()

    def execute(self, context):
        ob = context.object
        toggleConstraints(ob, ['CHILD_OF'], self.mute)
        ob.McpChildOfsOn = not self.mute
        return{'FINISHED'}    
