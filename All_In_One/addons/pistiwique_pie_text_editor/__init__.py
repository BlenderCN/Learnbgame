'''
Copyright (C) 2015 Pistiwique
YOUR@MAIL.com

Created by Pistiwique

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
    "name": "Pistiwique_pie_text_editor",
    "description": "",
    "author": "Pistiwique",
    "version": (0, 1, 0),
    "blender": (2, 74, 0),
    "location": "View3D",
    "wiki_url": "",
    "category": "Learnbgame"
}
    
    
import bpy      
from . pie_utils import InitPieTextEditor, InitPieTextPlus, InitCommentUncomment
from . operators import *

# load and reload submodules
##################################    
    
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__)



# register
################################## 

import traceback

addon_keymaps = []

def register_keymaps():
    global addon_keymaps    
    wm = bpy.context.window_manager
    
    km = wm.keyconfigs.addon.keymaps.new(name="Text Generic", space_type='TEXT_EDITOR')
    kmi = km.keymap_items.new(InitPieTextEditor.bl_idname, 'RIGHTMOUSE', 'PRESS')
    kmi = km.keymap_items.new(InitPieTextPlus.bl_idname, 'RIGHTMOUSE', 'PRESS', shift=True)
    kmi = km.keymap_items.new(CustomCopy.bl_idname, 'C', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new(CustomCut.bl_idname, 'X', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new(CustomPaste.bl_idname, 'V', 'PRESS', ctrl=True)
    kmi = km.keymap_items.new(InitCommentUncomment.bl_idname, 'THREE', 'PRESS', alt=True)
    kmi = km.keymap_items.new(CustomDoubleQuote.bl_idname, 'THREE', 'PRESS')
    kmi = km.keymap_items.new(CustomSimpleQuote.bl_idname, 'FOUR', 'PRESS')
    kmi = km.keymap_items.new(CustomBracket.bl_idname, 'FIVE', 'PRESS')
    kmi = km.keymap_items.new(CustomSquareBracket.bl_idname, 'FIVE', 'PRESS', alt=True)
    kmi = km.keymap_items.new(CustomBrace.bl_idname, 'FOUR', 'PRESS', alt=True)     

    addon_keymaps.append(km)

def unregister_keymaps():

    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
    
    
def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    register_keymaps()
    bpy.types.WindowManager.multi_line_enabled = bpy.props.BoolProperty(default=False)
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    unregister_keymaps()
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))