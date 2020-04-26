import bpy

from bpy.types import PropertyGroup, Object
from bpy.props import PointerProperty, BoolProperty


class option(PropertyGroup):
    target: PointerProperty(type=Object)
    shape: BoolProperty()
    slice: BoolProperty()
    applied: BoolProperty()
    applied_cycle: BoolProperty()
    inset: BoolProperty()
    copy: BoolProperty()

    array: BoolProperty()
    solidify: BoolProperty()
    bevel: BoolProperty()
    mirror: BoolProperty()
