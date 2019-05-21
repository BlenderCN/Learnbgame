import time
import datetime
import bpy
from bpy.props import StringProperty

bl_info = {
    'name': 'Skyfallen TheEngine 3D Data Importer',
    'author': 'Danil Gulin',
    'location': 'File > Import',
    'description': 'This script imports BMS and BMA files',
    'warning': '',
    'category': 'Import'
}


class ImportGeometry(bpy.types.Operator):
    bl_idname = 'import_geometry.skyfallen_geometry'
    bl_label = 'Skyfallen Geometry (*.bms, *.bma)'

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default='*.bms;*.bma', options={'HIDDEN'})

    def execute(self, context):
        print('Importing file', self.filepath)
        from . import import_geometry
        with open(self.filepath, 'rb') as file:
            import_geometry.read(file, context, self)
        return {'FINISHED'}

    def invoke(self, context, event):
        del event
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import_geometry(self, context):
    del context
    self.layout.operator(ImportGeometry.bl_idname, text=ImportGeometry.bl_label)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import_geometry)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import_geometry)


if __name__ == "__main__":
    register()
