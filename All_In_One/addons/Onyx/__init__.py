# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####


#//////////////////////////////// - AUTHORS YO - ///////////////////////////

bl_info = {
    "name": "Onyx",
    "author": "Takanu Kyriako",
    "version": (3, 0),
    "blender": (2, 7, 3),
    "api": 39347,
    "location": "3D View > Object Mode > Tools > Onyx",
    "description": "Quick Multi-Object Origin Tools",
    "wiki_url": "",
    "category": "Object"
}

# Start importing all the addon files
# The init file just gets things started, no code needs to be placed here.
if "bpy" in locals():
    import imp
    print(">>>>>>>>>>> Reloading Plugin", __name__, "<<<<<<<<<<<<")
    if "object_lib" in locals():
        imp.reload(object_lib)
    if "operators" in locals():
        imp.reload(operators)
    if "origin_ops" in locals():
        imp.reload(origin_ops)
    if "origin_menu" in locals():
        imp.reload(origin_menu)
    if "properties" in locals():
        imp.reload(properties)
    if "update" in locals():
        imp.reload(update)
    if "user_interface" in locals():
        imp.reload(user_interface)


#//////////////////////////////// - IMPORT - ///////////////////////////
#This imports various items from the Python API for use in the script
import bpy
from . import object_lib
from . import operators
from . import origin_ops
from . import origin_menu
from . import properties
from . import update
from . import user_interface

from math import *
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import AddonPreferences, PropertyGroup

class BlackHolePreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        row = layout.column(align=True)
        row.label("Hey!  HEY!  OVER HERE!")
        row.label("You can press Shift+Alt+C in Edit and Object Mode to access all of Onyx's tools.  Try it!")

addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.OXObj = PointerProperty(type=properties.OX_Object)
    bpy.types.Scene.OXScn = PointerProperty(type=properties.OX_Scene)

    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        # Object Mode
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS', alt=True, shift=True)
        kmi.properties.name = "pie.originextra"
#        kmi.active = True
        addon_keymaps.append(kmi)

        # Edit Mode
        km = wm.keyconfigs.addon.keymaps.new(name='Mesh')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS', alt=True, shift=True)
        kmi.properties.name = "pie.originextra"
#        kmi.active = True
        addon_keymaps.append(kmi)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.OXObj
    del bpy.types.Scene.OXScn

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['3D View Generic']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu_pie':
                if kmi.properties.name == "pie.originextra":
                    km.keymap_items.remove(kmi)

    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['Mesh']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu_pie':
                if kmi.properties.name == "pie.originextra":
                    km.keymap_items.remove(kmi)

if __name__ == "__main__":
    register()
