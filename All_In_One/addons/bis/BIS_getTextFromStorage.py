# Nikita Akimov
# interplanety@interplanety.org

import bpy
from . import TextManager


class BIS_getTextFromStorage(bpy.types.Operator):
    bl_idname = 'bis.get_text_from_storage'
    bl_label = 'BIS_GetFromStorage'
    bl_description = 'Get text from BIS'
    bl_options = {'REGISTER', 'UNDO'}

    text_id = bpy.props.IntProperty(
        name='text_id',
        default=0
    )
    showMessage = bpy.props.BoolProperty(
        default=False
    )

    def execute(self, context):
        rez = TextManager.TextManager.from_bis(self.text_id)
        if rez['stat'] == 'OK':
            if self.showMessage:
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message=rez['data']['text'])
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BIS_getTextFromStorage)


def unregister():
    bpy.utils.unregister_class(BIS_getTextFromStorage)
