bl_info = {
    "name": "Quake 3 Model (.md3)",
    "author": "Vitaly Verhovodov",
    "version": (0, 2, 1),
    "blender": (2, 72, 0),
    "location": "File > Import-Export > Quake 3 Model",
    "description": "Quake 3 Model format (.md3)",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/MD3",
    "tracker_url": "https://github.com/neumond/blender-md3/issues",
    "category": "Import-Export",
}


import bpy
import struct
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportMD3(bpy.types.Operator, ImportHelper):
    '''Import a Quake 3 Model MD3 file'''
    bl_idname = "import_scene.md3"
    bl_label = 'Import MD3'
    filename_ext = ".md3"
    filter_glob = StringProperty(default="*.md3", options={'HIDDEN'})

    def execute(self, context):
        from .import_md3 import MD3Importer
        MD3Importer(context)(self.properties.filepath)
        return {'FINISHED'}


class ExportMD3(bpy.types.Operator, ExportHelper):
    '''Export a Quake 3 Model MD3 file'''
    bl_idname = "export_scene.md3"
    bl_label = 'Export MD3'
    filename_ext = ".md3"
    filter_glob = StringProperty(default="*.md3", options={'HIDDEN'})

    def execute(self, context):
        try:
            from .export_md3 import MD3Exporter
            MD3Exporter(context)(self.properties.filepath)
            return {'FINISHED'}
        except struct.error:
            self.report({'ERROR'}, "Mesh does not fit within the MD3 model space. Vertex axies locations must be below 512 blender units.")
        except ValueError as e:
            self.report({'ERROR'}, str(e))
        return {'CANCELLED'}


def menu_func_import(self, context):
    self.layout.operator(ImportMD3.bl_idname, text="Quake 3 Model (.md3)")


def menu_func_export(self, context):
    self.layout.operator(ExportMD3.bl_idname, text="Quake 3 Model (.md3)")


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
