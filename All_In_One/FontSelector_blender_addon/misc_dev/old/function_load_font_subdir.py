import bpy
import os
import csv

from .preferences import get_addon_preferences
from .functions.misc_functions import clear_collection, absolute_path

from .global_variable import subdir_list

def load_font_subdir():
    #get addon prefs
    addon_preferences = get_addon_preferences()
    prefs = addon_preferences.prefs_folderpath
    prefpath = absolute_path(prefs)
    prefsubdir = os.path.join(prefpath, subdir_list)
    fontsub=bpy.data.window_managers['WinMan'].fontselector_sub
    
    #remove existing font subs
    clear_collection(fontsub)
    
    if os.path.isdir(prefpath) :
        if os.path.isfile(prefsubdir):
            with open(prefsubdir, 'r', newline='') as csvfile:
                line = csv.reader(csvfile, delimiter='\n')
                for l in line:
                    l1=str(l).replace("[", "")
                    l2=l1.replace("]", "")
                    l3=l2.replace("'", "")
                    l4=l3.replace('"', "")
                    newsub=fontsub.add()
                    newsub.name=l4
        else:
            print("Font Selector --- Preference File does not exist")