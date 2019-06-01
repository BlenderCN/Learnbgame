'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

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
    "name": "Asset Sketcher",
    "description": "",
    "author": "Andreas Esau",
    "version": (1, 1, 2),
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "https://blendermarket.com/products/asset-sketcher-v1",
    "category": "Learnbgame",
    }


import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty, PointerProperty
from . import asset_sketcher_properties as as_props
from . import ui

from . functions import *
from bpy.app.handlers import persistent
import os
# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
##################################

import traceback


class ExampleAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    def set_asset_preview(self,context):
        if not self.enable_asset_preview:
            context.window_manager.asset_sketcher.asset_preview = False
            bpy.data.scenes[0].asset_sketcher.asset_preview = False
        
    enable_asset_preview : bpy.props.BoolProperty(name="Enable Asset Preview", description="Enable Asset Preview for sketching. This feature is sort of unstable with Undoing brushstrokes.",default=True,update=set_asset_preview)
    
    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        row = layout.row()
        row.prop(self, "enable_asset_preview")
        row.label(icon="ERROR")
          

def register():
    try: bpy.utils.register_class(ExampleAddonPreferences)
    except: traceback.print_exc()
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    as_props.register() ### register asset sketcher properties
    ui.register_icons()
    ui.register()
    bpy.app.handlers.load_post.append(load_asset_list)
    bpy.app.handlers.save_pre.append(save_asset_list)
    

def unregister():    
    try: bpy.utils.unregister_class(ExampleAddonPreferences)
    except: traceback.print_exc()
    
    as_props.unregister() ### unregister asset sketcher properties
    ui.unregister_icons()
    ui.unregister()
    print("Unregistered {}".format(bl_info["name"]))
    
    
    bpy.app.handlers.load_post.remove(load_asset_list)
    bpy.app.handlers.save_pre.remove(save_asset_list)

@persistent
def save_asset_list(dummy):
    context = bpy.context
    save_load_asset_list(context,mode="SAVE")
    

@persistent
def load_asset_list(dummy):
    context = bpy.context
    save_load_asset_list(context,mode="LOAD")