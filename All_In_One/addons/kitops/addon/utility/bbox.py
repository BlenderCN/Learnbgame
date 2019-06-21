from mathutils import *

from . import math

def center(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (0, 1, 2, 3, 4, 5, 6, 7))
    return obj.matrix_world @ (0.125 * math.vector_sum(points))

def right(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (0, 1, 2, 3))
    return obj.matrix_world @ (0.25 * math.vector_sum(points))

def left(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (4, 5, 6, 7))
    return obj.matrix_world @ (0.25 * math.vector_sum(points))

def back(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (0, 1, 4, 5))
    return obj.matrix_world @ (0.25 * math.vector_sum(points))

def front(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (2, 3, 6, 7))
    return obj.matrix_world @ (0.25 * math.vector_sum(points))

def top(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (1, 2, 5, 6))
    return obj.matrix_world @ (0.25 * math.vector_sum(points))

def bottom(obj):
    points = (Vector(obj.bound_box[point][:]) for point in (0, 3, 4, 7))
    return obj.matrix_world @ (0.25 * math.vector_sum(points))
