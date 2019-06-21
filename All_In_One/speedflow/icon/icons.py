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


import os
import bpy
import bpy.utils.previews
 
mpm_icon_collections = {}
mpm_icons_loaded = False
 
def load_icons():
    global mpm_icon_collections
    global mpm_icons_loaded
 
    if mpm_icons_loaded: return mpm_icon_collections["main"]
 
    custom_icons = bpy.utils.previews.new()
 
    icons_dir = os.path.join(os.path.dirname(__file__))
    
    #modals
    custom_icons.load("icon_bevel", os.path.join(icons_dir, "bevel.png"), 'IMAGE')
    custom_icons.load("icon_tubify", os.path.join(icons_dir, "tubify.png"), 'IMAGE')
    custom_icons.load("icon_mirror", os.path.join(icons_dir, "mirror.png"), 'IMAGE')
    custom_icons.load("icon_rotate", os.path.join(icons_dir, "rotate.png"), 'IMAGE')
    custom_icons.load("icon_solidify", os.path.join(icons_dir, "solidify.png"), 'IMAGE')
    custom_icons.load("icon_subsurf", os.path.join(icons_dir, "subsurf.png"), 'IMAGE')
    custom_icons.load("icon_symetrize", os.path.join(icons_dir, "symetrize.png"), 'IMAGE')
    custom_icons.load("icon_array", os.path.join(icons_dir, "array.png"), 'IMAGE')
    custom_icons.load("icon_boolean", os.path.join(icons_dir, "boolean.png"), 'IMAGE')
    
    mpm_icon_collections["main"] = custom_icons
    mpm_icons_loaded = True
 
    return mpm_icon_collections["main"]
 
def clear_icons():
    global mpm_icons_loaded
    for icon in mpm_icon_collections.values():
        bpy.utils.previews.remove(icon)
    mpm_icon_collections.clear()
    mpm_icons_loaded = False