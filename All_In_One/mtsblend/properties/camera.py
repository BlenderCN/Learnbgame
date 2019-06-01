# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

import math

from ..extensions_framework import declarative_property_group

from .. import MitsubaAddon
from ..outputs import MtsLog


def CameraMediumParameter(attr, name):
    return [
        {
            'attr': '%s_medium' % attr,
            'type': 'string',
            'name': '%s_medium' % attr,
            'description': '%s; blank means vacuum' % name,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': attr,
            'src': lambda s, c: s.scene.mitsuba_nodegroups,
            'src_attr': 'medium',
            'trg': lambda s, c: c.mitsuba_camera,
            'trg_attr': '%s_medium' % attr,
            'name': name
        }
    ]


@MitsubaAddon.addon_register_class
class mitsuba_camera(declarative_property_group):
    ef_attach_to = ['Camera']

    controls = [
        'exterior',
        #'usemblur',
        #'motion_blur_samples',
        #['cammblur', 'objectmblur']
    ]

    properties = [
        {
            'type': 'bool',
            'attr': 'use_rdist',
            'name': 'Use Radial Distortion',
            'description': 'Enable lens radial distortion',
            'default': False,
        },
        {
            'attr': 'kc0',
            'type': 'float',
            'name': 'kc0',
            'default': 0.0,
            'min': -10.0,
            'max': 10.0,
        },
        {
            'attr': 'kc1',
            'type': 'float',
            'name': 'kc1',
            'default': 0.0,
            'min': -10.0,
            'max': 10.0,
        },
        {
            'type': 'bool',
            'attr': 'use_dof',
            'name': 'Depth of Field',
            'description': 'Use depth of field',
            'default': False,
        },
        {
            'attr': 'apertureRadius',
            'type': 'float',
            'description': 'DOF Aperture Radius',
            'name': 'Aperture Radius',
            'default': 0.03,
            'min': 0.01,
            'max': 1.0,
        },
        {
            'type': 'float',
            'attr': 'shutterTime',
            'name': 'Shutter time',
            'description': 'Amount of time, for which the shutter remains open (measured in frames)',
            'save_in_preset': True,
            'min': 0,
            'max': 3600,
            'default': 1
        },
    ] + CameraMediumParameter('exterior', 'Exterior medium')

    def api_output(self, scene, camera=None):
        '''
        scene           bpy.types.scene
        camera          bpy.types.camera

        Format this class's members into a Mitsuba dictionary

        Returns dict
        '''

        if camera is None:
            camera = next(cam for cam in scene.objects if cam.type == 'CAMERA' and cam.data.name == self.id_data.name)

            if camera is None:
                MtsLog("Error: Camera not found!")

                return

        cam_dict = {}

        cam = camera.data
        mcam = cam.mitsuba_camera

        cam_dict['id'] = '%s-camera' % camera.name

        # detect sensor type
        cam_dict['type'] = 'orthographic' if cam.type == 'ORTHO' else 'spherical' if cam.type == 'PANO' else 'perspective'

        if mcam.use_dof is True:
            cam_dict['type'] = 'telecentric' if cam.type == 'ORTHO' else 'thinlens'

        elif mcam.use_rdist is True and cam.type == 'PERSP':
            cam_dict['type'] = 'perspective_rdist'

        cam_dict['sampler'] = scene.mitsuba_sampler.api_output()
        cam_dict['film'] = mcam.mitsuba_film.api_output(scene, cam)

        if cam.type == 'PERSP':
            sensor = cam.sensor_height if cam.sensor_fit == 'VERTICAL' else cam.sensor_width
            cam_dict['fov'] = math.degrees(2.0 * math.atan((sensor / 2.0) / cam.lens))
            cam_dict['fovAxis'] = 'x' if cam_dict['film']['fitHorizontal'] else 'y'

        cam_dict['nearClip'] = cam.clip_start
        cam_dict['farClip'] = cam.clip_end

        if mcam.use_dof is True:
            cam_dict['apertureRadius'] = mcam.apertureRadius
            cam_dict['focusDistance'] = cam.dof_distance

        elif mcam.use_rdist is True and cam.type == 'PERSP':
            cam_dict['kc'] = '%d, %d' % (mcam.kc0, mcam.kc1)

        if scene.render.use_motion_blur:
            cam_dict['shutterOpen'] = 0.0
            cam_dict['shutterClose'] = 1.0

        if mcam.exterior_medium != '':
            cam_dict['exterior'] = {
                'type': 'ref',
                'id': '%s-medium' % mcam.exterior_medium,
            }

        return cam_dict


@MitsubaAddon.addon_register_class
class mitsuba_film(declarative_property_group):
    ef_attach_to = ['mitsuba_camera']

    def pixel_formats(self, context):
        if self.fileFormat == 'openexr':
            return [
                ('rgb', 'RGB', 'rgb'),
                ('rgba', 'RGBA', 'rgba'),
            ]

        if self.fileFormat == 'jpeg':
            return [
                ('rgb', 'RGB', 'rgb'),
                ('luminance', 'BW', 'luminance'),
            ]

        else:
            return [
                ('rgb', 'RGB', 'rgb'),
                ('rgba', 'RGBA', 'rgba'),
                ('luminance', 'BW', 'luminance'),
                ('luminanceAlpha', 'BWA', 'luminanceAlpha'),
            ]

    def set_type(self, context):
        if self.fileFormat == 'openexr':
            self.type = 'hdrfilm'
            self.fileExtension = 'exr'

        else:
            self.type = 'ldrfilm'

            if self.fileFormat == 'jpeg':
                self.fileExtension = 'jpg'

            else:
                self.fileExtension = 'png'

    controls = [
        'fileFormat',
        'pixelFormat',
        'componentFormat',
        'tonemapMethod',
        'gamma',
        'exposure',
        'key',
        'burn',
        'rfilter',
        'stddev',
        'B',
        'C',
        'lobes',
        'highQualityEdges',
        'statistics',
        'banner',
        'attachLog',
    ]

    visibility = {
        'componentFormat': {'fileFormat': 'openexr'},
        'tonemapMethod': {'type': 'ldrfilm'},
        'gamma': {'type': 'ldrfilm'},
        'exposure': {'type': 'ldrfilm', 'tonemapMethod': 'gamma'},
        'key': {'type': 'ldrfilm', 'tonemapMethod': 'reinhard'},
        'burn': {'type': 'ldrfilm', 'tonemapMethod': 'reinhard'},
        'stddev': {'rfilter': 'gaussian'},
        'B': {'rfilter': 'mitchell'},
        'C': {'rfilter': 'mitchell'},
        'lobes': {'rfilter': 'lanczos'},
        'attachLog': {'fileFormat': 'openexr'},
    }

    properties = [
        {
            'type': 'string',
            'attr': 'type',
            'name': 'Type',
            'default': 'ldrfilm',
            'save_in_preset': True
        },
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
            'description': 'Denotes the desired output file format',
            'items': [
                ('png', 'PNG', 'png'),
                ('jpeg', 'JPEG', 'jpeg'),
                ('openexr', 'OpenEXR', 'openexr')
            ],
            'default': 'png',
            'update': set_type,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'pixelFormat',
            'name': 'Pixel Format',
            'description': 'Specifies the desired pixel format',
            'items': pixel_formats,
            'expand': True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'componentFormat',
            'name': 'Component Format',
            'description': 'Specifies the desired floating point component format used for OpenEXR output',
            'items': [
                ('float16', 'Float16', 'float16'),
                ('float32', 'Float32', 'float32'),
            ],
            'default': 'float16',
            'expand': True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'tonemapMethod',
            'name': 'Tonemap Method',
            'description': 'Method used to tonemap recorded radiance values',
            'items': [
                ('gamma', 'Exposure and Gamma', 'gamma'),
                ('reinhard', 'Reinhard Tonemapping', 'reinhard'),
            ],
            'default': 'gamma',
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'gamma',
            'name': 'Gamma',
            'description': 'The gamma curve applied to correct the output image, where the special value -1 indicates sRGB. (Default: -1)',
            'default': -1.0,
            'min': -10.0,
            'max': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'exposure',
            'name': 'Exposure',
            'description': 'specifies an exposure factor in f-stops that is applied to the image before gamma correction (scaling the radiance values by 2^exposure ). (Default: 0, i.e. do not change the exposure)',
            'default': 0.0,
            'min': -10.0,
            'max': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'key',
            'name': 'Key',
            'description': 'Specifies whether a low-key or high-key image is desired. (Default: 0.18, corresponding to a middle-grey)',
            'default': 0.18,
            'min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'burn',
            'name': 'Burn',
            'description': 'Specifies how much highlights can burn out. (Default: 0, i.e. map all luminance values into the displayable range)',
            'default': 0.0,
            'min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'rfilter',
            'name': 'Reconstruction Filter',
            'description': 'Reconstruction filter method used generate final output image (default: gaussian)',
            'items': [
                ('box', 'Box filter', 'box'),
                ('tent', 'Tent filter', 'tent'),
                ('gaussian', 'Gaussian filter', 'gaussian'),
                ('mitchell', 'Mitchell-Netravali filter', 'mitchell'),
                ('catmullrom', 'Catmull-Rom filter', 'catmullrom'),
                ('lanczos', 'Lanczos Sinc filter', 'lanczos'),
            ],
            'default': 'gaussian',
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'stddev',
            'name': 'Standard Deviation',
            'description': 'Standard Deviation. (Default: 0.5)',
            'default': 0.5,
            'min': 0.1,
            'max': 10,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'B',
            'name': 'B Parameter',
            'description': 'B parameter. (Default: 0.33)',
            'default': 0.333333,
            'min': 0,
            'max': 10,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'C',
            'name': 'C Parameter',
            'description': 'C parameter. (Default: 0.33)',
            'default': 0.333333,
            'min': 0,
            'max': 10,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'lobes',
            'name': 'Lobes',
            'description': 'Specifies the amount of filter side-lobes. (Default: 3)',
            'default': 3,
            'min': 1,
            'max': 10,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'highQualityEdges',
            'name': 'High Quality Edges',
            'description': 'If enabled, regions slightly outside of the film plane will also be sampled',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'banner',
            'name': 'Mitsuba Logo',
            'description': 'Render will containg small Mitsuba logo',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'statistics',
            'name': 'Render Statistics',
            'description': 'Render will containg render statistics',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'attachLog',
            'name': 'Attach Log',
            'description': 'Mitsuba can optionally attach the entire rendering log file as a metadata field so that this information is permanently saved',
            'default': True,
            'save_in_preset': True
        },
    ]

    def resolution(self, scene):
        '''
        Calculate the output render resolution

        Returns     tuple(2) (floats)
        '''

        xr = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
        yr = scene.render.resolution_y * scene.render.resolution_percentage / 100.0

        xr = math.trunc(xr)
        yr = math.trunc(yr)

        return xr, yr

    def api_output(self, scene, camera):
        film_dict = {}

        film_dict['type'] = self.type

        (film_dict['width'], film_dict['height']) = self.resolution(scene)

        film_dict['pixelAspectX'] = scene.render.pixel_aspect_x
        film_dict['pixelAspectY'] = scene.render.pixel_aspect_y

        if camera.sensor_fit == 'HORIZONTAL':
            film_dict['fitHorizontal'] = True

        elif camera.sensor_fit == 'VERTICAL':
            film_dict['fitHorizontal'] = False

        else:
            frx = film_dict['width'] * film_dict['pixelAspectX']
            fry = film_dict['height'] * film_dict['pixelAspectY']
            film_dict['fitHorizontal'] = True if frx > fry else False

        film_dict['shiftX'] = camera.shift_x
        film_dict['shiftY'] = camera.shift_y

        film_dict['fileFormat'] = self.fileFormat
        film_dict['pixelFormat'] = self.pixelFormat

        if self.fileFormat == 'openexr':
            film_dict['componentFormat'] = self.componentFormat
            film_dict['attachLog'] = self.attachLog

        if self.type == 'ldrfilm':
            film_dict['tonemapMethod'] = self.tonemapMethod
            film_dict['gamma'] = self.gamma

            if self.tonemapMethod == 'reinhard':
                film_dict['key'] = self.key
                film_dict['burn'] = self.burn

            else:
                film_dict['exposure'] = self.exposure

        film_dict['banner'] = self.banner
        film_dict['highQualityEdges'] = self.highQualityEdges

        rfilt_dict = {}
        rfilt_dict['type'] = self.rfilter

        if self.rfilter in {'gaussian', 'mitchell', 'lanczos'}:
            if self.rfilter == 'gaussian':
                rfilt_dict['stddev'] = self.stddev

            elif self.rfilter == 'mitchell':
                rfilt_dict['B'] = self.B
                rfilt_dict['C'] = self.C

            else:
                rfilt_dict['lobes'] = self.lobes

        film_dict['rfilter'] = rfilt_dict

        if self.statistics:
            film_dict['label[10,10]'] = 'Integrator:$integrator[\'type\'], $film[\'width\']x$film[\'height\'],$sampler[\'sampleCount\']spp, rendertime:$scene[\'renderTime\'],memory:$scene[\'memUsage\']'

        return film_dict
