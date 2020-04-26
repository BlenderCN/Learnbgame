import bpy
import os

from bpy.app.handlers import persistent

from .prefs import get_addon_preferences
from .misc_functions import create_prop, get_content_txt, clear_coll_prop, create_custom_path_props


@persistent
def nd_start_handler(scene):
    prefs=get_addon_preferences()
    path=prefs.prefs_folderpath
    dirpath=os.path.join(path, 'folders')
    
    #create props if doesn't exist
    prop=create_prop()
    
    #clean custom path
    custompath=clear_coll_prop(prop.dirpath_coll)
    
    #check custom paths
    create_custom_path_props(dirpath, prop.dirpath_coll)
#    for f in os.listdir(dirpath):
#        new=prop.dirpath_coll.add()
#        new.name=f.split('.txt')[0]
#        new.path=get_content_txt(os.path.join(dirpath, f))

    print('ND loaded')