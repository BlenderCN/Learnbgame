import bpy
from . utils.addons import addon_exists


addon_keymaps = []


def register_keymap():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    # register to 3d view mode tab
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    kmi = km.keymap_items.new("wm.call_menu_pie", "Q", "PRESS", shift=True)
    kmi.properties.name = "hops_main_pie"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS")
    kmi.properties.name = "hops_main_menu"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("view3d.hops_helper_popup", "ACCENT_GRAVE", "PRESS", ctrl=True)
    # kmi.properties.tab = "MODIFIERS"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu", "M", "PRESS", alt=True)
    kmi.properties.name = "hops.material_list_menu"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu", "V", "PRESS", alt=True)
    kmi.properties.name = "hops.vieport_submenu"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("hops.mirror_mirror_x", 'X', 'PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.mirror_mirror_y", 'Y', 'PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.mirror_mirror_z", 'Z', 'PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.mirror_gizmo", 'X', 'PRESS', alt=True)
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')

    kmi = km.keymap_items.new("hops.bool_union", 'NUMPAD_PLUS', 'PRESS', ctrl=True, shift=False)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.bool_difference", 'NUMPAD_MINUS', 'PRESS', ctrl=True, shift=False)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.slash", 'NUMPAD_SLASH', 'PRESS', ctrl=True, shift=False)
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name='Mesh', space_type='EMPTY')

    kmi = km.keymap_items.new("hops.edit_bool_union", 'NUMPAD_PLUS', 'PRESS', ctrl=True, shift=False, alt=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.edit_bool_difference", 'NUMPAD_MINUS', 'PRESS', ctrl=True, shift=False, alt=True)
    addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
