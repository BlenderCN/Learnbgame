### BEGIN GPL LICENSE BLOCK #####
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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Modifier Setup Nodes",
    "author": "Lukas Toenne",
    "version": (0, 1, 0),
    "blender": (2, 6, 7),
    "location": "Node Editor",
    "description": "Nodes for setting up modifiers in objects",
    "warning": "",
    "category": "Learnbgame"
}

import os
directory = os.path.dirname(__file__)

import bpy
from bpy.types import AddonPreferences

# XXX any nicer way to make this work?
import sys
if directory not in sys.path:
    sys.path.append(directory)

from pynodes_framework import base, group
import typedesc, mod_node, object_nodes, driver, generator, nodes, database
 
class ModifierNodesPrefs(AddonPreferences):
    bl_idname = __name__


def register():
    bpy.utils.register_class(ModifierNodesPrefs)

    typedesc.register()
    group.register()

    object_nodes.register()
    mod_node.register()
    driver.register()

    blang_path = os.path.join(directory, 'modifiers')
    generator.load_all_modifiers(blang_path)

    # explicit node types to register
    nodes.register()

    mod_node.mod_node_item.register()

    database.register()

    prefs = bpy.context.user_preferences.addons[__name__].preferences

def unregister():
    database.unregister()

    mod_node.mod_node_item.unregister()

    nodes.unregister()

    generator.unload_all_modifiers()

    driver.unregister()
    object_nodes.unregister()
    mod_node.unregister()

    typedesc.unregister()
    group.unregister()

    bpy.utils.unregister_class(ModifierNodesPrefs)

if __name__ == "__main__":
    register()
