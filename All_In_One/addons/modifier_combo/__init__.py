if "bpy" in locals():
    import imp
    imp.reload(cache_class)
    imp.reload(gui)
    imp.reload(modifier_combo)
    imp.reload(modifier_proxy)
    imp.reload(ops)
else:
    from . import cache_class, gui, modifier_combo, modifier_proxy, ops


import bpy
import rna_keymap_ui
from .cache_class import PropCache, ComboCache, ComboListCache
from .ops import ModifierComboMenuTrigger
from bpy.props import IntProperty, CollectionProperty


bl_info = {
    "name" : "Modifier Combo",
    "description" : "Do combo as you like",
    "author" : "Kozo Oeda",
    "version" : (0, 1),
    "location" : "",
    "warning" : "",
    "support" : "COMMUNITY",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "3D View"
}


def get_keymap_item(km, kmi_idname):
    for keymap_item in km.keymap_items:
        if keymap_item.idname == kmi_idname:
            return keymap_item
    return None


class ManageModifierComboKeymap(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        kc = wm.keyconfigs.user
        kms = kc.keymaps
        keymap_names = ['3D View', 'Sculpt', 'Vertex Paint', 'Weight Paint', 'Image Paint']
        box = layout.box()

        idname = ModifierComboMenuTrigger.bl_idname

        box.label("Modifier Combo Menu")

        for n in range(len(keymap_names)):
            km_n = kms[keymap_names[n]]
            split = box.split()
            col = split.column()
            col.label(keymap_names[n])
            kmi_n = get_keymap_item(km_n, idname)

            if kmi_n:
                col.context_pointer_set("keymap", km_n)
                rna_keymap_ui.draw_kmi([], kc, km_n, kmi_n, col, 0)
            else:
                register_keymap()


addon_keymaps = []


def register_keymap():
    name_spacetypes = [('3D View', 'VIEW_3D'), ('Sculpt', 'EMPTY'), ('Vertex Paint', 'EMPTY'), ('Weight Paint', 'EMPTY'), ('Image Paint', 'EMPTY')]
    wm = bpy.context.window_manager

    for name_spacetype in name_spacetypes:
        km = wm.keyconfigs.addon.keymaps.new(name = name_spacetype[0], space_type = name_spacetype[1])

        kmi = km.keymap_items.new(ModifierComboMenuTrigger.bl_idname, 'NONE', 'PRESS', head = True)
        kmi.active = True

        addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.combo_list_cache = CollectionProperty(type = ComboListCache)
    bpy.types.Scene.combo_list_selected_index = IntProperty()
    register_keymap()


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.combo_list_cache
    del bpy.types.Scene.combo_list_selected_index
    unregister_keymap()


if __name__ == '__main__':
    register()
