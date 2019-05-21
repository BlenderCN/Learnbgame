# Nikita Akimov
# interplanety@interplanety.org

import bpy
from . import TextManager


class BIS_addTextToStorage(bpy.types.Operator):
    bl_idname = 'bis.add_text_to_storage'
    bl_label = 'BIS_AddToStorage'
    bl_description = 'Add text to BIS'
    bl_options = {'REGISTER', 'UNDO'}

    textName = bpy.props.StringProperty(
        name='textName',
        description='Add text with current name',
        default=''
    )
    showMessage = bpy.props.BoolProperty(
        default=False
    )

    def execute(self, context):
        if self.textName:
            current_text = bpy.data.texts[self.textName]
        else:
            current_text = context.area.spaces.active.text
        rez = TextManager.TextManager.to_bis(current_text, context.scene.bis_add_text_to_storage_vars.tags)
        if rez['stat'] == 'OK':
            context.scene.bis_add_text_to_storage_vars.tags = ''
            if self.showMessage:
                bpy.ops.message.messagebox('INVOKE_DEFAULT', message=rez['data']['text'])
        return {'FINISHED'}


class BIS_addTextToStorageVars(bpy.types.PropertyGroup):
    tags = bpy.props.StringProperty(
        name='Tags',
        description='Tags',
        default=''
    )


def register():
    bpy.utils.register_class(BIS_addTextToStorage)
    bpy.utils.register_class(BIS_addTextToStorageVars)
    bpy.types.Scene.bis_add_text_to_storage_vars = bpy.props.PointerProperty(type=BIS_addTextToStorageVars)


def unregister():
    del bpy.types.Scene.bis_add_text_to_storage_vars
    bpy.utils.unregister_class(BIS_addTextToStorageVars)
    bpy.utils.unregister_class(BIS_addTextToStorage)
