# coding: utf-8
import os
import sys
append_path=os.path.join(os.path.dirname(__file__), 'pymeshio')
sys.path.append(append_path)


bl_info={
    "category": "Learnbgame",
    "name": "blpymeshio(pmx)",
    "author": "ousttrue",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "Import-Export PMX meshes",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "https://github.com/ousttrue/blpymeshio",
}


try:
    import bpy # pylint: disable=E0401
    from . import bl
    #print("imported modules: "+__name__)


    if not bpy.context.user_preferences.system.use_international_fonts:
        print("enable use_international_fonts")
        bpy.context.user_preferences.system.use_international_fonts = True
        #bpy.context.user_preferences.system.language = 'ja_JP'


    class PymeshioAddonPreferences(bpy.types.AddonPreferences):
        bl_idname = __name__

        use_mqo_menu = bpy.props.BoolProperty(
            name='enable mqo importer/exporter menu',
            description='obsoleted',
            default=False)

        use_pmd_menu = bpy.props.BoolProperty(
            name='enable pmd importer/exporter menu',
            description='obsoleted',
            default=False) 

        def draw(self, context):
            layout = self.layout
            layout.prop(self, 'use_pmd_menu')
            layout.prop(self, 'use_mqo_menu')
            #layout.label(text='Path for PTVSD module. In macOS, path should be something like: "/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages"')

    from .import_pmd import ImportPmd
    from .export_pmd import ExportPmd
    from .import_mqo import ImportMqo
    from .export_mqo import ExportMqo
    from .import_pmx import ImportPmx
    print(ImportPmx)
    from .export_pmx import ExportPmx

except Exception as e:
    import traceback
    traceback.print_exc()

def register():
    bpy.utils.register_module(__name__)

    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    if addon_prefs.use_mqo_menu:
        bpy.types.INFO_MT_file_import.append(ImportMqo.menu_func)
        bpy.types.INFO_MT_file_export.append(ExportMqo.menu_func)
    if addon_prefs.use_pmd_menu:
        bpy.types.INFO_MT_file_import.append(ImportPmd.menu_func)
        bpy.types.INFO_MT_file_export.append(ExportPmd.menu_func)
    bpy.types.INFO_MT_file_import.append(ImportPmx.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportPmx.menu_func)

def unregister():
    bpy.types.INFO_MT_file_import.remove(ImportPmd.menu_func)
    bpy.types.INFO_MT_file_import.remove(ImportPmx.menu_func)
    bpy.types.INFO_MT_file_import.remove(ImportMqo.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportPmd.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportPmx.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportMqo.menu_func)
    bpy.utils.unregister_module(__name__)


if __name__=='__main__':
    register()
