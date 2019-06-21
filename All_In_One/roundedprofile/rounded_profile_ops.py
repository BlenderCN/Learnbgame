# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

'''
Created on 13 mar 2016
@author: Komi
'''

import bpy
from roundedprofile.mesh_updater import Updater

class RoundedProfileRemoveCorner(bpy.types.Operator):
    bl_idname = "mesh.rounded_profile_remove_corner"
    bl_label = "Remove"
    bl_options = {'REGISTER', 'UNDO'}
    cornerId = bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            Updater.removeCornerFromRoundedProfile(self, context, self.cornerId)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "RoundedProfile:remove corner works only in Object mode")
            return {'CANCELLED'}

class RoundedProfileAddCorner(bpy.types.Operator):
    bl_idname = "mesh.rounded_profile_add_corner"
    bl_label = "Add"
    bl_options = {'REGISTER', 'UNDO'}
    cornerId = bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            Updater.addCornerToRoundedProfile(self, context, self.cornerId)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "RoundedProfile:add corner works only in Object mode")
            return {'CANCELLED'}

class RoundedProfileResetCounters(bpy.types.Operator):
    bl_idname = "mesh.rounded_profile_reset_counters"
    bl_label = "Reset Counters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            Updater.resetCounts(self)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "RoundedProfile:reset counter works only in Object mode")
            return {'CANCELLED'}
