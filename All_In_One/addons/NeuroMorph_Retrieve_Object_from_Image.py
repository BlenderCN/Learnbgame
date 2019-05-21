#    NeuroMorph_Image_Stack_Interactions.py (C) 2016,  Biagio Nigro, Anne Jorstad, Tom Boissonnet
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

bl_info = {  
    "name": "NeuroMorph Retrieve Object From Image",
    "author": "Biagio Nigro, Anne Jorstad, Tom Boissonnet",
    "version": (1, 3, 0),
    "blender": (2, 7, 6),
    "location": "View3D > Object Image Superposition",
    "description": "Retrieve object from point selection on image plane",  # "Superimposes image files over 3D objects interactively",
    "warning": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Learnbgame"
}  
  
import bpy
from bpy.props import *
from mathutils import Vector
import mathutils
import math
import os
import sys
import re
from os import listdir

import NeuroMorph_3D_Drawing as nmsn  # This module requires NeuroMorph_Stack_Notation loaded to run



# Define the panel
class SuperimposePanel(bpy.types.Panel):
    bl_label = "Retrieve Object From Image"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):

        self.layout.label("--Retrieve Object from Image--")

        split = self.layout.row().split(percentage=0.33)
        col1 = split.column()
        col1.operator("object.point_operator", text='Display Grid')
        col2 = split.column().row()
        col2.prop(context.scene , "x_grid") 
        col2.prop(context.scene , "y_grid") 
        col2.prop(context.scene , "z_grid")
        
        row = self.layout.row()
        row.operator("object.pickup_operator", text='Display Object at Selected Vertex')
        
        row = self.layout.row()
        row.operator("object.show_names", text='Show Names')
        row.operator("object.hide_names", text='Hide Names')



# def active_node_mat(mat):
#     # TODO, 2.4x has a pipeline section, for 2.5 we need to communicate
#     # which settings from node-materials are used
#     if mat is not None:
#         mat_node = mat.active_node_material
#         if mat_node:
#             return mat_node
#         else:
#             return mat
#     return None            



class PointOperator(bpy.types.Operator):
    """Display grid on selected image for object point selection"""
    bl_idname = "object.point_operator"
    bl_label = "Choose Point Operator"
    
    def execute(self, context):
                      
     if bpy.context.mode == 'OBJECT': 
      if bpy.context.active_object is not None:  
             
        if (bpy.context.active_object.name=='Image Z'): 
            mt = bpy.context.active_object
            zlattice=mt.location.z
            x_off=bpy.context.scene.x_side
            y_off=bpy.context.scene.y_side
            xg=bpy.context.scene.x_grid
            yg=bpy.context.scene.y_grid
        elif (bpy.context.active_object.name=='Image X'):
            mt = bpy.context.active_object
            zlattice=mt.location.x
            x_off=bpy.context.scene.z_side
            y_off=bpy.context.scene.y_side
            xg=bpy.context.scene.z_grid
            yg=bpy.context.scene.y_grid
        elif (bpy.context.active_object.name=='Image Y'): 
            mt = bpy.context.active_object
            zlattice=mt.location.y
            x_off=bpy.context.scene.x_side
            y_off=bpy.context.scene.z_side
            xg=bpy.context.scene.x_grid
            yg=bpy.context.scene.z_grid
        else :
            return {"FINISHED"}
 
        tmpActiveObject = bpy.context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        #delete previous grids
        all_obj = [item.name for item in bpy.data.objects]
        for object_name in all_obj:
          if object_name[0:4]=='Grid':
            delThisObj(bpy.data.objects[object_name])

        bpy.context.scene.objects.active = tmpActiveObject  
          
        if (bpy.context.active_object.name=='Image Z'): 
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(0.0+x_off/2,0.0+y_off/2, zlattice-0.0001))
        elif (bpy.context.active_object.name=='Image X'):
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(zlattice-0.0001,0.0+y_off/2, 0.0+x_off/2), rotation=(0,3.141592/2,0)) 
        elif (bpy.context.active_object.name=='Image Y'): 
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=xg, y_subdivisions=yg, location=(0.0+x_off/2, zlattice-0.0001, 0.0+y_off/2), rotation=(3.141592/2,0,0)) 
        
        grid = bpy.context.active_object
        grid.scale.x=x_off/2
        grid.scale.y=y_off/2
        grid.draw_type = 'WIRE'  # don't display opaque grey on the reverse side

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
          
     return {"FINISHED"}


class PickupOperator(bpy.types.Operator):
    """Display mesh objects at all selected grid vertices (will be visible in their respective layers)"""
    # this will only work if all objects are in the same layer
    bl_idname = "object.pickup_operator"
    bl_label = "Pick up object Operator"
    
    def execute(self, context):
     if bpy.context.mode == 'EDIT_MESH':   
       if bpy.context.active_object is not None:
         if bpy.context.active_object.name[0:4]=="Grid":
           bpy.ops.object.mode_set(mode = 'OBJECT') 
           grid=bpy.context.active_object 
           selected_idx = [i.index for i in grid.data.vertices if i.select]
           lidx=len(selected_idx)
           l=len(bpy.data.objects)

           if l>0 and lidx>0:  # loop over all selected vertices
             mindist=float('inf')

             for myob in bpy.data.objects:
               picked_obj_name=""   
               if myob.type=='MESH':
                  if myob.name[0:4]!='Grid':
                    for v_index in selected_idx:
                      #get local coordinate, turn into word coordinate
                      vert_coordinate = grid.data.vertices[v_index].co  
                      vert_coordinate = grid.matrix_world * vert_coordinate

                      dist=-1.0
                      if pointInBox(vert_coordinate, myob)==True:
                        dist=findMinDist(vert_coordinate, myob)
                        if dist==0:
                           mindist=dist
                           picked_obj_name=myob.name
                           showObj(picked_obj_name)
                        elif dist>0 and pointInsideMesh(vert_coordinate, myob)==True:
                           mindist=dist
                           picked_obj_name=myob.name
                           showObj(picked_obj_name)

           all_obj = [item.name for item in bpy.data.objects]
           for object_name in all_obj:
             bpy.data.objects[object_name].select = False  
             if object_name[0:4]=='Grid':
                delThisObj(bpy.data.objects[object_name])
             
     return {"FINISHED"}


class ShowNameButton(bpy.types.Operator):
    """Display names of selected objects in the scene"""
    bl_idname = "object.show_names"
    bl_label = "Show Object names"

    def execute(self, context):

        # If show_relationship_lines is not set to false, a blue line
        # from the location of the name object to the origin appears.
        # This line exists between every child object and parent object,
        # but most objects in scene have "location" of (0,0,0).
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].show_relationship_lines = False  # hide parent-child relationship line

        if bpy.context.mode == 'OBJECT': 
         if bpy.context.active_object is not None:      
          if (bpy.context.active_object.type=='MESH'):    
           
            mt = bpy.context.active_object
            child=mt.children
            center=centermass(mt)

            #add empty and make it child
            bpy.ops.object.add(type='EMPTY', location=center)
            emo = bpy.context.active_object
            emo.parent = mt
            #bpy.ops.object.constraint_add(type='CHILD_OF')  # for versions of Blender <= 2.66
            #emo.constraints['Child Of'].target = mt
            #bpy.ops.constraint.childof_set_inverse(constraint=emo.constraints['Child Of'].name, owner='OBJECT')
            emo.name=mt.name+" "
            emo.show_name=True
            emo.empty_draw_size = emo.empty_draw_size / 100

            mt.select=False
            emo.select=False
            stringtmp=""
           
            for obch in child:
               obch.select=True
               bpy.context.scene.objects.active = obch
               if (obch.type=='MESH'):
                  ind=obch.name.find("_")
                  if ind!=-1:
                    stringname=obch.name[0:ind]
                    if (stringname!=stringtmp):

                       center=centermass(obch)
                       bpy.ops.object.add(type='EMPTY', location=center)
                       em = bpy.context.active_object
                       em.parent = mt
                       #bpy.ops.object.constraint_add(type='CHILD_OF')  # for versions of Blender <= 2.66
                       #em.constraints['Child Of'].target = mt
                       #bpy.ops.constraint.childof_set_inverse(constraint=em.constraints['Child Of'].name, owner='OBJECT')
                       em.name=stringname+" "
                       em.show_name=True
                       em.empty_draw_size = emo.empty_draw_size / 100
                       obch.select=False
                       emo.select=False
                       stringtmp=stringname

        return {'FINISHED'}


class HideNameButton(bpy.types.Operator):
    """Hide names of selected objects in the scene"""
    bl_idname = "object.hide_names"
    bl_label = "Hide Object names"

    def execute(self, context):
        if bpy.context.mode == 'OBJECT': 
         if bpy.context.active_object is not None:  
          mt = bpy.context.active_object    
          if (mt.type=='MESH'):    
           
           child=mt.children
                      
           mt.select=False
                     
           for obch in child:
               if (obch.type=='EMPTY'): 
                 obch.select = True
                 bpy.context.scene.objects.active = obch
        
                 bpy.ops.object.delete() 
        return {'FINISHED'}


#calculate center of mass of a mesh 
def centermass(me):
  sum=mathutils.Vector((0,0,0))
  for v in me.data.vertices:
    sum =sum+ v.co
  center = (sum)/len(me.data.vertices)
  return center 

#control mesh visibility
def showObj(obname):
   if bpy.data.objects[obname].hide == True:
         bpy.data.objects[obname].hide = False
      

#check if a point falls within bounding box of a mesh
def pointInBox(point, obj):
    
    bound=obj.bound_box
    minx=float('inf')
    miny=float('inf')
    minz=float('inf')
    maxx=-1.0
    maxy=-1.0
    maxz=-1.0
    
    minx=min(bound[0][0], bound[1][0],bound[2][0],bound[3][0],bound[4][0],bound[5][0],bound[6][0],bound[6][0])
    miny=min(bound[0][1], bound[1][1],bound[2][1],bound[3][1],bound[4][1],bound[5][1],bound[6][1],bound[6][1])
    minz=min(bound[0][2], bound[1][2],bound[2][2],bound[3][2],bound[4][2],bound[5][2],bound[6][2],bound[6][2])
    
    maxx=max(bound[0][0], bound[1][0],bound[2][0],bound[3][0],bound[4][0],bound[5][0],bound[6][0],bound[6][0])
    maxy=max(bound[0][1], bound[1][1],bound[2][1],bound[3][1],bound[4][1],bound[5][1],bound[6][1],bound[6][1])
    maxz=max(bound[0][2], bound[1][2],bound[2][2],bound[3][2],bound[4][2],bound[5][2],bound[6][2],bound[6][2])
    
    if (point[0]>minx and point[0]<maxx and point[1]>miny and point[1]<maxy and point[2]>minz and point[2]<maxz):
       return True
    else: 
       return False
    
# calculate minimum distance among a point in space and mesh vertices    
def findMinDist(point, obj):
    idx = [i.index for i in obj.data.vertices]
    min_dist=float('inf') 
    for v_index in idx:
       vert_coordinate = obj.data.vertices[v_index].co  
       vert_coordinate = obj.matrix_world * vert_coordinate
       a=(point[0]-vert_coordinate[0])*(point[0]-vert_coordinate[0])
       b=(point[1]-vert_coordinate[1])*(point[1]-vert_coordinate[1])
       c=(point[2]-vert_coordinate[2])*(point[2]-vert_coordinate[2])
       dist=math.sqrt(a+b+c)
       if (dist<min_dist):
            min_dist=dist
    return min_dist


# check if point is surrounded by a mesh
def pointInsideMesh(point,ob):
    
    if "surf" in ob.name or "vol" in ob.name or "solid" in ob.name:  # don't display measurement objects
        return False

    # copy values of ob.layers
    layers_ob = []
    for l in range(len(ob.layers)):
        layers_ob.append(ob.layers[l])

    axes = [ mathutils.Vector((1,0,0)), mathutils.Vector((0,1,0)), mathutils.Vector((0,0,1)), mathutils.Vector((-1,0,0)), mathutils.Vector((0,-1,0)), mathutils.Vector((0,0,-1))  ]
    orig=point
    layers_all = [True for l in range(len(ob.layers))]
    ob.layers = layers_all  # temporarily assign ob to all layers, for ray_cast()

    this_visibility = ob.hide
    ob.hide = False
    bpy.context.scene.update()

    max_dist = 10000.0
    outside = False
    count = 0
    for axis in axes:  # send out rays, if cross this object in every direction, point is inside
        result,location,normal,index = ob.ray_cast(orig,orig+axis*max_dist)  # this will error if ob is in a different layer
        if index != -1:
            count = count+1

    ob.layers = layers_ob
    ob.hide = this_visibility

    bpy.context.scene.update()
    
    if count<6:
        return False
    else: 
        # turn on the layer(s) containing ob in the scene
        for l in range(len(bpy.context.scene.layers)):
            bpy.context.scene.layers[l] = bpy.context.scene.layers[l] or layers_ob[l]

        return  True
      

# delete object
def delThisObj(obj):
    bpy.data.objects[obj.name].select = True
    #bpy.ops.object.select_name(name=obj.name)
    bpy.context.scene.objects.active = obj
    bpy.ops.object.delete() 


def ShowBoundingBox(obname):
    bpy.data.objects[obname].show_bounds = True
    return





def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.x_grid = bpy.props.IntProperty \
          (
            name = "nx",
            description = "Number of grid points in x",
            default = 50
          )

    bpy.types.Scene.y_grid = bpy.props.IntProperty \
          (
            name = "ny",
            description = "Number of grid points in y",
            default = 50
          )

    bpy.types.Scene.z_grid = bpy.props.IntProperty \
          (
            name = "nz",
            description = "Number of grid points in z",
            default = 50
          )

def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.x_grid
    del bpy.types.Scene.y_grid
    del bpy.types.Scene.z_grid

if __name__ == "__main__":
    register()
    