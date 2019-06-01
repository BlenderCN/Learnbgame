from mathutils import *

from . import math

def center(object):
    points = (Vector(object.bound_box[point][:]) for point in (0, 1, 2, 3, 4, 5, 6, 7))
    return object.matrix_world * (0.125 * math.vector_sum(points))

def left(object):
    points = (Vector(object.bound_box[point][:]) for point in (0, 1, 2, 3))
    return object.matrix_world * (0.25 * math.vector_sum(points))

def right(object):
    points = (Vector(object.bound_box[point][:]) for point in (4, 5, 6, 7))
    return object.matrix_world * (0.25 * math.vector_sum(points))

def front(object):
    points = (Vector(object.bound_box[point][:]) for point in (0, 1, 4, 5))
    return object.matrix_world * (0.25 * math.vector_sum(points))

def back(object):
    points = (Vector(object.bound_box[point][:]) for point in (2, 3, 6, 7))
    return object.matrix_world * (0.25 * math.vector_sum(points))

def top(object):
    points = (Vector(object.bound_box[point][:]) for point in (1, 2, 5, 6))
    return object.matrix_world * (0.25 * math.vector_sum(points))

def bottom(object):
    points = (Vector(object.bound_box[point][:]) for point in (0, 3, 4, 7))
    return object.matrix_world * (0.25 * math.vector_sum(points))
