import bpy
from bpy.types import Panel

class OX_Interface(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Onyx"
    bl_category = "Tools"

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return True

        return False

    def draw(self, context):
        layout = self.layout

        obj = context.object.OXObj

        # Core user interface for the plugin

        col_object = layout.column(align=True)
        col_object.alignment = 'EXPAND'
        row_object = col_object.row(align=True)
        row_object.prop(obj, "origin_point", text="", icon = "CURSOR")
        row_object.operator("origin.update_origin", icon = "ROTATE")

        if int(obj.origin_point) is 4:
            row_object = layout.row(align=True)
            row_object.prop(obj, "vertex_groups",text = "",  icon = "GROUP_VERTEX")
