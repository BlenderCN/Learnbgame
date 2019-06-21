import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty

from .. utility import names


class bc(PropertyGroup):

    snap: BoolProperty(
        name = names['snap'],
        description = 'Display snap options in topbar',
        default = True)

    destructive_menu: BoolProperty(
        name = names['destructive_menu'],
        description = 'Display menu for destructive behavior in topbar',
        default = True)

    mode_label: BoolProperty(
        name = names['mode_label'],
        description = 'Display label for mode in topbar',
        default = True)

    shape_label: BoolProperty(
        name = names['shape_label'],
        description = 'Display label for shape in topbar',
        default = True)

    operation_label: BoolProperty(
        name = names['operation_label'],
        description = 'Display label for operation in topbar',
        default = True)

    surface_label: BoolProperty(
        name = names['surface_label'],
        description = 'Display label for surface in topbar',
        default = True)

    wire_only: BoolProperty(
        name = names['wire_only'],
        description = 'Display only wires for shapes',
        default = False)

    wire_width: IntProperty(
        name = names['wire_width'],
        description = 'Width of drawn wire in pixels (DPI Factored)',
        subtype = 'PIXEL',
        default = 1)

    thick_wire: BoolProperty(
        name = names['thick_wire'],
        description = 'Increases the thickness of wires when displaying wires only',
        default = False)

    wire_size_factor: IntProperty(
        name = 'Size Multiplier',
        description = 'Multiplier for thick wire setting',
        min = 2,
        soft_max = 5,
        default = 2)

    snap_dot_size: IntProperty(
        name = 'Snap Dot Size',
        description = 'Snap dot size for snapping points',
        soft_min = 5,
        soft_max = 50,
        default = 5)

    bounds: BoolProperty(
        name = names['bounds'],
        description = 'Draw the bound box during the modal',
        default = True)

    topbar_pad: BoolProperty(
        name = 'Topbar Padding',
        description = 'Add space between elements in the topbar',
        default = True)

    pad_menus: BoolProperty(
        name = 'Pad Menus',
        description = 'Add padding around right most menu elements in the topbar',
        default = True)

    padding: IntProperty(
        name = 'Padding',
        description = 'Padding amount to use in the topbar\n\n'
                      'NOTE: If too high for your window the topbar will hide/collapse\n\n'
                      'Manually enter numbers above 3',
        min = 1,
        soft_max = 3,
        default = 1)

    middle_pad: IntProperty(
        name = 'Middle',
        description = 'Additional center padding amount to use in the topbar\n\n'
                      'NOTE: If too high for your window the topbar will hide/collapse\n\n'
                      'Manually enter numbers above 24',
        min = 0,
        soft_max = 24,
        default = 0)

    fade_distance: FloatProperty(
        name = 'Fade Distance',
        description = 'Distance to Fade snapping points',
        soft_min = 0.1,
        soft_max = 10,
        default = 1.2)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    label_row(preference.display, 'snap', layout.row())
    label_row(preference.display, 'destructive_menu', layout.row())
    label_row(preference.display, 'mode_label', layout.row())
    label_row(preference.display, 'shape_label', layout.row())
    label_row(preference.display, 'operation_label', layout.row())
    label_row(preference.display, 'surface_label', layout.row())

    layout.separator()

    label_row(preference.display, 'wire_only', layout.row())
    label_row(preference.display, 'thick_wire', layout.row())
    label_row(preference.display, 'wire_width', layout.row())

    layout.separator()

    label_row(preference.display, 'fade_distance', layout.row(), label='Fade Distance')

    if preference.display.wire_size_factor:
        label_row(preference.display, 'wire_size_factor', layout.row(), 'Wire Size Multiplier')

    label_row(preference.display, 'snap_dot_size', layout.row(), 'Snap Dot Size')

    layout.separator()

    label_row(preference.display, 'topbar_pad', layout.row(), label='Topbar Padding')

    if preference.display.topbar_pad:
        label_row(preference.display, 'pad_menus', layout.row(), label='Pad Menus')
        label_row(preference.display, 'padding', layout.row(), label='Amount')

    label_row(preference.display, 'middle_pad', layout.row(), label='Middle Padding')
