import os

from .json_functions import read_json
from ..preferences import get_addon_preferences
from .misc_functions import absolute_path

from ..global_variable import json_file

#get subdirectories item for enum property for font installation
def get_subdirectories_items_for_installation(self, context) :
    addon_preferences = get_addon_preferences()
    prefspath = absolute_path(addon_preferences.prefs_folderpath)
    json = os.path.join(prefspath, json_file)
    datas = read_json(json)

    subdir_list = []
    # load subdirs
    for subdir in datas['subdirectories'] : 
        subdir_list.append((subdir['name'], subdir['name'], subdir['filepath']))
    return subdir_list

#get subdirectories item for enum property for font installation
def get_subdirectories_filepath_installation() :
    addon_preferences = get_addon_preferences()
    prefspath = absolute_path(addon_preferences.prefs_folderpath)
    json = os.path.join(prefspath, json_file)
    datas = read_json(json)

    subdir_list = []
    # load subdirs
    for subdir in datas['subdirectories'] : 
        subdir_list.append((subdir['name'], subdir['filepath']))
    return subdir_list