import os
import bpy
from .render_settings import *


class RenderSettingsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Render Settings"
    bl_category = "Cube"

    def draw(self, context):
        layout = self.layout
        layout.operator("cube.save_render_settings_operator", icon='EXPORT')
        layout.operator("cube.load_render_settings_operator", icon='IMPORT')


class SaveRenderSettingsOperator(bpy.types.Operator):
    bl_idname = "cube.save_render_settings_operator"
    bl_label = "Save Render Settings"
    bl_description = "Export current render settings into a JSON file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        save_render_settings(context.scene, self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LoadRenderSettingsOperator(bpy.types.Operator):
    bl_idname = "cube.load_render_settings_operator"
    bl_label = "Load Render Settings"
    bl_description = "Import render settings from a JSON file"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        settings = load_render_settings(self.filepath)
        apply_render_settings(bpy.context.scene, settings)
        check, check_details = check_settings_blender_version(settings)
        # draw function for popup message
        def draw(self, context):
            self.layout.label(check_details)
        if not check:
            context.window_manager.popup_menu(draw, title="Warning", icon="ERROR")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
