'''
Copyright (C) 2015 Pistiwique, Pitiwazou
 
Created by Pistiwique, Pitiwazou
 
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
 

import bpy
import os 
import bpy.utils.previews
from os.path import join
from bpy.types import WindowManager
from bpy.props import EnumProperty
from ..function_utils.get_path import (get_library_path,
                                       get_addon_preferences,
                                       )
from ..function_utils.utils import run_preview_add_to_selection

AssetM_preview_collections = {}


def update_pcoll_preview():
    """ Update the preview collectron """
    
    global AssetM_preview_collections
    for pcoll in AssetM_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    
    register_AssetM_pcoll_preview()
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------    
    
def get_thumbnails_directory():
    """ Return, the filepath of the thumbnail directory """
    
    AM = bpy.context.window_manager.asset_m
    library_path = get_library_path()
    if AM.favourites_enabled and len(os.listdir(join(library_path, AM.library_type, AM.libraries, AM.categories, "Favorites"))):
        directory = "Favorites"
    else:
        directory = "icons"
#    directory = "Favorites" if AM.favourites_enabled else "icons"
    
    
    return join(library_path, AM.library_type, AM.libraries, AM.categories, directory)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
     
def enum_previews_from_directory_items(self, context):
    """EnumProperty callback"""
    
    AM = context.window_manager.asset_m
    enum_items = []
 
    if context is None:
        return enum_items
 
    wm = context.window_manager
    directory = get_thumbnails_directory()
 
    # Get the preview collection (defined in register func).
    pcoll = AssetM_preview_collections["main"]
    if directory == pcoll.AssetM_previews_dir:
        return pcoll.AssetM_previews
 
    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        extentions = (".jpeg", ".jpg", ".png")
        for fn in os.listdir(directory):
            if fn.lower().endswith(extentions):
                image_paths.append(fn)
 
        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            existing_thumb = [v for k, v in pcoll.items() if filepath == k]
            if existing_thumb:
                thumb = existing_thumb[0]
            else:   
                thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name.rsplit(".", 1)[0], "", thumb.icon_id, i))
 
    pcoll.AssetM_previews = enum_items
    pcoll.AssetM_previews_dir = directory
    return pcoll.AssetM_previews

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
def register_AssetM_pcoll_preview():
    """ Register the preview collection """
 
    WindowManager.AssetM_previews = EnumProperty(
        items = enum_previews_from_directory_items,
        update = run_preview_add_to_selection
        )
    
    pcoll = bpy.utils.previews.new()
    pcoll.AssetM_previews_dir = ""
    pcoll.AssetM_previews = ()
 
    AssetM_preview_collections["main"] = pcoll
 
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def unregister_AssetM_pcoll_preview():
    """ Unregister the preview collection """
 
    del WindowManager.AssetM_previews
 
    for pcoll in AssetM_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    AssetM_preview_collections.clear()