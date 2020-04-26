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

from .. import SunflowAddon

from extensions_framework import declarative_property_group
from extensions_framework import util as efutil



@SunflowAddon.addon_register_class
class sunflow_renderconfigure(declarative_property_group):
    """ 
    Sunflow render configurations panel. 
    """

    ef_attach_to = ['Scene']
    controls = [
                'sunflowPath',
                'javaPath',
                'memoryAllocated',
                ]
    visibility = {}
    enabled = {}
    alert = {}
    
        
    properties = [
        {
            'type'      : 'string',
            'attr'      : 'sunflowPath',
            'subtype'   : 'FILE_PATH',
            'name'      : 'Sunflow Path',
            'description': 'Path to sunflow rendering system sunflow.jar file.',
            'default'   : efutil.find_config_value('sunflow', 'defaults', 'jar_path', ''),
            'save_in_preset': True
        },
        {
            'type'      : 'string',
            'attr'      : 'javaPath',
            'subtype'   : 'FILE_PATH',
            'name'      : 'Java Server Path',
            'description': 'Path to Java.exe file of the server',
            'default'   : efutil.find_config_value('sunflow', 'defaults', 'java_path', ''),
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'memoryAllocated',
            'name': 'Memory (MB)',
            'description': 'Memory allocated for running jar executable in MB. ',
            'default': efutil.find_config_value('sunflow', 'defaults', 'memoryalloc', ''),
            'save_in_preset': True
        },
                     
                  ]    
    
    
@SunflowAddon.addon_register_class
class sunflow_passes(declarative_property_group):
    """ 
    Quick passes selection options.
    """

    ef_attach_to = ['Scene']
    controls = [
                'quickmode',
                'distOcclusion',
                ]
    visibility = {
                  'distOcclusion' : {'quickmode': 'quickambocc'}
                  }
    enabled = {}
    alert = {}
    
    properties = [
        {
            'type': 'enum',
            'attr': 'quickmode',
            'name': 'Quick Override Methods',
            'description': 'Command line overrides.',
            'default': 'quicknone',
            'items': [
                ('quicknone', 'None', 'Normal render mode.'),
                ('quickuvs', 'UV', 'Renders the UVs of objects.'),
                ('quicknormals', 'Normal', 'Renders the normals of objects. '),
                ('quickid', 'ID', 'Renders using a unique color for each instance. '),
                ('quickprims', 'Primitive', 'Renders using a unique color for each primitive. '),
                ('quickgray', 'Gray', 'Renders the all the objects in the scene gray diffuse, overriding all shaders'),
                ('quickwire', 'Wire', 'Renders objects as wireframe. aa and filter values taken into consideration.'),
                ('quickambocc', 'Occlusion', 'ambient occlusion mode with a certain distance'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'distOcclusion',
            'name': 'Occlusion Distance',
            'description': 'For quick AO (default 1.0).',
            'min': 0.0,
            'max': 300.0,
            'default': 1.0,
            'slider': True,
            'save_in_preset': True
        },
                  ]
    