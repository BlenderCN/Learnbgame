"""BlenderFDS, preferences panel"""

import bpy

# Get preference value like this:
# bpy.context.user_preferences.addons["blenderfds"].preferences.bf_debug

class BFPreferences(bpy.types.AddonPreferences):
    bl_idname = "blenderfds"

    bf_pref_simplify_ui = bpy.props.BoolProperty(
            name="Simplify Blender User Interface (Blender restart needed)",
            description="Simplify Blender User Interface (Blender restart needed)",
            default=True,
            )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("wm.bf_set_environment")
        row = layout.row()
        row.prop(self, "bf_pref_simplify_ui")


