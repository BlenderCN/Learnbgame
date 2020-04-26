import bpy

from .operators import *

bl_info = {
    "name": "Grease Writer",
    "description": "Automatic hand-drawn text animation",
    "author": "doakey3",
    "version": (0, 0, 4),
    "blender": (2, 80, 0),
    "wiki_url": "https://github.com/doakey3/GreaseDraw",
    "tracker_url": "https://github.com/doakey3/GreaseDraw/issues",
    "category": "Learnbgame",
    "location": "Properties, Grease Pencil Data"
}

class GREASEPENCIL_PT_greasewriter(bpy.types.Panel):
    bl_label = "Grease Writer"
    bl_idname = "GREASEPENCIL_PT_greasewriter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        if type(context.active_object.data).__name__ == "GreasePencil":
            return True
        else:
            return False

    def draw(self, context):
        scene = context.scene
        gpencil = context.active_object.data
        layout = self.layout
        row = layout.row()
        row.operator("grease_writer.decorate", icon="LIGHT_SUN")
        row.prop(gpencil, "decorator_style", text="")

        layout.separator()

        layout.operator("grease_writer.reanimate", icon="HAND")

        layout.separator()

        row = layout.row()
        row.prop(gpencil, 'stipple_length')
        row.prop(gpencil, 'stipple_skip')
        layout.operator("grease_writer.stippleit")

        layout.separator()

        layout.prop_search(gpencil, 'tracer_obj', scene, "objects", text="")
        row = layout.row()
        row.operator("grease_writer.trace", icon="PIVOT_CURSOR")
        row.prop(gpencil, 'trace2d')


class SCENE_PT_greasewriter(bpy.types.Panel):
    bl_label = "Grease Writer"
    bl_idname = "SCENE_PT_greasewriter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene, 'gw_scale')
        layout.prop(scene, 'gw_speed')
        layout.prop(scene, 'gw_kerning')
        layout.prop(scene, 'gw_word_space')
        layout.prop(scene, 'gw_line_height')
        layout.prop(scene, 'gw_thickness')
        layout.prop(scene, 'gw_color')
        layout.prop(scene, 'gw_font')
        row = layout.row()
        row.prop_search(scene, 'gw_source_text_file', bpy.data, "texts", text="")
        row.prop(scene, 'gw_source_text', text="")
        layout.operator("grease_writer.write", icon="FILE_TEXT")


def init_props():
    bpy.types.Scene.gw_scale = bpy.props.FloatProperty(
        name="Scale",
        description="Affects the text size",
        default=1.0,
        min=0.01
    )

    bpy.types.Scene.gw_speed = bpy.props.FloatProperty(
        name="Draw Speed",
        description="The distance a stroke lengthens with each frame of animation",
        default=1.0,
        min=0.01
    )

    bpy.types.Scene.gw_kerning = bpy.props.FloatProperty(
        name="Kerning",
        description="Affects the distance between characters.",
        default=1.0,
        min=0
    )

    bpy.types.Scene.gw_word_space = bpy.props.FloatProperty(
        name="Word Space",
        description="Affects the distance between words.",
        default=1.0,
        min=0
    )

    bpy.types.Scene.gw_line_height = bpy.props.FloatProperty(
        name="Line Height",
        description="Affects the height of a line. Default is 1.25 x the height of the letter M",
        default=1.0,
        min=0
    )

    bpy.types.Scene.gw_thickness = bpy.props.IntProperty(
        name="Thickness",
        description="Affects the default line thickness.",
        default=100,
        min=1
    )

    bpy.types.Scene.gw_color = bpy.props.FloatVectorProperty(
       subtype='COLOR_GAMMA',
       name="Color",
       description="Color to use when writing",
       size=3,
       default=(0, 0, 0),
       min=0.0,
       max=1.0
    )

    fonts = [
        ("consolas", "Consolas", "A monospace font based on Consolas by doakey3"),
        ("hershey_script_simplex", "Hershey's Script Simplex", "A cursive font made by by Dr. Allen Vincent Hershey"),
        ("hershey_roman_simplex", "Hershey's Roman Simplex", "A sans font made by by Dr. Allen Vincent Hershey"),
        ("shohrukh_russian", "Shohrukh's Russian", "A font made by Shohrukh for Russian characters"),
        ("shohrukh_tajik", "Shohrukh's Tajik", "A font made by Shohrukh for Tajik characters")
    ]

    bpy.types.Scene.gw_font = bpy.props.EnumProperty(
        name="Font",
        items=fonts,
        description="The font to be used for writing",
        default="consolas",
    )

    bpy.types.Scene.gw_source_text_file = bpy.props.StringProperty(
        name="source_text_file",
        description="The text file containing text to be written with grease pencil."
    )

    bpy.types.Scene.gw_source_text = bpy.props.StringProperty(
        name="source_text",
        description="The text to be written with grease pencil; has priority over the source text file property"
    )

    decorators = [
        ("underline", "Underline", "Draw an underline beneath the grease pencil layer"),
        ("over-underline", "Over-underline", "Draw an overline and underline"),
        ("box", "Box", "Draw a box around the grease pencil layer"),
        ("ellipse", "Ellipse", "Draw an ellipse around the grease pencil layer"),
        ("circle", "Circle", "Draw a circle around the grease pencil layer"),
        ("strike-through", "Strike-through", "Horizontally strike out the grease pencil layer"),
        ("x-out", "X-out", "X out the grease pencil layer"),
        ("helioid", "Helioid", "Make a sun-like decorator (spiked ellipse)")
    ]

    bpy.types.GreasePencil.decorator_style = bpy.props.EnumProperty(
        name="Decorators",
        items=decorators,
        description="The decorator to draw",
        default="underline",
    )

    bpy.types.GreasePencil.tracer_obj = bpy.props.StringProperty()

    bpy.types.GreasePencil.trace2d = bpy.props.BoolProperty(
        name="2D",
        description="Limit tracing to X and Y",
        default=True
    )

    bpy.types.GreasePencil.stipple_length = bpy.props.FloatProperty(
       name="Length",
       description="The length of the stipples",
       default=0.1,
       min=0.01,
    )

    bpy.types.GreasePencil.stipple_skip = bpy.props.IntProperty(
        name="Skip",
        description="Skips this many stipple-lengths between stipples",
        default=2,
        min=1
    )

classes = [
    GREASEPENCIL_PT_greasewriter,
    SCENE_PT_greasewriter,
    GREASEPENCIL_OT_reanimate,
    GREASEPENCIL_OT_write,
    GREASEPENCIL_OT_trace,
    GREASEPENCIL_OT_decorate,
    GREASEPENCIL_OT_stippleit
]

def register():
    init_props()

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
