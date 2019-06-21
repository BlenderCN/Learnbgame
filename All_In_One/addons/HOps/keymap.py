import bpy
from . utils.addons import addon_exists


addon_keymaps = []


def register_keymap():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if not kc:
        print('no keyconfig path found, skipped (we must be in batch mode)')
        return

    # register to 3d view mode tab
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    kmi = km.keymap_items.new("wm.call_menu_pie", "Q", "PRESS", shift=True)
    kmi.properties.name = "HOPS_MT_MainPie"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS")
    kmi.properties.name = "HOPS_MT_MainMenu"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("hops.helper", "ACCENT_GRAVE", "PRESS", ctrl=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu", "M", "PRESS", alt=True)
    kmi.properties.name = "HOPS_MT_MaterialListMenu"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu", "V", "PRESS", alt=True)
    kmi.properties.name = "HOPS_MT_ViewportSubmenu"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("hops.mirror_mirror_x", 'X', 'PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.mirror_mirror_y", 'Y', 'PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.mirror_mirror_z", 'Z', 'PRESS', alt=True, shift=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.mirror_gizmo", 'X', 'PRESS', alt=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("hops.bevel_helper", 'B', 'PRESS', ctrl=True, shift=True)
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

    km = kc.keymaps.new(name="Pose", space_type="EMPTY", region_type="WINDOW")

    kmi = km.keymap_items.new("hops.helper", "ACCENT_GRAVE", "PRESS", ctrl=True)
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name="Armature", space_type="EMPTY", region_type="WINDOW")

    kmi = km.keymap_items.new("hops.helper", "ACCENT_GRAVE", "PRESS", ctrl=True)
    addon_keymaps.append((km, kmi))

def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
