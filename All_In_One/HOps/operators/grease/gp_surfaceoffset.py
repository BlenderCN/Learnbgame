import bpy

from mathutils import Vector

from bpy.types import Operator
from bpy.props import FloatProperty


class HOPS_OT_GPCSurfaceOffset(Operator):
    bl_idname = 'hops.surfaceoffset'
    bl_label = 'GP Surface Offset'
    bl_description = 'Sets Grease Pencil to offset from surface'
    bl_options = {'REGISTER', 'UNDO'}

    surfaceoffset: FloatProperty(
        name = 'Surface Offset',
        description = 'Amount to offset on surface for snapping',
        default = 0.00001)

    def execute(self, context):
        object = bpy.context.active_object
        
        bpy.context.scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
        bpy.context.object.data.zdepth_offset = self.surfaceoffset
        
        return {'FINISHED'}
