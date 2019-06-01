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
    "name": "MCell MDL Format",
    "author": "Tom Bartol",
    "version": (0,1),
    "blender": (2, 6, 1),
    "api": 42614,
    "location": "File > Import-Export",
    "description": "Import-Export CellBlender geometry in MCell MDL mesh format regions",
    "warning": "",
    "wiki_url": "http://www.mcell.cnl.salk.edu",
    "tracker_url": "",
    "category": "Learnbgame",
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "export_mcell_mdl" in locals():
        imp.reload(export_mcell_mdl)
    if "import_mcell_mdl" in locals():
        imp.reload(import_mcell_mdl)


import os
import bpy
from bpy.props import CollectionProperty, StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportMCellMDL(bpy.types.Operator, ImportHelper):
    '''Load an MCell MDL geometry file with regions'''
    bl_idname = "import_mdl_mesh.mdl"
    bl_label = "Import MCell MDL"
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MCell MDL file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    add_to_model_objects = BoolProperty(
        name="Add to Model Objects",
        description="Automatically add all meshes to the Model Objects list",
        default=True,)

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)

        # Attempt to use fast swig importer (assuming make was successful)
        try:
            from . import import_mcell_mdl
            from . import mdlmesh_parser

            for path in paths:
                import_mcell_mdl.load(
                    self, context, path, self.add_to_model_objects)

        # Fall back on slow pure python parser (pyparsing)
        except ImportError:
            from . import import_mcell_mdl_pyparsing
        
            for path in paths:
                import_mcell_mdl_pyparsing.load(
                    self, context, path, self.add_to_model_objects)


        return {'FINISHED'}


class ExportMCellMDL(bpy.types.Operator, ExportHelper):
    '''Export selected mesh objects as MCell MDL geometry with regions'''
    bl_idname = "export_mdl_mesh.mdl"
    bl_label = "Export MCell MDL"

    #print ( "io_mesh_mcell_mdl/__init__.py/ExportMCellMDL initialization" )

    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        #print ( "io_mesh_mcell_mdl/__init__.py/ExportMCellMDL.poll()" )
        return len([obj for obj in context.selected_objects if obj.type == 'MESH']) != 0

    def execute(self, context):
        #print ( "io_mesh_mcell_mdl/__init__.py/ExportMCellMDL.execute()" )
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        from . import export_mcell_mdl
        object_list = [obj for obj in context.selected_objects if obj.type == 'MESH']
        with open(filepath, "w", encoding="utf8", newline="\n") as out_file:
            export_mcell_mdl.save_geometry(context, out_file, object_list)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(
        ImportMCellMDL.bl_idname, text="MCell MDL Geometry (.mdl)")


def menu_func_export(self, context):
    self.layout.operator(
        ExportMCellMDL.bl_idname, text="MCell MDL Geometry (.mdl)")


#def register():
#    bpy.utils.register_module(__name__)
#
#    bpy.types.INFO_MT_file_import.append(menu_func_import)
#    bpy.types.INFO_MT_file_export.append(menu_func_export)


#def unregister():
#    bpy.utils.unregister_module(__name__)
#
#    bpy.types.INFO_MT_file_import.remove(menu_func_import)
#    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
