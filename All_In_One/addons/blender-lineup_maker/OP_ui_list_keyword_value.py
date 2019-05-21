import bpy

def get_keyword_values(context):
    idx = context.scene.lm_keyword_value_idx
    keyword_values = context.scene.lm_keyword_values

    active = keyword_values[idx] if keyword_values else None

    return idx, keyword_values, active

class LM_UI_MoveKeywordValue(bpy.types.Operator):
    bl_idname = "scene.lm_move_keyword_value"
    bl_label = "Move Keyword value"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move keyword_value Name up or down.\nThis controls the position in the Menu."

    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    def execute(self, context):
        idx, keyword_value, _ = get_keyword_values(context)

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(keyword_value) - 1)

        keyword_value.move(idx, nextidx)
        context.scene.lm_keyword_value_idx = nextidx

        return {'FINISHED'}



class LM_UI_RenameKeywordValue(bpy.types.Operator):
    bl_idname = "scene.lm_rename_keyword_value"
    bl_label = "Rename Texture keyword_value"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Rename the selected Texture keyword_value Name"

    newmatname: bpy.props.StringProperty(name="New Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return context.scene.lm_keyword_values

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # row = column.split(percentage=0.31)
        # row.label("Old Name")
        # row.label(self.active.name)

        column.prop(self, "newmatname")

    def invoke(self, context, event):
        _, _, self.active = get_keyword_values(context)

        self.newmatname = self.active.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.newmatname:
            self.active.name = self.newmatname

        return {'FINISHED'}


class LM_UI_ClearKeywordValue(bpy.types.Operator):
    bl_idname = "scene.lm_clear_keyword_values"
    bl_label = "Clear All Texture keyword_value"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear All Texture keyword_value Names."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_keyword_values

    def execute(self, context):
        context.scene.lm_keyword_values.clear()

        return {'FINISHED'}


class LM_UI_RemoveKeywordValue(bpy.types.Operator):
    bl_idname = "scene.lm_remove_keyword_value"
    bl_label = "Remove Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove selected Texture keyword_value Name."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_keyword_values

    def execute(self, context):
        idx, keyword_value, _ = get_keyword_values(context)

        keyword_value.remove(idx)

        context.scene.lm_keyword_value_idx = min(idx, len(context.scene.lm_keyword_values) - 1)

        return {'FINISHED'}
