import bpy
import math

from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d, location_3d_to_region_2d, region_2d_to_location_3d
from mathutils.geometry import intersect_line_plane

from . import addon


def location2d_to_origin3d(x, y):
    return region_2d_to_origin_3d(bpy.context.region, bpy.context.region_data, (x, y))


def location2d_to_vector3d(x, y):
    return region_2d_to_vector_3d(bpy.context.region, bpy.context.region_data, (x, y))


def location2d_intersect3d(x, y, location, normal):
    origin = location2d_to_origin3d(x, y)
    return intersect_line_plane(origin, origin + location2d_to_vector3d(x, y), location, normal)


def location3d_to_location2d(location):
    return location_3d_to_region_2d(bpy.context.region, bpy.context.region_data, location)


def location2d_to_location3d(x, y, location):
    return region_2d_to_location_3d(bpy.context.region, bpy.context.region_data, (x, y), location)


def view_orientation():
    # self.region_3d.view_rotation
    r = lambda x: round(x, 3)
    view_rot = bpy.context.region_data.view_rotation.to_euler()

    orientation_dict = {(0.0, 0.0, 0.0): 'TOP',
                        (r(math.pi), 0.0, 0.0): 'BOTTOM',
                        (r(math.pi/2), 0.0, 0.0): 'FRONT',
                        (r(math.pi/2), 0.0, r(math.pi)): 'BACK',
                        (r(math.pi/2), 0.0, r(-math.pi/2)): 'LEFT',
                        (r(math.pi/2), 0.0, r(math.pi/2)): 'RIGHT'}

    return orientation_dict.get(tuple(map(r, view_rot)), 'UNDEFINED')
