# -*- coding: utf-8 -*-
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

bl_info = {
    "name": "Rename Objects",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 9),
    "location": "Bring up the Operator Search menu and type 'Rename Objects' ",
    "description": "Rename Objects by manually invoking the operator",
    "warning": "",
    "category": "Learnbgame"
}

"""Rename Objects quickly using an Operator"""

import bpy
from bpy.props import StringProperty

class RenameObjects(bpy.types.Operator):
    bl_idname = 'object.renames'
    bl_label = "Rename Objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def draw(self, context):
        layout = self.layout

        split = layout.split(percentage=0.5, align=True)
        col1 = split.column()
        col2 = split.column()
        col1.label("Name")
        col2.label("Show Name?")

        col1.prop(context.active_object, 'name', text='')
        col2.prop(context.active_object, 'show_name', text='')

        for object in filter(lambda obj: obj.name != context.active_object.name, context.selected_objects):
            col1.prop(object, 'name', text='')
            col2.prop(object, 'show_name', text='')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RenameObjects)

def unregister():
    bpy.utils.unregister_class(RenameObjects)

if __name__ == '__main__':
    register()
