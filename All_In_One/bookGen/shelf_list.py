import bpy

class BOOKGEN_UL_Shelves(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False)
