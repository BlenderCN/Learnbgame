import bpy

from ..preferences import get_addon_preferences

# suppress preferences filepath
def fontselector_suppress_fp(index) :
    #get addon prefs
    addon_preferences = get_addon_preferences()
    fplist = addon_preferences.font_folders
    
    fplist.remove(index)
    #operator refresh fonts if list created