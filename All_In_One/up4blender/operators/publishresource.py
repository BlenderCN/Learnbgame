import bpy

from unipipe import worker

from ..gui import popup


class UnipipePublishResource(bpy.types.Operator):
    """ Publish a resource based on current resource """
    bl_idname = "wm.unipipe_publish_resource"
    bl_label = "Publish resource"

    @classmethod
    def poll(cls, context):
        if worker.ImportWorker().get_resource_from_context() is not None:
            return True

    def execute(self, context):
        res = worker.ImportWorker().get_resource_from_context()
        worker.PublishWorker().publish_from_context(open_original_file=True)

        # TODO: Currently this causes crashing
        # popup.show_message_box(message='Successfully published "{}" for resource "{}"'.format(res.type, res.name),
        #                        title='Success...',
        #                        icon='INFO')

        self.report({'INFO'}, 'Successfully published "{}" for resource "{}"'.format(res.type, res.name))

        return {'FINISHED'}


class UnipipeUpdateResourceUVs(bpy.types.Operator):
    """ Update the UVs from material file to model file by publishing model from the shader file """
    bl_idname = "wm.unipipe_update_model_resource"
    bl_label = "Update/Publish UVs"

    @classmethod
    def poll(cls, context):
        res = worker.ImportWorker().get_resource_from_context()
        if res is not None and res.type == 'shader':
            return True

    def execute(self, context):

        res = worker.ImportWorker().get_resource_from_context()
        res.type = 'model'

        worker.PublishWorker().publish_from_context(open_original_file=True, update_work_file=True, resource=res)

        # TODO: Currently this causes crashing
        # popup.show_message_box(message='Successfully updated uvs (and model) for resource "{}"'.format(res.name),
        #                        title='Success...',
        #                        icon='INFO')

        self.report({'INFO'}, 'Successfully updated uvs (and model) for resource "{}"'.format(res.name))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(UnipipePublishResource)
    bpy.utils.register_class(UnipipeUpdateResourceUVs)


def unregister():
    bpy.utils.unregister_class(UnipipePublishResource)
    bpy.utils.unregister_class(UnipipeUpdateResourceUVs)
