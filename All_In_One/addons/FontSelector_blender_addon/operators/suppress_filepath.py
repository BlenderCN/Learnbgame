import bpy

from ..preferences import get_addon_preferences


class FontSelectorSuppressFP(bpy.types.Operator):
    bl_idname = "fontselector.suppress_fp"
    bl_label = ""
    bl_description = "Suppress Font Filepath"
    bl_options = {'REGISTER', 'UNDO'}
    
    index : bpy.props.IntProperty()
    
    @classmethod
    def poll(cls, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        fplist = addon_preferences.font_folders
        return len(fplist)>0
    
    def execute(self, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        fplist = addon_preferences.font_folders
        
        fplist.remove(self.index)
        return {'FINISHED'}