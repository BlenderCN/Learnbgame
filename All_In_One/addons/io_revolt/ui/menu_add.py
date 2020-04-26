import bpy
from ..common import *
from .hull import *

def menu_func_add(self, context):
    self.layout.separator()
    self.layout.menu(INFO_MT_revolt_add.bl_idname, icon = "OBJECT_DATA")


class INFO_MT_revolt_add(bpy.types.Menu):
    bl_idname = "INFO_MT_revolt_add"
    bl_label = "Re-Volt"
    
    def draw(self, context):
        self.layout.operator("object.add_hull_sphere", icon="MATSPHERE")
