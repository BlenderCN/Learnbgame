import bpy

from bpy.types import PropertyGroup
from bpy.props import StringProperty


class option(PropertyGroup):
    origin: StringProperty()
