import bpy

bl_info = {
    "name": "UV Sync Toggler",
    "author": "Stefan Heinemann",
    "blender": (2, 77, 0),
    "version": (0, 0, 1),
    "location": "Key Bindings",
    "description": "Provides an operator for keybindings to toggle the"
                   "keep UV and edit mode selection in sync",
    "category": "UV"
}


class ToggleUVSync(bpy.types.Operator):
    bl_idname = 'uv.toggle_uv_sync'
    bl_label  = "Uv sync toggler"

    def execute(self, context):
        scene = context.scene
        uv_sync = scene.tool_settings.use_uv_select_sync

        print(uv_sync)

        scene.tool_settings.use_uv_select_sync = not uv_sync

        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
