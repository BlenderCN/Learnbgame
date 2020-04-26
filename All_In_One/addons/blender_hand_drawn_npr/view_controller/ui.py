import logging

import bpy

logger = logging.getLogger(__name__)


class MainPanel(bpy.types.Panel):
    """Create a Panel in the Render properties window."""

    logger.debug("Instantiating MainPanel...")

    bl_label = "Hand Drawn NPR"
    bl_idname = "RENDER_PT_hdn_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        system_settings = context.scene.system_settings

        self.layout.label("General:")
        self.layout.prop(data=system_settings,
                         property="out_filepath")
        self.layout.prop(data=system_settings,
                         property="corner_factor",
                         text="Corner Factor")
        self.layout.prop(data=context.scene.system_settings,
                         property="is_hook_enabled",
                         text="Enable render post")
        row = self.layout.row()
        row.scale_y = 2.0
        row.operator("wm.render_npr", icon='RENDER_STILL')
        self.layout.separator()

        box = self.layout.box()
        box.label("Silhouette")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="silhouette_const")
        col.prop(data=system_settings,
                 property="silhouette_depth")
        col.prop(data=system_settings,
                 property="silhouette_diffuse")
        col.prop(data=system_settings,
                 property="silhouette_curvature")

        self.layout.separator()

        box = self.layout.box()
        box.prop(data=system_settings,
                 property="is_internal_enabled")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="internal_const")
        col.prop(data=system_settings,
                 property="internal_depth")
        col.prop(data=system_settings,
                 property="internal_diffuse")
        col.prop(data=system_settings,
                 property="internal_curvature")

        self.layout.separator()

        box = self.layout.box()
        box.prop(data=system_settings,
                 property="is_streamlines_enabled")
        box.prop(data=system_settings,
                 property="streamline_segments")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="streamline_const")
        col.prop(data=system_settings,
                 property="streamline_depth")
        col.prop(data=system_settings,
                 property="streamline_diffuse")
        col.prop(data=system_settings,
                 property="streamline_curvature")

        self.layout.separator()

        box = self.layout.box()
        box.prop(data=system_settings,
                 property="is_stipples_enabled")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="stipple_head_radius")
        col.prop(data=system_settings,
                 property="stipple_tail_radius")
        col.prop(data=system_settings,
                 property="stipple_length")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="stipple_diffuse")
        col.prop(data=system_settings,
                 property="stipple_shadow")
        col.prop(data=system_settings,
                 property="stipple_ao")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="stipple_density_factor")
        col.prop(data=system_settings,
                 property="stipple_density_exponent")
        col.prop(data=system_settings,
                 property="stipple_min_allowable")
        box.prop(data=system_settings,
                 property="stipple_threshold")
        box.prop(data=system_settings,
                 property="is_optimisation_enabled")


classes = (
    MainPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
