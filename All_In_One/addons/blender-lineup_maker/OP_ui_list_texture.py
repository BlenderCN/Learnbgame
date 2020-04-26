import bpy

def get_texture_channels(context):
    idx = context.scene.lm_texture_channel_idx
    texture_channels = context.scene.lm_texture_channels

    active = texture_channels[idx] if texture_channels else None

    return idx, texture_channels, active

class LM_UI_MoveTexture(bpy.types.Operator):
    bl_idname = "scene.lm_move_texture_channel"
    bl_label = "Move Texture Channel"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move Texture Channel Name up or down.\nThis controls the position in the Menu."

    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    def execute(self, context):
        idx, texture_channel, _ = get_texture_channels(context)

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(texture_channel) - 1)

        texture_channel.move(idx, nextidx)
        context.scene.lm_texture_channel_idx = nextidx

        return {'FINISHED'}



class LM_UI_RenameTexture(bpy.types.Operator):
    bl_idname = "scene.lm_rename_texture_channel"
    bl_label = "Rename Texture Channel"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Rename the selected Texture Channel Name"

    newmatname: bpy.props.StringProperty(name="New Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return context.scene.lm_texture_channels

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # row = column.split(percentage=0.31)
        # row.label("Old Name")
        # row.label(self.active.name)

        column.prop(self, "newmatname")

    def invoke(self, context, event):
        _, _, self.active = get_texture_channels(context)

        self.newmatname = self.active.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.newmatname:
            self.active.name = self.newmatname

        return {'FINISHED'}


class LM_UI_ClearTexture(bpy.types.Operator):
    bl_idname = "scene.lm_clear_texture_channels"
    bl_label = "Clear All Texture Channel"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear All Texture Channel Names."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_texture_channels

    def execute(self, context):
        context.scene.lm_texture_channels.clear()

        return {'FINISHED'}


class LM_UI_RemoveTexture(bpy.types.Operator):
    bl_idname = "scene.lm_remove_texture_channel"
    bl_label = "Remove Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove selected Texture Channel Name."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_texture_channels

    def execute(self, context):
        idx, texture_channel, _ = get_texture_channels(context)

        texture_channel.remove(idx)

        context.scene.lm_texture_channel_idx = min(idx, len(context.scene.lm_texture_channels) - 1)

        return {'FINISHED'}
