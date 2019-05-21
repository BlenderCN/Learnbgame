bl_info = {
    "name": "UberEnt PAPA format (Planetary Annihilation)",
    "author": "Raevn",
    "blender": (2, 67, 0),
    "location": "File > Import-Export",
    "description": "Imports/Exports PAPA meshes, uvs, bones and groups",
    "warning": "",
    "wiki_url": "http://forums.uberent.com/forums/viewtopic.php?f=72&t=47964",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    if ("import_papa") in locals():
        imp.reload(import_papa)
    if ("export_papa") in locals():
        imp.reload(export_papa)

import bpy
from bpy.props import *

from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportPAPA(bpy.types.Operator, ImportHelper):
    """Import from PAPA file format (.papa)"""
    bl_idname = "import_scene.uberent_papa"
    bl_label = "Import PAPA"
    bl_options = {'UNDO'}
    
    filename_ext = ".papa"
    filter_glob = StringProperty(default="*.papa", options={'HIDDEN'})

    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for importing the PAPA file", 
        maxlen= 1024, default= "")
    
    def execute(self, context):
        from . import import_papa
        
        return import_papa.load(self, context, self.properties.filepath)
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportPAPA(bpy.types.Operator, ExportHelper):
    """Export to PAPA file format (.papa)"""
    bl_idname = "export_scene.uberent_papa"
    bl_label = "Export PAPA"
    bl_options = {'UNDO'}
    
    filename_ext = ".papa"
    filter_glob = StringProperty(default="*.papa", options={'HIDDEN'})

    filepath = bpy.props.StringProperty(
        name="File Path", 
        description="File path used for exporting the PAPA file", 
        maxlen= 1024, default= "")
    
    def execute(self, context):
        from . import export_papa

        return export_papa.write(self, context, self.properties.filepath)
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportPAPA.bl_idname, text="Planetary Annihilation Model (.papa)")

def menu_func_export(self, context):
    self.layout.operator(ExportPAPA.bl_idname, text="Planetary Annihilation Model (.papa)")

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
