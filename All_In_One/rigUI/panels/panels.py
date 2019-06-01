import bpy
import collections

class rigUIPanel(bpy.types.Panel):
    bl_label = "Rig UI"
    bl_category = "RIG Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'


    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("rigui.store_ui_data")
