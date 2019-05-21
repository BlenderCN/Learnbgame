import bpy
import bpy.utils.previews


class HOPS_OT_CleanReOrigin(bpy.types.Operator):
    "RemovesDoubles/RecenterOrgin/ResetGeometry"
    bl_idname = "clean.reorigin"
    bl_label = "CleanRecenter"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove Doubles / Recenter Origin / Reset Geometry"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def execute(self, context):
        s_clean_rc()

        return {'FINISHED'}


def s_clean_rc():
    object = bpy.context.active_object
    # maybe convert to mesh then recenter
    bpy.ops.object.modifier_remove(modifier="Bevel")
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    bpy.ops.object.location_clear()
    object.hops.status = "UNDEFINED"
