import bpy
from bpy.props import IntProperty, BoolProperty
import bpy.utils.previews


class HOPS_OT_CleanReOrigin(bpy.types.Operator):
    "RemovesDoubles/RecenterOrgin/ResetGeometry"
    bl_idname = "clean.reorigin"
    bl_label = "Apply All Modifiers / Recenter Origin"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convert To Mesh / Remove Doubles / Recenter Geometry"

    origin_set: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "origin_set")

    def execute(self, context):
        s_clean_rc(self.origin_set)
        return {'FINISHED'}


def s_clean_rc(origin_set):
    object = bpy.context.active_object
    # maybe convert to mesh then recenter
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    if origin_set:
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.location_clear()
    else:
        pass
    object.hops.status = "UNDEFINED"
