import bpy
bl_info = {
    "name": "toggle_use_automerge",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Learnbgame",
}


class ToggleUseAutoMergeOperator(bpy.types.Operator):
    bl_idname = "mesh.toggle_use_automerge"
    bl_label = "TILA: Toggle Use Automerge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.use_mesh_automerge = not bpy.context.scene.tool_settings.use_mesh_automerge
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
