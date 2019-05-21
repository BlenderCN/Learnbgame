'''
Copyright (C) 2018 Samy Tichadou (tonton)
samytichadou@gmail.com

Created by Samy Tichadou (tonton)

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
    "name": "VCache",
    "description": "Cache Viewport",
    "author": "Samy Tichadou (tonton)",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "3d View > Down Header",
    #"warning": "This addon is still in development.",
    "wiki_url": "https://github.com/samytichadou/vcache/wiki",
    "tracker_url": "https://github.com/samytichadou/vcache/issues/new",
    "category": "Learnbgame"
}


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

from .operators.render_frame_range import VCacheOpenGLRange
from .operators.read_operator import VCachePlaybackRangeCache
from .gui import VCachePieMenuCaller, VCacheCacheSettingsMenu

# store keymaps here to access after registration
addon_keymaps = []


# register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    ### props ###
    
    bpy.types.Scene.vcache_draft = bpy.props.BoolProperty(
            name="Draft Mode",
            description="If True, Open GL Render will be downsized and Anti-Alliasing turned off for better performances",
            default=False
            )
    bpy.types.Scene.vcache_only_render = bpy.props.BoolProperty(
            name="Only Render Mode",
            description="If True, Open GL Render will be executed in Only Render mode",
            default=False
            )
    bpy.types.Scene.vcache_real_size = bpy.props.BoolProperty(
            name="Real Size Mode",
            description="Cached Images will have the viewport size without taking toolshelf and properties panels size into account",
            default=False
            )
    bpy.types.Scene.vcache_camera = bpy.props.StringProperty()
    
    ### keymap ###

    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(
        name='3D View',
        space_type='VIEW_3D',
        region_type='WINDOW')
    km2 = km.keymap_items.new(VCachePieMenuCaller.bl_idname, 'Y', 'PRESS', ctrl=True, alt=True)
    km3 = km.keymap_items.new(VCacheOpenGLRange.bl_idname, 'Y', 'PRESS', alt=True)
    km4 = km.keymap_items.new(VCachePlaybackRangeCache.bl_idname, 'Y', 'PRESS', ctrl=True)
    km5 = km.keymap_items.new(VCacheCacheSettingsMenu.bl_idname, 'Y', 'PRESS', shift=True)
    addon_keymaps.append(km)

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
    
    ### props ###
    
    del bpy.types.Scene.vcache_draft
    del bpy.types.Scene.vcache_only_render
    del bpy.types.Scene.vcache_real_size
    del bpy.types.Scene.vcache_camera
    
    ### keymap ###

    # PIE MENU keymap
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)

    # clear the list
    del addon_keymaps[:]