'''
Copyright (C) 2015 Pistiwique

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
    "name": "Viewport info",
    "description": "Display selected info in the viewport",
    "author": "Pistiwique",
    "version": (0, 0, 8),
    "blender": (2, 75, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame",
}


# load and reload submodules
##################################    

import sys
sys.modules["viewport_info"] = sys.modules[__name__]
    
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__)

# properties
##################################

import bpy

# register
################################## 

import traceback

from . properties import viewportInfoCollectionGroup
from . draw import *

def register():    
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    register_pcoll()
    bpy.types.WindowManager.show_text = bpy.props.PointerProperty(type = viewportInfoCollectionGroup)
    bpy.types.VIEW3D_PT_view3d_shading.append(displayViewportInfoPanel)
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    unregister_pcoll()
    bpy.types.VIEW3D_PT_view3d_shading.remove(displayViewportInfoPanel)

    del bpy.types.WindowManager.show_text
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))

