import bpy

from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

def region():
    _region = None
    for _region in bpy.context.area.regions:
        if _region.type == 'WINDOW':
            break

    return _region

def region3d():
    _region3d = None
    for space in bpy.context.area.spaces:
        if space.type == 'VIEW_3D':
            _region3d = space.region_3d
            break

    return _region3d

def mouse_origin(op):
    return region_2d_to_origin_3d(region(), region3d(), op.mouse)

def mouse_vector(op):
    return region_2d_to_vector_3d(region(), region3d(), op.mouse)

def at_cursor3d(object):
    return object.location == bpy.context.space_data.cursor_location
