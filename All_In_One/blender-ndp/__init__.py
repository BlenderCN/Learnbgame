# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "NDP(Non-Destructive Primitives)",
    "author" : "ChieVFX",
    "description" : "",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category": "Learnbgame",
}

import bpy

from . src.add_ui import SubmenuAdd
from . src.props_containers import PropertiesContainer, InitialPropertiesCacheContainer

from . src.update_op import OpUpdateGeometry

from . src.enums import prim_props, CustomProperty, PrimType


classes = [
    OpUpdateGeometry,
    PropertiesContainer,
    InitialPropertiesCacheContainer,

    SubmenuAdd,
]

from .src.utils_op import CLASSES as src_utils_op_CLASSES
classes.extend(src_utils_op_CLASSES)

from .src.add_op import CLASSES as src_op_add_CLASSES
classes.extend(src_op_add_CLASSES)

from .src.edit_op import CLASSES as src_op_edit_CLASSES
classes.extend(src_op_edit_CLASSES)

from .src.event_op import CLASSES as src_event_CLASSES
classes.extend(src_event_CLASSES)
from .src.event_op import register_events, unregister_events

addon_keymaps = []

def register():
    from bpy.utils import register_class
    for c in classes:
        register_class(c)

    bpy.types.Scene.ndp_cache_initial = bpy.props.PointerProperty(
        type = InitialPropertiesCacheContainer)

    bpy.types.Mesh.ndp_props = bpy.props.PointerProperty(
        type = PropertiesContainer,
        name = "NDP Props")
    
    register_events()

    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
       km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
       kmi = km.keymap_items.new("ndp.convert", 'C', 'PRESS', alt=True)
       addon_keymaps.append((km, kmi))
       kmi = km.keymap_items.new("ndp.toggle_wireframe", 'W', 'PRESS', ctrl=True)
       addon_keymaps.append((km, kmi))


def unregister():
    from bpy.utils import unregister_class
    
    for c in classes:
        unregister_class(c)
    
    unregister_events()

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    kcfg = bpy.context.window_manager.keyconfigs.addon


separator = lambda menu, context: menu.layout.separator()

from .src.ui_utils import menu_menu, menu_operator

def extend_menus(is_registering):
    _extend_menu_add(is_registering)

def _extend_menu_add(is_registering):
    prepend = bpy.types.VIEW3D_MT_add.prepend
    append = bpy.types.VIEW3D_MT_add.append

    menu_menu(SubmenuAdd, prepend)

extend_menus(True)