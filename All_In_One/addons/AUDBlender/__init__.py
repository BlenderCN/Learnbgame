import importlib

#    Addon information
bl_info = {
    'name': 'AUD Exporter',
    'author': 'merikesh',
    'location': 'File > Export > Export AUD (.usda)',
    'category': 'Export',
    "description": "Exporter to write usda ascii files out without requiring USD binaries",
    "version": (0, 0, 2),
    "blender": (2, 80, 0)
}

# Handle reloading (probably not necessary)
if "bpy" in locals():
    if "aud_exporter" in locals():
        importlib.reload(aud_exporter)

# Blender Imports
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator


# Register in Export menu
def menu_func_export(self, context):
    self.layout.operator(ExportAUD.bl_idname, text="AUD (.usda)")

# Register plugin
def register():
    bpy.utils.register_class(ExportAUD)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

# Unregister Plugin
def unregister():
    bpy.utils.unregister_class(ExportAUD)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


class ExportAUD(Operator, ExportHelper):
    """
    Exports a USD Ascii file that can be read by Pixar's USD library.
    This plugin is unaffiliated with Pixar, and does not require any extra dependencies
    or any compiled plugins to write out files.
    """
    bl_idname = "export_aud.usda"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export AUD (.usda)"

    # ExportHelper mixin class uses this
    filename_ext = ".usda"

    filter_glob: StringProperty(
        default="*.usda",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )

    write_animation: BoolProperty(
        name="Export Animation",
        description="Export animated values and geometry caches",
        default=False,
    )

    geo_cache: BoolProperty(
        name="Meshes as Geometry Cache",
        description="Export Meshes as Geometry Cache instead of Skeletons",
        default=False,
    )

    cameras: BoolProperty(
        name="Export Cameras",
        description="Export Cameras",
        default=False
    )

    lights: BoolProperty(
        name="Export Lights",
        description="Export Lights",
        default=False
    )

    def execute(self, context):
        from . import aud_exporter
        import importlib
        importlib.reload(aud_exporter)

        return aud_exporter.AUDExporter(context=context,
                                        selected=self.use_selection,
                                        animation=self.write_animation,
                                        geocache=self.geo_cache,
                                        cameras=self.cameras,
                                        lights=self.lights
                                        ).write(filepath=self.filepath)


if __name__ == "__main__":
    try:
        unregister()
    except Exception as e:
        print("Failed to unregister ExportAUD: {}".format(e))

    register()

    # test call
    bpy.ops.export_aud.usda('INVOKE_DEFAULT')
