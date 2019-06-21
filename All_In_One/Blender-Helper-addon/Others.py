import bpy


class Update_Scene_Operator(bpy.types.Operator):
    bl_idname = "object.update_scene"
    bl_label = "Update_Scene"

    def execute(self, context):
        bpy.context.scene.update()
        return {'FINISHED'}
