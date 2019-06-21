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

# <pep8 compliant>

import bpy
import os
from .sculpty import update_from_image


class MeshUpdateFromImage(bpy.types.Operator):
    bl_idname = "object.update_from_sculpt_map"
    bl_label = "Update from Sculpt Map"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(
        name="Sculpt Map",
        description="Sculpt Map to update mesh locations from.",
        maxlen=1024,
        default="",
        subtype='FILE_PATH')

    @classmethod
    def poll(cls, context):
        return context.active_object != None and \
            context.active_object.type == 'MESH'

    def execute(self, context):
        if context.active_object.type != 'MESH':
            return {'CANCELLED'}
        if not os.path.exists(self.filepath):
            return {'CANCELLED'}
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.editmode_toggle()
        img = bpy.data.images.load(self.filepath)
        update_from_image(context.active_object, img)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
