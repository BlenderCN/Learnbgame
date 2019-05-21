import bpy

from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d, location_3d_to_region_2d, region_2d_to_location_3d
from mathutils.geometry import intersect_line_plane

from . import addon


def location2d_to_origin3d(x, y):
    return region_2d_to_origin_3d(bpy.context.region, bpy.context.region_data, (x, y))


def location2d_to_vector3d(x, y):
    return region_2d_to_vector_3d(bpy.context.region, bpy.context.region_data, (x, y))


def location2d_intersect3d(x, y, location, normal):
    origin = location2d_to_origin3d(x, y)
    try:
        return intersect_line_plane(origin, origin + location2d_to_vector3d(x, y), location, normal)
    except: pass


def location3d_to_location2d(location):
    return location_3d_to_region_2d(bpy.context.region, bpy.context.region_data, location)


def location2d_to_location3d(x, y, location):
    return region_2d_to_location_3d(bpy.context.region, bpy.context.region_data, (x, y), location)
