import bpy
from bpy.props import *
from . command_creation import render_whole_animation, render_single_image

class CreateRenderAnimationCommand(bpy.types.Operator):
    bl_idname = "render.create_render_animation_command"
    bl_label = "Create Render Animation Command"
    bl_description = "Generates a new terminal command for this file"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        context.scene.terminal_command = render_whole_animation()
        return {"FINISHED"}

class CreateRenderFrameCommand(bpy.types.Operator):
    bl_idname = "render.create_render_frame_command"
    bl_label = "Create Render Frame Command"
    bl_description = "Generates a new terminal command for this file"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        context.scene.terminal_command = render_single_image(context.scene.frame_current)
        return {"FINISHED"}

class CopyTextToClipboard(bpy.types.Operator):
    bl_idname = "wm.copy_text_to_clipboard"
    bl_label = "Copy Text to Clipboard"
    bl_description = "Copy Text to Clipboard"
    bl_options = {"REGISTER"}

    text = StringProperty()

    def execute(self, context):
        context.window_manager.clipboard = self.text
        return {"FINISHED"}
