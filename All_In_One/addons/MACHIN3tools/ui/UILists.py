import bpy


class AppendMatsUIList(bpy.types.UIList):
    bl_idname = "MACHIN3_UL_append_mats"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.split(factor=0.7)
        row.label(text=item.name)
