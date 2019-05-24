
bl_info = {
    "name": "Import MikuMikuDance Format (.pmd)",
    "author": "Ze10",
    "version": (1, 0, 3),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "File > Import",
    "description": "Import to the MikuMikuDance Format (.pmd)",
    "warning": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    
    if "import_pmd" in locals():
    	imp.reload(import_pmd)
    	
else:
    from . import import_pmd

import bpy
import os

def menu_func_import(self, context): 
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".pmd"
    self.layout.operator(import_pmd.MMDImporter.bl_idname, text="MikuMikuDance (.pmd)", icon='PLUGIN').filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__=="__main__":
    register()
