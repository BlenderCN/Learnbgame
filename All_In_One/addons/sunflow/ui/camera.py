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


class camera_panel(bl_ui.properties_data_camera.CameraButtonsPanel, property_group_renderer):
    '''
    Camera objects listing panel
    '''
    COMPAT_ENGINES = 'SUNFLOW_RENDER'


@SunflowAddon.addon_register_class
class SunflowRender_PT_sunflowcameratypes(camera_panel):
    bl_label = 'Camera Type'
    # bl_options = {'DEFAULT_CLOSED'}    
    
    display_property_groups = [
        (('camera',), 'sunflow_camera')
    ]
    