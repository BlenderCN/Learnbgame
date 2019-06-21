'''
Copyright (C) 2016 Tim Zoet
ts.zoet@gmail.com

Created by Tim Zoet

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
    "name": "LOD Manager",
    "description": "Manage object Level Of Detail for increased render performance",
    "author": "Tim Zoet",
    "version": (1, 2),
    "blender": (2, 77, 0),
    "location": "View3D > Tools > Level Of Detail",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "tracker_url": "",
    "category": "Object"}


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
##################################

import traceback


def register():
    try:
        bpy.utils.register_module(__name__)
    except:
        traceback.print_exc()
    
    for module in modules:
        if hasattr(module, "register"):
            module.register()
            print("Registering module " + module.__name__)


def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        traceback.print_exc()
    
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
