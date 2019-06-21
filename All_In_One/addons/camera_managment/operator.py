import bpy
from datetime import datetime
from . import helpers


class ActionButton(bpy.types.Operator):
    bl_idname = "render.button"
    bl_label = "Button"

    name = bpy.props.StringProperty()
    type = bpy.props.StringProperty()

    def draw(self, context):
        self.layout.label(text=self.name)

    def execute(self, context):
        if self.type == 'ACTIVATE':
            context.scene.camera = bpy.data.objects[self.name]
            # context.scene.objects.active.select = False
            # context.scene.objects.active = bpy.data.objects[self.name]
            # context.scene.objects.active.select = True
        elif self.type == 'RENDER':
            context.scene.camera = bpy.data.objects[self.name]
            self.render(context)
        elif self.type == 'ALL':
            old_camera = context.scene.camera
            # bpy.ops.render.view_show('INVOKE_DEFAULT')
            for camera in helpers.get_all_cameras(context):
                context.scene.camera = camera
                self.render(context, True)

            context.scene.camera = old_camera
        else:
            pass
        return {'FINISHED'}

    def render(self, context, group=False):
        now = datetime.now()
        mode = 'EXEC_DEFAULT' if group else 'INVOKE_DEFAULT'
        filename = '{0}-{1}-{2}/{3}:{4}-{5}'.format(
            now.year, now.month, now.day,
            now.hour, now.minute,
            context.scene.camera.name
        )
        bpy.data.scenes[context.scene.name].render.filepath = 'blender_camera/{0}'.format(filename)
        bpy.ops.render.render(mode, write_still=True, use_viewport=(not group))
