import bpy
from ..common import *
from .widgets import *
from .. import tools

class RevoltLightPanel(bpy.types.Panel):
    bl_label = "Light and Shadow"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        return context.object and len(context.selected_objects) >= 1 and context.object.type == "MESH"

    def draw_header(self, context):
        self.layout.label("", icon="RENDER_STILL")

    def draw(self, context):
        view = context.space_data
        obj = context.object
        props = context.scene.revolt

        # Warns if texture mode is not enabled
        widget_texture_mode(self)

        if obj and obj.select:
            # Checks if the object has a vertex color layer
            if widget_vertex_color_channel(self, obj):
                pass
            else:
                # Light orientation selection
                box = self.layout.box()
                box.label(text="Shade Object")
                row = box.row()
                row.prop(props, "light_orientation", text="Orientation")
                if props.light_orientation == "X":
                    dirs = ["Left", "Right"]
                if props.light_orientation == "Y":
                    dirs = ["Front", "Back"]
                if props.light_orientation == "Z":
                    dirs = ["Top", "Bottom"]
                # Headings
                row = box.row()
                row.label(text="Direction")
                row.label(text="Light")
                row.label(text="Intensity")
                # Settings for the first light
                row = box.row(align=True)
                row.label(text=dirs[0])
                row.prop(props, "light1", text="")
                row.prop(props, "light_intensity1", text="")
                # Settings for the second light
                row = box.row(align=True)
                row.label(text=dirs[1])
                row.prop(props, "light2", text="")
                row.prop(props, "light_intensity2", text="")
                # Bake button
                row = box.row()
                row.operator("lighttools.bakevertex",
                             text="Generate Shading",
                             icon="LIGHTPAINT")

            # Shadow tool
            box = self.layout.box()
            box.label(text="Generate Shadow Texture")
            row = box.row()
            row.prop(props, "shadow_method")
            col = box.column(align=True)
            col.prop(props, "shadow_quality")
            col.prop(props, "shadow_softness")
            col.prop(props, "shadow_resolution")
            row = box.row()
            row.operator("lighttools.bakeshadow",
                         text="Generate Shadow",
                         icon="LAMP_SPOT")
            row = box.row()
            row.prop(props, "shadow_table", text="Table")

            # Batch baking tool
            box = self.layout.box()
            box.label(text="Batch Bake Light")
            box.prop(props, "batch_bake_model_rgb")
            box.prop(props, "batch_bake_model_env")
            box.operator("helpers.batch_bake_model")


class ButtonBakeShadow(bpy.types.Operator):
    bl_idname = "lighttools.bakeshadow"
    bl_label = "Bake Shadow"
    bl_description = "Creates a shadow plane beneath the selected object"

    def execute(self, context):
        tools.bake_shadow(self, context)
        return{"FINISHED"}


class ButtonBakeLightToVertex(bpy.types.Operator):
    bl_idname = "lighttools.bakevertex"
    bl_label = "Bake light"
    bl_description = "Bakes the light to the active vertex color layer"

    def execute(self, context):
        tools.bake_vertex(self, context)
        return{"FINISHED"}