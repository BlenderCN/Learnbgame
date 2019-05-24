#if __name__ != 'src':  # TODO: temp
bl_info = {
    'name': 'Ragnarok Online GND Format',
    'description': 'Import RSW, RSM and GND files from Ragnarok Online.',
    'author': 'Colin Basnett',
    'version': (1, 0, 0),
    'blender': (2, 79, 0),
    'location': 'File > Import-Export',
    'warning': 'This add-on is under development.',
    'wiki_url': 'https://github.com/cmbasnett/io_scene_rsw/wiki',
    'tracker_url': 'https://github.com/cmbasnett/io_scene_rsw/issues',
    'support': 'COMMUNITY',
    "category": "Learnbgame",
}

    if 'bpy' in locals():
        import importlib
        if 'gnd'            in locals(): importlib.reload(gnd)
        if 'rsm'            in locals(): importlib.reload(rsm)
        if 'rsw'            in locals(): importlib.reload(rsw)
        if 'gnd_importer'   in locals(): importlib.reload(gnd_importer)
        if 'rsm_importer'   in locals(): importlib.reload(rsm_importer)
        if 'rsw_importer'   in locals(): importlib.reload(rsw_importer)

    import bpy
    from .gnd import gnd
    from .rsm import rsm
    from .rsw import rsw
    from .gnd import importer as gnd_importer
    from .rsm import importer as rsm_importer
    from .rsw import importer as rsw_importer

    def register():
        bpy.utils.register_module(__name__)
        bpy.types.INFO_MT_file_import.append(gnd_importer.GndImportOperator.menu_func_import)
        bpy.types.INFO_MT_file_import.append(rsm_importer.RsmImportOperator.menu_func_import)
        bpy.types.INFO_MT_file_import.append(rsw_importer.RswImportOperator.menu_func_import)


    def unregister():
        bpy.utils.unregister_module(__name__)
        bpy.types.INFO_MT_file_import.remove(gnd_importer.GndImportOperator.menu_func_import)
        bpy.types.INFO_MT_file_import.remove(rsm_importer.RsmImportOperator.menu_func_import)
        bpy.types.INFO_MT_file_import.remove(rsw_importer.RswImportOperator.menu_func_import)
