import bpy
from bpy.props import StringProperty

import blend4avango
from .b4a_bin_suffix import get_platform_data

class B4AInitErrorMessage(bpy.types.Operator):
    bl_idname = "B4A.init_error_message"
    bl_label = "Blend4Avango initialization error!"
    bl_options = {"INTERNAL"}

    message = StringProperty(name="Message string")

    def execute(self, context):
        # NOTE: disable addon if binaries are incompatible
        if __package__ in bpy.context.user_preferences.addons:
            bpy.ops.wm.addon_disable(module=__package__)
        return {'FINISHED'}

    def cancel(self, context):
        # NOTE: disable addon if binaries are incompatible
        if __package__ in bpy.context.user_preferences.addons:
            bpy.ops.wm.addon_disable(module=__package__)

    def invoke(self, context, event):
        wm = context.window_manager
        context.window.cursor_set("DEFAULT")
        return wm.invoke_props_dialog(self, 450)

    def draw(self, context):
        self.layout.label(self.message, icon="ERROR")

class B4AVersionMismatchMessage(bpy.types.Operator):
    bl_idname = "b4a.version_mismatch_message"
    bl_label = "Warning: Blender version mismatch."
    bl_options = {"INTERNAL"}

    message = StringProperty(name="Message string")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        context.window.cursor_set("DEFAULT")
        return wm.invoke_props_dialog(self, 450)

    def draw(self, context):
        self.layout.label(self.message, icon="ERROR")

@bpy.app.handlers.persistent
def validate_version(arg):
    if (bpy.app.version[0] != blend4web.bl_info["blender"][0]
            or bpy.app.version[1] != blend4web.bl_info["blender"][1]):
        message = "Blender " \
                + ".".join(map(str, blend4web.bl_info["blender"][:-1])) \
                + " is recommended for the Blend4Avango addon. Current version is " \
                + ".".join(map(str, bpy.app.version[:-1]))

        # remove callback before another scene update aroused by init_error_message
        if validate_version in bpy.app.handlers.scene_update_pre:
            bpy.app.handlers.scene_update_pre.remove(validate_version)
        bpy.ops.B4A.version_mismatch_message("INVOKE_DEFAULT", message=message)

@bpy.app.handlers.persistent
def bin_invalid_message(arg):
    # remove callback before another scene update aroused by init_error_message
    if bin_invalid_message in bpy.app.handlers.scene_update_pre:
        bpy.app.handlers.scene_update_pre.remove(bin_invalid_message)

    platform_data = get_platform_data()
    message = "Addon is not compatible with \"" \
            + platform_data["system_name"] + " x" + platform_data["arch_bits"] \
            + "\" platform."
    bpy.ops.B4A.init_error_message("INVOKE_DEFAULT", message=message)

# NOTE: register class permanently to held it even after disabling an addon
bpy.utils.register_class(B4AInitErrorMessage)
bpy.utils.register_class(B4AVersionMismatchMessage)
