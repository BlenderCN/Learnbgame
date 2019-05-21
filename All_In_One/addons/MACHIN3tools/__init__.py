'''
Copyright (C) 2016-2018 MACHIN3, machin3.io, support@machin3.io

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''


bl_info = {
    "name": "MACHIN3tools",
    "author": "MACHIN3",
    "version": (0, 3, 10),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Streamlining Blender 2.80.",
    "warning": "",
    "wiki_url": "https://machin3.io/MACHIN3tools/docs",
    "category": "Learnbgame",
    }


import bpy
from bpy.props import PointerProperty
from . properties import M3SceneProperties
from . utils.registration import get_core, get_tools, get_pie_menus, get_menus
from . utils.registration import register_classes, unregister_classes, register_keymaps, unregister_keymaps, register_icons, unregister_icons, add_object_context_menu, remove_object_context_menu


def register():
    global classes, keymaps, icons

    # CORE

    core_classes = register_classes(get_core())


    # PROPERTIES

    bpy.types.Scene.M3 = PointerProperty(type=M3SceneProperties)

    # TOOLS, PIE MENUS, KEYMAPS, MENUS

    tool_classlists, tool_keylists, tool_count = get_tools()
    pie_classlists, pie_keylists, pie_count = get_pie_menus()
    menu_classlists, menu_keylists, menu_count = get_menus()

    classes = register_classes(tool_classlists + pie_classlists + menu_classlists) + core_classes
    keymaps = register_keymaps(tool_keylists + pie_keylists + menu_keylists)

    add_object_context_menu()


    # ICONS

    icons = register_icons()


    # REGISTRATION OUTPUT

    print("Registered %s %s with %d %s, %d pie %s and %s context %s" % (bl_info["name"], ".".join([str(i) for i in bl_info['version']]), tool_count, "tool" if tool_count == 1 else "tools", pie_count, "menu" if pie_count == 1 else "menus", menu_count, "menu" if menu_count == 1 else "menus"))


def unregister():
    global classes, keymaps, icons

    # TOOLS, PIE MENUS, KEYMAPS, MENUS

    remove_object_context_menu()

    unregister_keymaps(keymaps)
    unregister_classes(classes)


    # PROPERTIES

    del bpy.types.Scene.M3


    # ICONS

    unregister_icons(icons)

    print("Unregistered %s %s." % (bl_info["name"], ".".join([str(i) for i in bl_info['version']])))
