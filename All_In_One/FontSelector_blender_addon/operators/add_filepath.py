import bpy

from ..preferences import get_addon_preferences

class FontSelectorAddFP(bpy.types.Operator):
    bl_idname = "fontselector.add_fp"
    bl_label = ""
    bl_description = "Add Font Folder Path"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        fplist = addon_preferences.font_folders
        
        # Create font folder
        fplist.add() 
    
        return {'FINISHED'}