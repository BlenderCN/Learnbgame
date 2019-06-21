import os
import bpy

from unipipe import worker


class UnipipeRenderSettings(bpy.types.Operator):
    """ """
    bl_idname = "wm.unipipe_set_render_settings"
    bl_label = "Set Render Settings"

    @classmethod
    def poll(cls, context):
        res = worker.ImportWorker().get_resource_from_context()
        if res is not None and res.resource_type == 'narrative':
            return True

    def execute(self, context):
        res = worker.ImportWorker().get_resource_from_context()

        scene = bpy.data.scenes[0]
        render = scene.render

        if res.type == 'lighting':

            # Cycles render
            cycles = scene.cycles
            render.engine = 'CYCLES'
            cycles.device = 'GPU'

            # Sampling
            cycles.progressive = 'PATH'
            cycles.samples = 768
            cycles.preivew_samples = 768
            cycles.use_animated_seed = True
            cycles.sampling_pattern = 'CORRELATED_MUTI_JITTER'

            # Light Paths
            cycles.caustics_reflective = False
            cycles.caustics_refractive = False

            # Hair
            scene.cycles_curves.use_curves = True
            scene.cycles_curves.minimum_width = 1
            scene.cycles_curves.shape = 'RIBBONS'
            scene.cycles_curves.primitive = 'CURVE_SEGMENTS'
            scene.cycles_curves.subdivisions = 3

            # Film
            cycles.film_transparent = True

            # Performance
            render.tile_x = 8
            render.tile_y = 8
            cycles.tile_order = 'TOP_TO_BOTTOM'

            render.use_compositing = False

        elif res.type == 'compositing':
            # Cycles render # NOT really needed....
            cycles = scene.cycles
            render.engine = 'CYCLES'
            cycles.device = 'GPU'
            render.use_compositing = True

        else:
            # Workbench render
            render.engine = 'BLENDER_WORKBENCH'
            shading = bpy.data.scenes[0].display.shading
            shading.color_type = 'MATERIAL'
            shading.show_xray = False
            shading.show_shadows = False
            shading.show_cavity = True
            shading.show_object_outline = True
            shading.cavity_valley_factor = 1.7
            shading.cavity_ridge_factor = 0.4
            shading.show_specular_highlight = True
            render.use_compositing = False

        render.use_simplify = False  # Switch off simplify for full res when rendering
        render.use_sequencer = False

        self.report({'INFO'}, 'Render settings set for {} type: "{}"'.format(res.resource_type, res.type))

        return {'FINISHED'}


class UnipipeSetRenderPath(bpy.types.Operator):
    """ """
    bl_idname = "wm.unipipe_set_render_path"
    bl_label = "Set Render Path"

    @classmethod
    def poll(cls, context):
        res = worker.ImportWorker().get_resource_from_context()
        if res is not None and res.resource_type == 'narrative':
            return True

    def execute(self, context):
        res = worker.ImportWorker().get_resource_from_context()
        rev_w = worker.ReviewWorker()

        render = bpy.data.scenes[0].render

        if res.type == 'lighting':
            render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
            render.image_settings.color_mode = 'RGBA'
            render.image_settings.color_depth = '32'
            render.image_settings.exr_codec = 'PXR24'
            path = rev_w.construct_path(resource=res, ext='exr', padding=4)

        elif res.type == 'compositing':
            render.image_settings.file_format = 'PNG'
            render.image_settings.color_mode = 'RGB'
            render.image_settings.color_depth = '16'
            render.image_settings.compression = 10
            path = rev_w.construct_path(resource=res, ext='png', padding=4)

        else:
            render.image_settings.file_format = 'JPEG'
            render.image_settings.color_mode = 'RGB'
            render.image_settings.quality = 90
            path = rev_w.construct_path(resource=res, ext='jpg', padding=4)

        # Set Path
        render.filepath = path

        # Set generic output settings
        render.use_file_extension = True
        render.use_overwrite = False
        render.use_placeholder = True
        render.use_render_cache = False
        render.use_stamp_hostname = True

        clip_path = '../{}'.format(os.sep.join(path.rsplit(os.sep, 3)))

        self.report({'INFO'}, 'Render path for "{}": set to: "{}"'.format(res.name, clip_path))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(UnipipeRenderSettings)
    bpy.utils.register_class(UnipipeSetRenderPath)


def unregister():
    bpy.utils.unregister_class(UnipipeSetRenderPath)
    bpy.utils.unregister_class(UnipipeRenderSettings)