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

# Script copyright (C) Thomas PORTASSAU (50thomatoes50)
# Contributors: Campbell Barton, Jiri Hnidek, Paolo Ciccone, Thomas Larsson, http://blender.stackexchange.com/users/185/adhi


# <pep8-80 compliant>

bl_info = {
    "name": "Metasequoia format (.mqo)",
    "author": "Thomas Portassau (50thomatoes50), sapper-trle@github, jacquesmn@github",
    "blender": (2, 65, 0),
    "location": "File > Import-Export",
    "description": "Import-Export MQO, UV's, "
                   "materials and textures",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/MQO",
    "tracker_url": "https://github.com/50thomatoes50/blender.io_mqo/issues",
    "category": "Learnbgame"
}


#http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Multi-File_packages#init_.py
if "bpy" in locals():
    import imp
    if "import_mqo" in locals():
        imp.reload(import_mqo)
    if "export_mqo" in locals():
        imp.reload(export_mqo)

import os
import bpy
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       )
from bpy_extras.io_utils import (ExportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )


class ExportMQO(bpy.types.Operator, ExportHelper):
    bl_idname = "io_export_scene.mqo"
    bl_description = 'Export from mqo file format (.mqo)'
    bl_label = "Export mqo"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    # From ExportHelper. Filter filenames.
    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo", options={'HIDDEN'})

    scale = bpy.props.FloatProperty(
        name = "Scale",
        description="Scale mesh. Value > 1 means bigger, value < 1 means smaller",
        default = 1, min = 0.001, max = 1000.0)

    rot90 = bpy.props.BoolProperty(
        name = "Up axis correction",
        description="Blender up axis is Z but metasequoia up axis is Y\nExporter will invert value to be in the correcte direction",
        default = True)

    invert = bpy.props.BoolProperty(
        name = "Correction of inverted faces",
        description="Correction of inverted faces",
        default = True)

    edge = bpy.props.BoolProperty(
        name = "Export lost edge",
        description="Export edge with is not attached to a polygon",
        default = True)

    uv_exp = bpy.props.BoolProperty(
        name = "Export UV",
        description="Export UV",
        default = True)

    uv_cor = bpy.props.BoolProperty(
        name = "Convert UV",
        description="invert UV map to be in the direction has metasequoia",
        default = True)

    mat_exp = bpy.props.BoolProperty(
        name = "Export Materials",
        description="...",
        default = True)

    mod_exp = bpy.props.BoolProperty(
        name = "Export Modifier",
        description="Export modifier like mirror or/and subdivision surface",
        default = True)

    vcol_exp = bpy.props.BoolProperty(
        name = "Export Vertex Colors",
        description="Export vertex colors",
        default = True)

    def execute(self, context):
        msg = ".mqo export: Executing"
        self.report({'INFO'}, msg)
        print(msg)
        if self.scale < 1:
            s = "%.0f times smaller" % 1.0/self.scale
        elif self.scale > 1:
            s = "%.0f times bigger" % self.scale
        else:
            s = "same size"
        msg = ".mqo export: Objects will be %s"%(s)
        print(msg)
        self.report({'INFO'}, msg)
        from . import export_mqo
        meshobjects = [ob for ob in context.scene.objects if ob.type == 'MESH']
        export_mqo.export_mqo(self,
            self.properties.filepath,
            meshobjects,
            self.rot90, self.invert, self.edge, self.uv_exp, self.uv_cor, self.mat_exp, self.mod_exp, self.vcol_exp,
            self.scale)
        return {'FINISHED'}

    def invoke(self, context, event):
        meshobjects = [ob for ob in context.scene.objects if ob.type == 'MESH']
        if not meshobjects:
            msg = ".mqo export: Cancelled - No MESH objects to export."
            self.report({'ERROR'}, msg)
            print(msg,"\n")
            return{'CANCELLED'}
        pth, fn = os.path.split(bpy.data.filepath)
        nm, xtn = os.path.splitext(fn)
        if nm =="":
            nm = meshobjects[0].name
        self.properties.filepath = nm
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ImportMQO(bpy.types.Operator, ExportHelper):
    bl_idname = "io_import_scene.mqo"
    bl_description = 'Import from mqo file format (.mqo)'
    bl_label = "Import mqo"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    # From ExportHelper. Filter filenames.
    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo", options={'HIDDEN'})

    scale = bpy.props.FloatProperty(
        name = "Scale",
        description="Scale mesh. Value > 1 means bigger, value < 1 means smaller",
        default = 1, min = 0.001, max = 1000.0)

    rot90 = bpy.props.BoolProperty(
        name = "Up axis correction",
        description="Blender up axis is Z but metasequoia up axis is Y\nExporter will invert value to be in the correcte direction",
        default = True)

    debug = bpy.props.BoolProperty(
        name = "Show debug text",
        description="Print debug text to console",
        default = False)

    def execute(self, context):
        msg = ".mqo import: Opening %s"% self.properties.filepath
        print(msg)
        self.report({'INFO'}, msg)
        if self.scale < 1:
            s = "%.0f times smaller" % (1.0/self.scale)
        elif self.scale > 1:
            s = "%.0f times bigger" % self.scale
        else:
            s = "same size"
        msg = ".mqo import: Objects will be %s"%(s)
        print(msg)
        self.report({'INFO'}, msg)
        from . import import_mqo
        import_mqo.import_mqo(self,
            self.properties.filepath,
            self.rot90,
            self.scale,
            self.debug)
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportMQO.bl_idname, text="Metasequoia (.mqo)")


def menu_func_export(self, context):
    self.layout.operator(ExportMQO.bl_idname, text="Metasequoia (.mqo)")


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
