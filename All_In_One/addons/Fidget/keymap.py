import bpy


addon_keymaps = []


def register_keymap():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    kmi = km.keymap_items.new("fidget.viewport_buttons", 'Q', 'PRESS', ctrl=False, shift=True, alt=True)
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')

    kmi = km.keymap_items.new('wm.call_menu', 'W', 'PRESS', ctrl=False, shift=True, alt=False)
    kmi.properties.name = "fidget.custom_menu"
    addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
