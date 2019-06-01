'''
Copyright (C) 2018 PJ PENG
pjwaixingren@me.com

Created by pjpeng

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
    "name": "BL2SP",
    "description": "This addon use to development Game",
    "author": "pjwaixingren",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "www.pjcgart.com",
    "category": "Object" }


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
    bpy.types.Scene.spmeshseleted=bpy.props.BoolProperty(
        name='Sel_MESH',
        default=False,
        description='outmesh') 
    bpy.types.Scene.spmeshudmi=bpy.props.BoolProperty(name='Cre_UDIM',default=False)
    bpy.types.Scene.fbxcommonname=bpy.props.StringProperty(name="") 
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    #print("Registered {} with {} modules".format(bl_info["name"]))

def unregister():
    del bpy.types.Scene.spmeshseleted
    del bpy.tpyes.Scene.spmeshudmi
    del bpy.types.Scene.fbxcommonname
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    #print("Unregistered {}".format(bl_info["name"]))
