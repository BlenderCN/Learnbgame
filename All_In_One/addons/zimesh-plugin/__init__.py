import bpy
from .export_zimesh_operator import *

bl_info = {
    "name": "Exporter to Zimesh JSON",
    "author": "bajos",
    "description": "Exports scene to Zinot Engine Zimesh JSON format.",
    "category": "Import-Export",
    "location": "File > Export > Zimesh JSON (.json)"
}

def exporterMenu(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(ExportZimesh.bl_idname, text="Zimesh JSON (.json)")
    return None


def register():
    bpy.utils.register_class(ExportZimesh)
    bpy.types.INFO_MT_file_export.append(exporterMenu)
    return None


def unregister():
    bpy.utils.unregister_class(ExportZimesh)
    bpy.types.INFO_MT_file_export.remove(exporterMenu)
    return None
