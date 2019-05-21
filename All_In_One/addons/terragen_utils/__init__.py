'''
Copyright (C) 2017 Walter Perdan
info@kalwaltart.it

Created by WALTER PERDAN

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import bpy
import sys
import string
import struct
import os  # glob
from os import path, name, sep
from .ter_importer import import_ter
from .ter_exporter import export_ter
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (StringProperty, BoolProperty, EnumProperty,
                       IntProperty, FloatProperty, FloatVectorProperty)
from bpy.types import Operator


bl_info = {
    "name": "Terragen utils",
    "description": "addon to import/export .ter files",
    "author": "Walter Perdan",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "warning": "This addon is still in development.",
    "wiki_url": "https://github.com/kalwalt/terragen_utils/wiki",
    "tracker_url": "https://github.com/kalwalt/terragen_utils/issues",
    "category": "Learnbgame"
}


class ImportTer(Operator, ImportHelper):
    """Operator to import .ter Terragen files into blender as obj"""
    bl_idname = "import_ter.data"
    bl_label = "Import .ter"
    # bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".ter"

    filter_glob = StringProperty(
        default="*.ter",
        options={'HIDDEN'},
        maxlen=255,)  # Max internal buffer length, longer would be clamped.

    triangulate = BoolProperty(
        name="Triangulate",
        description="triangulate the terrain mesh",
        default=False)

    custom_properties = BoolProperty(
        name="CustomProperties",
        description="set custom properties of the terrain: size, scale,\
        baseheight, heightscale",
        default=False)

    custom_scale = FloatVectorProperty(
        name="CustomScale",
        description="set a custom scale of the terrain",
        default=(30.0, 30.0, 30.0))

    baseH = IntProperty(
        name="BaseHeight",
        description="set the baseheight of the terrain",
        default=0)

    heightS = IntProperty(
        name="HeightScale",
        description="set the maximum height of the terrain",
        default=100)

    def draw(self, context):
        layout = self.layout
        c = layout.column()
        c.label(text="Import a .ter file:", icon='IMPORT')
        layout.separator()
        layout.prop(self, 'triangulate')
        layout.prop(self, 'custom_properties')
        if self.custom_properties is True:
            c = layout.column()
            c.prop(self, 'custom_scale', text='Set the scale(x,y,z)', expand=False)
            layout.prop(self, 'baseH')
            layout.prop(self, 'heightS')

    def execute(self, context):
        return import_ter(self, context, self.filepath, self.triangulate,
                          self.custom_properties, self.custom_scale,
                          self.baseH, self.heightS)


class ExportTer(Operator, ExportHelper):
    """Operator to export .ter Terragen files"""
    bl_idname = "export_ter.data"
    bl_label = "Export .ter"
    # bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".ter"

    filter_glob = StringProperty(
        default="*.ter",
        options={'HIDDEN'},
        maxlen=255,)  # Max internal buffer length, longer would be clamped.

    custom_properties = BoolProperty(
        name="CustomProperties",
        description="set custom properties of the terrain: size, scale,\
        baseheight, heightscale",
        default=False)

    custom_scale = FloatVectorProperty(
        name="CustomScale",
        description="set a custom scale of the terrain",
        default=(30.0, 30.0, 30.0))

    baseH = IntProperty(
        name="BaseHeight",
        description="set the baseheight of the terrain",
        default=0)

    heightS = IntProperty(
        name="HeightScale",
        description="set the maximum height of the terrain",
        default=100)

    def draw(self, context):
        layout = self.layout
        c = layout.column()
        c.label(text="Export a .ter file:", icon='EXPORT')
        layout.separator()
        layout.prop(self, 'custom_properties')

        if self.custom_properties is True:
            c = layout.column()
            c.prop(self, 'custom_scale', text='Set the scale(x,y,z)', expand=False)
            layout.prop(self, 'baseH')
            layout.prop(self, 'heightS')

    def execute(self, context):
        return export_ter(self, context, self.filepath, self.custom_properties,
                          self.custom_scale, self.baseH, self.heightS)


def menu_func_import(self, context):
    self.layout.operator(ImportTer.bl_idname, text="Terragen (.ter)")


def menu_func_export(self, context):
    self.layout.operator(ExportTer.bl_idname, text="Terragen (.ter)")


def register():
    bpy.utils.register_class(ImportTer)
    bpy.utils.register_class(ExportTer)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportTer)
    bpy.utils.unregister_class(ExportTer)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
