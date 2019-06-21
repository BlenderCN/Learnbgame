import bpy
from . utils import MACHIN3 as m3


def register_keymaps():
    wm = bpy.context.window_manager

    keys = []

    # EDIT mode menu

    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')

    if m3.MM_prefs().keyboard_layout == "QWERTY":
        kmi = km.keymap_items.new("wm.call_menu", "X", "PRESS")
    else:
        kmi = km.keymap_items.new("wm.call_menu", "Y", "PRESS")

    kmi.properties.name = "machin3.mesh_machine_menu"
    keys.append((km, kmi))


    # OBJECT mode menu

    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    if m3.MM_prefs().keyboard_layout == "QWERTY":
        kmi = km.keymap_items.new("wm.call_menu", "X", "PRESS")
    else:
        kmi = km.keymap_items.new("wm.call_menu", "Y", "PRESS")

    kmi.properties.name = "machin3.mesh_machine_menu"
    keys.append((km, kmi))


    # SYMMETRIZE in edit mode

    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new("machin3.symmetrize", "X", "PRESS", alt=True)
    kmi.properties.axis = "X"
    kmi.properties.direction = "POSITIVE"

    keys.append((km, kmi))

    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new("machin3.symmetrize", "Y", "PRESS", alt=True)
    kmi.properties.axis = "Y"
    kmi.properties.direction = "NEGATIVE"
    keys.append((km, kmi))

    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new("machin3.symmetrize", "Z", "PRESS", alt=True)
    kmi.properties.axis = "Z"
    kmi.properties.direction = "POSITIVE"
    keys.append((km, kmi))

    return keys
