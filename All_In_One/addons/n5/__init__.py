'''
Copyright (C) 2015 YOUR NAME
YOUR@MAIL.com

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

bl_info = {
    "name": "n5",
    "description": "An Idea",
    "author": "MX",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "View3D",
    "warning": "This addon is always in development.",
    "wiki_url": "c:/",
    "category": "Learnbgame",
}
    
    
import bpy      


# load and reload submodules
##################################    
    
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
################################## 

import traceback
addon_keymaps = []

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    kmi = km.keymap_items.new('view3d.nmenu', 'Y', 'PRESS', ctrl = False, shift = False, alt=False) 
    kmi.active = True
    
    addon_keymaps.append(kmi)

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))

    global addon_keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps: 
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()