
if "bpy" in locals():
    import imp
    if "fenrir_export" in locals():
        imp.reload(fenrir_export)

import bpy
from io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty

bl_info = {
    "name": "Fenrir Mesh Export (.fent/.fani) Test",
    "author": "Karanlos (Erik Holm Sejersen)",
    "version": (0, 0, 1),
    "blender": (2, 5, 7),
    "api": 36079,
    "location": "File > Export > Fenrir (.fent/.fani)",
    "description": "Export to Fenrir Format (.fent/.fani)",
    "warning": "Won't really export anything usefull yet",
    "wiki_url": "http://rimfrost.co.uk/fenrir.html",
    "tracker_url": "",
    "category": "Learnbgame"
}

class FenrirExport(bpy.types.Operator, ExportHelper):
    bl_idname = "export.entity_data"
    bl_label = "Export Selected Mesh"
    
    filename_ext = ".fenent"
    
    use_setting = BoolProperty(name="Test Bool", description="Exmplate Tooltip", default=False)
    
    @classmethod
    def poll(cls, context):
        return context.active_object != None
    
    def execute(self, context):
        from . import fenrir_export
        return fenrir_export.writeData(context, self.filepath, self.use_setting)

def menu_func_export(self, context):
    self.layout.operator(FenrirExport.bl_idname, text="Export mesh, animation data to Fenrir engine")

def register():
    bpy.utils.register_class(FenrirExport)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(FenrirExport)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
    
    #Test
    bpy.ops.export.entity_data('INVOKE_DEFAULT')
