bl_info = {
    "name": "Westwood3D Tools",
    "author": "Huw Pascoe",
    "version": (1, 0),
    "blender": (2, 6, 3),
    "location": "Import, Export, Material Panel",
    "description": "Enables content authoring for C&C Renegade",
    "warning": "This is a preview and should not be used for projects",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(w3d_material)
    imp.reload(w3d_struct)
    imp.reload(w3d_aggregate)
    imp.reload(w3d_util)
    imp.reload(w3d_import)
    imp.reload(w3d_export)
else:
    from . import w3d_material, w3d_struct, w3d_aggregate, w3d_util, w3d_import, w3d_export

import bpy

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Material.westwood3d = bpy.props.PointerProperty(type=w3d_material.Westwood3DMaterial)
    bpy.types.INFO_MT_file_import.append(w3d_import.menu_func_import)
    bpy.types.INFO_MT_file_export.append(w3d_export.menu_func_export)
def unregister():
    bpy.types.INFO_MT_file_export.remove(w3d_export.menu_func_export)
    bpy.types.INFO_MT_file_import.remove(w3d_import.menu_func_import)
    del bpy.types.Material.westwood3d
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
