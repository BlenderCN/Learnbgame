

import bpy
from bpy.props import *

import mathutils
from mathutils import Vector,Matrix
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
            topVect = Vector((0,1,topZ)) @ mtx
            bottomVect = Vector((0,1,bottomZ)) @ mtx
        
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
        context.scene.collection.objects.link(obj)
        obj.select_set(True)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

# Add to the menu
def menu_func(self, context):
    self.layout.operator(AddHexCell.bl_idname, text="Hex Cell")

def register():
    bpy.utils.register_class(AddHexCell)

    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddHexCell)

    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()