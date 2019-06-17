import bpy

from bpy.types import PropertyGroup
from bpy.props import *

from .. utility import names


class bc(PropertyGroup):

    cut: FloatVectorProperty(
        name = names['cut'],
        description = 'Color of the shape when cutting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.604, 0.064, 0.064, 0.2))

    slice: FloatVectorProperty(
        name = names['slice'],
        description = 'Color of the shape when slicing',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.604, 0.422, 0.064, 0.2))

    inset: FloatVectorProperty(
        name = names['inset'],
        description = 'Color of the shape when insetting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.236, 0.064, 0.604, 0.2))

    join: FloatVectorProperty(
        name = names['join'],
        description = 'Color of the shape when joining',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.217, 0.604, 0.064, 0.2))

    make: FloatVectorProperty(
        name = names['make'],
        description = 'Color of the shape when making',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.604, 0.604, 0.604, 0.2))

    knife: FloatVectorProperty(
        name = names['knife'],
        description = 'Color of the shape when using knife',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.29, 0.52, 1.0, 0.2))

    negative: FloatVectorProperty(
        name = names['negative'],
        description = 'Color of the shape when behind a mesh object',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.1, 0.1, 0.1, 0.2))

    bbox: FloatVectorProperty(
        name = names['bbox'],
        description = 'Color of the shapes bound region',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.1, 0.1, 0.1, 0.033))

    wire: FloatVectorProperty(
        name = names['wire'],
        description = 'Color of the shape\'s wire',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.0, 0.0, 0.0, 0.33))

    snap_point: FloatVectorProperty(
        name = names['snap_point'],
        description = 'Color of snapping points',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.0, 0.0, 0.0, 0.4))

    snap_point_highlight: FloatVectorProperty(
        name = names['snap_point_highlight'],
        description = 'Color of snapping points highlighted',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (1.0, 1.0, 1.0, 0.65))

    reduce_opacity_editmode: BoolProperty(
        name = names['reduce_opacity_editmode'],
        description = 'Reduce opacity of shapes when in edit mode',
        default = True)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.color, 'cut', layout.row())
    label_row(preference.color, 'slice', layout.row())
    label_row(preference.color, 'inset', layout.row())
    label_row(preference.color, 'join', layout.row())
    label_row(preference.color, 'make', layout.row())
    label_row(preference.color, 'knife', layout.row())
    label_row(preference.color, 'wire', layout.row())
    label_row(preference.color, 'snap_point', layout.row())
    label_row(preference.color, 'snap_point_highlight', layout.row())
    label_row(preference.color, 'reduce_opacity_editmode', layout.row())
