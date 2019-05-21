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
from .. import SunflowAddon

from extensions_framework import declarative_property_group
from extensions_framework import util as efutil
from extensions_framework.validate import Logic_OR as LOR, Logic_AND as LAND


@SunflowAddon.addon_register_class
class sunflow_film(declarative_property_group):
    """ Properties for controlling the output file format currently (0.7.3) 
    supports only 4 file formats PNG, HDR, TARGA, OpenEXR. when render through 
    GUI, it only supports PNG output All other four formats are generated 
    through using command line arguments.       
        -nogui -o output.tga scenefile.sc
            
    """

    ef_attach_to = ['Camera']
    controls = []
    visibility = {}
    enabled = {}
    alert = {}
    
    
    def set_extension(self, context):
        if self.fileFormat == 'png':
            self.fileExtension = 'png'
        elif self.fileFormat == 'openexr':
            self.fileExtension = 'exr'
        elif self.fileFormat == 'hdr':
            self.fileExtension = 'hdr'
        elif self.fileFormat == 'targa':
            self.fileExtension = 'tga'
        else:
            self.fileExtension = ''
    
    properties = [
        {
            'type': 'string',
            'attr': 'fileExtension',
            'name': 'File Extension',
            'default': 'png',
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'fileFormat',
            'name': 'File Format',
            'description': 'Denotes sunflow film output file format (default PNG)',
            'items': [
                ('png', 'PNG', 'png'),
                ('hdr', 'HDR', 'hdr (only supported on command line mode)'),
                ('openexr', 'OpenEXR', 'openexr (only supported on command line mode)'),
                ('targa', 'Targa', 'targa (only supported on command line mode)')
            ],
            'default': 'png',
            'update': set_extension,
            'save_in_preset': True
        },
                  ]
    
@SunflowAddon.addon_register_class
class sunflow_camera(declarative_property_group):
    """ There are four camera types supported in sunflow Pinhole, Thinlens, 
    Spherical, Fisheye. Pinhole is the normal perspective camera available with 
    Blender. Thinlens is our special camera this is the only camera that support 
    DOF, Bokeh effect etc, Spherical and Fisheye are the classical lens type 
    available. All normal values like position of camera(eye), where the camera 
    is looking at(target), rotation about the line joinig eye and target 
    (up direction) are fetched from blender, camera field of vision and aspect 
    ratios are also picked from blender. Special values like DOK shutter and 
    Blades are implemented here.  
    
    """

    ef_attach_to = ['Camera']
                
    controls = [     
                'sunflowCameraText',
                'cameraType',
                # CMBLUR
                'cameraMBlur',
                'cameraMBlurSteps',
                # OMBLUR
                'objectMBlur',
                'objectMBlurGroup',
                'shutterTime',
                # DOF       
                'dofEnabledScene',
                'dofObject',
                'aperture',
                ['apertureBlades',
                'bladeRotation'],
                
                ]
    visibility = {
                   # DOF    
                  'dofEnabledScene'         : { 'cameraType':'thinlens' },
                  'dofObject'               : { 'cameraType':'thinlens' , 'dofEnabledScene': True },
                  'aperture'                : { 'cameraType':'thinlens' , 'dofEnabledScene': True },
                  'apertureBlades'          : { 'cameraType':'thinlens' , 'dofEnabledScene': True },
                  'bladeRotation'           : { 'cameraType':'thinlens' , 'dofEnabledScene': True },
                  # CMBLUR
                  'cameraMBlur'             : { 'cameraType': LOR(['thinlens', 'pinhole']) },
                  'cameraMBlurSteps'        : { 'cameraMBlur': True },
                  # OMBLUR
                  'objectMBlurGroup'        : { 'objectMBlur':True },
                  'shutterTime'             : { 'objectMBlur':True },
                  }
    enabled = {}
    alert = {}
    properties = [   
        {
            'type': 'text',
            'attr': 'sunflowCameraText',
            'name': 'Sunflow Lens:',
        },
        {
            'type': 'bool',
            'attr': 'dofEnabledScene',
            'name': 'Depth of Field',
            'description': 'This will enable Depth of Field using thin lens camera (default False).',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'objectMBlur',
            'name': 'Object Motion Blur',
            'description': 'Use object motion blur.',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'objectMBlurGroupName',
            'name': 'objectMBlurGroupName',
            'description': 'Current camera will motion blur objects in this group.' ,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': 'objectMBlurGroup',
            'name': 'Object Group',
            'description': 'Current camera will motion blur objects in this group if they are animated.',
            'src': lambda s, c: bpy.data,
            'src_attr': 'groups',
            'trg': lambda s, c: c.sunflow_camera,
            'trg_attr': 'objectMBlurGroupName',
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'shutterTime',
            'name': 'Shutter Time',
            'description': 'the times over which the moving camera is defined (default 1). ',
            'min': 0,
            'max':   20,
            'default': 1,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'cameraMBlur',
            'name': 'Camera Motion Blur',
            'description': 'Two types of motion blur available. This will enable camera motion blur using thin lens camera.',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'cameraMBlurSteps',
            'name': 'Blur Steps',
            'description': 'The number of frames to interpolate to get the motion blur effect (default 2). ',
            'min': 0,
            'max':   100,
            'default': 2,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'aperture',
            'name': 'Aperture',
            'description': 'Radius of the aperture, Higher values gives more defocus (default 1.0).',
            'min': 0.0,
            'max': 100.0,
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'apertureBlades',
            'name': 'Blades',
            'description': 'The number of blades in the aperture for polygonal bokeh (default 3). ',
            'min': 2,
            'max':   10000,
            'default': 3,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'bladeRotation',
            'name': 'Rotation',
            'description': 'Angle of rotation of aperture blade (default 1.0).',
            'min': 0.0,
            'max': 360.0,
            'default': 0.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'cameraType',
            'name': 'Camera Type',
            'description': 'Sunflow camera type (default Pinhole).',
            'default': 'pinhole',
            'items': [
                ('pinhole', 'Pinhole', 'The "standard" perspective camera.'),
                ('thinlens', 'Thinlens', 'This is our depth of field (dof) camera, which is also capable of doing bokeh effects.'),
                ('spherical', 'Spherical', 'This spherical camera produces a longitude/lattitude environment map.'),
                ('fisheye', 'Fisheye', 'A classic lens.'),
            ],
            'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': 'dofObject',
            'name': 'Focus',
            'description': 'Position of this object with respect to camera defines the focus of this camera (must be an EMPTY)',
            'src': lambda s, c: s.scene,
            'src_attr': 'objects',
            'trg': lambda s, c: c,
            'trg_attr': 'dof_object',
            'save_in_preset': True
        },
                  ]
