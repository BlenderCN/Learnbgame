import bpy


# -----------------------------------------------------------------------------
# This operator call User Preferences and show Substance Bridge settings.
# -----------------------------------------------------------------------------
class OpenSbsSettings(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs.settings"
    bl_label = "Make an set list on first."

    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        context.user_preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = "Substance Bridge"

        return {'FINISHED'}


def register():
    bpy.utils.register_class(OpenSbsSettings)


def unregister():
    bpy.utils.unregister_class(OpenSbsSettings)
