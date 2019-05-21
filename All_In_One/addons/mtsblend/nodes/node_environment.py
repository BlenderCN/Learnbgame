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

import bpy

from bpy.types import Node
from bpy.props import BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, StringProperty, EnumProperty

import mathutils

from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


class mitsuba_environment_node(mitsuba_node):
    bl_width_min = 160
    shader_type_compat = {'WORLD'}
    mitsuba_nodetype = 'ENVIRONMENT'


@MitsubaNodeTypes.register
class MtsNodeEnvironment_constant(mitsuba_environment_node, Node):
    '''Constant Environment node'''
    bl_idname = 'MtsNodeEnvironment_constant'
    bl_label = 'Constant Environment'
    plugin_types = {'constant'}

    def default_values(self, context):
        self.inputs['Radiance'].default_value = (0.1, 0.1, 0.1)

    samplingWeight = FloatProperty(
        name='Sampling weight',
        description='Relative amount of samples to place on this light source (e.g. the "importance")',
        default=1.0,
        min=1e-3,
        max=1e3,
    )

    scale = FloatProperty(
        name='Scale',
        description='Scale factor applied to radiance value.',
        default=1.0,
        min=1e-3,
        max=1e5,
    )

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_radiance', 'name': 'Radiance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketEnvironment', 'name': 'Environment'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'samplingWeight')
        layout.prop(self, 'scale')

    def get_environment_dict(self, export_ctx):
        params = {
            'type': 'constant',
            'id': 'Environment-constant',
            'radiance': self.inputs['Radiance'].get_spectrum_dict(export_ctx, self.scale),
            'samplingWeight': self.samplingWeight,
        }

        return params


@MitsubaNodeTypes.register
class MtsNodeEnvironment_envmap(mitsuba_environment_node, Node):
    '''Envmap Environment node'''
    bl_idname = 'MtsNodeEnvironment_envmap'
    bl_label = 'Environment Map'
    plugin_types = {'envmap'}

    filename = StringProperty(
        subtype='FILE_PATH',
        name='File',
        description='File path',
        default='',
    )

    scale = FloatProperty(
        name='Scale',
        description='Scale factor applied to radiance values from file input.',
        default=1.0,
        min=1e-3,
        max=1e5,
    )

    samplingWeight = FloatProperty(
        name='Sampling weight',
        description='Relative amount of samples to place on this light source (e.g. the "importance")',
        default=1.0,
        min=1e-3,
        max=1e3,
    )

    transform = StringProperty(
        name='Transform',
        description='Select object to take transorm matrix from.',
        default='',
    )

    rotation = FloatVectorProperty(
        subtype='EULER',
        name='Rotation',
        default=(0.0, 0.0, 0.0),
        unit='ROTATION',
    )

    custom_outputs = [
        {'type': 'MtsSocketEnvironment', 'name': 'Environment'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'filename')
        layout.prop(self, 'scale')
        layout.prop(self, 'samplingWeight')

        layout.prop_search(self, 'transform', bpy.data, 'objects')

        if not self.transform:
            layout.prop(self, 'rotation')

    def get_environment_transform(self):
        if self.transform:
            return bpy.data.objects[self.transform].matrix_world.copy()

        else:
            return mathutils.Euler(self.rotation).to_matrix().to_4x4()

    def get_environment_dict(self, export_ctx):
        params = {
            'type': 'envmap',
            'id': 'Environment-envmap',
            'filename': export_ctx.get_export_path(self.filename),
            'scale': self.scale,
            'samplingWeight': self.samplingWeight,
        }

        return params


@MitsubaNodeTypes.register
class MtsNodeEnvironment_sunsky(mitsuba_environment_node, Node):
    '''Sun & Sky Environment node'''
    bl_idname = 'MtsNodeEnvironment_sunsky'
    bl_label = 'Sun & Sky'
    plugin_types = {'sun', 'sky', 'sunsky'}

    def update_visibility(self, context):
        self.inputs['Ground Albedo'].enabled = self.model in {'sun', 'sunsky'}

    model = EnumProperty(
        name='Sky Type',
        items=[
            ('sunsky', 'Sun & Sky', 'sunsky'),
            ('sun', 'Sun Only', 'sun'),
            ('sky', 'Sky Only', 'sky'),
        ],
        default='sunsky',
        update=update_visibility,
    )

    turbidity = FloatProperty(
        name='Turbidity',
        default=3,
        min=1,
        max=10.0,
    )

    samplingWeight = FloatProperty(
        name='Sampling weight',
        description='Relative amount of samples to place on this light source (e.g. the "importance")',
        default=1.0,
        min=1e-3,
        max=1e3,
    )

    position = EnumProperty(
        name='Sun Position',
        items=[
            ('direction', 'Direction', 'direction'),
            ('time', 'Time', 'time'),
        ],
        default='direction',
        update=update_visibility,
    )

    direction = FloatVectorProperty(
        subtype='DIRECTION',
        name='Direction',
        default=(0.0, 0.0, 1.0),
    )

    year = IntProperty(
        name='Year',
        default=2010,
        min=0,
        max=10000,
    )

    month = IntProperty(
        name='Month',
        default=7,
        min=1,
        max=12,
    )

    day = IntProperty(
        name='Day',
        default=10,
        min=1,
        max=31,
    )

    hour = IntProperty(
        name='Hour',
        default=15,
        min=0,
        max=23,
    )

    minute = IntProperty(
        name='Minute',
        default=0,
        min=0,
        max=59,
    )

    second = IntProperty(
        name='Second',
        default=0,
        min=0,
        max=59,
    )

    latitude = FloatProperty(
        name='Latitude',
        default=35.6894,
        min=-90,
        max=90,
    )

    longitude = FloatProperty(
        name='Longitude',
        default=139.6917,
        min=-180,
        max=180,
    )

    timezone = FloatProperty(
        name='Timezone',
        default=9,
        min=-12,
        max=14,
    )

    transform = StringProperty(
        name='Transform',
        description='Select object to take rotation transform matrix from.',
        default='',
    )

    rotation = FloatVectorProperty(
        subtype='EULER',
        name='Rotation',
        default=(0.0, 0.0, 0.0),
        unit='ROTATION',
    )

    advanced = BoolProperty(
        name='Advanced',
        default=False,
    )

    extend = BoolProperty(
        name='Extend',
        description='Extend to the bottom hemisphere (super-unrealistic mode)',
        default=False
    )

    stretch = FloatProperty(
        name='Stretch Sky',
        description='Stretch factor to extend emitter below the horizon, must be in [1,2]. Default{1}, i.e. not used}',
        default=1.0,
        min=1.0,
        max=2.0,
    )

    skyScale = FloatProperty(
        name='Sky Scale',
        description='This parameter can be used to scale the the amount of illumination emitted by the sky emitter.',
        default=1.0,
        min=0.0,
        max=10.0,
    )

    sunScale = FloatProperty(
        name='Sun Scale',
        description='This parameter can be used to scale the the amount of illumination emitted by the sky emitter.',
        default=1.0,
        min=0.0,
        max=10.0,
    )

    sunRadiusScale = FloatProperty(
        name='Sun Radius',
        description='Scale factor to adjust the radius of the sun, while preserving its power. Set to 0 to turn it into a directional light source',
        default=1.0,
        min=0.0,
        max=10.0,
    )

    resolution = IntProperty(
        name='Resolution',
        description='Specifies the horizontal resolution of the precomputed image that is used to represent the sun/sky environment map \default{512, i.e. 512x256}',
        default=512,
        min=128,
        max=4096,
    )

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_groundAlbedo', 'name': 'Ground Albedo'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketEnvironment', 'name': 'Environment'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'model')
        layout.prop(self, 'turbidity')
        layout.prop(self, 'samplingWeight')

        layout.prop(self, 'position')

        if self.position == 'direction':
            layout.prop(self, 'direction', text='')
            row = layout.row()
            row.prop(self, 'direction', text='', expand=True)

        else:
            layout.prop(self, 'year')
            layout.prop(self, 'month')
            layout.prop(self, 'day')
            layout.prop(self, 'hour')
            layout.prop(self, 'minute')
            layout.prop(self, 'second')
            layout.prop(self, 'latitude')
            layout.prop(self, 'longitude')
            layout.prop(self, 'timezone')

        layout.prop_search(self, 'transform', bpy.data, 'objects')

        if not self.transform:
            layout.prop(self, 'rotation')

        icon = 'DISCLOSURE_TRI_DOWN' if self.advanced \
            else 'DISCLOSURE_TRI_RIGHT'
        row = layout.row()
        row.prop(self, "advanced", icon=icon, text='',
                icon_only=True, emboss=False)
        row.label('Advanced Options:')

        if self.advanced:
            if self.model in {'sky', 'sunsky'}:
                layout.prop(self, 'extend')
                layout.prop(self, 'stretch')
                layout.prop(self, 'skyScale')

            if self.model in {'sun', 'sunsky'}:
                layout.prop(self, 'sunScale')
                layout.prop(self, 'sunRadiusScale')

            layout.prop(self, 'resolution')

    def get_environment_transform(self):
        if self.transform:
            return bpy.data.objects[self.transform].matrix_world.copy()

        else:
            return mathutils.Euler(self.rotation).to_matrix().to_4x4()

    def get_environment_dict(self, export_ctx):
        params = {
            'type': self.model,
            'id': 'Environment-%s' % self.model,
            'samplingWeight': self.samplingWeight,
            'turbidity': self.turbidity,
        }

        if self.position == 'direction':
            params.update({
                'sunDirection': self.direction,
            })

        else:
            params.update({
                'year': self.year,
                'month': self.month,
                'day': self.day,
                'hour': float(self.hour),
                'minute': float(self.minute),
                'second': float(self.second),
                'latitude': self.latitude,
                'longitude': self.longitude,
                'timezone': self.timezone,
            })

        if self.model in {'sky', 'sunsky'}:
            params.update({
                'albedo': self.inputs['Ground Albedo'].get_spectrum_dict(export_ctx),
            })

        if self.advanced:
            params.update({'resolution': self.resolution})

            if self.model in {'sky', 'sunsky'}:
                params.update({
                    'stretch': self.stretch,
                    'extend': self.extend,
                })

                if self.model == 'sky':
                    params.update({
                        'scale': self.skyScale
                    })

                elif self.model == 'sunsky':
                    params.update({
                        'skyScale': self.skyScale,
                        'sunScale': self.sunScale,
                        'sunRadiusScale': self.sunRadiusScale
                    })

            elif self.model == 'sun':
                params.update({
                    'scale': self.sunScale,
                    'sunRadiusScale': self.sunRadiusScale
                })

        return params
