# Nikita Akimov
# interplanety@interplanety.org

import bpy
from .TextManager import TextManager


class BISUpdateText(bpy.types.Operator):
    bl_idname = 'bis.update_text_in_storage'
    bl_label = 'Update Text'
    bl_description = 'Update text in the BIS'
    bl_options = {'REGISTER', 'UNDO'}

    showMessage = bpy.props.BoolProperty(
        default=False
    )

    def execute(self, context):
        current_text = context.area.spaces.active.text
        if 'bis_uid' in current_text:
            rez = TextManager.update_in_bis(current_text['bis_uid'], current_text)
            if rez['stat'] == 'OK':
                if self.showMessage:
                    bpy.ops.message.messagebox('INVOKE_DEFAULT', message=rez['stat'] + ': ' + rez['data']['text'])
            else:
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message=rez['stat'] + ': ' + rez['data']['text'])
        else:
            bpy.ops.message.messagebox('INVOKE_DEFAULT', message='ERR: First save this Text to the BIS!')
        return {'FINISHED'}

    def draw(self, context):
        self.layout.separator()
        self.layout.label('Update current Text in the BIS storage?')
        self.layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)


def register():
    bpy.utils.register_class(BISUpdateText)


def unregister():
    bpy.utils.unregister_class(BISUpdateText)
