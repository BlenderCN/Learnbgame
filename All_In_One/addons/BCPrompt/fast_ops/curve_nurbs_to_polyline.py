import bpy
from mathutils import Vector


def nurbs_to_polyline(context, mode='active'):

    bpy.ops.object.mode_set(mode='OBJECT')
    ao = bpy.context.active_object

    if mode == 'active':
        ao.data.splines.active.type = 'POLY'
    elif mode == 'all':
        print('do all!')
        ...

    bpy.ops.object.mode_set(mode='EDIT')


class CurveNurbsToPolyline(bpy.types.Operator):
    bl_idname = "curve.nurbs_to_polyline"
    bl_label = "Curve NURBS to polyline"

    mode = bpy.props.StringProperty(default='active')

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None) and (context.active_object.type == 'CURVE')

    def execute(self, context):
        nurbs_to_polyline(context, self.mode)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CurveNurbsToPolyline)


def unregister():
    bpy.utils.unregister_class(CurveNurbsToPolyline)
