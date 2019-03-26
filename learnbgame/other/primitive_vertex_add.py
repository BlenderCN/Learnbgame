##############################################################################
# Copyright © 2013 Richard Wilks #
# Started November 1st #
# Last updated November 3rd #
# #
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or #
# (at your option) any later version. #
# #
# This program is distributed in the hope that it will be useful, #
# but WITHOUT ANY WARRANTY; without even the implied warranty of #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the #
# GNU General Public License for more details. #
# #
# A copy of the GPLv3 license is available at #
# https://www.gnu.org/licenses/gpl-3.0.html. #
##############################################################################

bl_info = {
    "name": "Add Vertex",
    "author": "Richard Wilks",
    "version": (0, 3, 1),
    "blender": (2, 69, 1),
    "location": "View3D > Add > Mesh",
    "description": "Adds an object with a single vertex.",
    "wiki_url": "https://github.com/RichardW3D/AddOnis/wiki/primitive_vertex_add",
    "warning": "",
    "category": "Object"}

import bpy

class primitive_vertex_add(bpy.types.Operator):
    """Add a vertex"""
    bl_idname = "mesh.primitive_vertex_add"
    bl_label = "Vertex"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        mesh = bpy.data.meshes.new("Vertex")
        mesh.vertices.add(1)
        
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=None)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(primitive_vertex_add.bl_idname, icon="PLUGIN")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
register()