import bpy
from mathutils import Vector


def adjust_bezier_controls(context, instruction='average'):

    '''
    W -> resize longest
    W -> resize shortest
    W -> normalize
    W -> average
    '''

    bpy.ops.object.mode_set(mode='OBJECT')
    ao = bpy.context.active_object

    active_spline = ao.data.splines.active
    for s in active_spline.bezier_points:
        if not (s.select_control_point and s.select_left_handle and s.select_right_handle):
            continue
        else:

            distance_1 = (s.co - s.handle_left).length
            distance_2 = (s.co - s.handle_right).length

            if instruction == 'average':
                avg = (distance_1 + distance_2) / 2
                s.handle_left = s.co.lerp(s.handle_left, avg / distance_1)
                s.handle_right = s.co.lerp(s.handle_right, avg / distance_2)
            # break
    bpy.ops.object.mode_set(mode='EDIT')


class CurveHandleEqualizer(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "curve.curve_handle_eq"
    bl_label = "Curve Handle Equalizer"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None) and (context.active_object.type == 'CURVE')

    def execute(self, context):
        adjust_bezier_controls(context, instruction='average')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CurveHandleEqualizer)


def unregister():
    bpy.utils.unregister_class(CurveHandleEqualizer)
