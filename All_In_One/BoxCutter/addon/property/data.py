import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class option(PropertyGroup):
    removeable: BoolProperty()
    q_beveled: BoolProperty()
