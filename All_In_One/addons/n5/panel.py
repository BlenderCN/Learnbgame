import bpy
import bpy,bgl,blf
from bpy.types import Menu
import os
import bmesh

class n5(bpy.types.Panel):
    bl_idname = "n"
    bl_label = "N"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "category"
    
    def draw(self, context):
        layout = self.layout
        
        layout.label("text")
        layout.menu("view3d.nmenu", text = "N5 Menu")
        layout.template_icon_view(WM, "nexus_five_previews")
        
class N5Menu(bpy.types.Menu):
    bl_idname = "view3d.nmenu"
    bl_label = "Nmenu"
    
    def draw(self, context):
        layout = self.layout
        
        layout.label("text")
        layout.template_icon_view(WM, "nexus_five_previews")

        
                