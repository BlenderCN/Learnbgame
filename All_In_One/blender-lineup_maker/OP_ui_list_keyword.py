import bpy

def get_keywords(context):
    idx = context.scene.lm_keyword_idx
    keywords = context.scene.lm_keywords

    active = keywords[idx] if keywords else None

    return idx, keywords, active

class LM_UI_MoveKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_move_keyword"
    bl_label = "Move Keyword"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move keyword Name up or down.\nThis controls the position in the Menu."

    direction: bpy.props.EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")])

    def execute(self, context):
        idx, keyword, _ = get_keywords(context)

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(keyword) - 1)

        keyword.move(idx, nextidx)
        context.scene.lm_keyword_idx = nextidx

        return {'FINISHED'}



class LM_UI_RenameKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_rename_keyword"
    bl_label = "Rename Texture keyword"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Rename the selected Texture keyword Name"

    newmatname: bpy.props.StringProperty(name="New Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return context.scene.lm_keywords

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # row = column.split(percentage=0.31)
        # row.label("Old Name")
        # row.label(self.active.name)

        column.prop(self, "newmatname")

    def invoke(self, context, event):
        _, _, self.active = get_keywords(context)

        self.newmatname = self.active.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.newmatname:
            self.active.name = self.newmatname

        return {'FINISHED'}


class LM_UI_ClearKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_clear_keywords"
    bl_label = "Clear All Texture keyword"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear All Texture keyword Names."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_keywords

    def execute(self, context):
        context.scene.lm_keywords.clear()

        return {'FINISHED'}


class LM_UI_RemoveKeyword(bpy.types.Operator):
    bl_idname = "scene.lm_remove_keyword"
    bl_label = "Remove Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove selected Texture keyword Name."

    @classmethod
    def poll(cls, context):
        return context.scene.lm_keywords

    def execute(self, context):
        idx, keyword, _ = get_keywords(context)

        keyword.remove(idx)

        context.scene.lm_keyword_idx = min(idx, len(context.scene.lm_keywords) - 1)

        return {'FINISHED'}
