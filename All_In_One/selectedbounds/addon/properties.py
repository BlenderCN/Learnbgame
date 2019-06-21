import bpy

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty, IntProperty

from .config import defaults as default

class selected_bounds(PropertyGroup):

    mode = EnumProperty(
        name = 'Display Mode',
        description = 'What objects to display bound indicators around.',
        items = [
            ('SELECTED', 'Selected Objects', 'The selected objects.'),
            ('ACTIVE', 'Active Object', 'The active object.'),
        ],
        default = default['mode']
    )

    color = FloatVectorProperty(
        name = 'Color',
        description = 'Color of the bound indicators.',
        subtype = 'COLOR',
        size = 4,
        min = 0.0,
        max = 1.0,
        default = default['color']
    )

    use_object_color = BoolProperty(
        name = 'Use Object Color',
        description = 'Use the object\'s color.',
        default = default['use_object_color']
    )

    width = IntProperty(
        name = 'Width',
        description = 'Width of the bound indicator lines in pixels.',
        min = 1,
        max = 8,
        subtype = 'PIXEL',
        default = default['width']
    )

    length = IntProperty(
        name = 'Length',
        description = 'Length of the bound indicator lines as they extend toward the corners. (50% makes a complete box)',
        min = 1,
        soft_min = 10,
        max = 50,
        subtype = 'PERCENTAGE',
        default = default['length']
    )
