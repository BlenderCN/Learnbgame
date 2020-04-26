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
    "name": "JSON anyland format (.json)",
    "author": "Mike Griffin",
    "version": (0, 1),
    "blender": (2, 57, 0),
    "location": "File > Import-Export > JSON Anyland File (.json) ",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    if "export_json" in locals():
        imp.reload(export_json)
    if "import_json" in locals():
        imp.reload(import_json)
else:
    import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

class JsonImporter(bpy.types.Operator):
    """Load Raw JSON mesh data"""
    bl_idname = "import_mesh.json"
    bl_label = "Import JSON"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        from . import import_json
        import_json.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class JsonExporter(bpy.types.Operator, ExportHelper):
    """Save Raw JSON mesh data"""
    bl_idname = "export_mesh.json"
    bl_label = "Export JSON"

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        from . import export_json
        export_json.write(self.filepath)
        return {'FINISHED'}

def menu_import(self, context):
    self.layout.operator(JsonImporter.bl_idname, text="Anyland JSON Geometry (.json)")

def menu_export(self, context):
    self.layout.operator(JsonExporter.bl_idname, text="Anyland JSON Geometry (.json)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
    register()
