import bpy

from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences
from bpy.props import *

from . utility import addon, update

names = {
    'cut_color': 'Cut color',
    'slice_color': 'Slice color',
    'join_color': 'Join color',
    'make_color': 'Make color',
    'knife_color': 'Knife color',
    'negative_color': 'Negative color',
    'bbox_color': 'Bbox color',
    'wire_color': 'Wire color',
    'show_bounds': 'Show bounds',
    'sort_modifiers': 'Sort modifiers',
    'auto_smooth': 'Auto smooth',
    'use_multi_edit': 'Use mult-edit',
    'display_wires': 'Display wires',
    'debug': 'Debug'}


class option(AddonPreferences):
    bl_idname = addon.name

    cut_color: FloatVectorProperty(
        name = names['cut_color'],
        description = 'Color of the shape when cutting',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.6, 0.2, 0.2, 0.4))

    slice_color: FloatVectorProperty(
        name = names['slice_color'],
        description = 'Color of the shape when slicing',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.62, 0.5, 0.2, 0.4))

    join_color: FloatVectorProperty(
        name = names['join_color'],
        description = 'Color of the shape when joining',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.2, 0.4, 0.1, 0.4))

    make_color: FloatVectorProperty(
        name = names['make_color'],
        description = 'Color of the shape when making',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.5, 0.5, 0.5, 0.4))

    knife_color: FloatVectorProperty(
        name = names['knife_color'],
        description = 'Color of the shape when using knife',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.29, 0.52, 1.0, 0.4))

    negative_color: FloatVectorProperty(
        name = names['negative_color'],
        description = 'Color of the shape when behind a mesh object',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.1, 0.1, 0.1, 0.2))

    bbox_color: FloatVectorProperty(
        name = names['bbox_color'],
        description = 'Color of the shapes bound region',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.1, 0.1, 0.1, 0.033))

    wire_color: FloatVectorProperty(
        name = names['wire_color'],
        description = 'Color of the shape\'s wire',
        size = 4,
        min = 0,
        max = 1,
        subtype='COLOR',
        default = (0.0, 0.0, 0.0, 0.33))

    show_bounds: BoolProperty(
        name = names['show_bounds'],
        description = 'Draw the bound box during the modal',
        default = True)

    sort_modifiers: BoolProperty(
        name = 'Sort Modifiers',
        description = ('Sort modifier order\n\n'
                       'Keep these modifiers after the booleans created'
                       ' \u2022 Bevel'
                       ' \u2022 Weighted Normal'
                       ' \u2022 Array'
                       ' \u2022 Mirror'),
        default = True)

    sort_bevel: BoolProperty(
        name = 'Sort Bevel',
        description = 'Ensure bevel modifiers are placed after any boolean modifiers created',
        default = True)

    sort_weighted_normal: BoolProperty(
        name = 'Sort Weighted Normal',
        description = 'Ensure weighted normal modifiers are placed after any boolean modifiers created',
        default = True)

    sort_array: BoolProperty(
        name = 'Sort Array',
        description = 'Ensure array modifiers are placed after any boolean modifiers created',
        default = True)

    sort_mirror: BoolProperty(
        name = 'Sort Mirror',
        description = 'Ensure mirror modifiers are placed after any boolean modifiers created',
        default = False)

    auto_smooth: BoolProperty(
        name = names['auto_smooth'],
        description = 'Auto smooth geometry when cutting into it',
        default = True)

    use_multi_edit: BoolProperty(
        name = names['use_multi_edit'],
        description = 'Bring created mesh objects into edit mode',
        default = True)

    display_wires: BoolProperty(
        name = names['display_wires'],
        description = 'Display object wires on mesh when cutting',
        default = True)

    debug: BoolProperty(
        name = names['debug'],
        description = 'Display output information in the system console',
        update = update.preference.debug,
        default=False)


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text=names['auto_smooth'])
        row.prop(self, 'auto_smooth', text='')

        row = layout.row()
        row.label(text=names['use_multi_edit'])
        row.prop(self, 'use_multi_edit', text='')

        row = layout.row()
        row.label(text=names['display_wires'])
        row.prop(self, 'display_wires', text='')

        row = layout.row()
        row.label(text=names['sort_modifiers'])
        row.prop(self, 'sort_modifiers', text='')

        if self.sort_modifiers:
            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(self, 'sort_bevel', text='', icon='MOD_BEVEL')
            row.prop(self, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
            row.prop(self, 'sort_array', text='', icon='MOD_ARRAY')
            row.prop(self, 'sort_mirror', text='', icon='MOD_MIRROR')

        row = layout.row()
        row.label(text=names['debug'])
        row.prop(self, 'debug', text='')

def register():
    register_class(option)

    if addon.preference().debug:
        print('\nBOXCUTTER (DEBUG)')
        addon.log(value=F'Added addon preferences')


def unregister():
    addon.log(value=F'Removed addon preferences')
    print('BOXCUTTER (EXIT)\n')

    unregister_class(option)
