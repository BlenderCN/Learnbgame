# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche (BYOB)
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

import bpy

from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_AND as A, Logic_OR as O

from .. import PBRTv3Addon


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
class IMAGEPIPELINE_OT_set_pbrtv3_crf(bpy.types.Operator):
    bl_idname = 'imagepipeline.set_pbrtv3_crf'
    bl_label = 'Set PBRTv3 Film Response Function'

    preset_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        camera_data = context.camera if hasattr(context, 'camera') else context.scene.camera.data
        return camera_data.pbrtv3_camera and camera_data.pbrtv3_camera.luxcore_imagepipeline

    def execute(self, context):
        camera_data = context.camera if hasattr(context, 'camera') else context.scene.camera.data
        camera_data.pbrtv3_camera.luxcore_imagepipeline.crf_preset = self.properties.preset_name

        camera_data.update_tag()

        return {'FINISHED'}

@PBRTv3Addon.addon_register_class
class IMAGEPIPELINE_MT_pbrtv3_crf(bpy.types.Menu):
    bl_label = 'CRF Preset'
    bl_description = 'Simulate analog film'

    # Flat-list menu system
    def draw(self, context):
        lt = self.layout.row()

        for i, crf_name in enumerate(sorted(crf_preset_names)):
            # Create a new column every 20 items
            if i % 20 == 0:
                cl = lt.column()

            op = cl.operator('IMAGEPIPELINE_OT_set_pbrtv3_crf', text=crf_name)
            op.preset_name = crf_name

@PBRTv3Addon.addon_register_class
class luxcore_imagepipeline(declarative_property_group):
    """
    Storage class for PBRTv3Core imagepipeline settings.
    """
    
    ef_attach_to = ['pbrtv3_camera']
    
    alert = {}

    controls = [
        # Output switcher
        'output_switcher_pass',
        'transparent_film',
        ['contour_scale', 'contour_range'],
        ['contour_steps', 'contour_zeroGridSize'],
        # Tonemapper
        'label_tonemapper_type',
        'tonemapper_type',
        ['use_auto_linear', 'linear_scale'],
        'label_camera_settings_help',
        ['reinhard_prescale', 'reinhard_postscale', 'reinhard_burn'],
        # Postpro plugin label
        'label_postpro',
        # Bloom
        'use_bloom',
        ['bloom_radius', 'bloom_weight'],
        # Color aberration
        ['use_color_aberration', 'color_aberration_amount'],
        # Vignetting
        ['use_vignetting', 'vignetting_scale'],
        # Film response
        'crf_label',
        'crf_type',
        'crf_preset_menu',
        'crf_file',
        # Background image
        'label_compositing',
        ['use_background_image', 'background_camera_view_only'],
        'background_image',
        'background_image_gamma',
        # Mist
        ['use_mist', 'mist_excludebackground'],
        ['mist_color', 'mist_amount'],
        ['mist_startdistance', 'mist_enddistance'],
        # Intervals
        'label_intervals',
        #['writeinterval_png', 'writeinterval_flm'],
        'displayinterval',
        'fast_initial_preview',
        'viewport_interval',
    ]
    
    visibility = {
        'contour_scale': {'output_switcher_pass': 'IRRADIANCE'},
        'contour_range': {'output_switcher_pass': 'IRRADIANCE'},
        'contour_steps': {'output_switcher_pass': 'IRRADIANCE'},
        'contour_zeroGridSize': {'output_switcher_pass': 'IRRADIANCE'},
        'label_camera_settings_help': {'tonemapper_type': 'TONEMAP_LUXLINEAR'},
        'use_auto_linear': {'tonemapper_type': 'TONEMAP_LINEAR'},
        'linear_scale': {'tonemapper_type': 'TONEMAP_LINEAR'},
        'reinhard_prescale': {'tonemapper_type': 'TONEMAP_REINHARD02'},
        'reinhard_postscale': {'tonemapper_type': 'TONEMAP_REINHARD02'},
        'reinhard_burn': {'tonemapper_type': 'TONEMAP_REINHARD02'},
        'bloom_radius': {'use_bloom': True},
        'bloom_weight': {'use_bloom': True},
        'color_aberration_amount': {'use_color_aberration': True},
        'vignetting_scale': {'use_vignetting': True},
        'crf_preset_menu': {'crf_type': 'PRESET'},
        'crf_file': {'crf_type': 'FILE'},
        'background_image': {'use_background_image': True},
        'background_image_gamma': {'use_background_image': True},
        'background_camera_view_only': {'use_background_image': True},
        'mist_excludebackground': {'use_mist': True},
        'mist_color': {'use_mist': True},
        'mist_amount': {'use_mist': True},
        'mist_startdistance': {'use_mist': True},
        'mist_enddistance': {'use_mist': True},
    }

    def update_background_image(self, context):
        # Enable alpha AOV so the background image plugin works
        if not context.scene.pbrtv3_channels.ALPHA and self.use_background_image:
            context.scene.pbrtv3_channels.ALPHA = True

    def update_mist(self, context):
        # Enable depth AOV so the mist plugin works
        if not context.scene.pbrtv3_channels.DEPTH and self.use_mist:
            context.scene.pbrtv3_channels.DEPTH = True

    properties = [
        # Output switcher
        {
            'type': 'enum',
            'attr': 'output_switcher_pass',
            'name': 'Input Pass',
            'description': 'Pass to use as imagepipeline input',
            'default': 'disabled',
            'items': [
                ('disabled', 'RGB (Default)', 'RGB colors (beauty/combined pass)'),
                ('ALPHA', 'Alpha', ''),
                ('MATERIAL_ID', 'Material ID', ''),
                ('OBJECT_ID', 'Object ID', ''),
                ('EMISSION', 'Emission', ''),
                ('DIRECT_DIFFUSE', 'Direct Diffuse', ''),
                ('DIRECT_GLOSSY', 'Direct Glossy', ''),
                ('INDIRECT_DIFFUSE', 'Indirect Diffuse', ''),
                ('INDIRECT_GLOSSY', 'Indirect Glossy', ''),
                ('INDIRECT_SPECULAR', 'Indirect Specular', ''),
                ('DEPTH', 'Depth', ''),
                ('POSITION', 'Position', ''),
                ('SHADING_NORMAL', 'Shading Normal', ''),
                ('GEOMETRY_NORMAL', 'Geometry Normal', ''),
                ('UV', 'UV', ''),
                ('DIRECT_SHADOW_MASK', 'Direct Shadow Mask', ''),
                ('INDIRECT_SHADOW_MASK', 'Indirect Shadow Mask', ''),
                ('RAYCOUNT', 'Raycount', ''),
                ('IRRADIANCE', 'Irradiance', '')
            ]
        },
        {
            'type': 'bool',
            'attr': 'transparent_film',
            'name': 'Transparent Film',
            'description': 'Make the world background transparent',
            'default': False,
        },
        # Contour lines settings (only for IRRADIANCE pass)
        {
            'type': 'float',
            'attr': 'contour_scale',
            'name': 'Scale',
            'description': 'Scale',
            'default': 179.0,
            'min': 0.0,
            'soft_min': 0.0,
            'soft_max': 1000.0
        },
        {
            'type': 'float',
            'attr': 'contour_range',
            'name': 'Range',
            'description': 'Max range of irradiance values (unit: lux), minimum is always 0',
            'default': 100.0,
            'min': 0.0,
            'soft_min': 0.0,
            'soft_max': 1000.0
        },
        {
            'type': 'int',
            'attr': 'contour_steps',
            'name': 'Steps',
            'description': 'Number of steps to draw in interval range',
            'default': 8,
            'min': 0,
            'soft_min': 2,
            'soft_max': 50
        },
        {
            'type': 'int',
            'attr': 'contour_zeroGridSize',
            'name': 'Grid Size',
            'description': 'size of the black grid to draw on image where irradiance values are not avilable '
                           '(-1 => no grid, 0 => all black, >0 => size of the black grid)',
            'default': 8,
            'min': -1,
            'soft_min': -1,
            'soft_max': 20
        },
        # Tonemapper
        {
            'type': 'text',
            'attr': 'label_tonemapper_type',
            'name': 'Tonemapper:',
        },
        {
            'type': 'enum',
            'attr': 'tonemapper_type',
            'name': 'Tonemapper',
            'description': 'The tonemapper converts the image from HDR to LDR',
            'default': 'TONEMAP_LINEAR',
            'items': [
                ('TONEMAP_LINEAR', 'Linear', 'Brightness is controlled by the scale value, can be set to auto-detect '
                                             'optimal brightness'),
                ('TONEMAP_LUXLINEAR', 'Camera Settings', 'Use camera settings (ISO, f-stop and shuttertime)'),
                ('TONEMAP_REINHARD02', 'Reinhard', 'Non-linear tonemapper that adapts to the image brightness'),
            ],
            'expand': True
        },
        {
            'type': 'text',
            'attr': 'label_camera_settings_help',
            'name': 'Brightness controlled by f/stop, ISO and exposure',
            'icon': 'INFO',
        },
        # Linear tonemapper settings
        {
            'type': 'bool',
            'attr': 'use_auto_linear',
            'name': 'Auto',
            'description': 'Auto-detect the optimal image brightness',
            'default': True
        },
        {
            'type': 'float',
            'attr': 'linear_scale',
            'name': 'Gain',
            'description': 'Brightness multiplier',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.00001,
            'soft_max': 100.0,
            'step': 1.0
        },
        # Reinhard tonemapper settings
        {
            'type': 'float',
            'attr': 'reinhard_prescale',
            'name': 'Pre',
            'description': 'Reinhard Pre-Scale factor',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 25.0,
            'soft_max': 25.0
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
            'soft_max': 25.0
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
            'soft_max': 25.0
        },
        # Postpro label
        {
            'attr': 'label_postpro',
            'type': 'text',
            'name': 'Lens Effects:',
        },
        # Bloom
        {
            'type': 'bool',
            'attr': 'use_bloom',
            'name': 'Bloom',
            'description': 'Apply bloom filter to the image',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'bloom_radius',
            'name': 'Radius',
            'description': 'Size of the bloom effect in percent of the image size',
            'default': 7.0,
            'min': 0.1,
            'max': 100.0,
            'precision': 1,
            'subtype': 'PERCENTAGE',
            'slider': True,
        },
        {
            'type': 'float',
            'attr': 'bloom_weight',
            'name': 'Strength',
            'description': 'Strength of the bloom effect (a linear mix factor)',
            'default': 25.0,
            'min': 0.0,
            'max': 100.0,
            'precision': 1,
            'subtype': 'PERCENTAGE',
            'slider': True,
        },
        # Color aberration
        {
            'type': 'bool',
            'attr': 'use_color_aberration',
            'name': 'Color Aberration',
            'description': 'Shift red and blue channels near the image edges',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'color_aberration_amount',
            'name': 'Amount',
            'description': 'Strength of the effect',
            'default': 0.005,
            'min': 0.0,
            'soft_max': 0.1,
            'max': 1.0,
            'slider': True,
        },
        # Vignetting
        {
            'type': 'bool',
            'attr': 'use_vignetting',
            'name': 'Vignetting',
            'description': 'Darken the corners of the image',
            'default': False
        },
        {
            'type': 'float',
            'attr': 'vignetting_scale',
            'name': 'Amount',
            'description': 'Strength of the effect',
            'default': 0.4,
            'min': 0.0,
            'soft_max': 0.6,
            'max': 1.0,
            'slider': True,
        },
        # Camera/Film response function (crf)
        {
            'attr': 'crf_label',
            'type': 'text',
            'name': 'Analog Film Simulation:',
        },
        {
            'type': 'enum',
            'attr': 'crf_type',
            'name': 'test',
            'description': 'CRF data to use',
            'default': 'NONE',
            'items': [
                ('NONE', 'None', ''),
                ('PRESET', 'Preset', 'Choose a CRF profile from a list of built-in presets'),
                ('FILE', 'File', 'Choose a CRF file'),
            ],
            'expand': True
        },
        {
            'type': 'ef_callback',
            'attr': 'crf_preset_menu',
            'method': 'draw_crf_preset_menu'
        },
        {
            'attr': 'crf_preset',
            'type': 'string',
            'name': 'Film Reponse Preset',
            'default': 'None'
        },
        {
            'attr': 'crf_file',
            'type': 'string',
            'name': '',
            'description': 'Path to the external .crf file',
            'default': '',
            'subtype': 'FILE_PATH',
        },
        # Background image
        {
            'attr': 'label_compositing',
            'type': 'text',
            'name': 'Compositing:',
        },
        {
            'type': 'bool',
            'attr': 'use_background_image',
            'name': 'Background Image',
            'description': 'Use a background image (requires alpha pass). The image will be stretched to fit the film size.',
            'default': False,
            'update': update_background_image
        },
        {
            'type': 'bool',
            'attr': 'background_camera_view_only',
            'name': 'Camera View Only',
            'description': 'Only use the background image when in camera mode. Only applies to the viewport render',
            'default': False,
        },
        {
            'attr': 'background_image',
            'type': 'string',
            'subtype': 'FILE_PATH',
            'name': 'Path',
            'description': 'Path to the image file on disk',
            'default': ''
        },
        {
            'type': 'float',
            'attr': 'background_image_gamma',
            'name': 'Gamma',
            'description': 'Gamma value of the image',
            'default': 2.2,
            'min': 0.0,
            'soft_min': 1.0,
            'max': 5.0,
        },
        # Mist
        {
            'type': 'bool',
            'attr': 'use_mist',
            'name': 'Mist',
            'description': '',
            'default': False,
            'update': update_mist
        },
        {
            'type': 'float_vector',
            'subtype': 'COLOR',
            'attr': 'mist_color',
            'name': '',
            'description': 'Mist color',
            'default': (0.3, 0.4, 0.55),
            'min': 0,
            'max': 1,
        },
        {
            'type': 'float',
            'attr': 'mist_amount',
            'name': 'Amount',
            'description': 'Strength of the mist overlay',
            'default': 0.3,
            'min': 0,
            'max': 1,
            'slider': True,
        },
        {
            'type': 'float',
            'subtype': 'DISTANCE',
            'attr': 'mist_startdistance',
            'name': 'Start',
            'description': 'Distance from the camera where the mist starts to be visible',
            'default': 100,
            'min': 0,
        },
        {
            'type': 'float',
            'subtype': 'DISTANCE',
            'attr': 'mist_enddistance',
            'name': 'End',
            'description': 'Distance from the camera where the mist is at full strength',
            'default': 1000,
            'min': 0,
        },
        {
            'type': 'bool',
            'attr': 'mist_excludebackground',
            'name': 'Exclude Background',
            'description': 'Disable mist over background parts of the image (where distance = infinity)',
            'default': True,
        },
        # Update and save intervals
        {
            'attr': 'label_intervals',
            'type': 'text',
            'name': 'Update Intervals:',
        },
        {
            'type': 'int',
            'attr': 'displayinterval',
            'name': 'Preview Interval (s)',
            'description': 'Period for updating rendering on screen (seconds)',
            'default': 10,
            'min': 1,
            'soft_min': 3
        },
        {
            'type': 'bool',
            'attr': 'fast_initial_preview',
            'name': 'Fast Initial Preview',
            'description': 'Update the image continuously for the first 15 seconds of the rendering. Not used when '
                           'rendering animations',
            'default': True
        },
        {
            'type': 'int',
            'attr': 'viewport_interval',
            'name': 'Viewport Display Interval (ms)',
            'description': 'Period for updating the viewport render (milliseconds)',
            'default': 100,
            'min': 5,
            'soft_min': 50
        },
    ]
