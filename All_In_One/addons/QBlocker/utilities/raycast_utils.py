import bpy
import mathutils
import bmesh
import math
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d
from .grid_utils import *
from .math_utils import *


# Get location in matrix space
def GetPlaneLocation(context, coord, matrix):
    matrix_inv = matrix.inverted()
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    view_vector = region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    ray_target = matrix_inv @ ray_target
    ray_origin = matrix_inv @ ray_origin

    ray_direction = ray_target - ray_origin

    return LinePlaneCollision(ray_direction, ray_origin)


# Get height location in matrix space at specific centerpoint
def GetHeightLocation(context, coord, matrix, secpos):
    matrix_inv = matrix.inverted()
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    view_vector = region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + view_vector

    ray_target = matrix_inv @ ray_target
    ray_origin = matrix_inv @ ray_origin
    if isGridFrontal(context):
        gridhit = GetGridHitPoint(context, coord)
        gridWpos = gridhit[0]
        gridMpos = matrix_inv @ gridWpos
        distance = math.sqrt(math.pow((secpos[0] - gridMpos[0]), 2) + math.pow((secpos[1] - gridMpos[1]), 2))
        return distance
    else:
        ray_direction = ray_target - ray_origin
        view_dirnew = -ray_target
        view_dirnew[2] = 0.0
        view_dirnew.normalize()
        hPos = LinePlaneCollision(ray_direction, ray_origin, PP=secpos, PN=view_dirnew)
        return hPos[2]
