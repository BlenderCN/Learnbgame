import bpy;
from bpy.types import  Panel

class F3B_TOOLS_PT_data_panel(Panel):
    bl_label = "F3b"
    bl_idname = "F3B_TOOLS_PT_data_panel"
    bl_context = "data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw(self, context):
        self.layout.use_property_split = True

def register():
    bpy.utils.register_class(F3B_TOOLS_PT_data_panel)
    from . import F3bMaterialLoader
    F3bMaterialLoader.register()
    from . import F3bLod
    F3bLod.register()
      

def unregister():
    bpy.utils.unregister_class(F3B_TOOLS_PT_data_panel)
    from . import F3bMaterialLoader
    F3bMaterialLoader.unregister()
    from . import F3bLod
    F3bLod.unregister()