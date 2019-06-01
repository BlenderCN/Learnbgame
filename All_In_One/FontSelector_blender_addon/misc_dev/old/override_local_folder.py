import bpy


from ..preferences import get_addon_preferences
from ..functions.misc_functions import absolute_path, clear_collection, get_all_font_files
from ..functions.update_functions import update_change_font

from ..global_variable import json_font_folders
from ..global_messages import override_loaded_msg


class FontSelectorOverrideFolder(bpy.types.Operator):
    bl_idname = "fontselector.override_folder"
    bl_label = "Toggle Override Folder"
    bl_description = "Use the Override Folder"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        wm = bpy.data.window_managers['WinMan']
        return wm.fontselector_folder_override != "" and not wm.fontselector_override
    
    def execute(self, context):
        wm = bpy.data.window_managers['WinMan']
        collection_font_list = wm.fontselector_list
        collection_subdir_list = wm.fontselector_sub
        override_folder = absolute_path(wm.fontselector_folder_override)

        fontpath_list, subdir_list = get_all_font_files(override_folder)

        # toggle override prop to false
        bpy.data.window_managers['WinMan'].fontselector_override = True

        # remove existing folder list
        clear_collection(collection_font_list)
        clear_collection(collection_subdir_list)

        # load fonts
        idx = 0
        for font in fontpath_list :
            try :
                # load font in blender datas to get name
                datafont = bpy.data.fonts.load(filepath = font[0])
                # add to font list
                newfont = collection_font_list.add()
                newfont.name = datafont.name
                newfont.filepath = datafont.filepath
                newfont.subdirectory = font[1]
                newfont.index = idx
                idx += 1
                # delete font
                bpy.data.fonts.remove(datafont, do_unlink=True)
            except RuntimeError :
                pass
        for subdir in subdir_list :
            newsubdir = collection_subdir_list.add()
            newsubdir.name = subdir[0]
            newsubdir.filepath = subdir[1]

        # update font in viewport
        update_change_font(self, context)

        # report user
        self.report({'INFO'}, override_loaded_msg)
            
        return {'FINISHED'}