import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
from mdl_writer import *


bl_info = {
    'name': "Four-kb model exporter",
    'author': 'Julian Goldsmith',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': "File > Export",
    'description': "Export Four-kb model",
    "category": "Learnbgame",
}


class MdlExporter(bpy.types.Operator, ExportHelper):
    bl_idname = 'export.fourkb'
    bl_label = 'Export Four-kb'
        
    filename_ext = '.mdl'
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})
        
    def execute(self, context):
        write(self.filepath)
        return {'FINISHED'}
    
        
def menu_export(self, context):
    self.layout.operator(MdlExporter.bl_idname, text="Four-kb model (.mdl)")
    
def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.INFO_MT_file_export.append(menu_export)
    
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.INFO_MT_file_export.remove(menu_export)

#if __name__ == "__main__":
#    register()