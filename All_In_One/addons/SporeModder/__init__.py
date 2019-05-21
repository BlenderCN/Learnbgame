try:
    import pydevd
    pydevd.settrace(stdoutToServer=True, stderrToServer=True, suspend=False)
except ImportError:
    pass

bl_info = {
    "name": "SporeModder Add-ons",
    "author": "Emd4600",
    "blender": (2, 7, 1),
    "version": (2, 0, 0),
    "location": "File > Import-Export",
    "description": "Import Spore .gmdl, .gmsh, .bmdl and .rw4 model formats. Exports .rw4 format.",
    "category": "Import-Export"
}

import sporemodder
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportBMDL(bpy.types.Operator, ImportHelper):
    bl_idname = "import_my_format.bmdl"
    bl_label = "Import BMDL"

    filename_ext = ".bmdl"
    filter_glob = bpy.props.StringProperty(default="*.bmdl", options={'HIDDEN'})

    def execute(self, context):
        from sporemodder.BMDLImporter import importBMDL

        file = open(self.filepath, 'br')
        result = {'CANCELLED'}
        try:
            result = importBMDL(file)
        finally:
            file.close()

        return result
    
    
class ImportGMDL(bpy.types.Operator, ImportHelper):
    bl_idname = "import_my_format.gmdl"
    bl_label = "Import GMDL"

    filename_ext = ".gmdl"
    filter_glob = bpy.props.StringProperty(default="*.gmdl", options={'HIDDEN'})

    def execute(self, context):
        from sporemodder.gmdlImporter import importGMDL

        file = open(self.filepath, 'br')
        result = {'CANCELLED'}
        try:
            result = importGMDL(file)
        finally:
            file.close()

        return result


class ImportGMSH(bpy.types.Operator, ImportHelper):
    bl_idname = "import_my_format.gmsh"
    bl_label = "Import GMSH"

    filename_ext = ".gmsh"
    filter_glob = bpy.props.StringProperty(default="*.gmsh", options={'HIDDEN'})

    def execute(self, context):
        from sporemodder.gmshImporter import importGMSH

        file = open(self.filepath, 'br')
        result = {'CANCELLED'}
        try:
            result = importGMSH(file)
        finally:
            file.close()

        return result


class ImportRW4(bpy.types.Operator, ImportHelper):
    bl_idname = "import_my_format.rw4"
    bl_label = "Import RW4"

    filename_ext = ".rw4"
    filter_glob = bpy.props.StringProperty(default="*.rw4", options={'HIDDEN'})

    importMaterials = bpy.props.BoolProperty(
        name="Import Materials",
        description="",
        default=True
    )
    importSkeleton = bpy.props.BoolProperty(
        name="Import Skeleton",
        description="",
        default=True
    )
    importMovements = bpy.props.BoolProperty(
        name="Import Movements",
        description="If present, import movements",
        default=True
    )

    def execute(self, context):
        from sporemodder import RW4Importer

        settings = RW4Importer.RW4ImporterSettings()
        settings.importMaterials = self.importMaterials
        settings.importSkeleton = self.importSkeleton
        settings.importMovements = self.importMovements

        file = open(self.filepath, 'br')
        result = {'CANCELLED'}
        try:
            result = RW4Importer.importRW4(file, settings)
        finally:
            file.close()

        return result


class ImportRW4Old(bpy.types.Operator, ImportHelper):
    bl_idname = "import_my_format.rw4_old"
    bl_label = "Import RW4 Old"

    filename_ext = ".rw4"
    filter_glob = bpy.props.StringProperty(default="*.rw4", options={'HIDDEN'})

    def execute(self, context):
        from sporemodder import RW4ImporterOld

        file = open(self.filepath, 'br')
        result = {'CANCELLED'}
        try:
            result = RW4ImporterOld.importRW4(file)
        finally:
            file.close()

        return result


class ExportRW4(bpy.types.Operator, ExportHelper):
    bl_idname = "export_my_format.rw4"
    bl_label = "Export RW4"

    filename_ext = ".rw4"
    filter_glob = bpy.props.StringProperty(default="*.rw4", options={'HIDDEN'})

    exportHandles = bpy.props.BoolProperty(
        name="Export Morphs",
        description="Export all actions marked as 'Use as morph'",
        default=True
    )
    exportAnims = bpy.props.BoolProperty(
        name="Export Movements",
        description="Export all action not marked as 'Use as morph",
        default=True
    )
    useLogging = bpy.props.BoolProperty(
        name="Create log file",
        description="Write a log in the path where you export the file",
        default=False
    )

    def execute(self, context):
        from sporemodder.RW4Exporter import exportRW4

        file = open(self.filepath, 'bw')
        result = {'CANCELLED'}
        try:
            result = exportRW4(file)
        finally:
            file.close()
        return result


def bmdlImporter_menu_func(self, context):
    self.layout.operator(ImportBMDL.bl_idname, text="Darkspore BMDL Model (.bmdl)")
    

def gmdlImporter_menu_func(self, context):
    self.layout.operator(ImportGMDL.bl_idname, text="Spore GMDL Model (.gmdl)")


def gmshImporter_menu_func(self, context):
    self.layout.operator(ImportGMSH.bl_idname, text="Spore GMSH Model (.gmsh)")


def rw4Importer_menu_func(self, context):
    self.layout.operator(ImportRW4.bl_idname, text="Spore RenderWare 4 (.rw4)")


def rw4ImporterOld_menu_func(self, context):
    self.layout.operator(ImportRW4Old.bl_idname, text="Spore RenderWare 4 Old (.rw4)")


def rw4Exporter_menu_func(self, context):
    self.layout.operator(ExportRW4.bl_idname, text="Spore RenderWare 4 (.rw4)")


def register():

    from sporemodder import RWMaterialConfig, RWAnimationConfig
    RWMaterialConfig.register()
    RWAnimationConfig.register()
    

    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(bmdlImporter_menu_func)
    bpy.types.INFO_MT_file_import.append(gmdlImporter_menu_func)
    bpy.types.INFO_MT_file_import.append(gmshImporter_menu_func)
    bpy.types.INFO_MT_file_import.append(rw4Importer_menu_func)
    bpy.types.INFO_MT_file_import.append(rw4ImporterOld_menu_func)
    bpy.types.INFO_MT_file_export.append(rw4Exporter_menu_func)
    # rw4Settings.register()


def unregister():
    # from sporemodder import rw4Settings
    # rw4Settings.unregister()

    from sporemodder import RWMaterialConfig, RWAnimationConfig
    RWMaterialConfig.unregister()
    RWAnimationConfig.unregister()

    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(bmdlImporter_menu_func)
    bpy.types.INFO_MT_file_import.remove(gmdlImporter_menu_func)
    bpy.types.INFO_MT_file_import.remove(gmshImporter_menu_func)
    #bpy.types.INFO_MT_file_import.remove(bmdlImporter_menu_func)
    bpy.types.INFO_MT_file_import.remove(rw4Importer_menu_func)
    bpy.types.INFO_MT_file_import.remove(rw4ImporterOld_menu_func)
    bpy.types.INFO_MT_file_export.remove(rw4Exporter_menu_func)

if __name__ == "__main__":
    register()