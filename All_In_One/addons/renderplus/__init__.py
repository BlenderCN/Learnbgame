# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------
# DEFAULT NOTIFICATION SOUND:
# "Notification Chime" (freesound.org/people/hykenfreak/sounds/202029)
# - By Hykenfreak (freesound.org/people/hykenfreak)
# - CC-BY (creativecommons.org/licenses/by/3.0)
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#  GENERAL IMPORTS
# ------------------------------------------------------------------------------
import os
import json
import logging
import logging.config
import sys
import pkgutil
import importlib


# ------------------------------------------------------------------------------
#  ADDON INFO
# ------------------------------------------------------------------------------

bl_info = {
    "name": "Render+",
    "description": "Rendering toolset",
    "author": "Diego Garcia Gangl <diego@sinestesia.co>",
    "version": (1, 0, 0),
    "BLENDER": (2, 70, 0),
    "location": "Properties > Render",
    "warning": "",
    "wiki_url": "http://cgcookiemarkets.com/blender/all-products/render/?view=docs",
    "link": "http://cgcookiemarkets.com/blender/all-products/render/",
    "tracker_url": "http://cgcookiemarkets.com/blender/all-products/render/?view=support",
    "category": "Render"
}


# ------------------------------------------------------------------------------
#  BLENDER PACKAGE LOADING
# ------------------------------------------------------------------------------

def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon. 
    
    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    def get_submodule_names(path = path[0], root = ""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else:
                module_names.append(root + module_name)
        return module_names 

    def import_submodules(names):
        modules = []
        for name in names:
            if name == 'batch_render.dispatcher':
                continue
                
            modules.append(importlib.import_module("." + name, package_name))
        return modules
        
    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)
    
    names = get_submodule_names()
    modules = import_submodules(names)        
    if reload: 
        reload_modules(modules) 
    return modules


modules = setup_addon_modules(__path__, __name__, "bpy" in locals())

import bpy



# ------------------------------------------------------------------------------
#  REGISTER / UNREGISTER
# ------------------------------------------------------------------------------

def register():

    # --------------------------------------------------------------------------
    #  CLASS AND DATA REGISTER

    bpy.utils.register_module(__name__)
    bpy.types.Scene.renderplus = bpy.props.PointerProperty(
        type=data.RP_Settings)

    # Have to re-assign this because context isn't set before,
    # when the data module is imported
    data.prefs = bpy.context.user_preferences.addons[__package__].preferences

    # --------------------------------------------------------------------------
    #  CALLBACKS REGISTER

    bpy.app.handlers.render_complete.append(dispatch.on_complete)
    bpy.app.handlers.render_cancel.append(dispatch.on_cancel)
    bpy.app.handlers.render_pre.append(dispatch.on_pre_render)
    bpy.app.handlers.load_post.append(dispatch.on_file_open)
    bpy.app.handlers.render_post.append(dispatch.on_post_render)
    bpy.app.handlers.scene_update_post.append(dispatch.on_scene_update)

    # --------------------------------------------------------------------------
    #  LOGGING SETUP

    debug_conf_file = utils.path('conf', 'log.json')
    with open(debug_conf_file, 'r') as stream:
        log_conf = json.load(stream)

    if data.prefs.enable_debug:
        log_conf['handlers']['file'] = {}
        log_conf['handlers']['file']['class'] = 'logging.FileHandler'
        log_conf['handlers']['file']['filename'] = data.prefs.debug_file
        log_conf['handlers']['file']['mode'] = 'a'
        log_conf['handlers']['file']['formatter'] = 'debug'
        log_conf['handlers']['file']['encoding'] = 'utf-8'
        log_conf['root']['handlers'] = ['console', 'file']
        log_conf['root']['level'] = 'DEBUG'


    try:
        logging.config.dictConfig(log_conf)

    except ValueError as e:
        print(repr(e))
        log = logging.getLogger(__name__)
        log.removeHandler('file')
        print('\n')
        print('-[RENDERPLUS]' + ('-' * 66))
        print(('\nCan\'t write support log in path "{0}"'
               '! Please check preferences.\n'.format(data.prefs.debug_file)))
        print('-' * 80)
        print('\n')

    else:
        log = logging.getLogger(__name__)

    # Get some system info
    if data.prefs.enable_debug and log:
        log.debug(' ')
        log.debug('-' * 80)

        if bpy.app.background:
            log.debug('LOG START [BACKGROUND]')
        else:
            log.debug('LOG START')

        log.debug('-' * 80)
        log.debug('System: ' + utils.sys)
        log.debug('Blender: ' + bpy.app.version_string)
        log.debug('Branch: ' + str(bpy.app.build_branch))
        log.debug('Build Options: ' + str(bpy.app.build_options))
        log.debug('Registered Handlers: ' + str(bpy.app.handlers))
        
        
    # --------------------------------------------------------------------------
    #  CUDA DEVICES FOR BATCH
    
    system_prefs = bpy.context.user_preferences.system
    compute_device = system_prefs.compute_device
    
    if system_prefs.compute_device_type == 'CUDA':
        count = 1
        
        # Test up to 64 GPUs in the system
        for i in range(0, 64):
            try:
                system_prefs.compute_device = 'CUDA_' + int(i)
                count += 1
            except TypeError:
                break
                
        # Set variables and clean up after testing 
        data.prefs.batch_cuda_devices = count
        data.prefs.batch_cuda_active = compute_device
        
        system_prefs.compute_device = compute_device
    
        
    
def unregister():

    del bpy.types.Scene.renderplus

    bpy.app.handlers.render_complete.remove(dispatch.on_complete)
    bpy.app.handlers.render_cancel.remove(dispatch.on_cancel)
    bpy.app.handlers.render_pre.remove(dispatch.on_pre_render)
    bpy.app.handlers.load_post.remove(dispatch.on_file_open)
    bpy.app.handlers.render_post.remove(dispatch.on_post_render)
    bpy.app.handlers.scene_update_post.remove(dispatch.on_scene_update)

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
