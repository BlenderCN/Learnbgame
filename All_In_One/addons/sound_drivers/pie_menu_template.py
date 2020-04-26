import bpy
from bpy.types import Menu
from bpy.utils import register_class, unregister_class

from sound_drivers.sounddriver import DriverManager_DriverOp

class PieMenuDriverPopup(bpy.types.Operator, DriverManager_DriverOp):
    """Edit Driver Details"""
    bl_idname = "driver.popup_driver"
    bl_label = "Driver Manager"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        if wm is None:
            # try and start the b***
            bpy.ops.wm.update_dm()
            wm = context.window_manager
        d = self.get_driver()
        if d:         
            bpy.ops.driver.edit('INVOKE_DEFAULT', dindex=d.index, toggle=True)
        return(wm.invoke_props_dialog(self))
        
    def draw(self, context):
        d = self.get_driver()
        if d:        
            scene = context.scene    
            gui = d.driver_gui(scene)
            if gui is not None:
                self.layout.prop(gui, "gui_types",
                             text="",
                             expand=True,
                             icon_only=True)
            d.draw_slider(self.layout)
            d.edit(self.layout, context)
            self.check(context)
        
    def execute(self, context):
        return {'FINISHED'}


class VIEW3D_PIE_template(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Select Mode"

    def draw(self, context):
        layout = self.layout
        layout.label("WHERE")
        obj = context.object
        dm = context.driver_manager
        pie = layout.menu_pie()

        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie
        dic = dm.get_object_dic("objects", obj.name)
        for dp, dr in dic.items():
            p = pie.menu_pie()
            for index, dindex in dr.items():
                box = pie.box()
                driver = dm.find(dindex)
                #driver.edit(box, context)
                driver.draw_slider(box)
                #driver.draw_default(box)
                #driver.driver_edit_draw(box, context)
                #dm.driver_draw(driver, box)
                op = box.operator("driver.popup_driver", text=dp, icon='DRIVER')
                op.dindex = dindex
                # op.toggle = True

addon_keymaps = []
def register():
    register_class(VIEW3D_PIE_template)
    register_class(PieMenuDriverPopup)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu_pie", type='D', value='PRESS', ctrl=True)
        kmi.properties.name = "VIEW3D_PIE_template"
        addon_keymaps.append((km, kmi))

def unregister():
    unregister_class(VIEW3D_PIE_template)
    bpy.utils.unregister_class(PieMenuDriverPopup)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()

    bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_template")
