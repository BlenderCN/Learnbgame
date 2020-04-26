import bpy
from bpy.props import StringProperty


class ResetOffsetPadding(bpy.types.Operator):
    bl_idname = "machin3.reset_infotext_offset_padding"
    bl_label = "MACHIN3: Rest Offset or Padding"
    bl_description = "Reset Offset/Padding"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty()

    def execute(self, context):
        dm = context.scene.DM

        if self.type == "OFFSET":
            dm.create_infotext_offset = (0, 0)

        elif self.type == "PADDING":
            dm.create_infotext_padding = (0, 0)

        return {'FINISHED'}
