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
from os.path import split, join, dirname, abspath, basename


def get_addon_path():
    """ Returns the addon path """
    
    (addon_path, current_dir) = split(dirname(abspath(__file__)))
    
    return addon_path

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def get_addon_preferences():
    """ Returns the addon prefences """
    
    addon_path = get_addon_path()
    addon_name = basename(addon_path)
    user_preferences = bpy.context.user_preferences
    
    return user_preferences.addons[addon_name].preferences
    
    
#------------------------------------------------------------------
#
#------------------------------------------------------------------

def get_library_path():
    """ Returns the library path defined in the addon prefences """
    
    addon_prefs = get_addon_preferences()
    return addon_prefs.asset_M_library_path

#------------------------------------------------------------------
#
#------------------------------------------------------------------

def get_directory(dir):
    """ Returns the "blends", "Favorites" or "icons" directory path """
    
    AM = bpy.context.window_manager.asset_m
    library = get_library_path()
    
    return join(library, AM.library_type, AM.libraries, AM.categories, dir)