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
    "name": "Wow M2 format (.m2)",
    "author": "Miton",
    "version": (0, 1),
    "blender": (2, 57, 0),
    "location": "File > Import-Export > Wow M2 (.M2) ",
    "description": "Import-Export Wow M2",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
        "Scripts/Import-Export/Wow_M2_IO",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    if "import_m2" in locals():
        imp.reload(import_m2)
    if "export_m2" in locals():
        imp.reload(export_m2)
else:
    import bpy
    
from bpy.props import IntProperty, StringProperty, BoolProperty, FloatVectorProperty
from bpy_extras.io_utils import ExportHelper

#from . import m2_UI
#from . import Utility

class M2Importer(bpy.types.Operator):
    """Load WMO mesh data"""
    bl_idname = "import_mesh.m2"
    bl_label = "Import M2"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.m2", options={'HIDDEN'})

    def execute(self, context):
        from . import import_m2
        import_m2.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class M2Exporter(bpy.types.Operator, ExportHelper):
    """Save M2 mesh data"""
    bl_idname = "export_mesh.m2"
    bl_label = "Export M2"
    bl_options = {'PRESET'}

    filename_ext = ".m2"
    filter_glob = StringProperty(default="*.m2", options={'HIDDEN'})
    
    wmo_id = IntProperty(
        name="WMO DBC Id",
        description="Used in WMOAreaTable (optional)",
        default= 0,
        )

    def execute(self, context):
        from . import export_wmo
        export_m2.write(self.filepath, self.wmo_id)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(M2Importer.bl_idname, text="Wow M2 (.m2)")


def menu_export(self, context):
    self.layout.operator(M2Exporter.bl_idname, text="Wow M2 (.m2)")


def register():
    bpy.utils.register_module(__name__)
    #wow_custom_ui.register()

    bpy.types.INFO_MT_file_import.append(menu_import)
    #bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    #wow_custom_ui.unregister()

    bpy.types.INFO_MT_file_import.remove(menu_import)
    #bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
