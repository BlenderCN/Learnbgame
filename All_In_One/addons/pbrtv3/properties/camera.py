# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
import math
import os

import bpy

from ..extensions_framework import util as efutil
from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O, Logic_AND as A

from .. import PBRTv3Addon
from ..export import get_worldscale, get_output_filename
from ..export import ParamSet, PBRTv3Manager
from ..export import fix_matrix_order
from ..outputs.pure_api import PBRTv3_VERSION
from ..outputs.luxcore_api import UsePBRTv3Core


def CameraVolumeParameter(attr, name):
    return [
        {
            'attr': '%s_volume' % attr,
            'type': 'string',
            'name': '%s_volume' % attr,
            'description': '%s volume; leave blank to use World default' % attr,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': attr,
            'src': lambda s, c: s.scene.pbrtv3_volumes,
            'src_attr': 'volumes',
            'trg': lambda s, c: c.pbrtv3_camera,
            'trg_attr': '%s_volume' % attr,
            'name': name,
            'icon': 'MOD_FLUIDSIM'
        },
    ]

def ArbitraryClippingPlane():
    """
    PBRTv3Core arbitrary clipping plane
    The user selects an object and its rotation and location are used as clipping plane parameters
    """
    return [
        {
            'attr': 'clipping_plane_obj',
            'type': 'string',
            'name': 'clipping_plane_obj',
            'description': 'Arbitrary clipping plane object (only rotation and location are used)',
        },
        {
            'type': 'prop_search',
            'attr': 'clipping_plane_selector',
            'src': lambda s, c: s.scene,
            'src_attr': 'objects',
            'trg': lambda s, c: c.pbrtv3_camera,
            'trg_attr': 'clipping_plane_obj',
            'name': 'Plane'
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_camera(declarative_property_group):
    """
    Storage class for PBRTv3 Camera settings.
    """

    ef_attach_to = ['Camera']

    controls = [
        'Exterior',
        'fstop',
        'sensitivity',
        'exposure_mode',
        ['exposure_start_norm', 'exposure_end_norm'],
        ['exposure_start_abs', 'exposure_end_abs'],
        ['exposure_degrees_start', 'exposure_degrees_end'],
        'separator_mblur',
        'usemblur',
        ['cammblur', 'objectmblur'],
        'motion_blur_samples',
        'shutterdistribution',
        'separator_after_mblur',
        #'enable_clipping_plane', # now drawn manually in ui/camera.py
        #'clipping_plane_selector',
        #'use_dof'
        # [0.3, 'use_dof','autofocus', 'use_clipping'],
        # 'blades',
        #       ['distribution', 'power'],
    ]

    visibility = {
        # 'autofocus':                { 'use_dof': True },
        # 'blades':                   { 'use_dof': True },
        #       'distribution':             { 'use_dof': True },
        #       'power':                    { 'use_dof': True },
        'exposure_start_norm': {'exposure_mode': 'normalised'},
        'exposure_end_norm': {'exposure_mode': 'normalised'},
        'exposure_start_abs': {'exposure_mode': 'absolute'},
        'exposure_end_abs': {'exposure_mode': 'absolute'},
        'exposure_degrees_start': {'exposure_mode': 'degrees'},
        'exposure_degrees_end': {'exposure_mode': 'degrees'},
        'shutterdistribution': {'usemblur': True},
        'motion_blur_samples': {'usemblur': True},
        'cammblur': {'usemblur': True},
        'objectmblur': {'usemblur': True},
        'separator_after_mblur': {'usemblur': True},
        #'enable_clipping_plane': lambda: UsePBRTv3Core(),
        #'clipping_plane_selector': A([{'enable_clipping_plane': True}, lambda: UsePBRTv3Core()])
    }

    properties = CameraVolumeParameter('Exterior', 'Exterior') + ArbitraryClippingPlane() + [
        {
            'type': 'bool',
            'attr': 'use_clipping',
            'name': 'Clipping',
            'description': 'Use near/far geometry clipping',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'use_dof',
            'name': 'Depth of Field',
            'description': 'Use depth of field',
            'default': False,
        },
        {
            'type': 'enum',
            'attr': 'dof_focus_type',
            'name': 'Focus',
            'description': 'Type of focus point',
            'default': 'manual',
            'items': [
                ('manual', 'Manual', 'Set the focal distance by hand'),
                ('object', 'Object', 'Use an object\'s origin as focal point'),
                ('autofocus', 'Autofocus', 'Automatically set the focal distance to the surface distance in the '
                                           'image center'),
            ]
        },
        { # TODO: remove
            'type': 'bool',
            'attr': 'autofocus',
            'name': 'Auto Focus',
            'description': 'Auto-focus for depth of field (to the image center), DOF target object will be ignored',
            'default': False,
        },
        {
            'type': 'int',
            'attr': 'blades',
            'name': 'Blades',
            'description': 'Number of aperture blades. Use 2 or lower for circular aperture',
            'min': 0,
            'default': 0,
        },
        {
            'type': 'enum',
            'attr': 'distribution',
            'name': 'Distribution',
            'description': 'This value controls the lens sampling distribution. '
                           'Non-uniform distributions allow for ring effects',
            'default': 'uniform',
            'items': [
                ('uniform', 'Uniform', 'Uniform'),
                ('exponential', 'Exponential', 'Exponential'),
                ('inverse exponential', 'Inverse Exponential', 'Inverse Exponential'),
                ('gaussian', 'Gaussian', 'Gaussian'),
                ('inverse gaussian', 'Inverse Gaussian', 'Inverse Gaussian'),
            ]
        },
        {
            'type': 'int',
            'attr': 'power',
            'name': 'Power',
            'description': 'Exponent for lens sampling distribution. Higher values give more pronounced ring-effects',
            'min': 0,
            'default': 0,
        },
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Camera type',
            'description': 'Choose camera type',
            'default': 'perspective',
            'items': [
                ('perspective', 'Perspective', 'perspective'),
                ('environment', 'Environment', 'environment'),
                # ('realistic', 'Realistic', 'realistic'),
            ]
        },
        {
            'type': 'float',
            'attr': 'fstop',
            'name': 'f/Stop',
            'description': 'Aperture, lower values result in stronger depth of field effect (if enabled) and '
                           'brighten the image (if the manual/camera settings tonemapper is selected)',
            'default': 2.8,
            'min': 0.01,  # for experimental values
            'max': 128.0,
            'step': 100
        },
        {
            'type': 'float',
            'attr': 'sensitivity',
            'name': 'ISO',
            'description': 'Sensitivity (ISO), only affects image brightness (if the manual/camera settings tonemapper '
                           'is selected)',
            'default': 320.0,
            'min': 10.0,
            'max': 6400.0,
            'step': 1000
        },
        {
            'type': 'enum',
            'attr': 'exposure_mode',
            'name': 'Exposure',
            'items': [
                ('normalised', 'Normalised', 'normalised'),
                ('absolute', 'Absolute', 'absolute'),
                ('degrees', 'Degrees', 'degrees'),
            ],
            'default': 'normalised',
        },
        {
            'type': 'int',
            'attr': 'motion_blur_samples',
            'name': 'Motion Subdivision',
            'description': 'Number of motion steps per frame. Increase for non-linear motion blur or high velocity '
                           'rotations',
            'default': 1,
            'min': 1,
            'max': 100,
        },
        {
            'type': 'float',
            'attr': 'exposure_start_norm',
            'name': 'Open',
            'description': 'Normalised shutter open time',
            'precision': 3,
            'default': 0.0,
            'min': 0.0,
            'max': 1.0,
        },
        {
            'type': 'float',
            'attr': 'exposure_end_norm',
            'name': 'Close',
            'description': 'Normalised shutter close time',
            'precision': 3,
            'default': 1.0,
            'min': 0.0,
            'max': 1.0,
        },
        {
            'type': 'float',
            'attr': 'exposure_start_abs',
            'name': 'Open',
            'description': 'Absolute shutter open time (seconds)',
            'precision': 6,
            'default': 0.0,
            'min': 0.0,
        },
        {
            'type': 'float',
            'attr': 'exposure_end_abs',
            'name': 'Close',
            'description': 'Absolute shutter close time (seconds)',
            'precision': 6,
            'default': 1.0,
            'min': 0.0,
        },
        {
            'type': 'float',
            'attr': 'exposure_degrees_start',
            'name': 'Open angle',
            'description': 'Shutter open angle',
            'precision': 1,
            'default': 0.0,
            'min': 0.0,
            'max': 2 * math.pi,
            'subtype': 'ANGLE',
            'unit': 'ROTATION'
        },
        {
            'type': 'float',
            'attr': 'exposure_degrees_end',
            'name': 'Close angle',
            'description': 'Shutter close angle',
            'precision': 1,
            'default': 2 * math.pi,
            'min': 0.0,
            'max': 2 * math.pi,
            'subtype': 'ANGLE',
            'unit': 'ROTATION'
        },
        {
            'type': 'separator',
            'attr': 'separator_mblur'
        },
        {
            'type': 'bool',
            'attr': 'usemblur',
            'name': 'Motion Blur',
            'default': False,
            'toggle': True
        },
        {
            'type': 'enum',
            'attr': 'shutterdistribution',
            'name': 'Distribution',
            'default': 'uniform',
            'items': [
                ('uniform', 'Uniform', 'uniform'),
                ('gaussian', 'Gaussian', 'gaussian'),
            ],
            'expand': True,
        },
        {
            'type': 'bool',
            'attr': 'cammblur',
            'name': 'Camera Motion Blur',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'objectmblur',
            'name': 'Object Motion Blur',
            'default': True
        },
        {
            'type': 'separator',
            'attr': 'separator_after_mblur'
        },
        {
            'type': 'bool',
            'attr': 'enable_clipping_plane',
            'name': 'Arbitrary Clipping Plane',
            'description': 'PBRTv3Core only',
            'default': False
        },
    ]

    def lookAt(self, camera, matrix=None):
        """
        Derive a list describing 3 points for a PBRTv3 LookAt statement

        Returns     tuple(9) (floats)
        """
        if matrix is None:
            matrix = camera.matrix_world.copy()

        ws = get_worldscale()
        matrix *= ws
        ws = get_worldscale(as_scalematrix=False)
        matrix = fix_matrix_order(matrix)  # matrix indexing hack
        matrix[0][3] *= ws
        matrix[1][3] *= ws
        matrix[2][3] *= ws

        # transpose to extract columns
        # TODO - update to matrix.col when available
        matrix = matrix.transposed()
        pos = matrix[3]
        forwards = -matrix[2]
        target = (pos + forwards)
        up = matrix[1]

        return pos[:3] + target[:3] + up[:3]

    def screenwindow(self, xr, yr, scene, cam, luxcore_export=False):
        """
        xr              float
        yr              float
        cam             bpy.types.camera
        luxcore_export  bool (leave crop handling to Blender)

        Calculate PBRTv3 camera's screenwindow parameter

        Returns list[4]
        """

        shiftX = cam.shift_x
        shiftY = cam.shift_y

        if cam.type == 'ORTHO':
            scale = cam.ortho_scale / 2.0
        else:
            scale = 1.0

        aspect = xr / yr
        invaspect = 1.0 / aspect

        if aspect > 1.0:
            sw = [
                ((2 * shiftX) - 1) * scale,
                ((2 * shiftX) + 1) * scale,
                ((2 * shiftY) - invaspect) * scale,
                ((2 * shiftY) + invaspect) * scale
            ]
        else:
            sw = [
                ((2 * shiftX) - aspect) * scale,
                ((2 * shiftX) + aspect) * scale,
                ((2 * shiftY) - 1) * scale,
                ((2 * shiftY) + 1) * scale
            ]

        # If we are using cropwindow, we want the full-frame screenwindow.
        # See border render handling code elsewhere in this file (do a search for "border")
        if (scene.render.use_border and not (
                    not scene.render.use_crop_to_border and (
                        not scene.pbrtv3_engine.render or (
                                    scene.pbrtv3_engine.export_type == 'EXT' and
                                    scene.pbrtv3_engine.binary_name == 'luxrender' and
                                    not scene.pbrtv3_engine.monitor_external)))) or (
                                    luxcore_export):
            x1, x2, y1, y2 = [
                scene.render.border_min_x, scene.render.border_max_x,
                scene.render.border_min_y, scene.render.border_max_y
            ]

            sw = [
                sw[0] * (1 - x1) + sw[1] * x1,
                sw[0] * (1 - x2) + sw[1] * x2,
                sw[2] * (1 - y1) + sw[3] * y1,
                sw[2] * (1 - y2) + sw[3] * y2
            ]

        return sw

    def exposure_time(self):
        """
        Calculate the camera exposure time in seconds
        """
        fps = PBRTv3Manager.CurrentScene.render.fps / PBRTv3Manager.CurrentScene.render.fps_base
        time = 1.0

        if self.exposure_mode == 'normalised':
            time = (self.exposure_end_norm - self.exposure_start_norm) / fps

        if self.exposure_mode == 'absolute':
            time = (self.exposure_end_abs - self.exposure_start_abs)

        if self.exposure_mode == 'degrees':
            time = (self.exposure_degrees_end - self.exposure_degrees_start) / (fps * 2 * math.pi)

        return time

    def api_output(self, scene, is_cam_animated):
        """
        scene           bpy.types.scene

        Format this class's members into a PBRTv3 ParamSet

        Returns tuple
        """

        cam = scene.camera.data
        xr, yr = self.pbrtv3_film.resolution(scene)

        params = ParamSet()

        if cam.type == 'PERSP' and self.type == 'perspective':
            params.add_float('fov', math.degrees(scene.camera.data.angle))

        params.add_float('screenwindow', self.screenwindow(xr, yr, scene, cam))
        # params.add_bool('autofocus', False)
        fps = scene.render.fps / scene.render.fps_base

        if self.exposure_mode == 'normalised':
            params.add_float('shutteropen', self.exposure_start_norm / fps)
            params.add_float('shutterclose', self.exposure_end_norm / fps)

        if self.exposure_mode == 'absolute':
            params.add_float('shutteropen', self.exposure_start_abs)
            params.add_float('shutterclose', self.exposure_end_abs)

        if self.exposure_mode == 'degrees':
            params.add_float('shutteropen', self.exposure_degrees_start / (fps * 2 * math.pi))
            params.add_float('shutterclose', self.exposure_degrees_end / (fps * 2 * math.pi))

        if self.use_dof:
            # Do not world-scale this, it is already in meters !
            params.add_float('lensradius', (cam.lens / 1000.0) / ( 2.0 * self.fstop ))

            # Write apperture params
            params.add_integer('blades', self.blades)
            params.add_integer('power', self.power)
            params.add_string('distribution', self.distribution)

        ws = get_worldscale(as_scalematrix=False)

        # if self.autofocus and self.use_dof:
        #     params.add_bool('autofocus', True)
        # else:
        #     if cam.dof_object is not None:
        #         params.add_float('focaldistance', ws * ((scene.camera.location - cam.dof_object.location).length))
        #     elif cam.dof_distance > 0:
        #         params.add_float('focaldistance', ws * cam.dof_distance)

        if self.use_clipping:
            params.add_float('hither', ws * cam.clip_start)
            params.add_float('yon', ws * cam.clip_end)

        if self.usemblur:
            # update the camera settings with motion blur settings
            params.add_string('shutterdistribution', self.shutterdistribution)

        cam_type = 'orthographic' if cam.type == 'ORTHO' else self.type if bpy.app.version < (2, 63, 5) else \
            'environment' if cam.type == 'PANO' else 'perspective'

        return cam_type, params

@PBRTv3Addon.addon_register_class
class pbrtv3_film(declarative_property_group):
    ef_attach_to = ['pbrtv3_camera']

    controls = [
        'lbl_internal',
        'internal_updateinterval',

        'lbl_external',
        'writeinterval',
        'flmwriteinterval',
        'displayinterval',

        # 'lbl_outputs',
        # ['write_png', 'write_png_16bit'],
        #       'write_tga',
        #       ['write_exr', 'write_exr_applyimaging', 'write_exr_halftype'],
        #       'write_exr_compressiontype',
        #       'write_zbuf',
        #       'zbuf_normalization',
        #       ['output_alpha', 'premultiply_alpha'],
        #       ['write_flm', 'restart_flm', 'write_flm_direct'],

        'ldr_clamp_method',
        'outlierrejection_k',
        'tilecount'
    ]

    # visibility = {
    # 'restart_flm': { 'write_flm': True },
    #       'premultiply_alpha': { 'output_alpha': True },
    #       'write_flm_direct': { 'write_flm': True },
    #       'write_png_16bit': { 'write_png': True },
    #       'write_exr_applyimaging': { 'write_exr': True },
    #       'write_exr_halftype': { 'write_exr': True },
    #       'write_exr_compressiontype': { 'write_exr': True },
    #       'write_zbuf': O([{'write_exr': True }, { 'write_tga': True }]),
    #       'zbuf_normalization': A([{'write_zbuf': True}, O([{'write_exr': True }, { 'write_tga': True }])]),
    #   }

    properties = [
        {
            'type': 'text',
            'attr': 'lbl_internal',
            'name': 'Internal rendering'
        },
        {
            'type': 'int',
            'attr': 'internal_updateinterval',
            'name': 'Update interval',
            'description': 'Period for updating render image (seconds)',
            'default': 10,
            'min': 2,
            'soft_min': 2,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'lbl_external',
            'name': 'External rendering'
        },
        {
            'type': 'int',
            'attr': 'writeinterval',
            'name': 'Write interval',
            'description': 'Period for writing images to disk (seconds)',
            'default': 180,
            'min': 2,
            'soft_min': 2,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'flmwriteinterval',
            'name': 'Flm write interval',
            'description': 'Period for writing flm files to disk (seconds)',
            'default': 900,
            'min': 2,
            'soft_min': 2,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'displayinterval',
            'name': 'Refresh interval',
            'description': 'Period for updating rendering on screen (seconds)',
            'default': 10,
            'min': 2,
            'soft_min': 2,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'lbl_outputs',
            'name': 'Output formats'
        },
        {
            'type': 'bool',
            'attr': 'write_png',
            'name': 'PNG',
            'description': 'Enable PNG output',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'write_png_16bit',
            'name': 'Use 16bit PNG',
            'description': 'Use 16bit per channel PNG instead of 8bit',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'write_exr',
            'name': 'OpenEXR',
            'description': 'Enable OpenEXR ouput',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'write_exr_halftype',
            'name': 'Use 16bit EXR',
            'description': 'Use "half" (16bit float) OpenEXR format instead of 32bit float',
            'default': False
        },
        {
            'type': 'enum',
            'attr': 'write_exr_compressiontype',
            'name': 'EXR Compression',
            'description': 'Compression format for OpenEXR output',
            'items': [
                ('RLE (lossless)', 'RLE (lossless)', 'RLE (lossless)'),
                ('PIZ (lossless)', 'PIZ (lossless)', 'PIZ (lossless)'),
                ('ZIP (lossless)', 'ZIP (lossless)', 'ZIP (lossless)'),
                ('Pxr24 (lossy)', 'Pxr24 (lossy)', 'Pxr24 (lossy)'),
                ('None', 'None', 'None'),
            ],
            'default': 'PIZ (lossless)'
        },
        {
            'type': 'bool',
            'attr': 'write_tga',
            'name': 'TARGA',
            'description': 'Enable TARGA ouput',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'write_flm',
            'name': 'Write FLM',
            'description': 'Write framebuffer (FLM) to disk to allow resuming and adjusting imaging options',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'restart_flm',
            'name': 'Restart FLM',
            'description': 'Restart render from the beginning even if an FLM is available',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'write_flm_direct',
            'name': 'Write FLM Directly',
            'description': 'Write FLM directly to disk instead of trying to build it in RAM first. Slower, \
            but uses less memory',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'output_alpha',
            'name': 'Enable alpha channel',
            'description': 'Enable alpha channel. This applies to all image formats. Integrated imaging must be \
            always premultiplied',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'premultiply_alpha',
            'name': 'Premultiply Alpha',
            'description': 'Premultiply alpha channel. This is applied during splatting, not image output',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'write_exr_applyimaging',
            'name': 'Tonemap EXR',
            'description': 'Apply imaging pipeline to OpenEXR output. Gamma correction will be skipped regardless',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'write_zbuf',
            'name': 'Enable Z-Buffer',
            'description': 'Include Z-buffer in OpenEXR and TARGA output',
            'default': False
        },
        {
            'type': 'enum',
            'attr': 'zbuf_normalization',
            'name': 'Z-Buffer Normalization',
            'description': 'Where to get normalization info for Z-buffer',
            'items': [
                ('Camera Start/End clip', 'Camera start/end clip', 'Use Camera clipping range'),
                ('Min/Max', 'Min/max', 'Min/max'),
                ('None', 'None', 'None'),
            ],
            'default': 'None'
        },
        {
            'type': 'int',
            'attr': 'outlierrejection_k',
            'name': 'Firefly rejection',
            'description': 'Firefly (outlier) rejection k parameter. 0=disabled',
            'default': 2,
            'min': 0,
            'soft_min': 0,
        },
        {
            'type': 'int',
            'attr': 'tilecount',
            'name': 'Tiles',
            'description': 'Number of film buffer tiles to use. 0=auto-detect',
            'default': 0,
            'min': 0,
            'soft_min': 0,
        },
        {
            'type': 'enum',
            'attr': 'ldr_clamp_method',
            'name': 'LDR Clamp method',
            'description': 'Method used to clamp bright areas into LDR range',
            'items': [
                ('lum', 'Luminosity', 'Preserve luminosity'),
                ('hue', 'Hue', 'Preserve hue'),
                ('cut', 'Cut', 'Clip channels individually'),
                ('darken', 'Darken', 'Darken highlights')
            ],
            'default': 'cut'
        },
    ]

    def resolution(self, scene):
        """
        Calculate the output render resolution

        Returns     tuple(2) (floats)
        """
        xr = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
        yr = scene.render.resolution_y * scene.render.resolution_percentage / 100.0

        xr = math.trunc(xr)
        yr = math.trunc(yr)

        return xr, yr

    def get_gamma(self):
        if self.pbrtv3_colorspace.preset:
            return getattr(colorspace_presets, self.pbrtv3_colorspace.preset_name).gamma
        else:
            return self.pbrtv3_colorspace.gamma

    def api_output(self):
        """
        Calculate type and parameters for PBRTv3 Film statement

        Returns     tuple(2) (string, list)
        """
        scene = PBRTv3Manager.CurrentScene
        xr, yr = self.resolution(scene)
        params = ParamSet()

        def calc_border_filmsize(scene, width, height):
            x_min, x_max, y_min, y_max = [
                scene.render.border_min_x, scene.render.border_max_x,
                scene.render.border_min_y, scene.render.border_max_y
            ]

            width = int(x_max * width) - int(x_min * width)
            height = int(y_max * height) - int(y_min * height)

            # In case border becomes too small
            width = max(width, 1)
            height = max(height, 1)

            return width, height

        # Border rendering handler, this gets a bit tricky. Blender ALWAYS expects to get back a cropped image,
        # it will handle the padding itself if the user asked for it.
        if scene.render.use_border:
            if scene.render.use_crop_to_border:  # user asked to crop, so always crop
                width, height = calc_border_filmsize(scene, xr, yr)
                params.add_integer('xresolution', width)
                params.add_integer('yresolution', height)

            # user asked for padded-to-full-frame output, there are a few cases where Lux needs to do this
            # itself since the rendered image will not be returned to Blender
            if not scene.render.use_crop_to_border:
                # If run-renderer (scene.pbrtv3_engine.render) is disabled or we are in un-monitored external mode,
                # we do not return the image to Blender and Lux must pad the image itself
                if not scene.pbrtv3_engine.render or (
                                    scene.pbrtv3_engine.export_type == 'EXT' and
                                    scene.pbrtv3_engine.binary_name == 'luxrender' and
                                    not scene.pbrtv3_engine.monitor_external):
                    # Subtract scene.render.border Y values from 1 to translate between Blender and Lux conventions
                    cropwindow = [
                        scene.render.border_min_x, scene.render.border_max_x,
                        1 - scene.render.border_min_y, 1 - scene.render.border_max_y
                    ]

                    params.add_float('cropwindow', cropwindow)
                    params.add_integer('xresolution', xr)  # Don't forget to set full frame resolution
                    params.add_integer('yresolution', yr)
                else:
                    # We are returning the image to blender which will pad for us,
                    # so have PBRTv3 send back a cropped frame anyway
                    width, height = calc_border_filmsize(scene, xr, yr)
                    params.add_integer('xresolution', width)
                    params.add_integer('yresolution', height)

        else:
            # Set resolution
            params.add_integer('xresolution', xr)
            params.add_integer('yresolution', yr)

        # ColourSpace
        if self.pbrtv3_colorspace.preset:
            cs_object = getattr(colorspace_presets, self.pbrtv3_colorspace.preset_name)
        else:
            cs_object = self.pbrtv3_colorspace

        # params.add_float('gamma', self.get_gamma())
        # params.add_float('colorspace_white', [cs_object.cs_whiteX, cs_object.cs_whiteY])
        # params.add_float('colorspace_red', [cs_object.cs_redX, cs_object.cs_redY])
        # params.add_float('colorspace_green', [cs_object.cs_greenX, cs_object.cs_greenY])
        # params.add_float('colorspace_blue', [cs_object.cs_blueX, cs_object.cs_blueY])

        # Camera Response Function
        if self.pbrtv3_colorspace.use_crf == 'file' and self.pbrtv3_colorspace.crf_file:
            if scene.camera.library is not None:
                local_crf_filepath = bpy.path.abspath(self.pbrtv3_colorspace.crf_file, scene.camera.library.filepath)
            else:
                local_crf_filepath = self.pbrtv3_colorspace.crf_file

            local_crf_filepath = efutil.filesystem_path(local_crf_filepath)
            if scene.pbrtv3_engine.allow_file_embed():
                from ..util import bencode_file2string

                params.add_string('cameraresponse', os.path.basename(local_crf_filepath))
                encoded_data = bencode_file2string(local_crf_filepath)
                params.add_string('cameraresponse_data', encoded_data.splitlines())
            else:
                params.add_string('cameraresponse', local_crf_filepath)

        if self.pbrtv3_colorspace.use_crf == 'preset':
            params.add_string('cameraresponse', self.pbrtv3_colorspace.crf_preset)

        # Output types
        params.add_string('filename', get_output_filename(scene)+'.png')
        # params.add_bool('write_resume_flm', self.write_flm)
        # params.add_bool('restart_resume_flm', self.restart_flm)
        # params.add_bool('write_flm_direct', self.write_flm_direct)

        if self.output_alpha:
            output_channels = 'RGBA'
            params.add_bool('premultiplyalpha', True)
        else:
            output_channels = 'RGB'

        # if scene.pbrtv3_engine.export_type == 'INT' and scene.pbrtv3_engine.integratedimaging:
            # Set up params to enable z buffer
            # we use the colorspace gamma, else autolinear gives wrong estimation,
            # gamma 1.0 per pixel is recalculated in pylux after
            # Also, this requires tonemapped EXR output
            # params.add_string('write_exr_channels', 'RGBA')
            # params.add_bool('write_exr_halftype', False)
            # params.add_bool('write_exr_applyimaging', True)
            # params.add_bool('premultiplyalpha',
                            # True if self.output_alpha else False)  # Blender 2.66 always expects premultiplyalpha
            # params.add_bool('write_exr_ZBuf', True)
            # params.add_string('write_exr_zbuf_normalizationtype', 'Camera Start/End clip')
        # else:
            # Otherwise let the user decide on tonemapped EXR and other EXR settings
            # params.add_bool('write_exr_halftype', self.write_exr_halftype)
            # params.add_bool('write_exr_applyimaging', self.write_exr_applyimaging)
            # params.add_bool('write_exr_ZBuf', self.write_zbuf)
            # params.add_string('write_exr_compressiontype', self.write_exr_compressiontype)
            # params.add_string('write_exr_zbuf_normalizationtype', self.zbuf_normalization)
            # params.add_bool('write_exr', self.write_exr)
            # params.add_string('write_exr_channels', output_channels)

        # params.add_bool('write_png', self.write_png)
        # params.add_string('write_png_channels', output_channels)

        # if self.write_png:
            # params.add_bool('write_png_16bit', self.write_png_16bit)

        # params.add_bool('write_tga', self.write_tga)
        # params.add_string('write_tga_channels', output_channels)

        if self.write_tga:
            params.add_bool('write_tga_ZBuf', self.write_zbuf)
            params.add_string('write_tga_zbuf_normalizationtype', self.zbuf_normalization)

        # params.add_string('ldr_clamp_method', self.ldr_clamp_method)

        # if scene.pbrtv3_engine.export_type == 'EXT':
        #     params.add_integer('displayinterval', self.displayinterval)
        #     params.add_integer('writeinterval', self.writeinterval)
        #     params.add_integer('flmwriteinterval', self.flmwriteinterval)
        # else:
        #     params.add_integer('writeinterval', self.internal_updateinterval)

        # Halt conditions
        # if scene.pbrtv3_halt.haltspp > 0:
            # params.add_integer('haltspp', scene.pbrtv3_halt.haltspp)

        # if scene.pbrtv3_halt.halttime > 0:
            # params.add_integer('halttime', scene.pbrtv3_halt.halttime)

        # if scene.pbrtv3_halt.haltthreshold > 0:
            # params.add_float('haltthreshold', 1 / 10.0 ** scene.pbrtv3_halt.haltthreshold)

        # Convergence Test
        if scene.pbrtv3_halt.convergencestep != 32:
            params.add_float('convergencestep', scene.pbrtv3_halt.convergencestep)

        # Filename for User Sampling Map
        if scene.pbrtv3_sampler.usersamplingmap_filename:
            if scene.pbrtv3_sampler.usersamplingmap_filename.endswith('.exr'):
                params.add_string('usersamplingmap_filename', scene.pbrtv3_sampler.usersamplingmap_filename)
            else:
                params.add_string('usersamplingmap_filename', scene.pbrtv3_sampler.usersamplingmap_filename + '.exr')

        # if self.outlierrejection_k > 0 and scene.pbrtv3_rendermode.renderer != 'sppm':
            # params.add_integer('outlierrejection_k', self.outlierrejection_k)

        # params.add_integer('tilecount', self.tilecount)

        # update the film settings with tonemapper settings
        params.update(self.pbrtv3_tonemapping.get_paramset())

        return 'image', params

# Valid CRF preset names (case sensitive):
# See lux/core/cameraresponse.cpp to keep this up to date

crf_preset_names = [s.strip() for s in
                    """Advantix_100CD
                    Advantix_200CD
                    Advantix_400CD
                    Agfachrome_ctpecisa_200CD
                    Agfachrome_ctprecisa_100CD
                    Agfachrome_rsx2_050CD
                    Agfachrome_rsx2_100CD
                    Agfachrome_rsx2_200CD
                    Agfacolor_futura_100CD
                    Agfacolor_futura_200CD
                    Agfacolor_futura_400CD
                    Agfacolor_futuraII_100CD
                    Agfacolor_futuraII_200CD
                    Agfacolor_futuraII_400CD
                    Agfacolor_hdc_100_plusCD
                    Agfacolor_hdc_200_plusCD
                    Agfacolor_hdc_400_plusCD
                    Agfacolor_optimaII_100CD
                    Agfacolor_optimaII_200CD
                    Agfacolor_ultra_050_CD
                    Agfacolor_vista_100CD
                    Agfacolor_vista_200CD
                    Agfacolor_vista_400CD
                    Agfacolor_vista_800CD
                    Ektachrome_100_plusCD
                    Ektachrome_100CD
                    Ektachrome_320TCD
                    Ektachrome_400XCD
                    Ektachrome_64CD
                    Ektachrome_64TCD
                    Ektachrome_E100SCD
                    F125CD
                    F250CD
                    F400CD
                    FCICD
                    Gold_100CD
                    Gold_200CD
                    Kodachrome_200CD
                    Kodachrome_25CD
                    Kodachrome_64CD
                    Max_Zoom_800CD
                    Portra_100TCD
                    Portra_160NCCD
                    Portra_160VCCD
                    Portra_400NCCD
                    Portra_400VCCD
                    Portra_800CD""".splitlines()]


@PBRTv3Addon.addon_register_class
class CAMERA_OT_set_pbrtv3_crf(bpy.types.Operator):
    bl_idname = 'camera.set_pbrtv3_crf'
    bl_label = 'Set PBRTv3 Film Response Function'

    preset_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'camera') and context.camera and \
               context.camera.pbrtv3_camera.pbrtv3_film.pbrtv3_colorspace

    def execute(self, context):
        context.camera.pbrtv3_camera.pbrtv3_film.pbrtv3_colorspace.crf_preset = self.properties.preset_name
        return {'FINISHED'}


@PBRTv3Addon.addon_register_class
class CAMERA_MT_pbrtv3_crf(bpy.types.Menu):
    bl_label = 'CRF Preset'

    # Flat-list menu system
    def draw(self, context):
        lt = self.layout.row()

        for i, crf_name in enumerate(sorted(crf_preset_names)):
            # Create a new column every 20 items
            if i % 20 == 0:
                cl = lt.column()

            op = cl.operator('CAMERA_OT_set_pbrtv3_crf', text=crf_name)
            op.preset_name = crf_name


@PBRTv3Addon.addon_register_class
class pbrtv3_colorspace(declarative_property_group):
    """
    Storage class for PBRTv3 Colour-Space settings.
    """

    ef_attach_to = ['pbrtv3_film']

    controls = [
        'cs_label',
        [0.1, 'preset', 'preset_name'],
        ['cs_whiteX', 'cs_whiteY'],
        ['cs_redX', 'cs_redY'],
        ['cs_greenX', 'cs_greenY'],
        ['cs_blueX', 'cs_blueY'],

        'gamma_label',
        'gamma',
        'crf_label',
        'use_crf',
        'crf_preset_menu',
        'crf_file'
    ]

    visibility = {
        'preset_name': {'preset': True},
        'cs_whiteX': {'preset': False},
        'cs_whiteY': {'preset': False},
        'cs_redX': {'preset': False},
        'cs_redY': {'preset': False},
        'cs_greenX': {'preset': False},
        'cs_greenY': {'preset': False},
        'cs_blueX': {'preset': False},
        'cs_blueY': {'preset': False},

        'crf_preset_menu': {'use_crf': 'preset'},
        'crf_file': {'use_crf': 'file'},

        'gamma_label': {'preset': False},
        'gamma': {'preset': False},
    }

    properties = [
        {
            'attr': 'cs_label',
            'type': 'text',
            'name': 'Color Space'
        },
        {
            'attr': 'gamma_label',
            'type': 'text',
            'name': 'Gamma'
        },
        {
            'attr': 'gamma',
            'type': 'float',
            'name': 'Gamma',
            'default': 2.2,
            'min': 0.1,
            'soft_min': 0.1,
            'max': 20.0,
            'soft_max': 20.0
        },
        {
            'attr': 'preset',
            'type': 'bool',
            'name': 'P',
            'default': True,
            'toggle': True
        },
        # TODO - change actual parameter values when user chooses a preset
        {
            'attr': 'preset_name',
            'type': 'enum',
            'name': 'Preset',
            'default': 'sRGB',
            'items': [
                ('sRGB', 'sRGB - HDTV (ITU-R BT.709-5)', 'sRGB'),
                ('romm_rgb', 'ROMM RGB', 'romm_rgb'),
                ('adobe_rgb_98', 'Adobe RGB 98', 'adobe_rgb_98'),
                ('apple_rgb', 'Apple RGB', 'apple_rgb'),
                ('ntsc_1953', 'NTSC (FCC 1953, ITU-R BT.470-2 System M)', 'ntsc_1953'),
                ('ntsc_1979', 'NTSC (1979) (SMPTE C, SMPTE-RP 145)', 'ntsc_1979'),
                ('pal_secam', 'PAL/SECAM (EBU 3213, ITU-R BT.470-6)', 'pal_secam'),
                ('cie_e', 'CIE (1931) E', 'cie_e'),
            ]
        },
        {
            'attr': 'cs_whiteX',
            'type': 'float',
            'name': 'White X',
            'precision': 6,
            'default': 0.314275
        },
        {
            'attr': 'cs_whiteY',
            'type': 'float',
            'name': 'White Y',
            'precision': 6,
            'default': 0.329411
        },
        {
            'attr': 'cs_redX',
            'type': 'float',
            'name': 'Red X',
            'precision': 6,
            'default': 0.63
        },
        {
            'attr': 'cs_redY',
            'type': 'float',
            'name': 'Red Y',
            'precision': 6,
            'default': 0.34
        },
        {
            'attr': 'cs_greenX',
            'type': 'float',
            'name': 'Green X',
            'precision': 6,
            'default': 0.31
        },
        {
            'attr': 'cs_greenY',
            'type': 'float',
            'name': 'Green Y',
            'precision': 6,
            'default': 0.595
        },
        {
            'attr': 'cs_blueX',
            'type': 'float',
            'name': 'Blue X',
            'precision': 6,
            'default': 0.155
        },
        {
            'attr': 'cs_blueY',
            'type': 'float',
            'name': 'Blue Y',
            'precision': 6,
            'default': 0.07
        },

        # Camera Response Functions
        {
            'attr': 'crf_label',
            'type': 'text',
            'name': 'Film Response Function',
        },
        {
            'attr': 'use_crf',
            'type': 'enum',
            'name': 'Use Film Response',
            'default': 'none',
            'items': [
                ('none', 'None', 'Don\'t use a Film Response'),
                ('file', 'File', 'Load a Film Response from file'),
                ('preset', 'Preset', 'Use a built-in Film Response Preset'),
            ],
            'expand': True
        },
        {
            'type': 'ef_callback',
            'attr': 'crf_preset_menu',
            'method': 'draw_crf_preset_menu',
        },
        {
            'attr': 'crf_file',
            'type': 'string',
            'subtype': 'FILE_PATH',
            'name': 'Film Reponse File',
            'default': '',
        },
        {
            'attr': 'crf_preset',
            'type': 'string',
            'name': 'Film Reponse Preset',
            'default': 'Film Response Preset',
        },
    ]


class colorspace_presets(object):
    class sRGB(object):
        gamma = 2.2  # This is still approximate
        cs_whiteX = 0.314275
        cs_whiteY = 0.329411
        cs_redX = 0.63
        cs_redY = 0.34
        cs_greenX = 0.31
        cs_greenY = 0.595
        cs_blueX = 0.155
        cs_blueY = 0.07

    class romm_rgb(object):
        gamma = 1.8
        cs_whiteX = 0.346
        cs_whiteY = 0.359
        cs_redX = 0.7347
        cs_redY = 0.2653
        cs_greenX = 0.1596
        cs_greenY = 0.8404
        cs_blueX = 0.0366
        cs_blueY = 0.0001

    class adobe_rgb_98(object):
        gamma = 2.2
        cs_whiteX = 0.313
        cs_whiteY = 0.329
        cs_redX = 0.64
        cs_redY = 0.34
        cs_greenX = 0.21
        cs_greenY = 0.71
        cs_blueX = 0.15
        cs_blueY = 0.06

    class apple_rgb(object):
        gamma = 1.8  # TODO: verify
        cs_whiteX = 0.313
        cs_whiteY = 0.329
        cs_redX = 0.625
        cs_redY = 0.34
        cs_greenX = 0.28
        cs_greenY = 0.595
        cs_blueX = 0.155
        cs_blueY = 0.07

    class ntsc_1953(object):
        gamma = 2.2  # TODO: verify
        cs_whiteX = 0.31
        cs_whiteY = 0.316
        cs_redX = 0.67
        cs_redY = 0.33
        cs_greenX = 0.21
        cs_greenY = 0.71
        cs_blueX = 0.14
        cs_blueY = 0.08

    class ntsc_1979(object):
        gamma = 2.2  # TODO: verify
        cs_whiteX = 0.313
        cs_whiteY = 0.329
        cs_redX = 0.63
        cs_redY = 0.34
        cs_greenX = 0.31
        cs_greenY = 0.595
        cs_blueX = 0.155
        cs_blueY = 0.07

    class pal_secam(object):
        gamma = 2.8
        cs_whiteX = 0.313
        cs_whiteY = 0.329
        cs_redX = 0.64
        cs_redY = 0.33
        cs_greenX = 0.29
        cs_greenY = 0.6
        cs_blueX = 0.15
        cs_blueY = 0.06

    class cie_e(object):
        gamma = 2.2
        cs_whiteX = 0.333
        cs_whiteY = 0.333
        cs_redX = 0.7347
        cs_redY = 0.2653
        cs_greenX = 0.2738
        cs_greenY = 0.7174
        cs_blueX = 0.1666
        cs_blueY = 0.0089


@PBRTv3Addon.addon_register_class
class pbrtv3_tonemapping(declarative_property_group):
    """
    Storage class for PBRTv3 ToneMapping settings.
    """

    ef_attach_to = ['pbrtv3_film']

    controls = [
        'tm_label',
        'type',

        # Reinhard
        ['reinhard_prescale', 'reinhard_postscale', 'reinhard_burn'],

        # Contrast
        'ywa',

        # Bloom
        'usebloom',
        ['bloom_radius', 'bloom_weight'],

        # Glare
        'useglare',
        ['glare_amount', 'glare_radius'],
        ['glare_blades', 'glare_threshold'],
        'glare_lashes_filename',
        'glare_pupil_filename',

        # Vignetting
        'usevignetting',
        ['vignetting_scale'],

        # Abberation
        'useabberation',
        ['abberation_amount'],
    ]

    visibility = {
        # Reinhard
        'reinhard_prescale': {'type': 'reinhard'},
        'reinhard_postscale': {'type': 'reinhard'},
        'reinhard_burn': {'type': 'reinhard'},

        # Linear
        # all params are taken from camera/colorspace settings

        # Contrast
        'ywa': {'type': 'contrast'},

        'bloom_radius': {'usebloom': True},
        'bloom_weight': {'usebloom': True},
        'glare_amount': {'useglare': True},
        'glare_radius': {'useglare': True},
        'glare_blades': {'useglare': True},
        'glare_threshold': {'useglare': True},
        'glare_lashes_filename': {'useglare': True},
        'glare_pupil_filename': {'useglare': True},
        'vignetting_scale': {'usevignetting': True},
        'abberation_amount': {'useabberation': True},
    }

    properties = [
        {
            'attr': 'tm_label',
            'type': 'text',
            'name': 'Tonemapping'
        },
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Tonemapper',
            'description': 'Choose tonemapping type',
            'default': 'autolinear',
            'items': [
                ('reinhard', 'Reinhard', 'Reinhard non-linear tonemapping'),
                ('linear', 'Linear (manual)', 'Linear tonemapping using camera controls'),
                ('autolinear', 'Linear (auto-exposure)', 'Simple auto-exposure'),
                ('contrast', 'Contrast', 'Scaleable contrast-based tonemapping'),
                ('maxwhite', 'Maxwhite', 'Set brightest pixel as RGB 1.0'),
                ('falsecolors', 'False Colors', 'Convert image to a false color readout of irradiance levels')
            ]
        },

        # Reinhard
        {
            'type': 'float',
            'attr': 'reinhard_prescale',
            'name': 'Pre',
            'description': 'Reinhard Pre-Scale factor',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 25.0,
            'soft_max': 25.0,
        },
        {
            'type': 'float',
            'attr': 'reinhard_postscale',
            'name': 'Post',
            'description': 'Reinhard Post-Scale factor',
            'default': 1.2,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 25.0,
            'soft_max': 25.0,
        },
        {
            'type': 'float',
            'attr': 'reinhard_burn',
            'name': 'Burn',
            'description': 'Reinhard Burn factor',
            'default': 6.0,
            'min': 0.01,
            'soft_min': 0.01,
            'max': 25.0,
            'soft_max': 25.0,
        },

        # Contrast
        {
            'type': 'float',
            'attr': 'ywa',
            'name': 'Ywa',
            'description': 'World adaption luminance',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 2e5,
            'soft_max': 2e5
        },

        {
            'type': 'bool',
            'attr': 'usebloom',
            'name': 'Bloom',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'bloom_radius',
            'name': 'Radius',
            'description': 'Bloom radius as a fraction of the largest image dimension',
            'subtype': 'FACTOR',
            'default': 0.07,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },
        {
            'type': 'float',
            'attr': 'bloom_weight',
            'name': 'Amount',
            'description': 'Amount of bloom to add to the image',
            'subtype': 'FACTOR',
            'default': 0.25,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },

        {
            'type': 'bool',
            'attr': 'useglare',
            'name': 'Glare',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'glare_amount',
            'name': 'Amount',
            'description': 'Amount of glare to add to the image',
            'subtype': 'FACTOR',
            'default': 0.03,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },
        {
            'type': 'float',
            'attr': 'glare_radius',
            'name': 'Radius',
            'description': 'Glare radius as a fraction of the largest image dimension',
            'subtype': 'FACTOR',
            'default': 0.03,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },
        {
            'type': 'int',
            'attr': 'glare_blades',
            'name': 'Blades',
            'description': 'Number of blades in diaphragm',
            'default': 3,
            'min': 3,
            'soft_min': 3,
            'max': 30,
            'soft_max': 30
        },
        {
            'type': 'float',
            'attr': 'glare_threshold',
            'name': 'Threshold',
            'description': 'Glare threshold factor relative to max pixel intensity',
            'subtype': 'FACTOR',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },
        {
            'type': 'string',
            'attr': 'glare_lashes_filename',
            'name': 'Eyelashes map',
            'description': 'For obstacle-based glare, map of eyelashes/obstacles',
            'subtype': 'FILE_PATH',
        },
        {
            'type': 'string',
            'attr': 'glare_pupil_filename',
            'name': 'Pupil mask',
            'description': 'For obstacle-based glare, pupil/diaphragm mask',
            'subtype': 'FILE_PATH',
        },

        {
            'type': 'bool',
            'attr': 'usevignetting',
            'name': 'Vignetting',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'vignetting_scale',
            'name': 'Scale',
            'description': 'Vignetting scale as fraction of the image dimensions',
            'subtype': 'FACTOR',
            'default': 0.4,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },

        {
            'type': 'bool',
            'attr': 'useabberation',
            'name': 'Abberation',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'abberation_amount',
            'name': 'Amount',
            'description': 'Abberation amount as fraction of the image dimensions',
            'subtype': 'FACTOR',
            'default': 0.005,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0
        },
    ]

    def get_paramset(self):
        cam = PBRTv3Manager.CurrentScene.camera.data
        params = ParamSet()
        # params.add_string('tonemapkernel', self.type)

        if self.type == 'reinhard':
            params.add_float('reinhard_prescale', self.reinhard_prescale)
            params.add_float('reinhard_postscale', self.reinhard_postscale)
            params.add_float('reinhard_burn', self.reinhard_burn)

        if self.type == 'linear':
            params.add_float('linear_sensitivity', cam.pbrtv3_camera.sensitivity)
            params.add_float('linear_exposure', cam.pbrtv3_camera.exposure_time())
            params.add_float('linear_fstop', cam.pbrtv3_camera.fstop)
            params.add_float('linear_gamma', cam.pbrtv3_camera.pbrtv3_film.get_gamma())

        if self.type == 'contrast':
            params.add_float('contrast_ywa', self.ywa)

        if self.usebloom:
            params.add_bool('bloom_enabled', True)
            params.add_float('bloom_radius', self.bloom_radius)
            params.add_float('bloom_weight', self.bloom_weight)

        # Glare
        if self.useglare:
            params.add_bool('glare_enabled', True)
            params.add_float('glare_amount', self.glare_amount)
            params.add_float('glare_radius', self.glare_radius)
            params.add_integer('glare_blades', self.glare_blades)
            params.add_float('glare_threshold', self.glare_threshold)
            params.add_string('glarelashesfilename', self.glare_lashes_filename)
            params.add_string('glarepupilfilename', self.glare_pupil_filename)

        # Vignetting
        if self.usevignetting:
            params.add_bool('vignetting_enabled', True)
            params.add_float('vignetting_scale', self.vignetting_scale)

        # Abberation
        if self.useabberation:
            params.add_bool('abberation_enabled', True)
            params.add_float('abberation_amount', self.abberation_amount)

        return params
