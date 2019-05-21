bl_info = {
    "name": "ROSE Online blender plugin",
    "author": "Ralph Minderhoud",
    "blender": (2, 77, 0),
    "version": (0, 0, 3),
    "location": "File > Import",
    "description": "Import files from ROSE Online",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_map" in locals():
        importlib.reload(import_map)
else:
    from .import_map import ImportMap
    from .import_zms import ImportZMS

import bpy

def menu(self, context):
    self.layout.separator()
    self.layout.operator(ImportMap.bl_idname, text="ROSE Map (.zon)")
    self.layout.operator(ImportZMS.bl_idname, text=ImportZMS.bl_label)

def register():
    bpy.utils.register_class(ImportMap)
    bpy.utils.register_class(ImportZMS)
    bpy.types.INFO_MT_file_import.append(menu)

def unregister():
    bpy.utils.unregister_class(ImportMap)
    bpy.utils.unregister_class(ImportZMS)
    bpy.types.INFO_MT_file_import.remove(menu)


if __name__ == "__main__":
    register()
