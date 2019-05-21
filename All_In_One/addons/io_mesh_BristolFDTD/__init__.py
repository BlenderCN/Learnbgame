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

# <pep8 compliant>

bl_info = {
    "name": "BristolFDTD format",
    "author": "Bruce Merry, Campbell Barton",
    "blender": (2, 5, 7),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export BristolFDTD mesh data withs UV's and vertex colors",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/Import-Export/BristolFDTD",
    "tracker_url": "",
    "support": 'OFFICIAL',
    "category": "Learnbgame"
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "export_BristolFDTD" in locals():
        imp.reload(export_BristolFDTD)
    if "import_BristolFDTD" in locals():
        imp.reload(import_BristolFDTD)

import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportBristolFDTD(bpy.types.Operator, ImportHelper):
    '''Load a BristolFDTD geometry file'''
    bl_idname = "import_mesh.bfdtd"
    bl_label = "Import BristolFDTD"

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the BristolFDTD file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = ".BristolFDTD"
    filter_glob = StringProperty(default="*.geo;*.inp;*.in", options={'HIDDEN'})

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)

        print('pre-import')
        print('os.getcwd() = ',os.getcwd())
        from . import import_BristolFDTD
        print('post-import')

        for path in paths:
            print('path = ',path)
            import_BristolFDTD.load(self, context, path)

        return {'FINISHED'}


class ExportBristolFDTD(bpy.types.Operator, ExportHelper):
    '''Export a single object as a BristolFDTD with normals, colours and texture coordinates.'''
    bl_idname = "export_mesh.bfdtd"
    bl_label = "Export BristolFDTD"

    filename_ext = ".BristolFDTD"
    filter_glob = StringProperty(default="*.BristolFDTD", options={'HIDDEN'})

    use_modifiers = BoolProperty(name="Apply Modifiers", description="Apply Modifiers to the exported mesh", default=True)
    use_normals = BoolProperty(name="Normals", description="Export Normals for smooth and hard shaded faces", default=True)
    use_uv_coords = BoolProperty(name="UVs", description="Exort the active UV layer", default=True)
    use_colors = BoolProperty(name="Vertex Colors", description="Exort the active vertex color layer", default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        from . import export_BristolFDTD
        return export_BristolFDTD.save(self, context, **self.as_keywords(ignore=("check_existing", "filter_glob")))

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "use_modifiers")
        row.prop(self, "use_normals")
        row = layout.row()
        row.prop(self, "use_uv_coords")
        row.prop(self, "use_colors")


def menu_func_import(self, context):
    self.layout.operator(ImportBristolFDTD.bl_idname, text="BristolFDTD (.BristolFDTD)")


def menu_func_export(self, context):
    self.layout.operator(ExportBristolFDTD.bl_idname, text="BristolFDTD (.BristolFDTD)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
