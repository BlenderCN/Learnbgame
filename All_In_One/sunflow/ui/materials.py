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
# Created on                          26-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------


import bpy
import bl_ui

from .. import SunflowAddon
from extensions_framework.ui import property_group_renderer
from extensions_framework import util as efutil


class sunflow_material_base(bl_ui.properties_material.MaterialButtonsPanel, property_group_renderer):
    '''
    Default material slot panel from blender.
    '''
    COMPAT_ENGINES = { 'SUNFLOW_RENDER' }
    
    def draw(self, context):
        if not hasattr(context, 'material'):
            return
        return super().draw(context)


@SunflowAddon.addon_register_class
class MATERIAL_PT_material(sunflow_material_base, bpy.types.Panel):
    '''
    Populate material UI Panel with sunflow materials. 
    '''
    
    bl_label = 'Sunflow Material'
    COMPAT_ENGINES = { 'SUNFLOW_RENDER' }
    
    display_property_groups = [
        (('material',), 'sunflow_material')
    ]
    