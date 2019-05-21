# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "Soldak MDM format",
    "author": "Yotam Barnoy",
    "blender": (2, 74, 0),
    "location": "File > Import-Export",
    "description": "Import-Export MDM, meshes, uvs, materials, textures, "
                   "cameras & lamps",
    "warning": "",
    "support": 'OFFICIAL',
    "category": "Learnbgame"
}

'''
if "bpy" in locals():
    import importlib
    if "import_mdm" in locals():
        importlib.reload(import_mdm)
'''

# When bpy is already in local, we know this is not the initial import...
# (Supports reloading the addon with F8 while blender is running)
if "bpy" in locals():
    # ...so we need to reload our submodule(s) using importlib
    import importlib
    if "import_soldak" in locals():
        importlib.reload(import_soldak)

import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        )
'''
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        axis_conversion,
        )
'''

class ImportSoldak(bpy.types.Operator):
    """Import from Soldak file format (.mdm)"""
    bl_idname = "import_mesh.soldak"
    bl_label = 'Import Soldak'
    bl_options = {'UNDO'}

    filename_ext = ".mdm"

    filter_glob = StringProperty(default="*.mdm", options={'HIDDEN'})
    filepath = StringProperty(options={'HIDDEN'})

    def execute(self, context):
        from . import import_mdm

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            ))

        return import_mdm.load(self, context, **keywords)


# Add to a menu
#def menu_func_export(self, context):
    #self.layout.operator(ExportSoldak.bl_idname, text="Soldak (.mdm)")


def menu_func_import(self, context):
    self.layout.operator(ImportSoldak.bl_idname, text="Soldak (.mdm)")


def register():
    bpy.utils.register_module(__name__)
    #bpy.utils.register_class(ImportSoldak)

    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.utils.unregister_class(ImportSoldak)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
