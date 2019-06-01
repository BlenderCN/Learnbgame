bl_info = {
    "name": "Rise of Nations BigHuge3D & BigHugeAnimation format",
    "author": "Petar Tasev",
    "version": (1, 0, 2016, 513),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Import-Export BH3 mesh, UVs, skeleton, and BHA animation",
    "warning": "",
    "wiki_url": "http://www.petartasev.com/modding/rise-of-nations/blender-addon/",
    "tracker_url": "https://github.com/Ryder25/Rise-of-Nations/issues",
    "support": 'COMMUNITY',
    "category": "Learnbgame",
}

# TODO: Figure out how reloading works
if "bpy" in locals():
    import importlib
    # blender
    if "bh3fileimporter" in locals():
        from blender import bh3fileimporter
        importlib.reload(bh3fileimporter)
    if "bh3fileexporter" in locals():
        from blender import bh3fileexporter
        importlib.reload(bh3fileexporter)
    # fileio
    if "binaryreader" in locals():
        from fileio import binaryreader
        importlib.reload(binaryreader)
    if "binarywriter" in locals():
        from fileio import binarywriter
        importlib.reload(binarywriter)
    # formats
    if "bh3binaryreader" in locals():
        from .formats.bh3 import bh3binaryreader
        importlib.reload(bh3binaryreader)
    if "bh3binarywriter" in locals():
        from .formats.bh3 import bh3binarywriter
        importlib.reload(bh3binarywriter)
    if "bh3bone" in locals():
        from .formats.bh3 import bh3bone
        importlib.reload(bh3bone)
    if "bh3file" in locals():
        from .formats.bh3 import bh3file
        importlib.reload(bh3file)


import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportBH3(Operator, ImportHelper):
    """Load a Rise of Nations BH3 file"""
    bl_idname = "import_scene.bh3"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import BH3"

    # ImportHelper mixin class uses this
    filename_ext = ".BH3"

    filter_glob = StringProperty(
        default="*.BH3",
        options={'HIDDEN'},
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    import_normals = BoolProperty(
       name="Import Normals",
       description="Import the normals from the file",
       default=True,
    )

    #    type = EnumProperty(
    #            name="Example Enum",
    #            description="Choose between two items",
    #            items=(('OPT_A', "First Option", "Description one"),
    #                   ('OPT_B', "Second Option", "Description two")),
    #            default='OPT_A',
    #            )

    def execute(self, context):
        from .blender.bh3fileimporter import BH3FileImporter
        file_importer = BH3FileImporter(self.import_normals)
        return file_importer.load(context, self.filepath)


class ExportBH3(Operator, ExportHelper):
    """Save a Rise of Nations BH3 file"""
    bl_idname = "export_scene.bh3"
    bl_label = "Export BH3"

    # ExportHelper mixin class uses this
    filename_ext = ".BH3"

    filter_glob = StringProperty(
        default="*.BH3",
        options={'HIDDEN'},
    )

    preserve_uvs = BoolProperty(
        name="Preserve UVs",
        description="Duplicate the mesh vertices so that they have 1:1 correspondence with their UVs",
        default=False,
    )

    def execute(self, context):
        from .blender.bh3fileexporter import BH3FileExporter
        file_exporter = BH3FileExporter(self.preserve_uvs)
        return file_exporter.save(context, self.filepath)


class ImportBHA(Operator, ImportHelper):
    """Load a Rise of Nations BHA file"""
    bl_idname = "import_anim.bha"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import BHA"

    # ImportHelper mixin class uses this
    filename_ext = ".BHA"

    filter_glob = StringProperty(
        default="*.BHA",
        options={'HIDDEN'},
    )

    stabilize_quaternions = BoolProperty(
       name="Stabilize Quaternions",
       description="Import each quaternion as the shortest arc from the previous keyframe",
       default=True,
    )

    def execute(self, context):
        from .blender.bhafileimporter import BHAFileImporter
        file_importer = BHAFileImporter(self.stabilize_quaternions)
        return file_importer.load(context, self.filepath)


class ExportBHA(Operator, ExportHelper):
    """Save a Rise of Nations BHA file"""
    bl_idname = "export_anim.bha"
    bl_label = "Export BHA"

    # ExportHelper mixin class uses this
    filename_ext = ".BHA"

    filter_glob = StringProperty(
        default="*.BHA",
        options={'HIDDEN'},
    )

    def execute(self, context):
        from .blender.bhafileexporter import BHAFileExporter
        file_exporter = BHAFileExporter()
        return file_exporter.save(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportBH3.bl_idname, text="Rise of Nations (.BH3)")


def menu_func_export(self, context):
    self.layout.operator(ExportBH3.bl_idname, text="Rise of Nations (.BH3)")


def menu_func_import_bha(self, context):
    self.layout.operator(ImportBHA.bl_idname, text="Rise of Nations (.BHA)")


def menu_func_export_bha(self, context):
    self.layout.operator(ExportBHA.bl_idname, text="Rise of Nations (.BHA)")


def register():
    bpy.utils.register_class(ImportBH3)
    bpy.utils.register_class(ExportBH3)
    bpy.utils.register_class(ImportBHA)
    bpy.utils.register_class(ExportBHA)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import_bha)
    bpy.types.INFO_MT_file_export.append(menu_func_export_bha)


def unregister():
    bpy.utils.unregister_class(ImportBH3)
    bpy.utils.unregister_class(ExportBH3)
    bpy.utils.unregister_class(ImportBHA)
    bpy.utils.unregister_class(ExportBHA)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_bha)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_bha)


if __name__ == "__main__":
    register()

    # from formats.bh3.bh3file import BH3File
    # bh3_file = BH3File()
    # bh3_file.read('C:\Games\Steam\SteamApps\common\Rise of Nations\\art\\riflemanO.BH3')
    # bh3_file.write('C:\Games\Steam\SteamApps\common\Rise of Nations\\art\\riflemanO_t.BH3')

    # test call
    # bpy.ops.import_scene.bh3('INVOKE_DEFAULT')
