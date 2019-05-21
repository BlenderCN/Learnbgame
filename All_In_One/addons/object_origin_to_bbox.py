# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and / or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#


bl_info = {
    "name": "Origin to BBox",
    "author": "marvin.k.breuer (MKB)",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "Editor: View 3D > Properties Panel [N]",
    "description": "set origin to bounding box (mesh/curve)",
    "warning": "",
    "wiki_url": "https://github.com/mkbreuer/ToolPlus",
    "tracker_url": "",
    "category": "Learnbgame",
    }



# IMPORT MODUL # 
import bpy
import bmesh
from bpy import *
from bpy.props import *

import mathutils, math, re
from mathutils.geometry import intersect_line_plane
from mathutils import Vector, Matrix
from math import radians
from math import pi

# https://blender.stackexchange.com/questions/33669/how-to-adapt-a-box-to-an-object-with-a-python-script
def build_box(self, context):
    width = self.scale.x
    height = self.scale.y
    depth = self.scale.z

                
    verts = [(+1.0 * width, +1.0 * height, -1.0 * depth),
             (+1.0 * width, -1.0 * height, -1.0 * depth),
             (-1.0 * width, -1.0 * height, -1.0 * depth),
             (-1.0 * width, +1.0 * height, -1.0 * depth),
             (+1.0 * width, +1.0 * height, +1.0 * depth),
             (+1.0 * width, -1.0 * height, +1.0 * depth),
             (-1.0 * width, -1.0 * height, +1.0 * depth),
             (-1.0 * width, +1.0 * height, +1.0 * depth),
             ]
    edges = []
    faces = [(0, 1, 2, 3),
             (4, 7, 6, 5),
             (0, 4, 5, 1),
             (1, 5, 6, 2),
             (2, 6, 7, 3),
             (4, 0, 3, 7),
            ]

    mesh = bpy.data.meshes.new(name="_bbox")
    mesh.from_pydata(verts, edges, faces)

    # add the mesh as an object into the scene with this utility module
    from bpy_extras import object_utils
    object_utils.object_data_add(context, mesh, operator=self)



def get_boxface(self, context):

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()

    me = bpy.context.object.data
   
    bm = bmesh.new()
    bm.from_mesh(me)      

    init=0


    # TOP +Z #
    if self.box_level == 'top':      
           
        if self.origin_location == 'center':     
           
            for v in bm.verts:
                 if init==0:
                     a=v.co.z
                    
                     init=1
              
                 elif v.co.z<a:
                     a=v.co.z
                     
            for v in bm.verts:
                 v.co.z-=a
                             
                 v.select_set(True)           
       
       
        if self.origin_location == 'plus_y':

            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.z-=c 
                             
                 v.select_set(True)              
            
      
        if self.origin_location == 'plus_y_plus_x':           
                  
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.z-=c
                 v.co.x-=a
                 
                 v.select_set(True)             


        if self.origin_location == 'plus_x':
       
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.x-=a
                 v.co.z-=c 
                             
                 v.select_set(True)                  
                            
            
        if self.origin_location == 'minus_y_plus_x':
         
            for v in bm.verts:
                 if init==0:            
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.z-=c
                 v.co.x-=a
                 
                 v.select_set(True)   
     

        if self.origin_location == 'minus_y':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.z-=c 
                             
                 v.select_set(True)   


        if self.origin_location == 'minus_y_minus_x':  
 
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.z-=c
                 v.co.x+=a
                 
                 v.select_set(True)                       
                 

        if self.origin_location == 'minus_x':
                          
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.x+=a
                 v.co.z-=c
                 
                 v.select_set(True)   


        if self.origin_location == 'plus_y_minus_x':
         
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.z-=c
                 v.co.x+=a
                 
                 v.select_set(True)              




    # MIDDLE #
    if self.box_level == 'middle':    
                   
        if self.origin_location == 'center':

            for v in bm.verts:                    
                
                 if init==0:
                     a=v.co.z
                     b=v.co.z
                 
                     init=1
              
                 elif v.co.z<a:
                     a=v.co.z
                     
                 elif v.co.z<b:
                     b=v.co.z

            for v in bm.verts:
                 v.co.z=a
                 v.co.z-=b
                             
                 v.select_set(True)
   
   
   
        if self.origin_location == 'plus_y':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.y
                  
                     init=1
               
                 elif v.co.y<a:
                     a=v.co.y
                     
            for v in bm.verts:
                 v.co.y-=a
                             
                 v.select_set(True)   
            
      
        if self.origin_location == 'plus_y_plus_x':           
           
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.x-=a 
                             
                 v.select_set(True)                             
    

        if self.origin_location == 'plus_x':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     init=1
                 elif v.co.x<a:
                     a=v.co.x
                     
            for v in bm.verts:
                 v.co.x-=a
                             
                 v.select_set(True)                 
                            
            
        if self.origin_location == 'minus_y_plus_x':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.x-=a 
                             
                 v.select_set(True)     
     

        if self.origin_location == 'minus_y':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.y
                     init=1
                 elif v.co.y<a:
                     a=v.co.y
                     
            for v in bm.verts:
                 v.co.y+=a
                             
                 v.select_set(True)   


        if self.origin_location == 'minus_y_minus_x':  
 
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.x+=a 
                             
                 v.select_set(True)   
                            
                 
        if self.origin_location == 'minus_x':
        
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     init=1
                 elif v.co.x<a:
                     a=v.co.x
                     
            for v in bm.verts:
                 v.co.x+=a
                             
                 v.select_set(True)                      


        if self.origin_location == 'plus_y_minus_x':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y

            for v in bm.verts:
                 v.co.y-=b
                 v.co.x+=a 
                             
                 v.select_set(True)                   






    # BOTTOM -Z #
    if self.box_level == 'bottom':       

        if self.origin_location == 'center':     
            
            for v in bm.verts:                    
                
                 if init==0:
                     a=v.co.z
                 
                     init=1
              
                 elif v.co.z<a:
                     a=v.co.z
                     
            for v in bm.verts:
                 v.co.z+=a
                             
                 v.select_set(True)
                
       
        if self.origin_location == 'plus_y':
            
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.z+=c 
                             
                 v.select_set(True)                  


        if self.origin_location == 'plus_y_plus_x':           
                  
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.z+=c
                 v.co.x-=a
                 
                 v.select_set(True)    
            

        if self.origin_location == 'plus_x':
       
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.x-=a
                 v.co.z+=c 
                             
                 v.select_set(True)               
                            
            
        if self.origin_location == 'minus_y_plus_x':
           
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z

            for v in bm.verts:
                 v.co.y+=b
                 v.co.z+=c
                 v.co.x-=a

                 v.select_set(True)        
            
     
        if self.origin_location == 'minus_y':
           
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.z+=c 
                             
                 v.select_set(True)   


        if self.origin_location == 'minus_y_minus_x':  
          
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y+=b
                 v.co.z+=c
                 v.co.x+=a

                 v.select_set(True)         
            
                 
        if self.origin_location == 'minus_x':
           
            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.x+=a
                 v.co.z+=c 
                             
                 v.select_set(True)                 


        if self.origin_location == 'plus_y_minus_x':

            for v in bm.verts:
                 if init==0:
                     a=v.co.x
                     b=v.co.y
                     c=v.co.z

                     init=1
                 
                 elif v.co.x < a:
                     a=v.co.x
                     
                 elif v.co.y < b:
                     b=v.co.y
                 
                 elif v.co.z < c:
                     c=v.co.z
                     
            for v in bm.verts:
                 v.co.y-=b
                 v.co.z+=c
                 v.co.x+=a
                 
                 v.select_set(True)                    

           
        
    bm.to_mesh(me)
    bm.free()
     

    bpy.ops.object.editmode_toggle()
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    return




# LISTS FOR SELECTED #
name_list = []
dummy_list = []


# OPERATOR #
class VIEW3D_OT_Bounding_Box_Origin_All(bpy.types.Operator):  
    """set origin to bounding box"""
    bl_idname = "tp_ops.bbox_origin_all"  
    bl_label = "Origin to BoundBox"  
    bl_options = {'REGISTER', 'UNDO'} 

    box_level : EnumProperty(
        items=[("top"     ,"Top +Z"      ,"constraint XY-Axis / plus Z-Axis"),
               ("middle"  ,"Middle XY"   ,"constraint XY-Axis / zero XY-Axis"),
               ("bottom"  ,"Bottom --Z"  ,"constraint XY-Axis / minus Z-Axis")],
               name = "Level",
               default = "middle")

    origin_location : EnumProperty( 
        items = [("center",         "center",  "center",    "BLANK1", 0),
                ("minus_y",         "--y",     "--y",       "BLANK1", 1), 
                ("minus_y_minus_x", "--y--x",  "--y--x",    "BLANK1", 2), 
                ("minus_x",         "--x",     "--x",       "BLANK1", 3), 
                ("plus_y_minus_x",  "+y--x",   "+y--x",     "BLANK1", 4), 
                ("plus_y",          "+y",      "+y",        "BLANK1", 5), 
                ("plus_y_plus_x",   "+y+x",    "+y+x",      "BLANK1", 6), 
                ("plus_x",          "+x",      "+x",        "BLANK1", 7),
                ("minus_y_plus_x",  "--x",     "--x",       "BLANK1", 8)],
                name = "Target",  
                default = "center",  
                description=" ")     

    scale : FloatVectorProperty(name="Scale", default=(1.0, 1.0, 1.0), subtype='TRANSLATION', description="scaling")
    layers : BoolVectorProperty(name="Layers", size=20, subtype='LAYER', options={'HIDDEN', 'SKIP_SAVE'})

    # generic transform props
    view_align : BoolProperty(name="Align to View", default=False)
    location : FloatVectorProperty(name="Location", subtype='TRANSLATION')
    rotation : FloatVectorProperty(name="Rotation", subtype='EULER')

    purge : BoolProperty(name="Purge unsed Mesh", default=True)

  
    # DRAW PROPS [F6] # 
    def draw(self, context):
        layout = self.layout
       
        col = layout.column(align=True)

        box = col.box().column(align=True)              
        box.separator() 
        
        row = box.row(align=True) 
        row.prop(self, 'box_level') 

        box.separator() 

        row = box.row(align=True) 
        row.prop(self, 'origin_location') 

        box.separator() 

        row = box.row(align=True) 
        row.prop(self, 'purge') 

        box.separator() 


    def execute(self, context):
       
        # store active   
        target = bpy.context.view_layer.objects.active 

        # attach all selected objects  
        selected = bpy.context.selected_objects

        # set 3d cursor
        bpy.ops.view3d.snap_cursor_to_selected()
          
        # store 3d cursor location in 3d view
        v3d = context.space_data
        if v3d.type == 'VIEW_3D':

            # get all selected objects  
            for obj in selected:
              
                # add all select to a name list: source selection
                name_list.append(obj.name)                                       
                
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')    

 
                # CREATE BOX DUMMY #                              
                # add defined mesh cube as bounding box to all selected objects
                build_box(self, context)  

                # rename bboxes
                bpy.context.object.name = obj.name + "_bbox_dummy"
                bpy.context.object.data.name = obj.name + "_bbox_dummy"
 
                # add bboxes as new object to name list: dummy_list
                new_object_name = obj.name + "_bbox_dummy"
                dummy_list.append(new_object_name) 
              
                # copy transforma data from active to dummy object 
                active = bpy.context.active_object      
                active.location = obj.location
                active.dimensions = obj.dimensions      
                active.rotation_euler = obj.rotation_euler

                # select dummy / deselect source
                bpy.data.objects[obj.name].select_set(state=False)                  
                bpy.data.objects[new_object_name].select_set(state=True)                                   
                
                # set bbox             
                get_boxface(self, context)

  
                # select dummy / deselect source
                bpy.data.objects[obj.name].select_set(state=False)                  
                bpy.data.objects[new_object_name].select_set(state=True)    
                
                bpy.ops.view3d.snap_cursor_to_active()

                # select source / deselect dummy
                bpy.data.objects[obj.name].select_set(state=True)                 
                bpy.data.objects[new_object_name].select_set(state=False)  

                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

          
                # DELETE DUMMY #   
                
                # deselect source / select dummy
                bpy.data.objects[obj.name].select_set(state=False)  
                bpy.data.objects[new_object_name].select_set(state=True) 
                
                bpy.ops.object.delete(use_global=True)


            # select all sources            
            for obj in selected:            
                bpy.data.objects[obj.name].select_set(state=True)        


        # reload active #     
        bpy.context.view_layer.objects.active = target
       
        del name_list[:]        
        del dummy_list[:]        


        for i in range(self.purge):  
            for dummy in bpy.data.meshes:
                if dummy.users == 0:
                    bpy.data.meshes.remove(dummy)

        return {'FINISHED'}




class VIEW3D_PT_Bounding_Box_Origin_All(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "Origin to BBox"
    bl_context = 'objectmode'     

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)

        box = col.box().column(align=True)              
        box.separator() 

        row = box.row(align=True)              
        row.label(text="Level +Z", icon= 'SHADING_BBOX')                     
      
        ob = context.object
        if ob: 
            row.prop(ob, "show_bounds", text="", icon='PIVOT_BOUNDBOX') 
 
        box.separator()    
       
        # TOP +Z#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="+y-x")
        props.origin_location='plus_y_minus_x'
        props.box_level='top'   
 
        props = row.operator('tp_ops.bbox_origin_all', text="+y")
        props.origin_location='plus_y'
        props.box_level='top'   

        props = row.operator('tp_ops.bbox_origin_all', text="+y+x")
        props.origin_location='plus_y_plus_x'
        props.box_level='top'   


        # MIDDLE +Z#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="-x")
        props.origin_location='minus_x'
        props.box_level='top'                        
            
        props = row.operator('tp_ops.bbox_origin_all', text="+z")
        props.origin_location='center'
        props.box_level='top'   

        props = row.operator('tp_ops.bbox_origin_all', text="+x")
        props.origin_location='plus_x'
        props.box_level='top'   

     
        # BOTTOM +Z#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="-y-x")
        props.origin_location='minus_y_minus_x'
        props.box_level='top'   

        props = row.operator('tp_ops.bbox_origin_all', text="-y")
        props.origin_location='minus_y'
        props.box_level='top'   

        props = row.operator('tp_ops.bbox_origin_all', text="-y+x")
        props.origin_location='minus_y_plus_x'            
        props.box_level='top'   


        box.separator() 

        row = box.row(align=True)              
        row.label(text="Level XY", icon= 'SHADING_BBOX')     

        box.separator() 

        # TOP +XY#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="+y-x")
        props.origin_location='plus_y_minus_x'
        props.box_level='middle'   
 
        props = row.operator('tp_ops.bbox_origin_all', text="+y")
        props.origin_location='plus_y'
        props.box_level='middle'   

        props = row.operator('tp_ops.bbox_origin_all', text="+y+x")
        props.origin_location='plus_y_plus_x'
        props.box_level='middle'   



        # MIDDLE +XY#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="-x")
        props.origin_location='minus_x'
        props.box_level='middle'                        
            
        props = row.operator('tp_ops.bbox_origin_all', text="xyz")
        props.origin_location='center'
        props.box_level='middle'         
     
        props = row.operator('tp_ops.bbox_origin_all', text="+x")
        props.origin_location='plus_x'
        props.box_level='middle'   


        # BOTTOM +XY#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="-y-x")
        props.origin_location='minus_y_minus_x'
        props.box_level='middle'   

        props = row.operator('tp_ops.bbox_origin_all', text="-y")
        props.origin_location='minus_y'
        props.box_level='middle'   

        props = row.operator('tp_ops.bbox_origin_all', text="-y+x")
        props.origin_location='minus_y_plus_x'            
        props.box_level='middle'   

       
        box.separator()        

        row = box.row(align=True)              
        row.label(text="Level -Z", icon= 'SHADING_BBOX')     

        box.separator() 

        # TOP -Z#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="+y-x")
        props.origin_location='plus_y_minus_x'      
        props.box_level='bottom'    
 
        props = row.operator('tp_ops.bbox_origin_all', text="+y")
        props.origin_location='plus_y'     
        props.box_level='bottom'      

        props = row.operator('tp_ops.bbox_origin_all', text="+y+x")
        props.origin_location='plus_y_plus_x'       
        props.box_level='bottom'                 
        

        # MIDDLE -Z#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="-x")
        props.origin_location='minus_x'     
        props.box_level='bottom'                         
            
        props = row.operator('tp_ops.bbox_origin_all', text="-z")
        props.origin_location='center'       
        props.box_level='bottom'        
     
        props = row.operator('tp_ops.bbox_origin_all', text="+x")
        props.origin_location='plus_x'      
        props.box_level='bottom'    


        # BOTTOM -Z#
        row = box.row(align=True)
        row.scale_x = 1.3
        row.scale_y = 1.3

        props = row.operator('tp_ops.bbox_origin_all', text="-y-x")
        props.origin_location='minus_y_minus_x'   
        props.box_level='bottom'       
        
        props = row.operator('tp_ops.bbox_origin_all', text="-y")
        props.origin_location='minus_y'    
        props.box_level='bottom'        
        

        props = row.operator('tp_ops.bbox_origin_all', text="-y+x")
        props.origin_location='minus_y_plus_x'                   
        props.box_level='bottom'    

        box.separator()     




# REGISTRY #        
def register():
        
    bpy.utils.register_class(VIEW3D_OT_Bounding_Box_Origin_All)
    bpy.utils.register_class(VIEW3D_PT_Bounding_Box_Origin_All)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_Bounding_Box_Origin_All)
    bpy.utils.unregister_class(VIEW3D_PT_Bounding_Box_Origin_All)


if __name__ == "__main__":
    register()
