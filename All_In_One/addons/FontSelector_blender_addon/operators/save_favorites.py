import bpy
import os
import csv

from ..preferences import get_addon_preferences
from ..functions.misc_functions import absolute_path, create_dir
from ..functions.json_functions import initialize_json_favorites_datas, add_favorite_json, read_json, create_json_file

from ..global_variable import json_favorites


class FontSelectorSaveFavorites(bpy.types.Operator):
    bl_idname = "fontselector.save_favorites"
    bl_label = "Save Favorites"
    bl_description = "Save Favorite Fonts in external Font Selector preference file"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        #get addon prefs
        addon_preferences = get_addon_preferences()
        prefs = addon_preferences.prefs_folderpath
        fontlist = bpy.data.window_managers['WinMan'].fontselector_list
        return prefs != '' and len(fontlist) > 0
    
    def execute(self, context):
        addon_preferences = get_addon_preferences()
        prefs_path = absolute_path(addon_preferences.prefs_folderpath)
        json_file = os.path.join(prefs_path, json_favorites)
        collection_font_list = bpy.data.window_managers['WinMan'].fontselector_list
        debug = addon_preferences.debug_value

        # check if folder exist and create it if not
        create_dir(prefs_path)

        # initialize json
        datas = initialize_json_favorites_datas()

        # add favorite font from list
        for font in collection_font_list :
            if font.favorite :
                datas = add_favorite_json(datas, font.name)

        if os.path.isfile(json_file) :

            # get old favorites
            old_datas = read_json(json_file)
            for old_fav in old_datas['favorites'] :
                if old_fav['font'] not in [f.name for f in collection_font_list] :
                    datas = add_favorite_json(datas, old_fav['font'])

            # delete old favorites file
            os.remove(json_file)

        # write file
        create_json_file(datas, json_file)

        # debug
        if debug:
            print('Favorites Saved')

        return {'FINISHED'}