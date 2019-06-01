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
    "name": "Wow WMO format (.wmo)",
    "author": "Happyhack",
    "version": (0, 1),
    "blender": (2, 57, 0),
    "location": "File > Import-Export > Wow WMO (.wmo) ",
    "description": "Import-Export Wow WMO",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
        "Scripts/Import-Export/Wow_WMO_IO",
    "tracker_url": "https://developer.blender.org/T25692",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    #if "wow_custom_ui" in locals():
    #    imp.reload(wow_custom_ui)
    if "import_wmo" in locals():
        imp.reload(import_wmo)
    if "export_wmo" in locals():
        imp.reload(export_wmo)
else:
    import bpy
    
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

from . import wow_custom_ui
#from . import Utility

class WMOImporter(bpy.types.Operator):
    """Load WMO mesh data"""
    bl_idname = "import_mesh.wmo"
    bl_label = "Import WMO"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.wmo", options={'HIDDEN'})

    def execute(self, context):
        from . import import_wmo
        import_wmo.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class WMOExporter(bpy.types.Operator, ExportHelper):
    """Save WMO mesh data"""
    bl_idname = "export_mesh.wmo"
    bl_label = "Export WMO"

    filename_ext = ".wmo"
    filter_glob = StringProperty(default="*.wmo", options={'HIDDEN'})

    """apply_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Use transformed mesh data from each object",
            default=True,
            )
    triangulate = BoolProperty(
            name="Triangulate",
            description="Triangulate quads",
            default=True,
            )"""

    def execute(self, context):
        from . import export_wmo
        export_wmo.write(self.filepath)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(WMOImporter.bl_idname, text="Wow WMO (.wmo)")


def menu_export(self, context):
    self.layout.operator(WMOExporter.bl_idname, text="Wow WMO (.wmo)")


def register():
    bpy.utils.register_module(__name__)
    wow_custom_ui.register()

    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    wow_custom_ui.unregister()

    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
