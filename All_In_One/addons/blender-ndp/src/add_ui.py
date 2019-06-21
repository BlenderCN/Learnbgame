import bpy
from .add_op import CLASSES

class SubmenuAdd(bpy.types.Menu):
    bl_idname = "NDP_MT_add"
    bl_label = "Non-Destructive"
    bl_icon = 'OUTLINER_OB_MESH'

    def draw(self, context):
        layout = self.layout
        for cls in CLASSES:
            layout.operator(cls.bl_idname, icon=cls.bl_icon)
