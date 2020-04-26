import bpy
from ..common import *

class RevoltHelpersPanelObj(bpy.types.Panel):
    bl_label = "Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Re-Volt"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label("", icon="HELP")

    def draw(self, context):

        layout = self.layout
        props = context.scene.revolt

        box = layout.box()
        box.label("3D View:")
        col = box.column(align=True)
        col.operator(
            "helpers.enable_texture_mode",
            icon="POTATO",
            text="Texture"
        )
        col.operator(
            "helpers.enable_textured_solid_mode",
            icon="TEXTURE_SHADED",
            text="Textured Solid"
        )

        box = layout.box()
        box.label("RVGL:")
        box.operator(
            "helpers.launch_rv"
        )


class RevoltHelpersPanelMesh(bpy.types.Panel):
    bl_label = "Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Re-Volt"
    bl_context = "mesh_edit"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label("", icon="HELP")

    def draw(self, context):

        layout = self.layout

        box = layout.box()
        box.label("3D View:")
        col = box.column(align=True)
        col.operator(
            "helpers.enable_texture_mode",
            icon="POTATO",
            text="Texture"
        )
        col.operator(
            "helpers.enable_textured_solid_mode",
            icon="TEXTURE_SHADED",
            text="Textured Solid"
        )
