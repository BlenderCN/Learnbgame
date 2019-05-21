import bpy
import mathutils


# Simple LinePlane Collision
def LinePlaneCollision(rayDirection,
                       rayPoint,
                       PP=(0.0, 0.0, 0.0),
                       PN=(0.0, 0.0, 1.0)):
    vec3PN = mathutils.Vector(PN)
    vec3PP = mathutils.Vector(PP)
    ndotu = vec3PN.dot(rayDirection)
    if abs(ndotu) < 1e-6:
        raise RuntimeError("no intersection or line is within plane")

    w = rayPoint - vec3PP
    si = -vec3PN.dot(w) / ndotu
    Psi = w + si * rayDirection + vec3PP
    return Psi


def GetBRect(points):
    b_left_x = min(point[0] for point in points)
    b_left_y = min(point[1] for point in points)
    t_right_x = max(point[0] for point in points)
    t_right_y = max(point[1] for point in points)
    return [mathutils.Vector((b_left_x, b_left_y, 0)), mathutils.Vector((t_right_x, t_right_y, 0))]
