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
    "name": "Connection Point",
    "blender": (2, 5, 7),
    "location": "View3D > Add > Mesh ",
    "description": "Adds a connection point",
    "category": "Add Mesh"}

import bpy
from bpy.props import *

import mathutils
from mathutils import *
from math import cos, sin, pi, radians


class AddConnectionPoint(bpy.types.Operator):
    '''Add a torus mesh'''
    bl_idname = "mesh.add_connection_point"
    bl_label = "Add Connection Point"
    bl_options = {'REGISTER', 'UNDO'}

    def CreateCircleMesh(self, verts, edges , size, axis):
        if not axis in ['x', 'y', 'z']:
            raise Exception("Axis '%s' is not valid. Valid values are 'x', 'y' and 'z'" % axis)
        
        if  'x' == axis:
            rotMat = Matrix.Rotation( radians(90), 4, 'Z')
        elif 'z' == axis:
            rotMat = Matrix.Rotation(radians(-90), 4, 'X')
        elif 'y' == axis:
            rotMat = Matrix.Rotation( radians(-90), 4, 'Y')
        
        sCnt = 20
        vCnt = len(verts)
        for i in range(0,sCnt):
            mtx = Matrix.Rotation( radians(i  * 360/sCnt), 3, 'Y' )
            vect = Vector((size,0,0)) * mtx * rotMat
            verts.append(vect)
        for i in range(vCnt+1,vCnt+sCnt):
            edges.append([i, i-1])
        edges.append([len(verts)-1, vCnt])
        
        vCnt = len(verts)
        aSize = size/3
        aSize2 = size/8
        aSize3 =aSize2/2
        
        v = [Vector((0, aSize, 0))* rotMat, Vector((0,0,0))* rotMat, Vector((aSize3, aSize-aSize2, aSize3))* rotMat, Vector((-aSize3, aSize-aSize2, aSize3))* rotMat, Vector((aSize3, aSize-aSize2, -aSize3))* rotMat, Vector((-aSize3, aSize-aSize2, -aSize3))* rotMat]
        verts.extend(v)
        edges.extend([[vCnt, vCnt+i] for i in range(1,len(v))])
        

        #axis name
        vCnt = len(verts)
        if 'x' == axis:
            v = [Vector((aSize3 +aSize2/4, aSize3+aSize2,0))* rotMat, Vector((aSize3*2 +aSize2/4, aSize3*2+aSize2,0))* rotMat, Vector((aSize3*2 +aSize2/4, aSize3+aSize2,0))* rotMat, Vector((aSize3 +aSize2/4, aSize3*2+aSize2,0))* rotMat]
            e = [[vCnt, vCnt+1], [vCnt+2, vCnt+3]]
        elif 'y' == axis:
            v = [Vector((aSize3 +aSize2/4, aSize3 + aSize3/2 +aSize2,0))* rotMat, Vector((aSize3 + aSize3/2 +aSize2/4, aSize3+aSize2,0))* rotMat, Vector((aSize3*2 +aSize2/4, aSize3 + aSize3/2 +aSize2,0))* rotMat, Vector((aSize3 + aSize3/2 +aSize2/4, aSize3/2 +aSize2,0))* rotMat]
            e = [[vCnt, vCnt+1], [vCnt+1, vCnt+2], [vCnt+1, vCnt+3]]
        else:
            v = [Vector((aSize3 +aSize2/4, aSize3+aSize2,0))* rotMat, Vector((aSize3*2 +aSize2/4, aSize3*2+aSize2,0))* rotMat, Vector((aSize3*2 +aSize2/4, aSize3+aSize2,0))* rotMat, Vector((aSize3 +aSize2/4, aSize3*2+aSize2,0))* rotMat]
            e = [[vCnt, vCnt+2], [vCnt+2, vCnt+3], [vCnt+3, vCnt+1]]
        verts.extend(v)
        edges.extend(e)
    
    def GetSelectedBone(self, armature):
        for bone in armature.pose.bones.values():
            if(bone.select):
                print("FOUND ZASA")
                return bone
        return None
        
    def execute(self, context):

        verts = []
        edges = []
        for axis in ['x', 'y', 'z']:
            self.CreateCircleMesh(verts, edges, 0.2, axis)

        mesh = bpy.data.meshes.new("cp_ConnectionPoint")
        mesh.from_pydata(verts, edges, [])
        mesh.update()
        
        bpy.ops.object.select_all(action='DESELECT')

        obj = bpy.data.objects.new("cp_ConnectionPoint", mesh)
        context.scene.objects.link(obj)
        
        
        selObj = context.scene.objects.active
        if selObj:
            obj.parent = selObj
            
            if "ARMATURE" == selObj.type:
                bone = self.GetSelectedBone(selObj)
                if bone:
                    obj.parent_bone=bone.name
                    obj.parent_type='BONE'
            
            obj.matrix_local = Matrix()
            selObj.select = False
        
        
        obj.select = True

        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

# Add to the menu
def menu_func(self, context):
    self.layout.operator(AddConnectionPoint.bl_idname, text="Connection Point")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
	

if __name__ == "__main__":
    register()
