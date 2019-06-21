import bpy
from ..common import *

class RevoltSettingsPanel(bpy.types.Panel):
    """

    """
    bl_label = "Add-On Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label("", icon="SCRIPTWIN")

    def draw(self, context):
        props = context.scene.revolt
        layout = self.layout

        # General settings
        
        layout.label("Re-Volt Directory:")
        box = self.layout.box()
        box.prop(props, "revolt_dir", text="")
        if props.revolt_dir == "":
            box.label("No directory specified", icon="INFO")
        elif os.path.isdir(props.revolt_dir):
            if "rvgl.exe" in os.listdir(props.revolt_dir):
                box.label(
                    "Folder exists (RVGL for Windows)",
                    icon="FILE_TICK"
                )
            elif "rvgl" in os.listdir(props.revolt_dir):
                box.label(
                    "Folder exists (RVGL for Linux)",
                    icon="FILE_TICK"
                )
            else:
                box.label(
                    "Folder exists, RVGL not found",
                    icon="INFO"
                )

        else:
            box.label("Not found", icon="ERROR")


        layout.label("General:")
        layout.prop(props, "prefer_tex_solid_mode")
        layout.separator()

        # General import settings
        layout.label("Import:")
        layout.prop(props, "enable_tex_mode")
        layout.prop(props, "prm_check_parameters")
        layout.separator()

        # General export settings
        layout.label("Export:")
        layout.prop(props, "triangulate_ngons")
        layout.prop(props, "use_tex_num")
        layout.prop(props, "apply_scale")
        layout.prop(props, "apply_rotation")
        layout.prop(props, "apply_translation")
        layout.separator()

        # PRM Export settings
        # layout.label("Export PRM (.prm/.m):")
        # layout.separator()

        # World Import settings
        layout.label("Import World (.w):")
        layout.prop(props, "w_parent_meshes")
        layout.prop(props, "w_import_bound_boxes")
        if props.w_import_bound_boxes:
            layout.prop(props, "w_bound_box_layers")
        layout.prop(props, "w_import_cubes")
        if props.w_import_cubes:
            layout.prop(props, "w_cube_layers")
        layout.prop(props, "w_import_big_cubes")
        if props.w_import_big_cubes:
            layout.prop(props, "w_big_cube_layers")
        layout.separator()

        # NCP Export settings
        layout.label("Export Collision (.ncp):")
        layout.prop(props, "ncp_export_selected")
        layout.prop(props, "ncp_export_collgrid")
        layout.prop(props, "ncp_collgrid_size")

