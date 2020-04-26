import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty

from .. utility import names
from .. operator.shape import change


class bc(PropertyGroup):

    allow_selection: BoolProperty(
        name = names['allow_selection'],
        description = 'Preserve mouse click for viewport selection',
        update = change.allow_selection,
        default = True)

    edit_disable_modifiers: BoolProperty(
        name = names['edit_disable_modifiers'],
        description = ('Disable CTRL and SHIFT key modifiers for drawing shapes in edit mode, allows path selection'
                       '\n  Note: Disables repeat shape (edit mode)'),
        default = True)

    enable_surface_toggle: BoolProperty(
        name = names['enable_surface_toggle'],
        description = 'Toggle surface draw method from Object to Cursor with Alt-W',
        default = False)

    alt_preserve: BoolProperty(
        name = 'Preserve Alt',
        description = 'Preserve Alt for other navigational controls during cut',
        default = False)

    rmb_cancel_ngon: BoolProperty(
        name = 'RMB Cancel Ngon',
        description = 'Cancel ngon on rmb click rather then remove points',
        default = False)

    alt_draw: BoolProperty(
        name = 'Alt Center',
        description = 'Alt centers the cutter when held while drawing',
        default = True)

    shift_draw: BoolProperty(
        name = 'Shift Uniform',
        description = 'Shift uniformely expands the cutter when held while drawing',
        default = True)


def label_row(path, prop, row, label=''):
    row.label(text=label if label else names[prop])
    row.prop(path, prop, text='')


def draw(preference, context, layout):
    keymap = context.window_manager.keyconfigs.user.keymaps['3D View']
    keymap_items = keymap.keymap_items

    row = layout.row()
    row.label(text=keymap_items['bc.topbar_activate'].name)

    row.prop(keymap_items['bc.topbar_activate'], 'type', text='', full_event=True)

    label_row(preference.keymap, 'allow_selection', layout.row(), label='Allow Selection')
    label_row(preference.keymap, 'enable_surface_toggle', layout.row())
    label_row(preference.keymap, 'edit_disable_modifiers', layout.row())
    label_row(preference.keymap, 'alt_preserve', layout.row(), label='Preserve Alt')
    label_row(preference.keymap, 'rmb_cancel_ngon', layout.row(), label='RMB Cancel Ngon')
    label_row(preference.keymap, 'alt_draw', layout.row(), label='Alt Center')
    label_row(preference.keymap, 'shift_draw', layout.row(), label='Shift Uniform')
