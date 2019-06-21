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

# Script copyright (C) Li Jun (AKA oyster @blenderartists.org, @blendercn.org)
# Contributors: Li Jun




bl_info = {
    "name": "LEGO LDRAW data (.dat, .ldr, .mpd) I/O",
    "author": "Li Jun",
    "version": (0, 0, 1),
    "blender": (2, 57, 0),
    "location": "File > Import-Export > LEGO LDRAW Faces (.dat, .ldr, .mpd) ",
    "description": "Import LEGO Dat/Ldr/Mpd into Blender; export Blender to LEGO Dat",
    "warning": "",
    "wiki_url": "https://github.com/retsyo/io_scene_legoldraw",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import importlib
    if "import_legoldraw" in locals():
        importlib.reload(import_legoldraw)
    if "export_legoldraw" in locals():
        importlib.reload(export_legoldraw)
else:
    import bpy

from bpy.props import StringProperty, BoolProperty,FloatProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper


class LegoLdrawImporter(bpy.types.Operator):
    """Load LEGO LDRAW data"""
    bl_idname = "import_mesh.legoldraw"
    bl_label = "Import Lego Ldraw"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.dat;*.ldr;*.mpd", options={'HIDDEN'})

    global_scale = FloatProperty(
            name="Scale",
            description='resize imported LEGO model',
            min=0.001, max=1000.0,
            default=0.04,
            )


    useMathutils = BoolProperty(
            name="use mathutils",
            description='if selected, use mathutils to speed up; else use pure python',
            default=True,
            )

    removeDoubles = BoolProperty(
            name="Remove doubles",
            description='if selected, remove doubles; else do not remove doubles',
            default=True,
            )


    useEditmode = EnumProperty(
            name="After import, goto",
            items=(('EDIT', "EDIT Mode", ""),
                   ('OBJECT', "OBJECT Mode", ""),
                   ),
            default='EDIT',
            )


    def execute(self, context):
        from . import import_legoldraw
        import_legoldraw.read(self.filepath, self.global_scale,
            self.useMathutils, self.removeDoubles, self.useEditmode)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LegoLdrawExporter(bpy.types.Operator, ExportHelper):
    """Save LEGO LDRAW data"""
    bl_idname = "export_mesh.legoldraw"
    bl_label = "Export Lego Ldraw"

    filename_ext = ".dat"
    filter_glob = StringProperty(default="*.dat", options={'HIDDEN'})

    onlyVisible = BoolProperty(
            name="Export invisible object too",
            description=('if selected, export visible and invisible objects;\n'
                'else export visible objects only'),
            default=True,
            )
    use_selection = BoolProperty(
            name="Export Selected only",
            description=('if selected, export selected objects only;\n'
                'else export all possible objects'),
            default=False,
            )

    def execute(self, context):
        from . import export_legoldraw
        export_legoldraw.write(self.filepath,
                         self.onlyVisible,
                         self.use_selection,
                         )

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(LegoLdrawImporter.bl_idname, text="Lego Ldraw (.dat; .ldr; .mpd)")


def menu_export(self, context):
    self.layout.operator(LegoLdrawExporter.bl_idname, text="Lego Ldraw (.dat)")


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
