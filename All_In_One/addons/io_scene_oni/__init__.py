bl_info = {
    "name": "Oni game data importer (.dat, .raw)",
    "description": "Import Oni game data files (.dat, .raw)",
    "author": "OrelGenya",
    'version': (0, 0, 1),
    'blender': (2, 67, 0),
    'location': "File > Import",
    'warning': "",
    "category": "Import-Export",
}

if 'bpy' in locals():
    import imp
    if 'io_scene_oni.oni_ui' in locals():
        imp.reload(io_scene_oni.oni_ui)
        imp.reload(io_scene_oni.oni_utils)
        imp.reload(io_scene_oni.oni_types)
else:
    from io_scene_oni.oni_ui import (
            OniImportOperator,
        )
    from io_scene_oni import (
            oni_ui,
            oni_utils,
            oni_types
        )

#import blender stuff
from bpy.utils import (
        register_module,
        unregister_module,
    )
from bpy.types import (
        INFO_MT_file_export,
        INFO_MT_file_import,
    )
from io_scene_oni.oni_ui import (
        OniImportOperator,
    )


def register():
    import imp
    imp.reload(oni_ui)
    imp.reload(oni_utils)
    imp.reload(oni_types)

    oni_ui.register()

    register_module(__name__)
    INFO_MT_file_import.append(OniImportOperator.menu_func)

def unregister():
    oni_ui.unregister()

    unregister_module(__name__)
    INFO_MT_file_import.remove(OniImportOperator.menu_func)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()