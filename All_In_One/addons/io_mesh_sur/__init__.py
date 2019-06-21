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
    "name": "SUR format",
    "author": "Marius Giurgi (DolphinDream)",
    "version": (2, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > Sur",
    "description": "Import-Export SUR files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'OFFICIAL',
    "category": "Learnbgame",
    }

# @todo write the wiki page

"""
Import-Export SUR files (ascii)

- Export can export with/without modifiers applied

"""

if "bpy" in locals():
    import importlib
    if "sur_utils" in locals():
        importlib.reload(sur_utils)
    if "blender_utils" in locals():
        importlib.reload(blender_utils)

import os

import bpy
from bpy.props import (
        StringProperty,
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        FloatProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        axis_conversion,
        )
from bpy.types import (
        Operator,
        OperatorFileListElement,
        )


class ImportSUR(bpy.types.Operator, ImportHelper):
    '''Load SUR triangle mesh data'''
    bl_idname = "import_mesh.sur"
    bl_label = "Import SUR"

    filename_ext = ".sur"

    filter_glob: StringProperty(
            default="*.sur",
            options={'HIDDEN'})

    files: CollectionProperty(
        name="File Path",
        description="File path used for importing the SUR file",
        type=bpy.types.OperatorFileListElement)

    directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        from . import sur_utils
        from . import blender_utils

        paths = [os.path.join(self.directory, name.name) for name in self.files]

        if not paths:
            paths.append(self.filepath)

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action='DESELECT')

        for path in paths:
            objName = bpy.path.display_name(os.path.basename(path))
            tris, pts = sur_utils.readSUR(path)

            blender_utils.create_and_link_mesh(objName, tris, pts)

        return {'FINISHED'}


class ExportSUR(bpy.types.Operator, ExportHelper):
    '''
    Save SUR triangle mesh data from the active object
    '''
    bl_idname = "export_mesh.sur"
    bl_label = "Export SUR"

    filename_ext = ".sur"

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply the modifiers before saving",
        default=True)

    def execute(self, context):
        from . import sur_utils
        from . import blender_utils

        obj = context.selected_objects[0]

        # apply the modifier ?
        try:
            mesh = obj.to_mesh(bpy.context.depsgraph, self.apply_modifiers)

        except SystemError:
            return ()

        # make list of vertex coordinates
        verts = []
        for vert in mesh.vertices:
            verts.append(vert.co)

        # make list of face vertex indices
        faces = []
        for face in mesh.polygons:
            # triangulate if necessary
            if len(face.vertices) == 4:
                f = [face.vertices[0], face.vertices[1], face.vertices[2]]
                faces.append(f)
                f = [face.vertices[2], face.vertices[3], face.vertices[0]]
                faces.append(f)
            else:
                f = [face.vertices[0], face.vertices[1], face.vertices[2]]
                faces.append(f)

        # save the surface
        sur_utils.writeSUR(self.filepath, faces, verts)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(ImportSUR.bl_idname,
                         text="SUR (.sur)").filepath = "*.sur"


def menu_export(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".sur"
    self.layout.operator(ExportSUR.bl_idname,
                         text="SUR (.sur)").filepath = default_path


classes = (
    ImportSUR,
    ExportSUR
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_export)


if __name__ == "__main__":
    register()
