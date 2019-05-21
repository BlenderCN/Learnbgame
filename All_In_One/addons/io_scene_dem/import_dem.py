import math

import bpy
from mathutils import Euler, Vector

from .quake.dem import Dem


def load(operator, context, filepath='', global_scale=1.0):
    dem = Dem.open(filepath)
    dem.close()

    coords = []
    times = []
    angles = []

    for message_block in dem.message_blocks[3:-2]:
        for message in message_block.messages:
            time = 0
            if hasattr(message, 'time'):
                time = message.time

            if hasattr(message, 'entity') and hasattr(message, 'origin') and message.entity == 1:
                x, y, z = message.origin
                x = (x or 0) * global_scale
                y = (y or 0) * global_scale
                z = (z or 0) * global_scale
                coords.append((x, y, z))
                times.append(time)

                ax, ay, az = message_block.view_angles
                va = math.radians(az), math.radians(ax), math.radians(ay)

                angles.append(va)

                break

    curve = bpy.data.curves.new('myCurve', type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2

    polyline = curve.splines.new('BEZIER')

    polyline.bezier_points.add(len(coords))
    for i, coord in enumerate(coords):
        x, y, z = coord
        polyline.bezier_points[i].co = (x, y, z)
        polyline.bezier_points[i].handle_right_type = 'VECTOR'
        polyline.bezier_points[i].handle_left_type = 'VECTOR'

    ob = bpy.data.objects.new('myCurve', curve)
    bpy.context.scene.objects.link(ob)

    ob = bpy.data.objects.new('client_view', None)
    ob.empty_draw_size = 16 * global_scale
    ob.empty_draw_type = 'CUBE'
    bpy.context.scene.objects.link(ob)

    for i in range(len(coords)):
        ob.location = Vector(coords[i])
        ob.rotation_euler = Euler(angles[i], 'XYZ')
        ob.keyframe_insert(data_path="location", frame=i)
        ob.keyframe_insert(data_path="rotation_euler", frame=i)


    return {'FINISHED'}
