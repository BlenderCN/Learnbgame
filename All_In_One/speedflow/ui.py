import bpy
from bpy.types import Menu
from . icon.icons import load_icons
from . array import *
from . bevel import *
from . boolean import *
from . mirror import *
from . rotate import *
from . solidify import *
from . subsurf import *
from . symetrize import *
from . tubify import *

#Pie Menu     
class Speedflow_Pie_Menu(Menu):
    bl_idname = "pie.speedflow_pie_menu"
    bl_label = "Speedflow"
 
    @classmethod
    def poll(cls, context):
        return context.object is not None and context.selected_objects
    
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        icons = load_icons()
 
        #4 - LEFT 
        rotate = icons.get("icon_rotate")
        pie.operator("object.rotate_modal", text="Rotate", icon_value=rotate.icon_id)
        
        #6 - RIGHT
        bevel = icons.get("icon_bevel")
        pie.operator("object.bevel_width", text = "Adjust Bevel", icon_value=bevel.icon_id)

        #2 - BOTTOM
        box = pie.split().column()
        row = box.split(align=True)
        row.scale_y = 1.4
        row.scale_x = 1.2
        mirror = icons.get("icon_mirror")
        row.operator("object.mirror_modal", text="Mirror", icon_value=mirror.icon_id)
        row = box.split(align=True)
        row.scale_y = 1.4
        row.scale_x = 1.2
        symetrize = icons.get("icon_symetrize")
        row.operator("object.symetrize_modal", text="Symmetrize", icon_value=symetrize.icon_id)
        
        #8 - TOP
        array = icons.get("icon_array")
        pie.operator("object.array_modal", text="Array", icon_value=array.icon_id)

        #7 - TOP - LEFT 
        solidify = icons.get("icon_solidify")
        pie.operator("object.solidify_modal", text="Solidify", icon_value=solidify.icon_id)
         
        #9 - TOP - RIGHT
        boolean = icons.get("icon_boolean")
        pie.operator("object.boolean_modal", text="Boolean", icon_value=boolean.icon_id)
        
        #1 - BOTTOM - LEFT
        tubify = icons.get("icon_tubify")
        pie.operator("object.tubify_modal", text="Tubify", icon_value=tubify.icon_id)
        
        #3 - BOTTOM - RIGHT
        subsurf = icons.get("icon_subsurf")
        pie.operator("object.subsurf_modal", text = "Adjust Subsurf", icon_value=subsurf.icon_id)


#Menu
class Speedflow_Simple_Menu(bpy.types.Menu):
    bl_idname = "speedflow_simple_menu"
    bl_label = "Speedflow"
    
    @classmethod
    def poll(cls, context):
        return context.object is not None and context.selected_objects

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        icons = load_icons()
        
        #Bevel
        bevel = icons.get("icon_bevel")
        layout.operator("object.bevel_width", text = "Adjust Bevel", icon_value=bevel.icon_id)
        
        #Boolean
        boolean = icons.get("icon_boolean")
        layout.operator("object.boolean_modal", text="Boolean", icon_value=boolean.icon_id)
        
        #Subsurf
        subsurf = icons.get("icon_subsurf")
        layout.operator("object.subsurf_modal", text = "Adjust Subsurf", icon_value=subsurf.icon_id)

        #Mirror
        mirror = icons.get("icon_mirror")
        layout.operator("object.mirror_modal", text="Mirror", icon_value=mirror.icon_id)
        
        #Symmetrize
        symetrize = icons.get("icon_symetrize")
        layout.operator("object.symetrize_modal", text="Symmetrize", icon_value=symetrize.icon_id)
        
        #Array
        array = icons.get("icon_array")
        layout.operator("object.array_modal", text="Array", icon_value=array.icon_id)

        #Solidify
        solidify = icons.get("icon_solidify")
        layout.operator("object.solidify_modal", text="Solidify", icon_value=solidify.icon_id)
         
        #Tubify
        tubify = icons.get("icon_tubify")
        layout.operator("object.tubify_modal", text="Tubify", icon_value=tubify.icon_id)
        
        #Rotate
        rotate = icons.get("icon_rotate")
        layout.operator("object.rotate_modal", text="Rotate", icon_value=rotate.icon_id)


#Panel       
class Speedflow(bpy.types.Panel):
    bl_idname = "speedflow"
    bl_label = "Speedflow"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.selected_objects

    def draw(self, context):
        layout = self.layout
        
        icons = load_icons()
        
        #Bevel
        bevel = icons.get("icon_bevel")
        layout.operator("object.bevel_width", text = "Adjust Bevel", icon_value=bevel.icon_id)
        
        #Subsurf
        subsurf = icons.get("icon_subsurf")
        layout.operator("object.subsurf_modal", text = "Adjust Subsurf", icon_value=subsurf.icon_id)
        
        #Solidify
        solidify = icons.get("icon_solidify")
        layout.operator("object.solidify_modal", text="Solidify", icon_value=solidify.icon_id)
        
        #Boolean
        boolean = icons.get("icon_boolean")
        layout.operator("object.boolean_modal", text="Boolean", icon_value=boolean.icon_id)
        
        #Mirror
        mirror = icons.get("icon_mirror")
        layout.operator("object.mirror_modal", text="Mirror", icon_value=mirror.icon_id)
        
        #Symmetrize
        symetrize = icons.get("icon_symetrize")
        layout.operator("object.symetrize_modal", text="Symmetrize", icon_value=symetrize.icon_id)
        
        #Array
        array = icons.get("icon_array")
        layout.operator("object.array_modal", text="Array", icon_value=array.icon_id)

        #Tubify
        tubify = icons.get("icon_tubify")
        layout.operator("object.tubify_modal", text="Tubify", icon_value=tubify.icon_id)
        
        #Rotate
        rotate = icons.get("icon_rotate")
        layout.operator("object.rotate_modal", text="Rotate", icon_value=rotate.icon_id)