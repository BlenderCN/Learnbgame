bl_info = {
        "name": "CryTek(AION) CGF format",
        "author": "Jeremy Chen (jeremy7rd@outlook.com)",
        "version": (1, 0, 0),
        "blender": (2, 78, 0),
        "location": "File > Import-Export",
        "description": "Import-Export CGF, Import CGF mesh, UV's, materials and textures",
        "warning": "",
        "support": "TESTING",
        "category": "Learnbgame",
}

if "bpy" in locals():
    import importlib
    if "import_cgf" in locals():
        importlib.reload(import_cgf)

import bpy
import bpy.props
import bpy_extras
import mathutils

from mathutils import Vector, Matrix
from bpy.props import(
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        CollectionProperty,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        _check_axis_conversion
        )

import re
import glob
import os
import hashlib

from struct import *

IORIPOrientationHelper = orientation_helper_factory("IORIPOrientationHelper", axis_forward='Y', axis_up='Z')

class AionImporter(bpy.types.Operator, ImportHelper, IORIPOrientationHelper):
    """Load a CtyTek(AION) CGF File"""
    bl_idname = "import_scene.cgf"
    bl_label = "Import CGF/CAF"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = '.cgf'
    filter_glob = bpy.props.StringProperty(
            default = "*.cgf;*.caf",
            options = {'HIDDEN'},
            )
    # directory = StringProperty(options={'HIDDEN'})
    #  files = CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement)

    flip_x_axis = bpy.props.BoolProperty(
       default=False, name="Invert X axis",
       description="Flip the x axis values of the model",
       )

    import_skeleton = bpy.props.BoolProperty(
        default=True, name="Import Skeleton",
        description="Import the Skeleton bones",
        )

    skeleton_auto_connect = bpy.props.BoolProperty(
        default=True, name="Auto connect bone",
        description="Auto connect skeleton bones"
        )

    import_animations = bpy.props.BoolProperty(
        default=False, name="Import Animations",
        description="Import animations by searching the cal"
        )

    def execute(self, context):
        import os
        #  fnames = [f.name for f in self.files]
        #  if len(fnames) == 0 or not os.path.isfile(os.path.join(self.directory, fnames[0])):
            #  self.report({'ERROR'}, 'No file is selected for import')
            #  return {'FINISHED'}

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "flip_x_axis",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward, from_up=self.axis_up).to_4x4()
        if self.flip_x_axis:
            global_matrix = mathutils.Matrix.Scale(-1, 3, (1.0, 0.0, 0.0)).to_4x4() * global_matrix

        keywords['global_matrix'] = global_matrix
        keywords['use_cycles'] = (context.scene.render.engine == 'CYCLES')

        if bpy.data.is_saved and context.user_preferences.filepaths.use_relative_paths:
            keywords['relpath'] = os.path.dirname(bpy.data.filepath)

        self.report({'INFO'}, "Call import_cgf.load(context, **keywords)")

        from .import_cgf import ImportCGF

        importer = ImportCGF()
        return importer.load(context, **keywords)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "axis_forward")
        layout.prop(self, "axis_up")

        row = layout.row(align=True)
        row.prop(self, "flip_x_axis")

        box = layout.box()
        row = box.row()
        row.prop(self, "import_skeleton", expand=True)

        row = box.row()
        if self.import_skeleton == True:
            row.prop(self, "skeleton_auto_connect")

        row = layout.row(align=True)
        row.prop(self, "import_animations")

def menu_func_import(self, context):
    self.layout.operator(AionImporter.bl_idname, text="CryTek(AION) (.cgf, .caf)")

classes = (
    AionImporter,
    )

def register():
    script_dir = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
    try:
        os.sys.path.index(script_dir)
    except ValueError:
        os.sys.path.append(script_dir)

    global classes, menu_func_import
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

