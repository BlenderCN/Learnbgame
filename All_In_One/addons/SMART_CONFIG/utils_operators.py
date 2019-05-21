import bpy

from .functions import print_addon_modules

### print addons list operators ###
class SmartConfig_Print_Addons_List(bpy.types.Operator):
    bl_idname = "smartconfig.print_addons"
    bl_label = "Show Addons List"
    bl_description = "Print in the console the list of activated Addons Modules"
    
    def execute(self, context):
        print_addon_modules(self, context)
        return{'FINISHED'}