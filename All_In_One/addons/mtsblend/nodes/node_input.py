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

from bpy.types import Node, PropertyGroup
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, StringProperty, EnumProperty, CollectionProperty

from .. import MitsubaAddon

from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


class mitsuba_input_node(mitsuba_node):
    bl_width_min = 180
    mitsuba_nodetype = 'INPUT'


@MitsubaNodeTypes.register
class MtsNodeInput_rgb(mitsuba_input_node, Node):
    """RGB spectrum node"""
    bl_idname = 'MtsNodeInput_rgb'
    bl_label = 'RGB'
    shader_type_compat = {'OBJECT', 'WORLD'}
    plugin_types = {'rgb', 'srgb'}

    color_mode = EnumProperty(
        name="Mode",
        description='Color mode.',
        items=[
            ('rgb', 'RGB', 'rgb'),
            ('srgb', 'sRGB', 'srgb'),
        ],
        default='rgb',
    )

    color = FloatVectorProperty(
        subtype='COLOR',
        name='Color',
        description='Color',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )

    gain_r = FloatProperty(
        name='Red Scale',
        description='Scale amount for red value',
        default=1.0,
        min=0.0,
    )

    gain_g = FloatProperty(
        name='Green Scale',
        description='Scale amount for green value',
        default=1.0,
        min=0.0,
    )

    gain_b = FloatProperty(
        name='Blue Scale',
        description='Scale amount for blue value',
        default=1.0,
        min=0.0,
    )

    custom_outputs = [
        {'type': 'MtsSocketSpectrum', 'name': 'Spectrum'},
        {'type': 'MtsSocketColor', 'name': 'Color'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'color_mode')
        col = layout.column()
        col.template_color_picker(self, 'color', value_slider=True)
        col.prop(self, 'color', text='')
        row = layout.row(align=True)
        row.label('RGB Scale:')
        row.prop(self, 'gain_r', text='')
        row.prop(self, 'gain_g', text='')
        row.prop(self, 'gain_b', text='')

    def get_spectrum_dict(self, export_ctx, multiplier=1.0):
        return export_ctx.spectrum({
            'type': self.color_mode,
            'value': [
                self.color.r * self.gain_r * multiplier,
                self.color.g * self.gain_g * multiplier,
                self.color.b * self.gain_b * multiplier
            ],
        })

    def get_color_dict(self, export_ctx):
        return self.get_spectrum_dict(export_ctx)

    def set_from_dict(self, ntree, params):
        if params['type'] == 'srgb':
            self.color_mode == 'srgb'

        else:
            self.color_mode == 'rgb'

        values = [float(x) for x in params['value'].split()]
        gain = max(values)

        if gain <= 1.0:
            self.color = (values[0], values[1], values[2])
            self.gain_r = 1.0
            self.gain_g = 1.0
            self.gain_b = 1.0

        else:
            self.color = (values[0] / gain, values[1] / gain, values[2] / gain)
            self.gain_r = gain
            self.gain_g = gain
            self.gain_b = gain


@MitsubaAddon.addon_register_class
class SpectrumSample(PropertyGroup):
    wavelength = IntProperty(name="Wavelength", default=0, min=0)
    value = FloatProperty(name="Value", default=1.0, min=0.0)


@MitsubaNodeTypes.register
class MtsNodeInput_spectrum(mitsuba_input_node, Node):
    """Spectrum node"""
    bl_idname = 'MtsNodeInput_spectrum'
    bl_label = 'Spectrum'
    shader_type_compat = {'OBJECT', 'WORLD'}
    plugin_types = {'spectrum'}

    def update_items(self, context):
        sample_count = len(self.spectrum_samples) + 1
        diff = self.samples - sample_count

        if diff > 0:
            for n in range(diff):
                self.spectrum_samples.add()

    samples = IntProperty(
        name='Samples',
        description='Amount of Spectrum samples',
        default=1,
        min=1,
        max=40,
        update=update_items
    )

    # First spectrum sample
    wavelength = IntProperty(name="Wavelength", default=0, min=0)
    value = FloatProperty(name="Value", default=1.0, min=0.0)

    # Additional spectrum samples
    spectrum_samples = CollectionProperty(type=SpectrumSample)

    custom_outputs = [
        {'type': 'MtsSocketSpectrum', 'name': 'Spectrum'},
        {'type': 'MtsSocketColor', 'name': 'Color'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'samples')
        row = layout.row()
        row.label('Wavelength:')
        row.label('Value:')
        row = layout.row()
        row.prop(self, 'wavelength', text='')
        row.prop(self, 'value', text='')

        if self.samples > 1:
            for i in range(self.samples - 1):
                try:
                    spd = self.spectrum_samples[i]
                    row = layout.row()
                    row.prop(spd, 'wavelength', text='')
                    row.prop(spd, 'value', text='')

                except:
                    print('Error displaying spectrum samples.')
                    return

    def get_spectrum_dict(self, export_ctx, multiplier=1.0):
        spd_items = [(self.wavelength, self.value * multiplier)]

        if self.samples > 1:
            (lastwlen, lastval) = spd_items[0]

            for i in range(self.samples - 1):
                try:
                    spd = self.spectrum_samples[i]
                    (wlen, val) = (spd.wavelength, spd.value * multiplier)

                    if wlen > lastwlen:
                        spd_items.append((wlen, val))
                        (lastwlen, lastval) = (wlen, val)

                    else:
                        raise Exception()

                except:
                    print('Warning: Inconsistent spectrum samples.')
                    break

        print('Got %d spectrum samples' % len(spd_items))
        print(spd_items)

        if len(spd_items) > 1:
            return export_ctx.spectrum({
                'type': 'spectrum',
                'value': spd_items,
            })

        else:
            return export_ctx.spectrum({
                'type': 'spectrum',
                'value': self.value,
            })

    def get_color_dict(self, export_ctx):
        return self.get_spectrum_dict(export_ctx)

    def set_from_dict(self, ntree, params):
        try:
            items = params['value'].split(', ')
            num_samples = len(items)
            self.samples = num_samples

            spec_sample = items[0].split(':')
            self.wavelength = spec_sample[0]
            self.value = spec_sample[1]

            for i in range(num_samples - 1):
                spec_sample = items[i + 1].split(':')
                spd = self.spectrum_samples[i]
                spd.wavelength = spec_sample[0]
                spd.value = spec_sample[1]

        except:
            pass


@MitsubaNodeTypes.register
class MtsNodeInput_spdfile(mitsuba_input_node, Node):
    """SPD file node"""
    bl_idname = 'MtsNodeInput_spdfile'
    bl_label = 'SPD File'
    shader_type_compat = {'OBJECT', 'WORLD'}
    plugin_types = {'spdfile'}

    filename = StringProperty(
        subtype='FILE_PATH',
        name='File',
        description='File path',
        default='',
    )

    custom_outputs = [
        {'type': 'MtsSocketSpectrum', 'name': 'Spectrum'},
        {'type': 'MtsSocketColor', 'name': 'Color'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'filename')

    def get_spectrum_dict(self, export_ctx, multiplier=1.0):
        return export_ctx.spectrum({
            'type': 'spectrum',
            'value': self.filename,
        })

    def get_color_dict(self, export_ctx):
        return self.get_spectrum_dict(export_ctx)

    def set_from_dict(self, ntree, params):
        if 'filename' in params:
            self.filename == params['filename']


@MitsubaNodeTypes.register
class MtsNodeInput_blackbody(mitsuba_input_node, Node):
    """Blackbody spectrum node"""
    bl_idname = 'MtsNodeInput_blackbody'
    bl_label = 'Blackbody'
    shader_type_compat = {'OBJECT', 'WORLD'}
    plugin_types = {'blackbody'}

    temperature = FloatProperty(name='Temperature', default=5000.0, min=0.0, max=100000.0)
    scale = FloatProperty(name='Scale', default=1.0, min=0.0, max=100000.0)

    custom_outputs = [
        {'type': 'MtsSocketSpectrum', 'name': 'Spectrum'},
        {'type': 'MtsSocketColor', 'name': 'Color'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'temperature')
        layout.prop(self, 'scale')

    def get_spectrum_dict(self, export_ctx, multiplier=1.0):
        return export_ctx.spectrum({
            'type': 'blackbody',
            'temperature': self.temperature,
            'scale': self.scale * 0.001 * multiplier,
        })

    def get_color_dict(self, export_ctx):
        return self.get_spectrum_dict(export_ctx)

    def set_from_dict(self, ntree, params):
        if 'temperature' in params:
            self.temperature == params['temperature']

        if 'scale' in params:
            self.scale == params['scale']


@MitsubaNodeTypes.register
class MtsNodeInput_uvmapping(mitsuba_input_node, Node):
    """UV Mapping node"""
    bl_idname = 'MtsNodeInput_uvmapping'
    bl_label = 'UV Mapping'
    shader_type_compat = {'OBJECT'}
    plugin_types = {'uvmapping'}

    uscale = FloatProperty(name='U Scale', default=1.0, min=-10000.0, max=10000.0)
    vscale = FloatProperty(name='V Scale', default=1.0, min=-10000.0, max=10000.0)
    uoffset = FloatProperty(name='U Offset', default=0.0, min=-10000.0, max=10000.0)
    voffset = FloatProperty(name='V Offset', default=0.0, min=-10000.0, max=10000.0)

    custom_outputs = [
        {'type': 'MtsSocketUVMapping', 'name': 'UV Mapping'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'uscale')
        layout.prop(self, 'vscale')
        layout.prop(self, 'uoffset')
        layout.prop(self, 'voffset')

    def get_uvmapping_dict(self):
        params = {}

        if self.uscale != 1.0 or self.vscale != 1.0:
            params.update({
                'uscale': self.uscale,
                'vscale': self.vscale,
            })

        if self.uoffset != 0.0 or self.voffset != 0.0:
            params.update({
                'uoffset': self.uoffset,
                'voffset': self.voffset,
            })

        return params

    def set_from_dict(self, ntree, params):
        if 'uscale' in params:
            self.uscale = params['uscale']

        if 'vscale' in params:
            self.vscale = params['vscale']

        if 'uoffset' in params:
            self.uoffset = params['uoffset']

        if 'voffset' in params:
            self.voffset = params['voffset']
