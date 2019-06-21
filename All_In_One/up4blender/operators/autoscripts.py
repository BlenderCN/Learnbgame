import os
import bpy

from ..gui import popup


class RenameMeshBasedOnGeo(bpy.types.Operator):
    """ Import(append) a published model resource based on the current resource """
    bl_idname = "wm.rename_mesh_based_on_geo"
    bl_label = "Rename mesh based on geo"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        objects = bpy.data.objects
        count = 0

        for each in objects:

            if each.type == 'MESH':
                each.data.name = each.name.replace('geo', 'mesh')
                count += 1

        popup.show_message_box(message='Successfully renamed {} pieces of mesh'.format(count),
                               title='Success...',
                               icon='INFO')

        self.report({'INFO'}, 'Successfully renamed {} meshes'.format(count))

        return {'FINISHED'}


def register():
    bpy.utils.register_class(RenameMeshBasedOnGeo)


def unregister():
    bpy.utils.unregister_class(RenameMeshBasedOnGeo)
