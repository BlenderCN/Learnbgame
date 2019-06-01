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
from extensions_framework.validate import Logic_OR as LOR, Logic_AND as LAND


@SunflowAddon.addon_register_class
class sunflow_world(declarative_property_group):
    """ 
    To include the ibl texture in world panel    
    """

    ef_attach_to = ['Scene']
    
    controls = [
                'worldLighting',
                'worldTexture',
                ['iblLock',
                'iblSamples'],
                'worldCenter',
                'worldUPtext',
                'worldUP',
                ]
    
    visibility = {
                  'worldTexture'    : { 'worldLighting': 'ibl' },
                  'iblLock'         : { 'worldLighting': 'ibl' },
                  'iblSamples'      : { 'worldLighting': 'ibl' },
                  'worldCenter'     : { 'worldLighting': 'ibl' },
                  'worldUPtext'     : { 'worldLighting': 'ibl' },
                  'worldUP'         : { 'worldLighting': 'ibl' },
                  }
    
    def set_worldUp(self, context):
        if   self.worldUP == 'x':
            self.worldUPString = '1  0  0'
        elif self.worldUP == 'y':
            self.worldUPString = '0  1  0'
        elif self.worldUP == 'z':
            self.worldUPString = '0  0  1'
        else:
            self.worldUPString = '0  0  1'
            
    enabled = {}
    alert = {}
    properties = [
                  
        {
            'type': 'enum',
            'attr': 'worldLighting',
            'name': 'World Lighting',
            'description': 'Gives the world lighting settings these light will give the overall illumination os the scene(remember these lights wont emit photons).',
            'default': 'papersky',
            'items': [
                ('papersky', 'Paper Sky', 'See the above World Horizon Color settings.'),
                ('sunsky', 'Sun Sky', 'See the SUN light settings in the light properties panel.'),
                ('ibl', 'Image Based Lighting', 'Insert a world texture with HDR image in the texture panel.'),
            ],
            # 'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'worldCenter',
            'subtype': 'XYZ',
            'description' : 'Specifes the center position of the ibl image in the world',
            'name' : 'Center',
            'default' : (0.0, 0.0, 1.0),
            'precision': 3,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'worldUPtext',
            'name': 'UP Direction:',
        },
        {
            'type': 'enum',
            'attr': 'worldUP',
            'name': 'World UP Direction',
            'description': 'Gives the world upside direction.',
            'default': 'z',
            'items': [
                ('x', 'X', 'x.'),
                ('y', 'Y', 'y.'),
                ('z', 'Z', 'z.'),
            ],
            'update' : set_worldUp,
            'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'worldUPString' ,
            'name': 'worldUPString' ,
            'default': '0  0  1',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'iblLock',
            'name': 'Lock',
            'description': 'Importance sampling.',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'iblSamples',
            'name': 'Samples',
            'description': 'The number of samples to be taken (default 1000000). ',
            'min': 0,
            'max':   2048,
            'default': 16,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'texturename' ,
            'name': 'texturename' ,
            'description': 'Texture',
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': 'worldTexture' ,
            'src': lambda s, c: c.world,
            'src_attr': 'texture_slots',
            'trg': lambda s, c: c.sunflow_world,
            'trg_attr': 'texturename',
            'name': 'Texture'
        },
                  ]
    
    