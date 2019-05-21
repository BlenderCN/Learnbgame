# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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
from ..extensions_framework.validate import Logic_AND as A

from .. import LuxRenderAddon


# Valid CRF preset names (case sensitive):
# See lux/core/cameraresponse.cpp to keep this up to date
crf_preset_names = [s.strip() for s in
                    """None
                    Advantix_100CD
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

@LuxRenderAddon.addon_register_class
class IMAGEPIPELINE_OT_set_luxrender_crf(bpy.types.Operator):
    bl_idname = 'imagepipeline.set_luxrender_crf'
    bl_label = 'Set LuxRender Film Response Function'

    preset_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.camera.luxrender_camera and \
               context.camera.luxrender_camera.luxcore_imagepipeline_settings

    def execute(self, context):
        context.camera.luxrender_camera.luxcore_imagepipeline_settings.crf_preset = self.properties.preset_name
        return {'FINISHED'}

@LuxRenderAddon.addon_register_class
class IMAGEPIPELINE_MT_luxrender_crf(bpy.types.Menu):
    bl_label = 'CRF Preset'
    bl_description = 'Simulate analog film'

    # Flat-list menu system
    def draw(self, context):
        lt = self.layout.row()

        for i, crf_name in enumerate(sorted(crf_preset_names)):
            # Create a new column every 20 items
            if i % 20 == 0:
                cl = lt.column()

            op = cl.operator('IMAGEPIPELINE_OT_set_luxrender_crf', text=crf_name)
            op.preset_name = crf_name

@LuxRenderAddon.addon_register_class
class luxcore_imagepipeline_settings(declarative_property_group):
    """
    Storage class for LuxCore imagepipeline settings.
    """
    
    ef_attach_to = ['luxrender_camera']
    
    alert = {}

    controls = [
        'advanced',
        # Output switcher
        ['label_output_switcher', 'output_switcher_pass'],
        ['contour_scale', 'contour_range'], 
        ['contour_steps', 'contour_zeroGridSize'],
        # Tonemapper
        ['label_tonemapper', 'tonemapper_type'],
        'linear_scale',
        ['reinhard_prescale', 'reinhard_postscale', 'reinhard_burn'],
        # Film response
        'crf_label',
        'crf_preset_menu',
        # Intervals
        #'spacer_intervals',
        'label_intervals',
        #['writeinterval_png', 'writeinterval_flm'],
        'displayinterval',
    ]
    
    visibility = {
        'label_output_switcher': {'advanced': True},
        'output_switcher_pass': {'advanced': True},
        'contour_scale': A([{'output_switcher_pass': 'IRRADIANCE'}, {'advanced': True}]),
        'contour_range': A([{'output_switcher_pass': 'IRRADIANCE'}, {'advanced': True}]),
        'contour_steps': A([{'output_switcher_pass': 'IRRADIANCE'}, {'advanced': True}]),
        'contour_zeroGridSize': A([{'output_switcher_pass': 'IRRADIANCE'}, {'advanced': True}]),
        'linear_scale': {'tonemapper_type': 'TONEMAP_LINEAR'},
        'reinhard_prescale': {'tonemapper_type': 'TONEMAP_REINHARD02'},
        'reinhard_postscale': {'tonemapper_type': 'TONEMAP_REINHARD02'},
        'reinhard_burn': {'tonemapper_type': 'TONEMAP_REINHARD02'},
    }

    properties = [
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'description': 'Configure advanced settings',
            'default': False,
            'save_in_preset': True
        },
        # Output switcher
        {
            'type': 'text',
            'attr': 'label_output_switcher',
            'name': 'Input Pass:',
        },
        {
            'type': 'enum',
            'attr': 'output_switcher_pass',
            'name': '',
            'description': 'Pass to use as imagepipeline input',
            'default': 'disabled',
            'items': [
                ('disabled', 'RGB (Default)', 'RGB colors (beauty/combined pass)'),
                ('ALPHA', 'Alpha', ''),
                ('MATERIAL_ID', 'Material ID', ''),
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
            ],
            'save_in_preset': True
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
            'soft_max': 1000.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'contour_range',
            'name': 'Range',
            'description': 'Max range of irradiance values (unit: lux), minimum is always 0',
            'default': 100.0,
            'min': 0.0,
            'soft_min': 0.0,
            'soft_max': 1000.0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'contour_steps',
            'name': 'Steps',
            'description': 'Number of steps to draw in interval range',
            'default': 8,
            'min': 0,
            'soft_min': 2,
            'soft_max': 50,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'contour_zeroGridSize',
            'name': 'Grid Size',
            'description': 'size of the black grid to draw on image where irradiance values are not avilable (-1 => no grid, 0 => all black, >0 => size of the black grid)',
            'default': 8,
            'min': -1,
            'soft_min': -1,
            'soft_max': 20,
            'save_in_preset': True
        },
        # Tonemapper
        {
            'type': 'text',
            'attr': 'label_tonemapper',
            'name': 'Tonemapper:',
        },
        {
            'type': 'enum',
            'attr': 'tonemapper_type',
            'name': '',
            'description': 'The tonemapper converts the image from HDR to LDR',
            'default': 'TONEMAP_AUTOLINEAR',
            'items': [
                ('TONEMAP_AUTOLINEAR', 'Linear (Auto)', 'Simple auto-exposure'),
                ('TONEMAP_LINEAR', 'Linear', 'Brightness is controlled by the scale value'),
                ('TONEMAP_LUXLINEAR', 'Linear (Camera Settings)', 'Uses camera settings (ISO, f-stop and shuttertime)'),
                ('TONEMAP_REINHARD02', 'Reinhard', 'Non-linear tonemapper that adapts to the image brightness'),
            ],
            'save_in_preset': True
        },
        # Linear tonemapper settings
        {
            'type': 'float',
            'attr': 'linear_scale',
            'name': 'Brightness',
            'description': 'Brightness factor of the image',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.001,
            'soft_max': 100.0,
            'save_in_preset': True
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
            'soft_max': 25.0,
            'save_in_preset': True
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
            'save_in_preset': True
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
            'save_in_preset': True
        },
        # Camera/Film response function (crf)
        {
            'attr': 'crf_label',
            'type': 'text',
            'name': 'Analog Film Simulation:',
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
            'default': 'None',
            'save_in_preset': True
        },
        # Update and save intervals
        {
            'attr': 'spacer_intervals',
            'type': 'text',
            'name': '',
        },
        {
            'attr': 'label_intervals',
            'type': 'text',
            'name': 'Write Intervals:',
        },
        {
            'type': 'int',
            'attr': 'writeinterval_png',
            'name': 'PNG',
            'description': 'Period for writing images to disk (seconds)',
            'default': 180,
            'min': 2,
            'soft_min': 2,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'writeinterval_flm',
            'name': 'FLM',
            'description': 'Period for writing flm files to disk (seconds)',
            'default': 900,
            'min': 2,
            'soft_min': 2,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'displayinterval',
            'name': 'Preview Interval',
            'description': 'Period for updating rendering on screen (seconds)',
            'default': 10,
            'min': 1,
            'soft_min': 3,
            'save_in_preset': True
        },
    ]
