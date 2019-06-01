import bpy

from .. utility import addon

keys = []


def register():
    global keys

    kc = bpy.context.window_manager.keyconfigs.addon

    # Activate tool
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

    kmi = km.keymap_items.new(idname='bc.toolbar_activate', type='W', value='PRESS', alt=True)
    keys.append((km, kmi))

    # Draw shape
    kmi = km.keymap_items.new(idname='bc.draw_shape', type='LEFTMOUSE', value='PRESS', ctrl=True)
    # kmi.properties.repeat = True
    keys.append((km, kmi))

    # Draw shape
    kmi = km.keymap_items.new(idname='bc.draw_shape', type='LEFTMOUSE', value='ANY')
    kmi.map_type = 'TWEAK'
    keys.append((km, kmi))

    addon.log(value='Added keymap items')


def unregister():
    global keys

    for km, kmi in keys:
        km.keymap_items.remove(kmi)

    keys.clear()