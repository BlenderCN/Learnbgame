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
import bpy.utils.previews
from os.path import join, dirname
 
asset_m_icon_collections = {}
asset_m_icons_loaded = False
 
def load_icons():
    global asset_m_icon_collections
    global asset_m_icons_loaded
 
    if asset_m_icons_loaded: return asset_m_icon_collections["main"]
 
    custom_icons = bpy.utils.previews.new()
 
    icons_dir = join(dirname(__file__))
 
    custom_icons.load("favorites_asset", join(icons_dir, "favorites.png"), 'IMAGE')
    custom_icons.load("no_favorites_asset", join(icons_dir, "no_favorites.png"), 'IMAGE')
    
    custom_icons.load("rename_asset", join(icons_dir, "rename.png"), 'IMAGE')
    custom_icons.load("no_rename_asset", join(icons_dir, "no_rename.png"), 'IMAGE')
    
    custom_icons.load("name_asset", join(icons_dir, "name.png"), 'IMAGE')
    custom_icons.load("no_name_asset", join(icons_dir, "no_name.png"), 'IMAGE')
    
    #Hardops icon
    custom_icons.load("hardops_asset", join(icons_dir, "hardops.png"), 'IMAGE')
    
    asset_m_icon_collections["main"] = custom_icons
    asset_m_icons_loaded = True
 
    return asset_m_icon_collections["main"]
 
def clear_icons():
    global asset_m_icons_loaded
    for icon in asset_m_icon_collections.values():
        bpy.utils.previews.remove(icon)
    asset_m_icon_collections.clear()
    asset_m_icons_loaded = False
