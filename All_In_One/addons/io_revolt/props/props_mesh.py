"""
Name:    props_mesh
Purpose: Provides the mesh data class for Re-Volt meshes

Description:
Meshes in Re-Volt have special properties which can be accessed and modified
using the mesh data defined here.

"""


import bpy

from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    CollectionProperty,
    IntVectorProperty,
    FloatVectorProperty,
    PointerProperty
)
from ..common import *
from ..layers import *


class RVMeshProperties(bpy.types.PropertyGroup):
    face_material = EnumProperty(
        name = "Material",
        items = MATERIALS,
        get = get_face_material,
        set = set_face_material,
        description = "Surface Material"
    )
    face_texture = IntProperty(
        name = "Texture",
        get = get_face_texture,
        set = set_face_texture,
        default = 0,
        min = -1,
        max = 9,
        description = "Texture page number:\n-1 is none,\n"
                      "0 is texture page A\n"
                      "1 is texture page B\n"
                      "2 is texture page C\n"
                      "3 is texture page D\n"
                      "4 is texture page E\n"
                      "5 is texture page F\n"
                      "6 is texture page G\n"
                      "7 is texture page H\n"
                      "8 is texture page I\n"
                      "9 is texture page J\n"
                      "For this number to have an effect, "
                      "the \"Use Texture Number\" export setting needs to be "
                      "enabled"
    )
    face_double_sided = BoolProperty(
        name = "Double sided",
        get = lambda s: bool(get_face_property(s) & FACE_DOUBLE),
        set = lambda s, v: set_face_property(s, v, FACE_DOUBLE),
        description = "The polygon will be visible from both sides in-game"
    )
    face_translucent = BoolProperty(
        name = "Translucent",
        get = lambda s: bool(get_face_property(s) & FACE_TRANSLUCENT),
        set = lambda s, v: set_face_property(s, v, FACE_TRANSLUCENT),
        description = "Renders the polyon transparent\n(takes transparency "
                      "from the \"Alpha\" vertex color layer or the alpha "
                      "layer of the texture"
    )
    face_mirror = BoolProperty(
        name = "Mirror",
        get = lambda s: bool(get_face_property(s) & FACE_MIRROR),
        set = lambda s, v: set_face_property(s, v, FACE_MIRROR),
        description = "This polygon covers a mirror area. (?)"
    )
    face_additive = BoolProperty(
        name = "Additive blending",
        get = lambda s: bool(get_face_property(s) & FACE_TRANSL_TYPE),
        set = lambda s, v: set_face_property(s, v, FACE_TRANSL_TYPE),
        description = "Renders the polygon with additive blending (black "
                      "becomes transparent, bright colors are added to colors "
                      "beneath)"
    )
    face_texture_animation = BoolProperty(
        name = "Animated",
        get = lambda s: bool(get_face_property(s) & FACE_TEXANIM),
        set = lambda s, v: set_face_property(s, v, FACE_TEXANIM),
        description = "Uses texture animation for this poly (only in .w files)"
    )
    face_no_envmapping = BoolProperty(
        name = "No EnvMap (.prm)",
        get = lambda s: bool(get_face_property(s) & FACE_NOENV),
        set = lambda s, v: set_face_property(s, v, FACE_NOENV),
        description = "Disables the environment map for this poly (.prm only)"
    )
    face_envmapping = BoolProperty(
        name = "EnvMapping (.w)",
        get = lambda s: bool(get_face_property(s) & FACE_ENV),
        set = lambda s, v: set_face_property(s, v, FACE_ENV),
        description = "Enables the environment map for this poly (.w only).\n\n"
                      "If enabled on pickup.m, sparks will appear"
                      "around the poly"
    )
    face_cloth = BoolProperty(
        name = "Cloth effect (.prm)",
        get = lambda s: bool(get_face_property(s) & FACE_CLOTH),
        set = lambda s, v: set_face_property(s, v, FACE_CLOTH),
        description = "Enables the cloth effect used on the Mystery car"
    )
    face_skip = BoolProperty(
        name = "Do not export",
        get = lambda s: bool(get_face_property(s) & FACE_SKIP),
        set = lambda s, v: set_face_property(s, v, FACE_SKIP),
        description = "Skips the polygon when exporting (not Re-Volt related)"
    )
    face_env = FloatVectorProperty(
        name = "Environment Color",
        subtype = "COLOR",
        size = 4,
        min = 0.0,
        max = 1.0,
        soft_min = 0.0,
        soft_max = 1.0,
        get = get_face_env,
        set = set_face_env,
        description = "Color of the environment map for World meshes"
    )
    face_ncp_double = BoolProperty(
        name = "Double-sided",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_DOUBLE),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_DOUBLE),
        description="Enables double-sided collision"
    )
    face_ncp_object_only = BoolProperty(
        name = "Object Only",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_OBJECT_ONLY),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_OBJECT_ONLY),
        description="Enable collision for objects only (ignores camera)"
    )
    face_ncp_camera_only = BoolProperty(
        name = "Camera Only",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_CAMERA_ONLY),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_CAMERA_ONLY),
        description="Enable collision for camera only"
    )
    face_ncp_non_planar = BoolProperty(
        name = "Non-planar",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_NON_PLANAR),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_NON_PLANAR),
        description="Face is non-planar"
    )
    face_ncp_no_skid = BoolProperty(
        name = "No Skid Marks",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_NO_SKID),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_NO_SKID),
        description="Disable skid marks"
    )
    face_ncp_oil = BoolProperty(
        name = "Oil",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_OIL),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_OIL),
        description="Ground is oil"
    )
    face_ncp_nocoll = BoolProperty(
        name = "No Collision",
        get=lambda s: bool(get_face_ncp_property(s) & NCP_NOCOLL),
        set=lambda s, v: set_face_ncp_property(s, v, NCP_NOCOLL),
        description="Face will be ignored when exporting"
    )
