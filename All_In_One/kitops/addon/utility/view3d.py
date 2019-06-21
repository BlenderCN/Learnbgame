import bpy

from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d


def region():
    _region = None
    # for area in bpy.context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         for _region in area.regions:
    #             if _region == bpy.context.region:
    #                 print(_region.type)
    #                 print(bpy.context.region.type)
    #             if _region.type == 'WINDOW':
    #                 # print(_region)
    #                 # print('')
    #                 break
    # return _region
    return bpy.context.region


def region3d():
    # _region3d = None
    # for area in bpy.context.screen.areas:
    #     if area.type == 'VIEW_3D':
    #         for space in area.spaces:
    #             if space.type == 'VIEW_3D':
    #                 _region3d = space.region_3d
    #                 # print(_region3d)
    #                 # print(bpy.context.region_data)
    #                 # print('')
    #                 break
    #
    # return _region3d
    return bpy.context.region_data


def mouse_origin(op):
    return region_2d_to_origin_3d(region(), region3d(), op.mouse)


def mouse_vector(op):
    return region_2d_to_vector_3d(region(), region3d(), op.mouse)


def at_cursor3d(obj):
    return obj.location == bpy.context.scene.cursor.location
