import bpy;
from . import helpers;

class CameraPanel(bpy.types.Panel):
    bl_label = "Camera Panel"
    bl_idname = "Camera_Render_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        all = row.operator('render.button', text='render all cameras')
        all.type = 'ALL'

        for camera in helpers.get_all_cameras(context):
            row = layout.row()
            split = row.split(0.4)
            col = split.column()
            sr = col.row()
            icon = 'OUTLINER_OB_CAMERA' if camera == context.scene.camera else 'CAMERA_DATA'
            sr.label(text=camera.name, icon=icon)

            col = split.column()
            subrow = col.row()

            activate = subrow.operator('render.button', text='primary')
            activate.name = camera.name
            activate.type = 'ACTIVATE'

            render = subrow.operator('render.button', text='render')
            render.name = camera.name
            render.type = 'RENDER'
