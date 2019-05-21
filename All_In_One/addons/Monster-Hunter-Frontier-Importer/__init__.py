# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 02:31:16 2019

@author: AsteriskAmpersand
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 13:38:47 2019

@author: AsteriskAmpersand
"""
#from .dbg import dbg_init
#dbg_init()

content=bytes("","UTF-8")
bl_info = {
    "name": "MHF FMod Model Importer",
    "category": "Import-Export",
    "author": "AsteriskAmpersand (Code) & Vuze (Structure)",
    "location": "File > Import-Export > FMod/MHF",
    "version": (1,0,0)
}
 
import bpy

from .operators.fmodimport import ImportFMOD
from .operators.fmodimport import menu_func_import as mhf_model_menu_func_import
def register():
    bpy.utils.register_class(ImportFMOD)
    bpy.types.INFO_MT_file_import.append(mhf_model_menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportFMOD)
    bpy.types.INFO_MT_file_import.remove(mhf_model_menu_func_import)

if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
