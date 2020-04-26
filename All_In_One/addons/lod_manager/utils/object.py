import bpy
from mathutils import Vector


def get_bounding_sphere(obj):
    lower = obj.matrix_world * Vector(obj.bound_box[0])
    upper = obj.matrix_world * Vector(obj.bound_box[6])
    center = (lower + upper) / 2
    radius = (lower - upper).length / 2
    return center, radius


def get_bounding_box(obj):
    lower = obj.matrix_world * Vector(obj.bound_box[0])
    upper = obj.matrix_world * Vector(obj.bound_box[6])
    return lower, upper