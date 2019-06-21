import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class bc(PropertyGroup):

    shape: BoolProperty(
        name = 'Expand Shape',
        default = False)

    display: BoolProperty(
        name = 'Expand Display',
        default = False)

    input: BoolProperty(
        name = 'Expand Input',
        default = False)

    behavior: BoolProperty(
        name = 'Expand Behavior',
        default = False)

    hops: BoolProperty(
        name = 'Expand HardOps',
        default = False)
