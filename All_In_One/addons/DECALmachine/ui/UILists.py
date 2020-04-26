import bpy


class DecalLibsUIList(bpy.types.UIList):
    bl_idname = "MACHIN3_UL_decal_libs"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        isvisibleicon = "VISIBLE_IPO_ON" if item.isvisible else "VISIBLE_IPO_OFF"
        islockedicon = "LOCKED" if item.islocked else "BLANK1"

        split = layout.split(factor=0.7)

        row = split.row()
        row.label(text=item.name)
        row = split.row()
        row.prop(item, "isvisible", text="", icon=isvisibleicon, emboss=False)
        row.prop(item, "islocked", text="", icon=islockedicon, emboss=False)
        row.prop(item, "ispanel", text="Slice")
