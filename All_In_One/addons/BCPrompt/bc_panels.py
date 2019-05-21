import bpy


class TextSyncPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_idname = "TextSyncPanel"
    bl_label = "text sync checker"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        text_block = context.edit_text
        return hasattr(text_block, 'is_modified')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 4

        # show the operator if the text has
        # changed on disk.
        if context.edit_text.is_modified:
            row.operator("text.text_upsync")

classes = [TextSyncPanel]
register, unregister = bpy.utils.register_classes_factory(classes)
