bl_info={
    "category": "Import-Export",
    "name": "MmdUtil(pmd/pmx)",
    "author": "ousttrue",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import-Export PMD/PMX meshes",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "https://github.com/ousttrue/MmdUtility",
    "tracker_url": "https://github.com/ousttrue/MmdUtility",
}


if "bpy" in locals():
    import imp
    imp.reload(import_pmx)
    imp.reload(export_pmx)
else:
    from . import import_pmx
    from . import export_pmx
import bpy


def register():
    if not bpy.context.user_preferences.system.use_international_fonts:
        print("enable use_international_fonts")
        bpy.context.user_preferences.system.use_international_fonts = True

    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(import_pmx.ImportPmx.menu_func)
    bpy.types.INFO_MT_file_export.append(export_pmx.ExportPmx.menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(import_pmx.ImportPmx.menu_func)
    bpy.types.INFO_MT_file_export.remove(export_pmx.ExportPmx.menu_func)


if __name__ == "__main__":
    register()

