'''ui implementations of outosmoothextras'''
import bpy
from . import operators

class AutoSmoothExtras(bpy.types.Panel):
    bl_idname = "normals"
    bl_label = "Auto Smooth Extras"
    bl_context = "data"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_category = "normals"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        C = context
        obj = context.active_object
        if 'MESH' in obj.type:
            d = obj.data
            layout = self.layout
            r = layout.row()
            r.prop(d, "use_auto_smooth")
            r.prop(d, "show_double_sided")
            r = layout.row()
            r.prop(d, "auto_smooth_angle")            
            r.operator("mesh.auto_smooth_mark_sharps")
            r = layout.row()
            r.operator("mesh.auto_smooth_mark_edgecrease")
            r = layout.row()
            r.operator("mesh.auto_smooth_mark_bewelweights")

if __name__ == '__main__':
    
    def register():
        try: bpy.utils.register_module(__name__)
        except: traceback.print_exc()
        
        print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

    def unregister():
        try: bpy.utils.unregister_module(__name__)
        except: traceback.print_exc()
        
        print("Unregistered {}".format(bl_info["name"]))
    
    