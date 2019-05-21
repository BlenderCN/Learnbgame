bl_info = {
    "name": "Serious Editor ASCII formats",
    "author": "Tomislav Kristo & nano",
    "version": (1,0),
    "blender": (2,7,8),
    "api": 33333,
    "location": "File > Import-Export > Serious Editor 3 ASCII",
    "description": "Allows for the import & export of various data formats used by Serious Editor.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}
    
if "bpy" in locals():
    import imp
    if "blutils" in locals():
        imp.reload(blutils)
    if "se3" in locals():
        imp.reload(se3)
    if "import_amf" in locals():
        imp.reload(import_amf)
    if "import_asf" in locals():
        imp.reload(import_asf)
    if "export_amf" in locals():
        imp.reload(export_amf)
    if "export_asf" in locals():
        imp.reload(export_asf)
    if "export_aaf" in locals():
        imp.reload(export_aaf)

import bpy

from bpy.props import BoolProperty

from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper

class ImportSEd3AMF(bpy.types.Operator, ImportHelper):
    """Import ASCII Mesh File as mesh object in current scene"""
    bl_idname = "import_mesh.sed3_amf"
    bl_label = "Import AMF"

    filename_ext = ".amf"
    filter_glob = bpy.props.StringProperty(default="*.amf", options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        from . import import_amf
        return import_amf.read_file(self, context)

class ImportSEd3ASF(bpy.types.Operator, ImportHelper):
    """Import ASCII Skeleton File as armature object in current scene"""
    bl_idname = "import_armature.sed3_asf"
    bl_label = "Import ASF"

    filename_ext = ".asf"
    filter_glob = bpy.props.StringProperty(default="*.asf", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        from . import import_asf
        return import_asf.se3_get_skeleton_from_file(self, context)

class ExportSEd3AMF(bpy.types.Operator, ExportHelper):
    """Export selected meshes to ASCII Mesh File layers"""
    bl_idname = "export_mesh.sed3_amf"
    bl_label = "Export AMF"
    
    filename_ext = ".amf"
    filter_glob = bpy.props.StringProperty(default="*.amf", options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selected_objects = list(context.selected_objects)
        
        if not selected_objects:
            if active_object:
                selected_objects.append(active_object)
            else:
                return False
        
        for object in selected_objects:
            if object.type != 'MESH':
                return False
        
        return True
    
    def execute(self, context):
        from . import export_amf
        return export_amf.write_file(self.filepath, context)

class ExportSEd3ASF(bpy.types.Operator, ExportHelper):
    """Export active armature to ASCII Skeleton File"""
    bl_idname = "export_armature.sed3_asf"
    bl_label = "Export ASF"
    
    filename_ext = ".asf"
    filter_glob = bpy.props.StringProperty(default="*.asf", options={'HIDDEN'})
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'
    
    def execute(self, context):
        from . import export_asf
        return export_asf.write_file(self.filepath, context)

class ExportSEd3AAF(bpy.types.Operator, ExportHelper):
    """Export selected object animation from playback to ASCII Animation File"""
    bl_idname = "export_animation.sed3_aaf"
    bl_label = "Export AAF"
    
    filename_ext = ".aaf"
    filter_glob = bpy.props.StringProperty(default="*.aaf", options={'HIDDEN'})
    
    animation_name = bpy.props.StringProperty(name="Animation Name", description="Animation name to export", maxlen=256)
    
    @classmethod
    def poll(self, context):
        return context.active_object != None
        
    def execute(self, context):
        from . import export_aaf
        return export_aaf.write_file(self.filepath, self.animation_name, context)

class INFO_MT_file_import_sed3(bpy.types.Menu):
    bl_idname = "INFO_MT_file_import_sed3"
    bl_label = "Serious Editor ASCII (.amf)"
    
    def draw(self, context):
        self.layout.operator(ImportSEd3AMF.bl_idname, text="Mesh File (.amf)")
        #self.layout.operator(ImportSEd3ASF.bl_idname, text="Skeleton File (.asf)")

class INFO_MT_file_export_sed3(bpy.types.Menu):
    bl_idname = "INFO_MT_file_export_sed3"
    bl_label = "Serious Editor ASCII (.amf, .asf, .aaf)"
    
    def draw(self, context):
        self.layout.operator(ExportSEd3AMF.bl_idname, text="Mesh File (.amf)")
        self.layout.operator(ExportSEd3ASF.bl_idname, text="Skeleton File (.asf)")
        self.layout.operator(ExportSEd3AAF.bl_idname, text="Animation File (.aaf)")

def menu_func_import(self, context):
    self.layout.menu("INFO_MT_file_import_sed3")

def menu_func_export(self, context):
    self.layout.menu("INFO_MT_file_export_sed3")

def register():
    bpy.utils.register_class(ImportSEd3AMF)
    #bpy.utils.register_class(ImportSEd3ASF)
    
    bpy.utils.register_class(ExportSEd3AMF)
    bpy.utils.register_class(ExportSEd3ASF)
    bpy.utils.register_class(ExportSEd3AAF)
    
    bpy.utils.register_class(INFO_MT_file_import_sed3)
    bpy.utils.register_class(INFO_MT_file_export_sed3)
    
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportSEd3AMF)
    #bpy.utils.unregister_class(ImportSEd3ASF)

    bpy.utils.unregister_class(ExportSEd3AMF)
    bpy.utils.unregister_class(ExportSEd3ASF)
    bpy.utils.unregister_class(ExportSEd3AAF)
    
    bpy.utils.unregister_class(INFO_MT_file_import_sed3)
    bpy.utils.unregister_class(INFO_MT_file_export_sed3)
    
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()