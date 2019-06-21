import bpy
import os
import platform
import subprocess

from ..functions.misc_functions import absolute_path, open_folder_in_explorer

class FontSelectorOpenFontFolder(bpy.types.Operator):
    bl_idname = "fontselector.open_font_folder"
    bl_label = "Open Font Folder"
    bl_description = "Open missing Font File Folder in Explorer"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        try :
            active = context.active_object
            active.type == 'FONT'
            active.data.fontselector_font_missing == True
            chk = 1
        except :
            chk = 0
        return chk == 1
    
    def execute(self, context):
        active = context.active_object
        filepath = absolute_path(active.data.font.filepath)
        path = os.path.dirname(filepath)

        if os.path.isfile(filepath) :
            open_folder_in_explorer(path)
        else :
            bpy.ops.fontselector.dialog_message('INVOKE_DEFAULT', code = 9)

        return {'FINISHED'}