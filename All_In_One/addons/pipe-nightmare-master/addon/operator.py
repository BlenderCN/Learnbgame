import bpy

from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty, FloatProperty

from . import interface, utilities
from .config import defaults as default


class pipe_nightmare(Operator):
    bl_idname = 'object.pipe_nightmare'
    bl_label = 'Add Pipes'
    bl_description = 'Generate random pipes.'
    bl_options = {'PRESET', 'REGISTER', 'UNDO'}


    amount = IntProperty(
        name = 'Pipes',
        description = 'Number of pipes',
        min = 1,
        soft_max = 250,
        default = default['amount']
    )

    width = FloatProperty(
        name = 'Region Width',
        description = 'Width of the area that the pipes occupy.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['width']
    )

    height = FloatProperty(
        name = 'Region Height',
        description = 'Height of the area that the pipes occupy',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['height']
    )

    depth = FloatProperty(
        name = 'Region Depth',
        description = 'Depth of the area that the pipes occupy',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['depth']
    )

    uniform = BoolProperty(
        name = 'Uniform Placement',
        description = 'Place the generated pipes at equal intervals throughout the region depth.',
        default = default['uniform']
    )

    length_x_min = FloatProperty(
        name = 'Minimum',
        description = 'Minimum length of horizantal pipes.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['length_x_min']
    )

    length_x_max = FloatProperty(
        name = 'Maximum',
        description = 'Maximum length of horizantal pipes.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['length_x_max']
    )

    length_y_min = FloatProperty(
        name = 'Minimum',
        description = 'Minimum length of vertical pipes.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['length_y_min']
    )

    length_y_max = FloatProperty(
        name = 'Maximum',
        description = 'Maximum length of vertical pipes.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_min = 0.1,
        soft_max = 10.0,
        default = default['length_y_max']
    )

    thickness_min = FloatProperty(
        name = 'Minimum',
        description = 'The minimum thickness of the pipes.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_max = 0.2,
        precision = 3,
        default = default['thickness_min']
    )

    thickness_max = FloatProperty(
        name = 'Maximum',
        description = 'The maximum thickness of the pipes.',
        subtype = 'DISTANCE',
        min = 0.001,
        soft_max = 0.2,
        precision = 3,
        default = default['thickness_max']
    )

    straight = IntProperty(
        name = 'Straight Pipes',
        description = 'The amount of pipes that are straight',
        subtype = 'PERCENTAGE',
        min = 0,
        max = 100,
        default = default['straight']
    )

    decoration = IntProperty(
        name = 'Decorations',
        description = 'Amount of pipes that have additional decorations located along them.',
        subtype = 'PERCENTAGE',
        min = 0,
        max = 100,
        default = default['decoration']
    )

    split = IntProperty(
        name = 'Split',
        description = 'Amount of pipes that should be split up into smaller pipes that occupy the same path.',
        subtype = 'PERCENTAGE',
        min = 0,
        max = 100,
        default = default['split']
    )

    bevel = IntProperty(
        name = 'Bevel',
        description = 'Amount of pipes that should have rounded corners.',
        subtype = 'PERCENTAGE',
        min = 0,
        max = 100,
        default = default['bevel']
    )

    bevel_size = IntProperty(
        name = 'Bevel Size',
        description = 'Percentage size of the beveled corner compared to shortest length of pipe leading to/from the corner.',
        subtype = 'PERCENTAGE',
        min = 0,
        max = 50,
        default = default['bevel_size']
    )

    surface = IntProperty(
        name = 'Surface',
        description = 'The surface resolution of the pipes.',
        min = 1,
        max = 64,
        default = default['surface']
    )

    seed = IntProperty(
        name = 'Seed',
        description = 'The seed random basis for generating pipes.',
        default = default['seed']
    )

    convert = BoolProperty(
        name = 'Convert to Mesh',
        description = 'Convert the generated pipes into a single mesh object.',
        default = default['convert']
    )

    create_empty = BoolProperty(
        name = 'Create Empty',
        description = 'Create an empty as the parent for all the pipes. (Slower but allows for easier control)',
        default = default['create_empty']
    )

    tile = BoolProperty(
        name = 'Tileable',
        description = 'Make the pipes tileable along the Y axis.',
        default = default['tile']
    )

    depth_locations = []

    @classmethod
    def poll(operator, context):

        return context.mode == 'OBJECT'


    def check(self, context):

        return True


    def draw(self, context):

        interface.operator(self, context)


    def execute(self, context):

        utilities.generate(self, context)

        return {'FINISHED'}
