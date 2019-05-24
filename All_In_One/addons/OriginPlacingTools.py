#####################################################################
# An add-on with some tools to help placing the origin of meshes    #
# Actualy uncommented (see further version, or contact me)          #
# Author: Lapineige                                                 #
# License: GPL v3                                                  #
#####################################################################
  
  
############# Add-on description (used by Blender)
bl_info = {
    "name": "Origin Placing Tools",
    "description": "Tools to help placing the origin",
    "author": "Lapineige",
    "version": (1, 0),
    "blender": (2, 7, 1),
    "location": "View 3D > Toolbar > Tools (tab) > Origin Tools (panel)",
    "warning": "", 
    "wiki_url": "http://www.le-terrier-de-lapineige.over-blog.com",
    "tracker_url": "http://www.le-terrier-de-lapineige.over-blog.com",
    "category": "Learnbgame",
}
############# 


import bpy
from math import sqrt
from mathutils import Vector

bpy.types.Scene.OriginTools_show_param = bpy.props.BoolProperty(default=False, description="Show/hide parameters, allowing more control or more screen space")
bpy.types.Scene.OriginTools_orientation_mode = bpy.props.EnumProperty(items = [("0", "Center", "Center on 2 axis of the bounding box, and place at extreme on the last", 1),("1", "Corner", "Place on a corner of the bounding box", 2),("2", "Cursor", "Use distance from 3D cursor", 3)], description="Method of origin placing")
bpy.types.Scene.OriginTools_orientation_x = bpy.props.EnumProperty(items = [("1", "Last", "", 1),("0", "First", "", 2)], description="Choose corner coordinate on X axis")
bpy.types.Scene.OriginTools_orientation_y = bpy.props.EnumProperty(items = [("1", "Last", "", 1),("0", "First", "", 2)], description="Choose corner coordinate on Y axis")
bpy.types.Scene.OriginTools_orientation_z = bpy.props.EnumProperty(items = [("1", "Last", "", 1),("0", "First", "", 2)], description="Choose corner coordinate on Z axis")
bpy.types.Scene.OriginTools_orientation_axis = bpy.props.EnumProperty(items = [("0", "X", "", 1),("1", "Y", "", 2),("2", "Z", "", 3)], description="Axis which affect the placing")
bpy.types.Scene.OriginTools_orientation_side = bpy.props.EnumProperty(items = [("0", "Negative", "", 1),("1", "Positive", "", 2)], description="Side of the origin along axis (+/- coordinates)")
bpy.types.Scene.OriginTools_orientation_method = bpy.props.EnumProperty(items = [("0", "Axis", "Set the corner with axis parameters", 1),("1", "Named", "Choose in a list of corners", 2)], description="Corner defining method")
bpy.types.Scene.OriginTools_orientation_list = bpy.props.EnumProperty(items = [("0", "XminYminZmin", "", 1),("1", "XminYmaxZmin", "", 2),("2", "XminYminZmax", "", 3),("3", "XminYmaxZmax", "", 4),("4", "XmaxYminZmin", "", 5),("5", "XmaxYmaxZmin", "", 6),("6", "XmaxYminZmax", "", 7),("7", "XmaxYmaxZmax", "", 8)], description="Choose cursor position on the mesh bounding box")
bpy.types.Scene.OriginTools_cursor_mode = bpy.props.EnumProperty(items = [("0", "Vertex", "Place on the nearest vertex 3D from cursor position", 1),("1", "Bounding Box", "Place on the nearest bounding box corner from cursor position", 2)], description="Choose origin placing target")


class PlaceOrigin(bpy.types.Operator):
    """ """
    bl_idname = "object.place_origin"
    bl_label = "Place the Origin"

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == "MESH"
        return False
    
    def execute(self, context):
        obj = context.active_object
        current_mode = context.object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.mode_set(mode=current_mode)
        
        bbox = obj.bound_box
        l = [None]*8
        l[0],l[1],l[2],l[3],l[4],l[5],l[6],l[7] = bbox[0],bbox[3],bbox[1],bbox[2],bbox[4],bbox[7],bbox[5],bbox[6]
        if context.scene.OriginTools_orientation_mode == "1":
            if int(context.scene.OriginTools_orientation_method):
                vert_number = int(context.scene.OriginTools_orientation_list)
            else:
                vert_number = int(context.scene.OriginTools_orientation_x)*4 + int(context.scene.OriginTools_orientation_y)*1 + int(context.scene.OriginTools_orientation_z)*2
        elif context.scene.OriginTools_orientation_mode == "0":
            axis = int(context.scene.OriginTools_orientation_axis)
            side = int(context.scene.OriginTools_orientation_side)
            vert_number = int(axis) + (side and not axis)*4 - (not side and axis==1)*1 - (not side and axis==2)*2
        
        x1,y1,z1 = obj.location[0],obj.location[1],obj.location[2]
        
        if context.scene.OriginTools_orientation_mode == "1":
            obj.location[0],obj.location[1],obj.location[2] = l[vert_number][0] + obj.location[0],l[vert_number][1] + obj.location[1],l[vert_number][2] + obj.location[2]
        elif context.scene.OriginTools_orientation_mode == "2":
            obj.location = self.cursor_2_origin_loc(context)
        else:
            k = [0,0,0]
            count = 0
            for j in range(0,3):
                for i in context.object.bound_box:
                    count += i[j]
                k[j] = count/8
            for count in range(0,3):
                if count == axis:
                    obj.location[axis] = l[vert_number][axis] + obj.location[axis]
                    continue
                obj.location[count] = k[count] + obj.location[count]
                
        x2,y2,z2 = obj.location[0],obj.location[1],obj.location[2]
        
        for vert in obj.data.vertices:
            vert.co[0] = vert.co[0] - (x2-x1)
            vert.co[1] = vert.co[1] - (y2-y1)
            vert.co[2] = vert.co[2] - (z2-z1)
        return {'FINISHED'}

    def cursor_2_origin_loc(self,context):
        if context.scene.OriginTools_cursor_mode == '0':
            distance = 0
            count = 0
            for vert in context.object.data.vertices:
                d_vector = context.scene.cursor_location-(vert.co + context.object.location)
                d = sqrt(d_vector[0]**2+d_vector[1]**2+d_vector[2]**2)
                if d < distance or (distance==0 and d != 0 and count==0):
                    distance = d
                    closest_vert = vert
                count =+ 1
            return closest_vert.co
        else:
            distance = 0
            count = 0
            for corner in context.object.bound_box:
                d_vector = context.scene.cursor_location-(Vector((corner[0],corner[1],corner[2])) + context.object.location)
                d = sqrt(d_vector[0]**2+d_vector[1]**2+d_vector[2]**2)
                if d < distance or (distance==0 and d != 0 and count==0):
                    distance = d
                    closest_corner = corner
                count =+ 1
            return closest_corner
    
    
class OriginTools(bpy.types.Panel):
    """  """
    bl_label = "Origin Tools"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        split= layout.split(percentage=.3)
        split.label(text="Basic:")
        split.operator_menu_enum("object.origin_set", "type") # Blender default tool
        
        layout.operator("object.place_origin")
        if context.scene.OriginTools_show_param:
            layout.prop(context.scene, "OriginTools_show_param", text="Hide parameters", icon="TRIA_DOWN")
            layout.label(text="Alignement type:")
            layout.prop(context.scene, "OriginTools_orientation_mode", expand=True)
            if context.scene.OriginTools_orientation_mode == "1":
                layout.prop(context.scene, "OriginTools_orientation_method", expand=True)
                if not int(context.scene.OriginTools_orientation_method):
                    layout.prop(context.scene, "OriginTools_orientation_x",  text="X corner")
                    layout.prop(context.scene, "OriginTools_orientation_y",  text="Y corner")
                    layout.prop(context.scene, "OriginTools_orientation_z",  text="Z corner")
                else:
                    layout.prop(context.scene, "OriginTools_orientation_list", text="")
                layout.prop(context.object, "show_bounds", text="Show Boundaries")
            elif context.scene.OriginTools_orientation_mode == "2":
                layout.prop(context.scene, "OriginTools_cursor_mode", expand=True)
                if int(context.scene.OriginTools_cursor_mode):
                    layout.prop(context.object, "show_bounds", text="Show Boundaries")
            else:
                layout.prop(context.scene, "OriginTools_orientation_axis",  text="Axis")
                layout.prop(context.scene, "OriginTools_orientation_side",  text="Side")
                layout.prop(context.object, "show_bounds", text="Show Boundaries")
        else:
            layout.prop(context.scene, "OriginTools_show_param", text="Show parameters", icon="TRIA_RIGHT")

def register():
    bpy.utils.register_class(OriginTools)
    bpy.utils.register_class(PlaceOrigin)

def unregister():
    bpy.utils.unregister_class(OriginTools)
    bpy.utils.unregister_class(PlaceOrigin)


if __name__ == "__main__":
    register()

