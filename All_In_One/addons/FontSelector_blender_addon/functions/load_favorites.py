import bpy
import os
import csv

from ..preferences import get_addon_preferences
from .misc_functions import absolute_path
from .json_functions import read_json

from ..global_variable import json_favorites

def load_favorites() :
    addon_preferences = get_addon_preferences()
    prefs_path = absolute_path(addon_preferences.prefs_folderpath)
    json_file = os.path.join(prefs_path, json_favorites)
    collection_font_list = bpy.data.window_managers['WinMan'].fontselector_list
    debug = addon_preferences.debug_value

    favorites_list = []
    if os.path.isfile(json_file) :   
        datas = read_json(json_file)
        for fav in datas['favorites'] :
            favorites_list.append(fav['font'])
            for font in collection_font_list :
                if fav['font'] == font.name :
                    font.favorite = True

    # debug
    if debug:
        print('Favorites Loaded')