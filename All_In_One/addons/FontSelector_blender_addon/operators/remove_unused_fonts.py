import bpy

from ..functions.misc_functions import remove_unused_font

class FontSelectorRemoveUnused(bpy.types.Operator):
    bl_idname = "fontselector.remove_unused"
    bl_label = "Remove unused Fonts"
    bl_description = "Remove Unused Fonts form Blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.fonts)>0
    
    def execute(self, context):
        removed_font_count = remove_unused_font()
        if removed_font_count > 0 :
            info = str(removed_font_count)+' unused Font(s) removed'
            self.report({'INFO'}, info)  
        else:
            info = 'No unused Font to remove'
            self.report({'INFO'}, info)      
            
        return {'FINISHED'}