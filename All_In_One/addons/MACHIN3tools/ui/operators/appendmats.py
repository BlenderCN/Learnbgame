import bpy
from bpy.props import StringProperty, EnumProperty
from ... utils.registration import get_prefs
from ... utils import MACHIN3 as m3


def get_mat():
    idx = get_prefs().appendmatsIDX
    mats = get_prefs().appendmats

    active = mats[idx] if mats else None

    return idx, mats, active


class AddSeparator(bpy.types.Operator):
    bl_idname = "machin3.add_separator"
    bl_label = "Add Separator"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Add Separator"

    def execute(self, context):
        appendmats = get_prefs().appendmats

        sep = appendmats.add()
        sep.name = "---"

        return {'FINISHED'}


class Populate(bpy.types.Operator):
    bl_idname = "machin3.populate_appendmats"
    bl_label = "MACHIN3: Populate"
    bl_description = "Populate list with material names from source file."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return get_prefs().appendmatspath

    def execute(self, context):
        idx, mats, _ = get_mat()

        with bpy.data.libraries.load(get_prefs().appendmatspath, link=False) as (data_from, _):
            for name in getattr(data_from, "materials"):
                if name not in mats:
                    am = mats.add()
                    am.name = name

        return {'FINISHED'}


class Move(bpy.types.Operator):
    bl_idname = "machin3.move_appendmat"
    bl_label = "Move Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Move Material Name up or down.\nThis controls the position in the Append Material Menu.\nSave prefs to remember."

    direction: EnumProperty(items=[("UP", "Up", ""),
                                   ("DOWN", "Down", "")])

    def execute(self, context):
        idx, mats, _ = get_mat()

        if self.direction == "UP":
            nextidx = max(idx - 1, 0)
        elif self.direction == "DOWN":
            nextidx = min(idx + 1, len(mats) - 1)

        mats.move(idx, nextidx)
        get_prefs().appendmatsIDX = nextidx

        return {'FINISHED'}


class Rename(bpy.types.Operator):
    bl_idname = "machin3.rename_appendmat"
    bl_label = "Rename Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Rename the selected Material Name"

    newmatname: StringProperty(name="New Name")

    def check(self, context):
        return True

    @classmethod
    def poll(cls, context):
        return get_prefs().appendmats

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        # row = column.split(percentage=0.31)
        # row.label("Old Name")
        # row.label(self.active.name)

        column.prop(self, "newmatname")

    def invoke(self, context, event):
        _, _, self.active = get_mat()

        self.newmatname = self.active.name

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if self.newmatname:
            self.active.name = self.newmatname

        return {'FINISHED'}


class Clear(bpy.types.Operator):
    bl_idname = "machin3.clear_appendmats"
    bl_label = "Clear All Material Names"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Clear All Material Names.\nSave prefs to remember."

    @classmethod
    def poll(cls, context):
        return get_prefs().appendmats

    def execute(self, context):
        get_prefs().appendmats.clear()

        return {'FINISHED'}


class Remove(bpy.types.Operator):
    bl_idname = "machin3.remove_appendmat"
    bl_label = "Remove Material Name"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove selected Material Name.\nSave prefs to remember."

    @classmethod
    def poll(cls, context):
        return get_prefs().appendmats

    def execute(self, context):
        idx, mats, _ = get_mat()

        mats.remove(idx)

        get_prefs().appendmatsIDX = min(idx, len(get_prefs().appendmats) - 1)

        return {'FINISHED'}
