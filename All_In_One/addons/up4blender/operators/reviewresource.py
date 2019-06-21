import bpy

from unipipe import worker


class UnipipeOutputReviewSetup(bpy.types.Operator):
    """ """
    bl_idname = "wm.unipipe_output_review_setup"
    bl_label = "Output Review Item"

    @classmethod
    def poll(cls, context):
        res = worker.ImportWorker().get_resource_from_context()
        if res is not None and res.resource_type == 'narrative':
            return True

    def execute(self, context):
        res = worker.ImportWorker().get_resource_from_context()

        rev_w = worker.ReviewWorker()
        # ../review/narrative/shot_0001_0002_000/preViz/default/1/sequence/shot_0001_0002_0000_preViz_default.#####.jpg
        path = rev_w.construct_path(resource=res, ext='jpg', padding=4)

        render = bpy.data.scenes[0].render

        # Set path and file settings
        render.filepath = path
        render.use_file_extension = True
        render.use_overwrite = False
        render.use_placeholder = True
        render.use_render_cache = False
        render.image_settings.file_format = 'JPEG'
        render.image_settings.color_mode = 'RGB'
        render.image_settings.quality = 90

        render.use_simplify = False  # Switch off simplify for full res when rendering

        if res.type in ['lighting']:
            # Eevee render
            render.engine = 'BLENDER_EEVEE'
            scene_eevee = bpy.data.scenes[0].eevee
            scene_eevee.use_gtao = True
            scene_eevee.use_sss = True
            scene_eevee.use_ssr = True
            scene_eevee.use_dof = True
            scene_eevee.use_motion_blur = True
            scene_eevee.taa_samples = 16
            scene_eevee.taa_render_samples = 16

        else:
            # Workbench render
            render.engine = 'BLENDER_WORKBENCH'
            shading = bpy.data.scenes[0].display.shading
            shading.color_type = 'MATERIAL'
            shading.show_xray = False
            shading.show_shadows = False
            shading.show_cavity = True
            shading.show_object_outline = False
            shading.cavity_valley_factor = 1.7
            shading.cavity_ridge_factor = 0.4
            shading.show_specular_highlight = True

        #bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
        #popup.show_message_box(message='Successfully updated uvs (and model) for resource "{}"'.format(res.name),
        #                       title='Success...',
        #                       icon='INFO')

        self.report({'INFO'}, 'Rendering set for "{}": to: "{}"'.format(res.name, path))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(UnipipeOutputReviewSetup)


def unregister():
    bpy.utils.unregister_class(UnipipeOutputReviewSetup)
