import bpy
from bpy.props import *

def draw_in_render_panel(self, context):
    layout = self.layout
    scene = context.scene

    col = layout.column(align = True)
    col.active = bpy.data.is_saved
    col.label("Create Terminal Command:")

    row = col.row(align = True)
    row.operator("render.create_render_frame_command",
        text = "Frame",
        icon = "RENDER_STILL")
    row.operator("render.create_render_animation_command",
        text = "Animation",
        icon = "RENDER_ANIMATION")
    row.prop(scene, "terminal_command", text = "", icon = "CONSOLE")
    props = row.operator("wm.copy_text_to_clipboard", text = "", icon = "COPYDOWN")
    props.text = scene.terminal_command

def register():
    bpy.types.RENDER_PT_render.append(draw_in_render_panel)
    bpy.types.Scene.terminal_command = StringProperty(name = "Terminal Command")

def unregister():
    bpy.types.RENDER_PT_render.remove(draw_in_render_panel)
    del bpy.types.Scene.terminal_command
