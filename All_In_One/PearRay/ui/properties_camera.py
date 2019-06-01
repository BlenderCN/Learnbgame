import bpy


from bl_ui import properties_data_camera
for member in dir(properties_data_camera):
    subclass = getattr(properties_data_camera, member)
    try:
        subclass.COMPAT_ENGINES.add('PEARRAY_RENDER')
    except:
        pass
del properties_data_camera


class CameraDataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        cam = context.camera
        rd = context.scene.render
        return cam and (rd.use_game_engine is False) and (rd.engine in cls.COMPAT_ENGINES)


class CAMERA_PT_pr_cam_settings(CameraDataButtonsPanel, bpy.types.Panel):
    bl_label = "PearRay Settings"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw_header(self, context):
        cam = context.camera

    def draw(self, context):
        layout = self.layout

        cam = context.camera

        layout.prop(cam.pearray, "zoom")

        split = layout.split()

        split.prop(cam.pearray, "fstop")
        split.prop(cam.pearray, "apertureRadius")