import bpy
from ... utils.context import ExecutionContext


class HOPS_OT_SphereCast(bpy.types.Operator):
    bl_idname = "hops.sphere_cast"
    bl_label = "Sphere / Cast"
    bl_description = "Adds subdivision and cast modifier to object making it a sphere"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        object = bpy.context.active_object
        sphereCast(object)

        return {"FINISHED"}


def sphereCast(object):
    with ExecutionContext(mode="OBJECT", active_object=object):
        bpy.ops.object.subdivision_set(level=3)
        bpy.ops.object.modifier_add(type='CAST')
        bpy.context.object.modifiers["Cast"].factor = 1
