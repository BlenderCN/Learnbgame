import bpy
import mathutils
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, location_3d_to_region_2d
from .math_utils import *


# create matrix from vector for gridsnap
def GetGridMatrix(Zvec):
    mat = mathutils.Matrix()
    mat[0][0], mat[0][1], mat[0][2] = Zvec[1], Zvec[2], Zvec[0]
    mat[1][0], mat[1][1], mat[1][2] = Zvec[2], Zvec[0], Zvec[1]
    mat[2][0], mat[2][1], mat[2][2] = -Zvec[0], -Zvec[1], -Zvec[2]
    return mat


# get the position and vector on grid
def GetGridHitPoint(context, coord):
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    view_vector = region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = region_2d_to_origin_3d(region, rv3d, coord)
    grid_vector = GetGridVector(context)
    return LinePlaneCollision(view_vector, ray_origin, (0.0, 0.0, 0.0), grid_vector), grid_vector


# check if view side ortho
def GetGridVector(context):
    view_matrix = context.region_data.view_matrix
    viewY = view_matrix[1].copy()
    viewY.resize_3d()
    viewDot = viewY.dot((0.0, 0.0, 1.0))
    if int(viewDot) == 1:
        viewZ = view_matrix[2].copy()
        viewZ.resize_3d()
        return -viewZ
    else:
        return (0.0, 0.0, 1.0)


# true if orto side view
def isGridFrontal(context):
    view_matrix = context.region_data.view_matrix
    viewY = view_matrix[1].copy()
    viewY.resize_3d()
    viewY.normalize()
    sumY = abs(viewY[0]) + abs(viewY[1]) + abs(viewY[2])
    if abs(sumY - 1) < 0.00001:
        return True
    else:
        return False
