from enum import Enum


class Operators(Enum):
    PREVIEW = "object.b4b_preview",
    RENDER = "object.b4b_render",
    LOD_EXPORT = "object.b4b_lod_export",
    LOD_FIT = "object.b4b_lod_fit",
    LOD_CUSTOM = "object.b4b_lod_custom",
    LOD_DELETE = "object.b4b_lod_delete",
    SUN_ADD = "object.b4b_sun_add",
    SUN_DELETE = "object.b4b_sun_delete",
    CAM_ADD = "object.b4b_camera_add",
    CAM_DELETE = "object.b4b_camera_delete",


class Rotation(Enum):
    SOUTH = 0
    EAST = 1
    NORTH = 2
    WEST = 3


class Zoom(Enum):
    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
