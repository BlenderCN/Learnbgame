import bpy

from bpy.types import PropertyGroup
from bpy.props import *

from .. utility import names
from .. operator.shape import change


class bc(PropertyGroup):

    offset: FloatProperty(
        name = names['offset'],
        description = 'Shape offset along z axis',
        update = change.offset,
        precision = 3,
        default = 0.002)

    lazorcut_limit: FloatProperty(
        name = names['lazorcut_limit'],
        description = 'How thin the shape must be before triggering a lazorcut cut',
        precision = 3,
        default = 0.005)

    circle_vertices: IntProperty(
        name = names['circle_vertices'],
        description = 'Bevel segments',
        update = change.circle_vertices,
        min = 1,
        soft_max = 32,
        max = 128,
        default = 32)

    inset_thickness: FloatProperty(
        name = names['inset_thickness'],
        description = 'Shape inset thickness',
        update = change.inset_thickness,
        precision = 4,
        default = 0.02)

    array_count: IntProperty(
        name = names['array_count'],
        description = 'Array count',
        update = change.array_count,
        min = 1,
        soft_max = 32,
        default = 2)

    solidify_thickness: FloatProperty(
        name = names['solidify_thickness'],
        description = 'Shape solidify thickness',
        update = change.solidify_thickness,
        precision = 4,
        default = 0.01)

    bevel_width: FloatProperty(
        name = names['bevel_width'],
        description = 'Bevel width',
        update = change.bevel_width,
        min = 0,
        precision = 3,
        default = 0.02)

    bevel_segments: IntProperty(
        name = names['bevel_segments'],
        description = 'Bevel segments',
        update = change.bevel_segments,
        min = 1,
        soft_max = 20,
        max = 100,
        default = 6)

    quad_bevel: BoolProperty(
        name = names['quad_bevel'],
        description = 'Use two bevel modifiers to achieve better corner topology',
        update = change.quad_bevel,
        default = True)

    straight_edges: BoolProperty(
        name = names['straight_edges'],
        description = 'Use a series of bevel modifiers to provide straight edge flow in corners',
        update = change.straight_edges,
        default = False)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.shape, 'offset', layout.row())
    label_row(preference.shape, 'lazorcut_limit', layout.row())

    layout.separator()

    label_row(preference.shape, 'circle_vertices', layout.row())
    label_row(preference.shape, 'inset_thickness', layout.row())

    layout.separator()

    label_row(preference.shape, 'array_count', layout.row())
    label_row(preference.shape, 'solidify_thickness', layout.row())
    label_row(preference.shape, 'bevel_width', layout.row())
    label_row(preference.shape, 'bevel_segments', layout.row())
    label_row(preference.shape, 'quad_bevel', layout.row())
    label_row(preference.shape, 'straight_edges', layout.row())
