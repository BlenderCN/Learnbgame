import bpy
from ... utils.objects import obj_quads_to_tris


class HOPS_OT_DrawUV(bpy.types.Operator):
        bl_idname = "hops.draw_uv"
        bl_label = "Draw UV"
        bl_description = "Draw UVs in the 3d view"
        bl_options = {'REGISTER', 'UNDO'}

        @classmethod
        def poll(cls, context):
            object = context.active_object
            if object is None: return False
            return object.type == "MESH"

        def execute(self, context):

            try:
                hops_draw_uv()
            except RuntimeError:
                bpy.ops.ed.undo()

            return {"FINISHED"}


def hops_draw_uv():
    bpy.ops.ed.undo_push()
    bpy.ops.ed.undo_push()
    obj_quads_to_tris()
    bpy.ops.hops.draw_object_uvs()
    bpy.ops.ed.undo()
