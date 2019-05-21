bl_info = {
    "name": "Quick Tools",
    "description": "A series of tools and menus to enhance and speed up workflow",
    "author": "Jonathan Williamson",
    "version": (0, 8),
    "blender": (2, 6, 8),
    "location": "View3D - 'Q' key gives a menu in Object, Edit, and Sculpt modes.",
    "warning": '',  # used for warning icon and text in addons panel
    "wiki_url": "http://cgcookie.com/blender/docs/quick-tools-documentation/",
    "tracker_url": "https://github.com/CGCookie/quicktools/issues",
    "category": "Learnbgame"
}

import os
import sys

# Add the current __file__ path to the search path
sys.path.append(os.path.dirname(__file__))

import bpy

import quick_operators
import quick_object_mode
import quick_edit_mode
import quick_sculpt_mode
import quick_mode_switch
import quick_scene


addon_keymaps = []        

def register():
   quick_operators.register()
   quick_object_mode.register()
   quick_edit_mode.register()
   quick_sculpt_mode.register()
   quick_mode_switch.register()
   quick_scene.register()

   kc = bpy.context.window_manager.keyconfigs.addon
   
   # create the mode switch menu hotkey
   km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', alt=True)
   kmi.properties.name = 'mode.switch_menu' 
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the scene options menu hotkey
   km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
   kmi = km.keymap_items.new('wm.call_menu', 'ACCENT_GRAVE', 'PRESS', shift=True)
   kmi.properties.name = 'scene.quick_options' 
   kmi.active = True
   addon_keymaps.append((km, kmi))


   # create the object mode tools menu hotkey
   km = kc.keymaps.new(name='Object Mode')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
   kmi.properties.name = 'object.tools_menu' 
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('wm.call_menu', 'W', 'PRESS', alt=True)
   kmi.properties.name = 'object.quick_pet_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the object mode Display menu hotkey
   km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', shift=True)
   kmi.properties.name = 'object.display_options'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   # create the edit mode tools menu hotkey
   km = kc.keymaps.new(name='Mesh')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
   kmi.properties.name = 'mesh.tools_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('wm.call_menu', 'W', 'PRESS', alt=True)
   kmi.properties.name = 'object.quick_pet_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))
   
   # create the sculpt mode tools menu hotkey
   km = kc.keymaps.new(name='Sculpt')
   kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS')
   kmi.properties.name = 'sculpt.tools_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('wm.call_menu', 'W', 'PRESS')
   kmi.properties.name = 'sculpt.brush_settings_menu'
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('sculpt.symmetry', 'X', 'PRESS', shift=True)
   kmi.properties.axis = -1
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('sculpt.symmetry', 'Y', 'PRESS', shift=True)
   kmi.properties.axis = 0
   kmi.active = True
   addon_keymaps.append((km, kmi))

   kmi = km.keymap_items.new('sculpt.symmetry', 'Z', 'PRESS', shift=True)
   kmi.properties.axis = 1
   kmi.active = True
   addon_keymaps.append((km, kmi))
 
def unregister():
    quick_scene.unregister()
    quick_mode_switch.unregister()
    quick_sculpt_mode.unregister()
    quick_edit_mode.unregister()
    quick_object_mode.unregister()
    quick_operators.unregister()
    
    # remove the add-on keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()