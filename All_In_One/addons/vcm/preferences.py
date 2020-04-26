import bpy

# select_mouse = bpy.context.user_preferences.inputs.select_mouse


class VCMAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # def register():
        # bpy.context.user_preferences.inputs.select_mouse = 'LEFT'

    # def unregister():
        # bpy.context.user_preferences.inputs.select_mouse = select_mouse
