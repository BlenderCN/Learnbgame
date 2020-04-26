bl_info = {
    "name": "d_delete_withoutConfirm",
    "author": "Way2Close",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "description": "Deletes element from msm",
    "category": "3D View"}

import bpy


class Delete_withoutConfirm(bpy.types.Operator):
    """Deletes element from msm"""
    bl_idname = "edit.delete_without_confirm"
    bl_label = "delete_withoutConfirm"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # delete_withoutConfirm

        # get msm
        msm = bpy.context.tool_settings.mesh_select_mode

        # cancel if no active
        if not bpy.context.active_object:
            return {'FINISHED'}

        if bpy.context.active_object.mode == "EDIT":

            if msm[0]:
                # delete verts
                bpy.ops.mesh.delete(type = 'VERT')

            elif msm[1]:
                # delete edges
                bpy.ops.mesh.delete(type = 'EDGE')

            elif msm[2]:
                # delete faces
                bpy.ops.mesh.delete(type = 'FACE')

        return {'FINISHED'}


classes = (
    Delete_withoutConfirm,
)

register, unregister = bpy.utils.register_classes_factory(classes)


if __name__ == "__main__":
    register()
