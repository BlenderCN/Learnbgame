bl_info = {
    "name": "JSON Mesh Export",
    "author": "Nathan Faucett",
    "blender": (2,6,8),
    "version": (0,0,2),
    "location": "File > Import-Export",
    "description":  "Import-Export JSON data format (only export avalable now)",
    "category": "Learnbgame",
    "wiki_url": "https://github.com/warmwaffles/io_mesh_json",
    "tracker_url": "https://github.com/warmwaffles/io_mesh_json",
}

import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper


# ################################################################
# Import JSON
# ################################################################

class ImportJSON( bpy.types.Operator, ImportHelper ):
    bl_idname = "import.json"
    bl_label = "Import JSON"

    filename_ext = ".json"
    filter_glob = StringProperty( default="*.json", options={"HIDDEN"})
    
    def execute( self, context ):
        import io_mesh_json.import_json
        return io_mesh_json.import_json.load( self, context, **self.properties )


# ################################################################
# Export JSON
# ################################################################

class ExportJSON( bpy.types.Operator, ExportHelper ):
    bl_idname = "export.json"
    bl_label = "Export JSON"

    filename_ext = ".json"
    
    def invoke( self, context, event ):
        return ExportHelper.invoke( self, context, event )
    
    @classmethod
    def poll( cls, context ):
        return context.active_object != None
    
    def execute( self, context ):
        print("Selected: " + context.active_object.name )
        
        if not self.properties.filepath:
            raise Exception("filename not set")
        
        filepath = self.filepath
        
        import io_mesh_json.export_json
        return io_mesh_json.export_json.save( self, context, **self.properties )


# ################################################################
# Common
# ################################################################

def menu_func_export( self, context ):
    default_path = bpy.data.filepath.replace(".blend", ".json")
    self.layout.operator( ExportJSON.bl_idname, text="JSON (.json)").filepath = default_path

def menu_func_import( self, context ):
    self.layout.operator( ImportJSON.bl_idname, text="JSON (.json)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
