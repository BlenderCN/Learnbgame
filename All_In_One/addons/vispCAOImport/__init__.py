
bl_info = {
    "name": "ViSP CAO",
    "author": "Vikas Thamizharasan",
    "blender": (2, 7, 6),
    "location": "File > Import",
    "description": "Import CAO",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
from bpy.props import *
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
                                 orientation_helper_factory,
                                 axis_conversion,
                                 )
_modules = []

__import__(name=__name__, fromlist=_modules)
_namespace = globals()
_modules_loaded = [_namespace[name] for name in _modules]
del _namespace

if "bpy" in locals():
    import imp
    if "import_cao" in locals():
        imp.reload(import_cao)
    from importlib import reload
    _modules_loaded[:] = [reload(val) for val in _modules_loaded]
    del reload

IOCAOOrientationHelper = orientation_helper_factory("IOCAOOrientationHelper", axis_forward='-Z', axis_up='Y')

class ImportCAO(bpy.types.Operator, ImportHelper, IOCAOOrientationHelper):
    bl_idname = "import_scene.cao"
    bl_label = "Import CAO"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".cao"
    filter_glob = StringProperty(
            default="*.cao",
            options={'HIDDEN'},
            )

    global_clamp_size = FloatProperty(
            name="Clamp Size",
            description="Clamp bounds under this value (zero to disable)",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=0.0,
            )

    def execute(self, context):
        from . import import_cao

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob"
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            import os
            keywords["relpath"] = os.path.dirname((bpy.data.path_resolve("filepath", False).as_bytes()))

        return import_cao.load(self, context, **keywords)

def menu_func_import(self, context):
    self.layout.operator(ImportCAO.bl_idname, text="ViSP .cao")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
