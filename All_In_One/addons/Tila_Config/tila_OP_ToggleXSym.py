import bpy
bl_info = {
    "name": "toggle_X_Symetry",
    "author": "Tilapiatsu",
    "version": (1, 0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "category": "Learnbgame",
}


class ToggleXSymOperator(bpy.types.Operator):
    bl_idname = "mesh.toggle_x_symetry"
    bl_label = "TILA: Toggle Use Automerge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.object.data.use_mirror_x = not bpy.context.object.data.use_mirror_x
        return {'FINISHED'}


def register():
    pass


def unregister():
    pass


if __name__ == "__main__":
    register()
