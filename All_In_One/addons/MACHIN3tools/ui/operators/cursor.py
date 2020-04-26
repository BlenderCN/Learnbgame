import bpy


class CursorToOrigin(bpy.types.Operator):
    bl_idname = "machin3.cursor_to_origin"
    bl_label = "MACHIN3: Cursor to Origin"
    bl_description = "Resets Cursor location and rotation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.cursor.location.zero()
        context.scene.cursor.rotation_mode = 'XYZ'
        context.scene.cursor.rotation_euler.zero()

        return {'FINISHED'}
