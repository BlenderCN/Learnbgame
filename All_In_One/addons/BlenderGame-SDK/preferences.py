import bpy

class GameEditorPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    engine_path = bpy.props.StringProperty(
        name="Path to game engine",
        subtype="DIR_PATH")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "engine_path")

def register():
    bpy.utils.register_class(GameEditorPreferences)

def unregister():
    bpy.utils.unregister_class(GameEditorPreferences)