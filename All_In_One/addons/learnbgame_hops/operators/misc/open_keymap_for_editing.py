import bpy
from ... import keymap


class HOPS_OT_OpenKeymapForEditing(bpy.types.Operator):
    bl_idname = "hops.open_keymap_for_editing"
    bl_label = "Open Keymap for Editing"
    bl_description = "Load the keymap.py file so that you can change the keys in the Text Editor"

    def execute(self, context):
        path = keymap.__file__
        bpy.data.texts.load(path)
        return {"FINISHED"}
