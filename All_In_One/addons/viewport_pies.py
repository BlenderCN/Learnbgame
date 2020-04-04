bl_info = {
    "name": "Viewport Pies",
    "author": "Sebastian Koenig",
    "version": (0, 1),
    "blender": (2, 7, 2),
    "description": "Viewport Pies",
    "category": "Learnbgame",
}



import bpy
from bpy.types import Menu



########### CUSTOM OPERATORS ###############


class VIEW3D_OT_show_all_wires(bpy.types.Operator):
    """Show all wires for selected objects"""
    bl_idname = "object.show_all_wires"
    bl_label = "Show all wires"
 
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'VIEW_3D'

    def show_all_wires(context):
        wired = []
        clean = []
        obs=[]
        for ob in bpy.context.selected_objects:
            if ob.type=="MESH" or ob.type=="CURVE":
                obs.append(ob)
        for ob in obs:
            if ob.show_wire:
                wired.append(ob)
        for ob in obs:
            if len(wired)>=1:
                ob.show_wire = False
            else:
                ob.show_wire = True
    
 
    def execute(self, context):
        self.show_all_wires()
        return {'FINISHED'}
 





################### PIES #####################

class VIEW3D_PIE_display(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Viewport Pies"
    bl_idname = "object.display_pie"

    def draw(self, context):
        context = bpy.context
        layout = self.layout
        tool_settings = context.scene.tool_settings
        space = context.space_data

        pie = layout.menu_pie()

        pie.prop(space, "show_textured_solid", icon="TEXTURE")
        pie.prop(space, "show_only_render", icon="SMOOTH")
        pie.prop(space, "use_matcap", icon="MATCAP_06")
        pie.operator("object.show_all_wires", icon="WIRE")
        pie.operator("view3d.view_all", text="Center Cursor", icon="CURSOR").center=True
        pie.operator("view3d.view_selected", icon="ZOOM_SELECTED")
        pie.operator("view3d.view_all", icon="RESTRICT_VIEW_OFF").center=False
        pie.operator("view3d.localview", icon="VIEWZOOM")




########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_PIE_display)
    bpy.utils.register_class(VIEW3D_OT_show_all_wires)


    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS', shift=True).properties.name = "object.display_pie"

  




def unregister():

    bpy.utils.unregister_class(VIEW3D_PIE_display)
    bpy.utils.unregister_class(VIEW3D_OT_show_all_wires)


if __name__ == "__main__":
    register()
