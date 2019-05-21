bl_info = {
    "name":         "FrostTree MDL Import-Export",
    "author":       "FrostTree Games",
    "blender":      (2,8,2),
    "version":      (0,0,1),
    "location":     "File > Import-Export",
    "description":  "Export MDL file formats",
    "category":     "Import-Export"
}

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.props import StringProperty

#from io_quakemdl import mdl2Mesh

class ImportMDLFormat(bpy.types.Operator, ImportHelper):
    """Load a Quake MDL file"""

    bl_idname       = "import_mesh.quake_mdl_v6"
    bl_label        = "FrostTree MDL Import"

    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    def execute(self, context):
        from . import import_mdl
        keywords = self.as_keywords (ignore=("filter_glob",))
        return import_mdl.import_mdl(self, context, **keywords)
    

class ExportMDLFormat(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_mesh.quake_mdl_v6"
    bl_label        = "FrostTree MDL Export"
    
    filename_ext    = ".mdl"
    def execute(self, context):
        print('inside exporter')
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportMDLFormat.bl_idname, text = "FrostTree MDL Import Format(.mdl)")

def menu_func_export(self, context):
    self.layout.operator(ExportMDLFormat.bl_idname, text="FrostTree MDL Export Format(.mdl)")

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
