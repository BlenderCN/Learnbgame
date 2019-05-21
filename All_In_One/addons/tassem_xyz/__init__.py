bl_info = {
    "name": "Tassem XYZ Stuff",
    "description": "Loading and manipulating atoms from XYZ files",
    "author": "Tassem",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "File -> Import -> xyz (.xyz)",
    "warning": "",
    "category": "Import-Export",
}


from ase.io.cube import read_cube_data
import bpy
import os.path
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
import time
from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        IntProperty,
        FloatProperty,
        )

from tassem_xyz.draw_cube import *

class import_cube(Operator, ImportHelper):
    bl_idname = "import_xyz.xyz"
    bl_label  = "Import XYZ file (*.xyz)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".xyz"
    filter_glob  = StringProperty(default="*.xyz", options={'HIDDEN'},)

    def draw(self,context):
        layout = self.layout

    def execute(self,context):
        start = time.time()
        filepath_pdb = bpy.path.abspath(self.filepath)
        draw_cube_now(filepath_pdb)
        end = time.time()
        total_time = end - start
        print('Total time: %10.5f' % total_time)
        
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(import_cube.bl_idname, text="XYZ file (.xyz)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
