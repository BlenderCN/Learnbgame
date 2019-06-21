import bpy
import os

from ..bc_utils import print_addon_msg


addon_keymaps = []


def add_keymap(origin):
    print_addon_msg(origin, ': operators registered')

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        print('no keyconfig path found, skipping')
        return

    """ Console: Add Ctrl + Enter """

    km = kc.keymaps.new(name='Console', space_type='CONSOLE')
    kmi = km.keymap_items

    new_shortcut = kmi.new('console.do_action', 'RET', 'PRESS', ctrl=1)
    addon_keymaps.append((km, new_shortcut))

    """ Text Editor: Add fwslash """

    km = kc.keymaps.new(name='Text', space_type='TEXT_EDITOR')
    kmi = km.keymap_items

    new_shortcut = kmi.new('text.do_comment', 'SLASH', 'PRESS', ctrl=1)
    addon_keymaps.append((km, new_shortcut))

    """ Text Editor: Add text cycle using wheel to """

    cycle_textblocks = 'text.cycle_textblocks'

    new_shortcut = kmi.new(cycle_textblocks, 'WHEELUPMOUSE', 'PRESS', alt=1)
    new_shortcut.properties.direction = 1
    addon_keymaps.append((km, new_shortcut))

    new_shortcut = kmi.new(cycle_textblocks, 'WHEELDOWNMOUSE', 'PRESS', alt=1)
    new_shortcut.properties.direction = -1
    addon_keymaps.append((km, new_shortcut))


def remove_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
