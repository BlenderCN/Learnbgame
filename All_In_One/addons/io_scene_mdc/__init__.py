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


bl_info = {
    "name": "RtCW/ET Model (.mdc)",
    "author": "Norman Mitschke",
    "version": (0, 9, 0),
    "blender": (2, 69, 0),
    "location": "File > Import-Export > RtCW/ET Model (.mdc)",
    "description": "MDC Model format (.mdc)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export",
}


import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportMDC(bpy.types.Operator, ImportHelper):

    '''Import a RtCW Model MDC file'''
    bl_idname = "import_scene.mdc"
    bl_label = 'Import MDC'
    filename_ext = ".mdc"
    filter_glob = StringProperty(default="*.mdc", options={'HIDDEN'})

    toNewScene = BoolProperty(
            name="To New Scene",
            description="Import model to new scene",
            default=True,
            )

    normals = EnumProperty(
            name="Vertex Normals",
            description="Select import method of vertex normals",
            items= [('blender', "Blender", ""),('mdcObject', "MDC as objects","")],
            default='blender',
            )

    normalsLayer = EnumProperty(
            name="Normals Layer",
            description="Define layer for normal objects (optional)",
            items= [('1', "Layer 1", ""),('2', "Layer 2", ""),('3', "Layer 3","")],
            default='1',
            )

    gamePath = StringProperty(
          name = "Game Path",
          default = "",
          description = "Define game path for model textures (optional)",
          )


    def execute(self, context):

        from . import mdc_modules
        from .mdc_modules.options import ImportOptions

        importOptions = ImportOptions(self.properties.filepath, \
                                      self.gamePath, \
                                      self.toNewScene, \
                                      self.normals, \
                                      self.normalsLayer)

        from .import_mdc import MDCImport

        errMsg = MDCImport().run(importOptions)
        if errMsg != None:
            self.report({'ERROR'}, "MDCImport error: " + errMsg)
            print("MDCImport error: " + errMsg)
            return {'CANCELLED'}

        print("MDCImport ok.")

        return {'FINISHED'}


    def draw(self, context):

        row = self.layout.row(align=True)

        self.layout.prop(self, "toNewScene")

        self.layout.prop(self, "gamePath")

        self.layout.prop(self, "normals")
        self.layout.prop(self, "normalsLayer")


class ExportMDC(bpy.types.Operator, ExportHelper):

    '''Export a RtCW Model MDC file'''
    bl_idname = "export_scene.mdc"
    bl_label = 'Export MDC'
    filename_ext = ".mdc"
    filter_glob = StringProperty(default="*.mdc", options={'HIDDEN'})

    selection = BoolProperty(
            name="Selected Objects",
            description="Include only selected objects",
            default=False,
            )

    normalObjects = BoolProperty(
            name="Object Vertex Normals",
            description="Include vertex normal objects",
            default=True,
            )


    def execute(self, context):

        from . import mdc_modules
        from .mdc_modules.options import ExportOptions

        exportOptions = ExportOptions(self.properties.filepath, \
                                      self.selection, \
                                      self.normalObjects)

        from .export_mdc import MDCExport

        errMsg = MDCExport().run(exportOptions)
        if errMsg != None:
            self.report({'ERROR'}, "MDCExport error: " + errMsg)
            print("MDCExport error: " + errMsg)
            return {'CANCELLED'}

        print("MDCExport ok.")

        return {'FINISHED'}


    def draw(self, context):

        row = self.layout.row(align=True)

        self.layout.prop(self, "selection")

        self.layout.prop(self, "normalObjects")


def menu_func_import(self, context):
    self.layout.operator(ImportMDC.bl_idname, text=bl_info['name'])

def menu_func_export(self, context):
    self.layout.operator(ExportMDC.bl_idname, text=bl_info['name'])


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
