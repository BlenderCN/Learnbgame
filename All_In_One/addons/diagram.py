# BEGIN GPL LICENSE BLOCK #####
#
# Copyright (C) 2016  Philip Eriksson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Diagram",
    "description": "Generates animated diagram from data table in file.",
    "author": "Philip Eriksson",
    "version": (0, 1, 20),
    "blender": (2, 76, 0),
    "warning": "This add-on is in alpha development",
    "location": "File > Import > Table data (.csv)",
    "tracker_url": "https://github.com/Lominean/Blender-Diagram/labels/bug",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class generate_graph(bpy.types.Operator):
    bl_idname = "import.diagram"
    bl_label = "Import CSV"
    bl_options = {'UNDO'}
    bl_description = "Add animated graph"
    
    filename_ext = ".csv"
    filter_glob = StringProperty(default="*.csv", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.operator("object.select_all")

    @classmethod
    def poll(cls, context):
        return context.scene != None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import(self, context):
    import os
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".csv"
    self.layout.operator(generate_graph.bl_idname, text="Table data (.csv)").filepath = default_path

        
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()