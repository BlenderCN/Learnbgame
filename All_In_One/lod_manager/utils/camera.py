import bpy
from mathutils import Vector
from .object import get_bounding_sphere


def in_frustum(camera, obj, radius=0.0):
    matrix = camera.matrix_world.inverted()
    w = 0.5 * camera.data.sensor_width / camera.data.lens
    res_x = bpy.context.scene.render.resolution_x
    res_y = bpy.context.scene.render.resolution_y
    if res_x > res_y:
        x = w
        y = w * res_y / res_x
    else:
        x = w * res_x / res_y
        y = w

    lr = Vector([x, -y, -1])
    ur = Vector([x, y, -1])
    ll = Vector([-x, -y, -1])
    ul = Vector([-x, y, -1])
    normals = [
        lr.cross(ll).normalized(),
        ll.cross(ul).normalized(),
        ul.cross(ur).normalized(),
        ur.cross(lr).normalized()
    ]

    if radius > 0:
        center, _ = get_bounding_sphere(obj)
    else:
        center, radius = get_bounding_sphere(obj)
    center = matrix * center

    for n in normals:
        d = center.dot(n)
        if d < -radius:
            return False

    return True
