import bpy
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper_factory,
    axis_conversion,
)

IOMPETOrientationHelper = orientation_helper_factory("IOMPETOrientationHelper", axis_forward='Z', axis_up='Y')

bl_info = {
    "name": "PangYa Model",
    "author": "John Chadwick",
    "blender": (2, 74, 0),
    "location": "File > Import-Export",
    "description": "Import-Export PangYa .pet and .mpet files.",
    "category": "Import-Export"
}

# ImportMpet implements the operator for importing Mpet models.
class ImportMpet(bpy.types.Operator, ImportHelper, IOMPETOrientationHelper):
    """Import from Pangya Model (.pet, .mpet)"""
    bl_idname = 'import_scene.pangya_mpet'
    bl_label = 'Import Pangya Model'
    bl_options = {'UNDO'}

    filename_ext = '.mpet;.pet'
    filter_glob = bpy.props.StringProperty(
        default='*.mpet;*.pet',
        options={'HIDDEN'},
    )

    def execute(self, context):
        from . import import_mpet

        matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4()

        return import_mpet.load(self, context, self.filepath, matrix)

# ExportMpet implements the operator for exporting to Mpet.
class ExportMpet(bpy.types.Operator, ExportHelper):
    """Export to Pangya Model (.pet, .mpet)"""
    bl_idname = 'export_scene.pangya_mpet'
    bl_label = 'Export Pangya Model'

    filename_ext = '.mpet;.pet'
    filter_glob = bpy.props.StringProperty(
        default='*.mpet;*.pet',
        options={'HIDDEN'},
    )

    use_selection = bpy.props.BoolProperty(
        name='Selection Only',
        description='Export selected objects only',
        default=False,
    )

    def execute(self, context):
        from . import export_mpet
        return export_mpet.save(self, context)


# Registration/Menu items
def menu_func_export(self, context):
    self.layout.operator(ExportMpet.bl_idname, text="PangYa Model (.pet, .mpet)")


def menu_func_import(self, context):
    self.layout.operator(ImportMpet.bl_idname, text="PangYa Model (.pet, .mpet)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
