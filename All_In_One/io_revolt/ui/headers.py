import bpy
from ..common import *

class EditModeHeader(bpy.types.Panel):
    """
    Fixes the tab at the top in edit mode.
    """
    bl_label = "Edit Mode Header"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        props = context.scene.revolt
        row  = self.layout.row()
        # PRM/NCP toggle
        row.prop(props, "face_edit_mode", expand=True)


class RevoltIOToolPanel(bpy.types.Panel):
    """
    Tool panel in the left sidebar of the viewport for performing
    various operations
    """
    bl_label = "Import/Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        # i/o buttons
        props = context.scene.revolt

        row = self.layout.row(align=True)
        row.operator("import_scene.revolt", text="Import", icon="IMPORT")
        row.operator("export_scene.revolt", text="Export", icon="EXPORT")
        row.operator("export_scene.revolt_redo", text="", icon="FILE_REFRESH")