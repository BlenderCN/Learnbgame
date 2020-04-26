bl_info = {
    "name": "MQO (Metasequoia) format",
    "author": "Nutti",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Import/Export MQO files",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "https://github.com/nutti/blender-mqo",
    "category": "Learnbgame",
}


if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    utils.bl_class_registry.BlClassRegistry.cleanup()
    importlib.reload(preferences)
    importlib.reload(ops)
else:
    import bpy
    from . import utils
    from . import preferences
    from . import ops

import os


def register_updater(bl_info):
    config = utils.addon_updater.AddonUpdatorConfig()
    config.owner = "nutti"
    config.repository = "blender-mqo"
    config.current_addon_path = os.path.dirname(os.path.realpath(__file__))
    config.branches = ["master", "develop"]
    config.addon_directory = config.current_addon_path[:config.current_addon_path.rfind("/")]
    config.min_release_version = bl_info["version"]
    config.target_addon_path = "src/blender_mqo"
    updater = utils.addon_updater.AddonUpdatorManager.get_instance()
    updater.init(bl_info, config)


def register():
    register_updater(bl_info)
    bpy.utils.register_class(ops.BoolPropertyCollection)
    utils.bl_class_registry.BlClassRegistry.register()

    if utils.compatibility.check_version(2, 80, 0) >= 0:
        file_import_menu_type = bpy.types.TOPBAR_MT_file_import
        file_export_menu_type = bpy.types.TOPBAR_MT_file_export
    else:
        file_import_menu_type = bpy.types.INFO_MT_file_import
        file_export_menu_type = bpy.types.INFO_MT_file_export

    file_import_menu_type.append(ops.topbar_mt_file_import_fn)
    file_export_menu_type.append(ops.topbar_mt_file_export_fn)

    bpy.types.Scene.dynamic_bool_property = bpy.props.CollectionProperty(
        type=ops.BoolPropertyCollection)


def unregister():
    del bpy.types.Scene.dynamic_bool_property

    if utils.compatibility.check_version(2, 80, 0) >= 0:
        file_import_menu_type = bpy.types.TOPBAR_MT_file_import
        file_export_menu_type = bpy.types.TOPBAR_MT_file_export
    else:
        file_import_menu_type = bpy.types.INFO_MT_file_import
        file_export_menu_type = bpy.types.INFO_MT_file_export

    file_export_menu_type.remove(ops.topbar_mt_file_export_fn)
    file_import_menu_type.remove(ops.topbar_mt_file_import_fn)

    utils.bl_class_registry.BlClassRegistry.unregister()
    bpy.utils.unregister_class(ops.BoolPropertyCollection)


if __name__ == "__main__":
    register()