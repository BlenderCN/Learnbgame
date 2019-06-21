import bpy

from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty, EnumProperty

from .config import defaults as default

class fast_lattice(PropertyGroup):

    method = EnumProperty(
        name = 'Conforming Method',
        description = 'Method to use when conforming the lattice to your selection',
        items = [
            ('WORLD', 'World Aligned', 'The world aligned method that only produces a lattice that fits around the selection without alignment'),
            ('ALIGN', 'Fit To Selection', 'Try to fit the the lattice to the selection'),
        ],
        default = default['method']
    )

    accuracy = FloatProperty(
        name = 'Accuracy',
        description = 'How accurate the lattice will conform to the selection (Increasing this value takes longer to calculate)',
        min = 0.001,
        max = 5.0,
        soft_max = 1.0,
        default = default['accuracy']
    )

    interpolation_type = EnumProperty(
        name = 'Interpolation Type',
        description = 'Interpolation type to use for the created lattice',
        items = [
            ('KEY_BSPLINE', 'BSpline', ''),
            ('KEY_CATMULL_ROM', 'Catmull-Rom', ''),
            ('KEY_CARDINAL', 'Cardinal', ''),
            ('KEY_LINEAR', 'Linear', '')
        ],
        default = default['interpolation_type']
    )
