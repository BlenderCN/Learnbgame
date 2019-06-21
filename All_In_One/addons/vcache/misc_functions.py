import bpy
import os

from .preferences import get_addon_preferences

#update create cache folder         
def create_cache_folder():
    #get addon prefs
    addon_preferences = get_addon_preferences()
    cachefolder = addon_preferences.prefs_folderpath
    path=absolute_path(cachefolder)
    if os.path.isdir(path)==False:
        os.makedirs(path)
        print('VCache --- Cache Folder Created')
        
#get absolute path
def absolute_path(path):
    npath=os.path.abspath(bpy.path.abspath(path))
    return npath

#suppress files with pattern
def suppress_files_pattern(folder, pattern):
    if os.path.isdir(folder)==True:
        for f in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, f))==True:
                if pattern in f:
                    os.remove(os.path.join(folder, f))