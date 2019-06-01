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

import bpy

from roundedprofile.mesh_updater import Updater


class AddRoundedProfile(bpy.types.Operator):
    """Add rounded profile"""  # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.rounded_profile_add"  # unique identifier for buttons and menu items to reference.
    bl_label = "Add rounded profile"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            Updater.createRoundedProfile(self, context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "RoundedProfile: works only in Object mode")
            return {'CANCELLED'}

    def draw (self, context):
        layout = self.layout
        row = layout.row()
        row.label('Edit Rounded Profile Parameters in:')
        row = layout.row()
        row.label('Tools > Addons > Rounded Profile panel')
        

    ##### POLL #####
    @classmethod
    def poll(cls, context):
        # return bpy.context.mode == "OBJECT"
        return True
    
