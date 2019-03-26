# #################################################################
#  Copyright (C) 2010 by Conquera Team
#  Part of the Conquera Project
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
# #################################################################


bl_info = {
    "name": "Hex Cell",
    "blender": (2, 5, 7),
    "location": "View3D > Add > Mesh ",
    "description": "Adds a hex cell",
    "category": "Add Mesh"}

import bpy
from bpy.props import *

import mathutils
from mathutils import *
from math import cos, sin, pi, radians


class AddHexCell(bpy.types.Operator):
    '''Add a torus mesh'''
    bl_idname = "mesh.add_hex_cell"
    bl_label = "Add Hex Cell"
    bl_options = {'REGISTER', 'UNDO'}


    def Body(self, bottomZ = -1, topZ = 0):
        faces = []
        verts = []
        
   
        for i in range(0,6):
            mtx = Matrix.Rotation( radians(i  * 60), 3, 'Z' )
            topVect = Vector((0,1,topZ)) * mtx
            bottomVect = Vector((0,1,bottomZ)) * mtx
        
            verts.append(topVect)
            verts.append(bottomVect)

        for i in range(1,6):
            faces.append([i*2, (i-1)*2, (i-1)*2+1, i*2+1])
     
        faces.append([0, 10, 11, 1])
 
        return  faces, verts

    def execute(self, context):

        faces, verts = self.Body()

        mesh = bpy.data.meshes.new("HexCell")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        bpy.ops.object.select_all(action='DESELECT')

        obj = bpy.data.objects.new("HexCell", mesh)
        context.scene.objects.link(obj)
        obj.select = True

        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

# Add to the menu
def menu_func(self, context):
    self.layout.operator(AddHexCell.bl_idname, text="Hex Cell")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()