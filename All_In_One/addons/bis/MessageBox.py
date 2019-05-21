# Nikita Akimov
# interplanety@interplanety.org

import bpy


class MessageBox(bpy.types.Operator):
    bl_idname = 'message.messagebox'
    bl_label = ''

    message = bpy.props.StringProperty(
        name='message',
        description='message',
        default=''
    )

    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.layout.label(self.message)
        self.layout.label('')


def register():
    bpy.utils.register_class(MessageBox)


def unregister():
    bpy.utils.unregister_class(MessageBox)


if __name__ == '__main__':
    register()
