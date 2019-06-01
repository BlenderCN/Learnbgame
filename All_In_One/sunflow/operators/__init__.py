# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          18-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------


import os
import bpy
from .. import SunflowAddon
from extensions_framework import util as efutil

from ..outputs import sunflowLog


def save_settings(context):    
    scene = context.scene
    config_updates = {}
    
    jar_path = os.path.abspath(efutil.filesystem_path(scene.sunflow_renderconfigure.sunflowPath))
    if os.path.exists(jar_path):
        config_updates['jar_path'] = jar_path
    else:
        sunflowLog("Unable to find path jar_path")
    
    java_path = os.path.abspath(efutil.filesystem_path(scene.sunflow_renderconfigure.javaPath))
    # if os.path.isdir(java_path) and os.path.exists(java_path):
    if os.path.exists(java_path):
        config_updates['java_path'] = java_path
    else:
        sunflowLog("Unable to find path java_path")
        
    
    memoryalloc = scene.sunflow_renderconfigure.memoryAllocated
    config_updates['memoryalloc'] = memoryalloc
    
        
    try:
        for k, v in config_updates.items():
            efutil.write_config_value('sunflow', 'defaults', k, v)
            sunflowLog("writing values")
    except Exception as err:
        sunflowLog('WARNING: Saving sunflow configuration failed, please set your user scripts dir: %s' % err)
    


@SunflowAddon.addon_register_class
class SUNFLOW_OT_save_settings(bpy.types.Operator):
    bl_idname = 'sunflow.save_settings'
    bl_label = 'Save Config'
        
    def execute(self, context):
        save_settings(context)
        return {'FINISHED'}    

