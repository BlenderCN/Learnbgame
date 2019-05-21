"""PAM menus module"""

import bpy

from .. import mapping

# Version where pie menus have been implemented
MINIMUM_VERSION = "2.72 (sub 0)"

class PAMMappingMenu(bpy.types.Menu):
    """Mapping menu"""
    bl_idname = "pam.mapping_menu"
    bl_label = "Mapping"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        for (key, name, _, _, _) in mapping.LAYER_TYPES[1:]:
            pie.operator("pam.mapping_layer_set", "Add layer as %s" % name).type = key

        pie.operator("pam.mapping_self_inhibition", "Add layer as self-inhibition mapping")

def register():
    """Call upon module register"""
    if not bpy.app.background and bpy.app.version_string >= MINIMUM_VERSION:
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.new(name="3D View Generic", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu_pie", "SPACE", "PRESS", shift=True, ctrl=True)
        kmi.properties.name = "pam.mapping_menu"


def unregister():
    """Call upon module unregister"""
    if not bpy.app.background and bpy.app.version_string >= MINIMUM_VERSION:
        wm = bpy.context.window_manager
        km = wm.keyconfigs.addon.keymaps.find(name="3D View Generic", space_type="VIEW_3D")
        kmi = km.keymap_items["wm.call_menu_pie"]
        km.keymap_items.remove(kmi)
