import bpy

from bpy.types import PropertyGroup, Object, Mesh
from bpy.props import *


class Points(PropertyGroup):
    location3d: FloatVectorProperty()
    location2d: FloatVectorProperty(size=2)
    alpha: FloatProperty()
    highlight: BoolProperty()
    index: IntProperty()
    display: BoolProperty()


class option(PropertyGroup):
    object: PointerProperty(type=Object)
    mesh: PointerProperty(type=Mesh)
    grid: BoolProperty()
    display: BoolProperty()

    points: CollectionProperty(type=Points)

    location: FloatVectorProperty()
    normal: FloatVectorProperty()
    index: IntProperty()
    hit: BoolProperty()
