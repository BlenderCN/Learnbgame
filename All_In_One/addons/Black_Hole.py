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
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####


#//////////////////////////////// - AUTHORS YO - ///////////////////////////

bl_info = {
    "name": "Black Hole",
    "author": "Crocadillian/Takanu @ Polarised Games",
    "version": (1,0),
    "blender": (2, 7, 3),
    "api": 39347,
    "location": "3D View > Object Mode > Tools > Black Hole",
    "description": "Adds additional Object Origin tools",
    "wiki_url": "",
    "category": "Learnbgame",
}
    
#//////////////////////////////// - IMPORT - ///////////////////////////    
#This imports various items from the Python API for use in the script
import bpy
from math import *
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

#//////////////////////////////// - UPDATES - ///////////////////////////   
def Update_ObjectOrigin(self, context):
    
    # Create an array to store all found objects
    objects_to_select = []
    
    sel = context.active_object
    
    print("---Inside Update_ObjectOrigin---")
    
    if sel.BHObj.update_toggle is False:
    
        # Store the active object
        active = context.active_object
            
        # Find all the selected objects in the scene and store them
        for object in context.selected_objects:
            if object.name != active.name:
                print("! - Found Selected Object")
                objects_to_select.append(object) 
                
        # First, we need to process the active object, as it already has the correct enum.
        print("# - Active Object Name")
        print(active)
        FocusObject(active) 
        
        # Get the origin point and call the respective def
        newInt = int(active.BHObj.origin_point)
        enum = active.BHObj.origin_point
        
        SetObjectOrigin(active, newInt, context)
            
        # Now were going to focus each selected object using the update loop, to prevent a recursion
        # loop
        for object in objects_to_select:
            object.BHObj.update_toggle = True
            FocusObject(object)
            object.BHObj.origin_point = enum
        
        active.BHObj.update_toggle = False
        FocusObject(active)
            
        # Now were at the end, re-select the objects in the correct order.  
        for object in objects_to_select:
            SelectObject(object)
            object.BHObj.update_toggle = False
            
        return None
        
    else:
        # Focus on the object
        print("# - Selected Object Name")
        FocusObject(sel) 
        print(sel.name)
        
        # Get the origin point and call the respective def
        newEnum = int(context.active_object.BHObj.origin_point)
        SetObjectOrigin(sel, newEnum, context)
        
        return None
        
    
        
    return None 
    
def Update_ObjectVGOrigin(self, context):
    
    # Create an array to store all found objects
    objects_to_select = []
    objects_to_make_active = []
    
    print("Rawr?")
    
    # Store the active object
    objects_to_make_active.append(bpy.context.active_object)
            
    # Find all the selected objects in the scene and store them
    for object in context.selected_objects:
        objects_to_select.append(object)
        
    # Focus on the object with the newly selected vertex group
    FocusObject(bpy.context.active_object.object) 
        
    # Get the origin point and call the respective def
    newEnum = int(self.origin_point)
    VGSelect = int(bpy.context.active_object.GTMnu.vertex_groups)
    
    # If the index isnt one (which is the None selection), change the origin!)
    if VGSelect != 1:    
        SetObjectOrigin(object, newEnum, context)
        
    bpy.ops.object.select_all(action='DESELECT') 
        
    # Re-select all stored objects         
    for objectSelect in objects_to_select:
        bpy.ops.object.select_pattern(pattern=objectSelect.name)
             
    for objectActive in objects_to_make_active:
        bpy.ops.object.select_pattern(pattern=objectActive.name)
        bpy.context.scene.objects.active = objectActive
        
    return None 

#//////////////////////////////// - PROPERTY DEFINITIONS - ///////////////////////////  
    
# All properties relating to a specific object
class BH_Object(PropertyGroup):
    
    origin_point = EnumProperty(
        name="Set Object Origin",
        items=(
        ('1', 'Origin to Object Base', 'Sets the origin to the lowest point of the object, using the object Z axis.'),   
        ('2', 'Origin to Lowest Point', 'Sets the origin to the lowest point of the object, using the scene Z axis'),  
        ('3', 'Origin to Centre of Mass', 'Sets the origin using the objects centre of mass.'),
        ('4', 'Origin to Vertex Group', 'Sets the origin using a given vertex group'),
        ('5', 'Origin to 3D Cursor', 'Sets the origin using a given vertex group'),
        ),
        update = Update_ObjectOrigin)
        
    update_toggle = BoolProperty(
        name = "Update Toggle",
        description = "Prevents recursion loops in specific, multi-select operations",
        default = False)
    
# Used to get the vertex groups of a selected object
def GetVertexGroups(scene, context):
    
    items = [
        ("1", "None",  "", 0),
    ]

    ob = bpy.context.active_object
    u = 1

    for i,x in enumerate(ob.vertex_groups):
        
        items.append((str(i+1), x.name, x.name))

    return items
    
# Used to generate the menu enumerator for vertex groups
class BH_Menu(PropertyGroup):
    
    vertex_groups = EnumProperty(
        name="Select Vertex Group",
        items=GetVertexGroups,
        update=Update_ObjectVGOrigin)

    
#//////////////////////////////// - USER INTERFACE - ///////////////////////////  

class BH_Interface(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Black Hole"
    bl_category = "Tools"
    
    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return True
                
        return False
    
    def draw(self, context):
        layout = self.layout
        
        obj = context.object.BHObj
        mnu = context.object.BHMnu
        
        # Core user interface for the plugin
        
        col_object = layout.column(align=True)
        col_object.alignment = 'EXPAND'
        row_object = col_object.row(align=True)
        row_object.prop(obj, "origin_point", text="", icon = "CURSOR")
        row_object.operator("object.bh_update_origin", icon = "ROTATE")
        
        if int(obj.origin_point) is 4:
            row_object = layout.row(align=True)
            row_object.prop(mnu, "vertex_groups",text = "",  icon = "GROUP_VERTEX")
            
#//////////////////////////////// - DEFINITIONS - ///////////////////////////  
def FocusObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name) 
    
def SelectObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    target.select = True
    
def ActivateObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
        
        
#//////////////////////////////// - CLASSES - ///////////////////////////  
class BH_Update_Origin(bpy.types.Operator):
    """Updates the origin point based on each object's origin setting, for all selected objects"""
    
    bl_idname = "object.bh_update_origin"
    bl_label = ""
    
    def execute(self, context):
        print(self)
        
        atv = context.active_object
        sel = context.selected_objects
        
        for obj in sel:
            
            FocusObject(obj)
            Update_ObjectOrigin(obj, context)
            
        FocusObject(atv)
        Update_ObjectOrigin(atv, context)
        
        for obj in sel:
            SelectObject(obj)
            
        ActivateObject(atv)
        
        return {'FINISHED'}
        
def SetObjectOrigin(object, enum, context):
    
    print("Inside ASKETCH_SetObjectOrigin")
        
    # Set to Object Base
    if enum == 1:
        print("Setting to Object Base")
        
        # Enter the object!
        object_data = bpy.context.object.data
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        #Setup the correct tools to select vertices
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        sel_mode = context.tool_settings.mesh_select_mode
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        i = -1
        lowestZ = 0
        
        # First find the lowest Z value in the object
        for vertex in object_data.vertices:
            i += 1
            #print (i)
            
            # Used to define a reference point for the first vertex, in case 0 is
            # lower than any vertex on the model.
            if i == 0:
                lowestZ = vertex.co.z
            
            else:
                if vertex.co.z < lowestZ:
                    lowestZ = vertex.co.z
        
        # Now select all vertices with lowestZ
        
        for vertex in object_data.vertices:
            if vertex.co.z == lowestZ:
                vertex.select = True
                #print("Vertex Selected!")

        #Restore previous settings
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        context.tool_settings.mesh_select_mode = sel_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                  
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.object.editmode_toggle()
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        FocusObject(object)
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
    # Set to Absolute Lowest
    elif enum == 2:
        print("Setting to Absolute Lowest")
        
        # Enter the object!
        object_data = bpy.context.object.data
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        #Setup the correct tools to select vertices
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        sel_mode = context.tool_settings.mesh_select_mode
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        i = -1
        lowestZ = 0
        
        # First find the lowest Z value in the object
        for vertex in object_data.vertices:
            i += 1
            #print (i)
            
            # This code converts vertex coordinates from object space to world space.
            vertexWorld = object.matrix_world * vertex.co
            
            # Used to define a reference point for the first vertex, in case 0 is
            # lower than any vertex on the model.
            if i == 0:
                lowestZ = vertexWorld.z
            
            else:
                if vertexWorld.z < lowestZ:
                    lowestZ = vertexWorld.z
        
        # Now select all vertices with lowestZ
        
        for vertex in object_data.vertices:
            vertexWorld = object.matrix_world * vertex.co
            
            if vertexWorld.z == lowestZ:
                vertex.select = True
                #print("Vertex Selected!")

        #Restore previous settings
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        context.tool_settings.mesh_select_mode = sel_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                  
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.object.editmode_toggle()
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        FocusObject(object)
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
                
    # Set to COM
    elif enum == 3:
        print("Setting to COM")
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
    elif enum == 4:
        print("Setting to Vertex Group")
        
        # Enter the object!
        object_data = bpy.context.object.data
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        #Setup the correct tools to select vertices
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        sel_mode = context.tool_settings.mesh_select_mode
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        index = int(bpy.context.active_object.GTMnu.vertex_groups) - 1
        
        #Search through all vertices in the object to find the ones belonging to the
        #Selected vertex group
        for vertex in object_data.vertices:
            for group in vertex.groups:
                if group.group == index:
                    vertex.select = True
                    #print("Vertex Selected!")
                    
        #Restore previous settings
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        context.tool_settings.mesh_select_mode = sel_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                  
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.object.editmode_toggle()
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        FocusObject(object)
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
    # Set to COM
    elif enum == 5:
        print("Setting to 3D Cursor")
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


#//////////////////////// - REGISTER/UNREGISTER DEFINITIONS - ////////////////////////
property_classes = (BH_Object, BH_Menu)

def register():
    
    # Register the properties first
    for cls in property_classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Object.BHObj = PointerProperty(type=BH_Object)
    bpy.types.Object.BHMnu = PointerProperty(type=BH_Menu)
        
    bpy.utils.register_module(__name__) 
    
def unregister():
    
    # Unregister the properties first
    del bpy.types.Object.BHObj
    del bpy.types.Object.BHMnu
    
    for cls in property_classes:
        bpy.utils.unregister_class(cls)
    
    bpy.utils.unregister_module(__name__) 
    
if __name__ == "__main__":
    register()
