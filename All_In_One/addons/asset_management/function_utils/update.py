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
from os.path import join, isdir
from .get_path import (get_library_path,
                       get_addon_path,
                       )
from .utils import store_library_setup


def library_type_updater(self, context):
    """ Empty the different variables storage """
    
    AM = context.window_manager.asset_m
    del(AM.library_list[:])
    if AM.lib_name:
        AM.libraries = AM.lib_name
    
    category_updater(self, context)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def category_updater(self, context):
    """ Empty the different variables storage """
    
    AM = context.window_manager.asset_m
    addon_path = get_addon_path()
    if AM.libraries != "Render Scenes":
        AM.previous_lib = AM.libraries
    
    if AM.library_type == 'materials' and AM.adding_options:
        library_path = get_library_path()
        if isdir(join(library_path, AM.library_type, "Render Scenes")):

            if AM.libraries == 'Render Scenes':
                if not AM.as_mat_scene:
                    AM.as_mat_scene = True
                    
            else:
                if AM.as_mat_scene:
                    AM.as_mat_scene = False
  
    del(AM.category_list[:])
    if AM.library_type != 'hdri':
        del(AM.datablock_list[:])
    
    if AM.cat_name:
        AM.categories = AM.cat_name  

    AM.lib_name = ""
    AM.cat_name = ""
    
    if AM.library_type == 'assets' and AM.import_choise == 'link':
        del(AM.groups_list[:])
        del(AM.script_list[:])
    
    store_library_setup()
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
 
def import_choise_updater(self, context):
    """ Update the group list """
 
    AM = context.window_manager.asset_m
    if AM.library_type == 'assets' and AM.import_choise == 'link':
        del(AM.groups_list[:])
        del(AM.script_list[:])

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def update_material_name(self, context):
    """ Update active material name """
    
    AM = context.window_manager.asset_m

    bpy.context.active_object.active_material.name = AM.rename_mat
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def background_alpha(self, context):
    """ Setup the background alpha """
    
    AM = bpy.context.window_manager.asset_m 
    if AM.background_alpha == 'TRANSPARENT': 
        alpha_mode = 'TRANSPARENT'
 
    elif AM.background_alpha == 'SKY':
        alpha_mode = 'SKY'
 
    bpy.context.scene.render.alpha_mode = alpha_mode