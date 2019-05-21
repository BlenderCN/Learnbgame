'''
Copyright (C) 2017 Samuel Bernou

Created by YOUR NAME

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


# register the addon + modules found in globals() (taken from Amaranth addon)
bl_info = {
    "name": "samutility",
    "author": "Samuel Bernou",
    "version": (0, 0, 3),
    "blender": (2, 78),
    "location": "Anywhere!",
    "description": "Complementary tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scene",
}


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils

from .mods import subdiv_equalize
from .code import mesh_dump
from .render import view_tweak
from .scene import group_remover


from .object import (
    duplicate_mirror,
    recalc_normals,
    Bbox_object,
    decrement_name,
    )


importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



'''# exemple of multi import from a folder
from samtools.render import (
    only_render,
    sauce,
    )
'''

# register
##################################

addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    #only_render
    kmi = km.keymap_items.new("samutils.show_only_render", "Z", "PRESS", shift=True, alt=True)

    #lock_cam_to_view
    kmi = km.keymap_items.new("samutils.lock_cam_to_view", "C", "PRESS", shift=True, alt=True)

    #go material view
    kmi = km.keymap_items.new("samutils.material_mode", "Z", "PRESS", shift=True, alt=True, ctrl=True)


    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()



import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    if not bpy.app.background:
        register_keymaps()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    if not bpy.app.background:
        unregister_keymaps()
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
