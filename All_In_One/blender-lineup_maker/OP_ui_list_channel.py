import bpy

def get_channels(context):
    idx = context.scene.lm_channel_idx
    channels = context.scene.lm_channels

    active = channels[idx] if channels else None

    return idx, channels, active

class LM_UI_MoveChannel(bpy.types.Operator):
    bl_idname = "scene.lm_move_channel"
    bl_label = "Move Channel"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move Channel Name up or down.\nThis controls the position in the Menu."

    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    def execute(self, context):
        idx, channel, _ = get_channels(context)

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(channel) - 1)

        channel.move(idx, nextidx)
        context.scene.lm_channel_idx = nextidx

        return {'FINISHED'}



class LM_UI_RenameChannel(bpy.types.Operator):
    bl_idname = "scene.lm_rename_channel"
    bl_label = "Rename Texture Channel"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Rename the selected Texture Channel Name"

    newmatname: bpy.props.StringProperty(name="New Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return context.scene.lm_channels

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # row = column.split(percentage=0.31)
        # row.label("Old Name")
        # row.label(self.active.name)

        column.prop(self, "newmatname")

    def invoke(self, context, event):
        _, _, self.active = get_channels(context)

        self.newmatname = self.active.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.newmatname:
            self.active.name = self.newmatname

        return {'FINISHED'}


class LM_UI_ClearChannel(bpy.types.Operator):
    bl_idname = "scene.lm_clear_channels"
    bl_label = "Clear All Texture Channel"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear All Texture Channel Names."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_channels

    def execute(self, context):
        context.scene.lm_channels.clear()

        return {'FINISHED'}


class LM_UI_RemoveChannel(bpy.types.Operator):
    bl_idname = "scene.lm_remove_channel"
    bl_label = "Remove Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove selected Texture Channel Name."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_channels

    def execute(self, context):
        idx, channel, _ = get_channels(context)

        channel.remove(idx)

        context.scene.lm_channel_idx = min(idx, len(context.scene.lm_channels) - 1)

        return {'FINISHED'}
