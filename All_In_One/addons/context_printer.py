bl_info = {
    "name": "Context",
    "category": "Scene",
}

import bpy
from bpy.props import StringProperty


class SceneContext(bpy.types.Operator):
    """Context"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.context"        # unique identifier for buttons and menu items to reference.
    bl_label = "show context"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    exact = StringProperty()

    # execute() is called by blender when running the operator.
    def execute(self, context):

        output = ''
        if not self.exact:
            # The original script
            for i in dir(context):
                print(i)
                output += '\n' + i
                for k in dir(i):
                    output += '\n' + i + '____' + k
                    # print('____'+k)
        else:
            for i in dir(exec(self.exact)):
                output += '\n' + i
        a = bpy.data.texts.new("_context_")
        a.write(output)

        # this lets blender know the operator finished successfully.
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(SceneContext)


def unregister():
    bpy.utils.unregister_class(SceneContext)


if __name__ == "__main__":
    register()

