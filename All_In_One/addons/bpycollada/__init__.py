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

# Script copyright (C) Tim Knip, floorplanner.com
# Contributors: Tim Knip (tim@floorplanner.com)

bl_info = {
    'name'       : 'COLLADA format',
    'author'     : 'Tim Knip, Dusan Maliarik',
    'blender'    : (2, 5, 7),
    'api'        : 35622,
    'location'   : 'File > Import',
    'description': 'Import COLLADA',
    'warning'    : '',
    'wiki_url'   : 'https://github.com/skrat/blender-pycollada/wiki',
    'tracker_url': 'https://github.com/skrat/blender-pycollada/issues',
    'support'    : 'OFFICIAL',
    'category'   : 'Import'}


if 'bpy' in locals():
    import imp
    if 'import_collada' in locals():
        imp.reload(import_collada)
    if 'export_collada' in locals():
        imp.reload(export_collada)

import os
import bpy
from bpy.props import BoolProperty
from bpy.props import CollectionProperty
from bpy.props import EnumProperty
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class IMPORT_OT_collada(bpy.types.Operator, ImportHelper):
    """ COLLADA import operator. """

    bl_idname= 'import_scene.collada'
    bl_label = "Import COLLADA"
    bl_options = {'UNDO'}

    filter_glob = StringProperty(
            default='*.dae;*.kmz',
            options={'HIDDEN'},
            )
    files = CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
            )
    directory = StringProperty(
            subtype='DIR_PATH',
            )

    transparent_shadows = BoolProperty(
            default=False,
            name="Transparent shadows",
            description="Import all materials receiving transparent shadows",
            )

    raytrace_transparency = BoolProperty(
            default=False,
            name="Raytrace transparency",
            description="Raytrace transparent materials",
            )

    transformation = EnumProperty(
            name="Transformations",
            items=(
                ('MUL',     "Multiply", ""),
                ('PARENT',  "Parenting", ""),
                ('APPLY',   "Apply", ""),
                ),
            default='MUL'
            )

    def execute(self, context):
        from . import import_collada
        kwargs = self.as_keywords(ignore=('filter_glob', 'files'))
        if not os.path.isfile(kwargs['filepath']):
            self.report({'ERROR'}, "COLLADA import failed, not a file " + \
                    kwargs['filepath'])
            return {'CANCELLED'}
        return import_collada.load(self, context, **kwargs)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class EXPORT_OT_collada(bpy.types.Operator, ExportHelper):
    """ COLLADA export operator. """

    bl_idname= 'export_scene.collada'
    bl_label = "Export COLLADA"
    bl_options = {'UNDO'}

    filename_ext = '.dae'
    filter_glob = StringProperty(
            default='*.dae;*.kmz',
            options={'HIDDEN'},
            )
    directory = StringProperty(
            subtype='DIR_PATH',
            )

    export_as = EnumProperty(
            name="Export as",
            items=(('dae_only', "DAE only", ""),
                   ('dae_textures', "DAE and textures", ""),
                   ('kmz', "KMZ with textures", ""),
                   ),
            default='dae_only',
            )

    axis_up = EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Z',
            )

    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    def execute(self, context):
        from . import export_collada
        kwargs = self.as_keywords(ignore=('filter_glob',))
        if os.path.exists(self.filepath) and \
                not os.path.isfile(self.filepath):
            self.report({'ERROR'}, "COLLADA export failed, not a file " + \
                    kwargs['filepath'])
            return {'CANCELLED'}
        return export_collada.save(self, context, **kwargs)


def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_collada.bl_idname,
            text="COLLADA (py) (.dae, .kmz)")

def menu_func_export(self, context):
    self.layout.operator(EXPORT_OT_collada.bl_idname,
            text="COLLADA (py) (.dae, .kmz)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()

