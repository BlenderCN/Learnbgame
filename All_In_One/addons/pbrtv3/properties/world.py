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

import bpy

from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O, Logic_AND as A

from .. import PBRTv3Addon
from ..export import ParamSet
from ..export.materials import ExportedTextures
from ..outputs.pure_api import PBRTv3_VERSION
from ..outputs.luxcore_api import UsePBRTv3Core
from ..outputs.luxcore_api import ScenePrefix
from ..properties.material import texture_append_visibility
from ..properties.texture import (
    ColorTextureParameter, FloatTextureParameter, FresnelTextureParameter
)
from ..util import dict_merge


def WorldVolumeParameter(attr, name):
    return [
        {
            'attr': '%s_volume' % attr,
            'type': 'string',
            'name': '%s_volume' % attr,
            'description': '%s_volume' % attr,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': attr,
            'src': lambda s, c: s.scene.pbrtv3_volumes,
            'src_attr': 'volumes',
            'trg': lambda s, c: c.pbrtv3_world,
            'trg_attr': '%s_volume' % attr,
            'name': name,
            'icon': 'MOD_FLUIDSIM'
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_world(declarative_property_group):
    ef_attach_to = ['Scene']

    controls = [
        'default_interior',
        'default_exterior'
    ]

    properties = [
                     {
                         'attr': 'preview_object_size',
                         'type': 'float',
                         'name': 'Preview Object Size',
                         'description': 'Real Size of the Preview Objects Edges or Sphere-Diameter',
                         'min': 0.01,
                         'soft_min': 0.01,
                         'max': 100.0,
                         'soft_max': 100.0,
                         'step': 100,
                         'default': 2.0,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                     }
                 ] + \
                 WorldVolumeParameter('default_interior', 'Default Interior') + \
                 WorldVolumeParameter('default_exterior', 'Default Exterior')


class VolumeDataColorTextureParameter(ColorTextureParameter):
    # texture_collection = 'textures'
    def texture_collection_finder(self):
        def func(s, c):
            return s.world if s.world else s.material  # Look in the current world object for fresnel textures

        return func

    def texture_slot_set_attr(self):
        def func2(s, c):
            return c

        return func2


class VolumeDataFloatTextureParameter(FloatTextureParameter):
    # texture_collection = 'textures'
    def texture_collection_finder(self):
        def func(s, c):
            return s.world if s.world else s.material  # Look in the current world object for fresnel textures

        return func

    def texture_slot_set_attr(self):
        def func2(s, c):
            return c

        return func2


class VolumeDataFresnelTextureParameter(FresnelTextureParameter):
    # texture_collection = 'textures'
    def texture_collection_finder(self):
        def func(s, c):
            return s.world if s.world else s.material  # Look in the current world object for fresnel textures

        return func

    def texture_slot_set_attr(self):
        def func2(s, c):
            return c

        return func2

# Volume related Textures
TFR_IOR = VolumeDataFresnelTextureParameter('fresnel', 'IOR', add_float_value=True, min=0.0, max=25.0, default=1.0)

TC_absorption = VolumeDataColorTextureParameter('absorption', 'Absorption', default=(1.0, 1.0, 1.0))
TC_sigma_a = VolumeDataColorTextureParameter('sigma_a', 'Absorption', default=(1.0, 1.0, 1.0))
TC_sigma_s = VolumeDataColorTextureParameter('sigma_s', 'Scattering', default=(0.0, 0.0, 0.0))
TC_emission = VolumeDataColorTextureParameter('emission', 'Emission Color', default=(1.0, 1.0, 1.0))


def volume_types():
    v_types = [
        ('clear', 'Clear', 'Use for clear/colored glass'),
        ('homogeneous', 'Homogeneous', 'Use for volumes with uniform scattering, e.g. milk, skin, orange juice'),
        ('heterogeneous', 'Heterogeneous', 'Use for volumes with non-uniform scattering, e.g. clouds')
    ]

    return v_types


@PBRTv3Addon.addon_register_class
class pbrtv3_volume_data(declarative_property_group):
    """
    Storage class for PBRTv3 volume data. The
    pbrtv3_volumes object will store 1 or more of
    these in its CollectionProperty 'volumes'.
    """

    ef_attach_to = []  # not attached
    alert = {}

    controls = [
                   'type',
               ] + \
               [
                   'draw_ior_menu',
               ] + \
               TFR_IOR.controls + \
               [
                   'separator'
               ] + \
               TC_absorption.controls + \
               TC_sigma_a.controls + \
               [
                   'depth',
                   'absorption_scale',
                   'separator'
               ] + \
               TC_sigma_s.controls + \
               [
                   'scattering_scale',
                   'separator_asymmetry',
                   'g',
                   'stepsize',
                   'priority',
                   'multiscattering',
                   'use_emission'
               ] + \
               TC_emission.controls + \
               [
                   'gain'
               ]

    visibility = dict_merge(
        {
            'scattering_scale': {'type': O(['homogeneous', 'heterogeneous'])},
            'separator_asymmetry': {'type': O(['homogeneous', 'heterogeneous'])},
            'g': {'type': O(['homogeneous', 'heterogeneous'])},
            'stepsize': {'type': 'heterogeneous'},
            'depth': O([A([{'type': 'clear'}, {'absorption_usecolortexture': False}]),
                        A([{'type': O(['homogeneous', 'heterogeneous'])}, {'sigma_a_usecolortexture': False}])]),
            'priority': lambda: UsePBRTv3Core(),
            'multiscattering': A([{'type': O(['homogeneous', 'heterogeneous'])}, lambda: UsePBRTv3Core()]),
            'gain': A([{'use_emission': True}, lambda: UsePBRTv3Core()])
        },
        TFR_IOR.visibility,
        TC_absorption.visibility,
        TC_sigma_a.visibility,
        TC_sigma_s.visibility,
        TC_emission.visibility
    )

    visibility = texture_append_visibility(visibility, TC_absorption, {'type': 'clear'})
    visibility = texture_append_visibility(visibility, TC_sigma_a, {'type': O(['homogeneous', 'heterogeneous'])})
    visibility = texture_append_visibility(visibility, TC_sigma_s, {'type': O(['homogeneous', 'heterogeneous'])})
    visibility = texture_append_visibility(visibility, TC_emission, {'use_emission': True})

    properties = [
                     {
                         'attr': 'nodetree',
                         'type': 'string',
                         'description': 'Node tree',
                         'name': 'Node Tree',
                         'default': ''
                     },
                     {
                         'type': 'separator',
                         'attr': 'separator'
                     },
                     {
                         'type': 'separator',
                         'attr': 'separator_asymmetry'
                     },
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'enum',
                         'attr': 'type',
                         'name': 'Type',
                         'items': volume_types(),
                         'expand': True,
                         'save_in_preset': True
                     },
                 ] + \
                 TFR_IOR.properties + \
                 TC_absorption.properties + \
                 TC_sigma_a.properties + \
                 TC_sigma_s.properties + \
                 [
                     {
                         'type': 'float',
                         'attr': 'depth',
                         'name': 'Abs. at depth',
                         'description': 'Object will match absorption color at this depth in metres',
                         'default': 1.0,
                         'min': 0.00001,
                         'soft_min': 0.00001,
                         'max': 1000.0,
                         'soft_max': 1000.0,
                         'precision': 6,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'absorption_scale',
                         'name': 'Abs. scale',
                         'description': 'Scale the absorption by this value',
                         'default': 1.0,
                         'min': 0.00001,
                         'soft_min': 0.00001,
                         'max': 1000.0,
                         'soft_max': 1000.0,
                         'precision': 6,
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'scattering_scale',
                         'name': 'Scattering Scale',
                         'description': 'Scattering colour will be multiplied by this value',
                         'default': 1.0,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 100000.0,
                         'soft_max': 100000.0,
                         'precision': 6,
                         'save_in_preset': True
                     },
                     {
                         'type': 'float_vector',
                         'attr': 'g',
                         'name': 'Asymmetry',
                         'description': 'Scattering asymmetry RGB. -1 means backscatter, 0 is isotropic, 1 is '
                                        'forwards scattering',
                         'default': (0.0, 0.0, 0.0),
                         'min': -1.0,
                         'soft_min': -1.0,
                         'max': 1.0,
                         'soft_max': 1.0,
                         'precision': 4,
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'stepsize',
                         'name': 'Step Size',
                         'description': 'Length of ray marching steps, smaller values resolve more detail, but are slower',
                         'default': 0.1,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 100.0,
                         'soft_max': 100.0,
                         'precision': 3,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     },
                     {
                         'type': 'int',
                         'attr': 'priority',
                         'name': 'Volume priority',
                         'description': '[PBRTv3Core only] Volume priority, volumes with higher values get priority if '
                                        'there is overlap',
                         'default': 0,
                         'min': 0,
                         'max': 65535,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'multiscattering',
                         'name': 'Multiscattering',
                         'description': '[PBRTv3Core only] Compute multiple scattering events in this volume (recommended '
                                        'for volumes with high scattering scale)',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_emission',
                         'name': 'Light Emitter',
                         'description': '[PBRTv3Core only] Volume light emission (e.g. for fire)',
                         'default': False,
                         'save_in_preset': True
                     },
                 ]+ \
                 TC_emission.properties + \
                 [
                     {
                         'type': 'float',
                         'attr': 'gain',
                         'name': 'Gain',
                         'description': '[PBRTv3Core only] Multiplier for the emission color',
                         'default': 1.0,
                         'min': 0.00001,
                         'soft_min': 0.00001,
                         'soft_max': 1000.0,
                         'precision': 6,
                         'step': 100.0,
                         'save_in_preset': True
                     },
                 ]


    def api_output(self, lux_context):
        vp = ParamSet()

#        import pydevd
#        pydevd.settrace('localhost', port=9999, stdoutToServer=True, stderrToServer=True)

        def absorption_at_depth_scaled(i):
            # This is copied from the old LuxBlend, I don't pretend to understand it, DH
            depthed = (-math.log(max([(float(i)), 1e-30])) / (self.depth)) * self.absorption_scale * (
                (float(i)) == 1.0 and -1 or 1)
            # print('abs xform: %f -> %f' % (i,depthed))
            return depthed

        if self.type == 'clear':
            vp.update(TFR_IOR.get_paramset(self))
            vp.update(TC_absorption.get_paramset(self, value_transform_function=absorption_at_depth_scaled))

            if self.absorption_usecolortexture and self.absorption_scale != 1.0:

                tex_found = False
                for psi in vp:
                    if psi.type == 'texture' and psi.name == 'absorption':
                        tex_found = True
                        absorption_tex = psi.value

                if tex_found:
                    sv = ExportedTextures.next_scale_value()
                    texture_name = 'absorption_scaled_%i' % sv
                    ExportedTextures.texture(
                        lux_context,
                        texture_name,
                        'color',
                        'scale',
                        ParamSet() \
                        .add_color(
                            'tex1',
                            [self.absorption_scale] * 3
                        ) \
                        .add_texture(
                            'tex2',
                            absorption_tex
                        )
                    )
                    ExportedTextures.export_new(lux_context)
                    # overwrite the absorption tex name with the scaled tex
                    vp.add_texture('absorption', texture_name)

        if self.type == 'homogeneous':
            def scattering_scale(i):
                return i * self.scattering_scale

            vp.update(TFR_IOR.get_paramset(self))
            vp.add_color('g', self.g)
            vp.update(TC_sigma_a.get_paramset(self, value_transform_function=absorption_at_depth_scaled))
            vp.update(TC_sigma_s.get_paramset(self, value_transform_function=scattering_scale))

            if self.sigma_a_usecolortexture and self.absorption_scale != 1.0:
                tex_found = False

                for psi in vp:
                    if psi.type == 'texture' and psi.name == 'sigma_a':
                        tex_found = True
                        sigma_a_tex = psi.value

                if tex_found:
                    sv = ExportedTextures.next_scale_value()
                    texture_name = 'sigma_a_scaled_%i' % sv
                    ExportedTextures.texture(
                        lux_context,
                        texture_name,
                        'color',
                        'scale',
                        ParamSet() \
                        .add_color(
                            'tex1',
                            [self.absorption_scale] * 3
                        ) \
                        .add_texture(
                            'tex2',
                            sigma_a_tex
                        )
                    )

                    ExportedTextures.export_new(lux_context)
                    # overwrite the sigma_a tex name with the scaled tex
                    vp.add_texture('sigma_a', texture_name)

            if self.sigma_s_usecolortexture and self.scattering_scale != 1.0:
                tex_found = False

                for psi in vp:
                    if psi.type == 'texture' and psi.name == 'sigma_s':
                        tex_found = True
                        sigma_s_tex = psi.value

                if tex_found:
                    sv = ExportedTextures.next_scale_value()
                    texture_name = 'sigma_s_scaled_%i' % sv
                    ExportedTextures.texture(
                        lux_context,
                        texture_name,
                        'color',
                        'scale',
                        ParamSet() \
                        .add_color(
                            'tex1',
                            [self.scattering_scale] * 3
                        ) \
                        .add_texture(
                            'tex2',
                            sigma_s_tex
                        )
                    )

                    ExportedTextures.export_new(lux_context)
                    # overwrite the sigma_s tex name with the scaled tex
                    vp.add_texture('sigma_s', texture_name)

        if self.type == 'heterogeneous':
            def scattering_scale(i):
                return i * self.scattering_scale

            vp.update(TFR_IOR.get_paramset(self))
            vp.add_color('g', self.g)
            vp.add_float('stepsize', self.stepsize)
            vp.update(TC_sigma_a.get_paramset(self, value_transform_function=absorption_at_depth_scaled))
            vp.update(TC_sigma_s.get_paramset(self, value_transform_function=scattering_scale))

            if self.sigma_a_usecolortexture and self.absorption_scale != 1.0:
                tex_found = False

                for psi in vp:
                    if psi.type == 'texture' and psi.name == 'sigma_a':
                        tex_found = True
                        sigma_a_tex = psi.value

                if tex_found:
                    sv = ExportedTextures.next_scale_value()
                    texture_name = 'sigma_a_scaled_%i' % sv
                    ExportedTextures.texture(
                        lux_context,
                        texture_name,
                        'color',
                        'scale',
                        ParamSet() \
                        .add_color(
                            'tex1',
                            [self.absorption_scale] * 3
                        ) \
                        .add_texture(
                            'tex2',
                            sigma_a_tex
                        )
                    )
                    ExportedTextures.export_new(lux_context)
                    # overwrite the sigma_a tex name with the scaled tex
                    vp.add_texture('sigma_a', texture_name)

            if self.sigma_s_usecolortexture and self.scattering_scale != 1.0:
                tex_found = False

                for psi in vp:
                    if psi.type == 'texture' and psi.name == 'sigma_s':
                        tex_found = True
                        sigma_s_tex = psi.value

                if tex_found:
                    sv = ExportedTextures.next_scale_value()
                    texture_name = 'sigma_s_scaled_%i' % sv
                    ExportedTextures.texture(
                        lux_context,
                        texture_name,
                        'color',
                        'scale',
                        ParamSet() \
                        .add_color(
                            'tex1',
                            [self.scattering_scale] * 3
                        ) \
                        .add_texture(
                            'tex2',
                            sigma_s_tex
                        )
                    )
                    ExportedTextures.export_new(lux_context)
                    # overwrite the sigma_s tex name with the scaled tex
                    vp.add_texture('sigma_s', texture_name)

        return self.type, vp

    def load_paramset(self, world, ps):
        psi_accept = {
            'g': 'color'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

            if psi['type'].lower() == 'texture':
                # assign the referenced texture to the world
                tex_slot = world.texture_slots.add()
                tex_slot.texture = bpy.data.textures[psi['value']]

        TFR_IOR.load_paramset(self, ps)
        TC_absorption.load_paramset(self, ps)
        TC_sigma_a.load_paramset(self, ps)
        TC_sigma_s.load_paramset(self, ps)

        # reverse the scattering scale factor
        def sct_col_in_range(val):
            return val >= 0.01 and val <= 0.99

        def find_scale(Sr, Sg, Sb):
            scale_val = 100000.0

            # simultaneously scale all abs values to a sensible range
            while not (sct_col_in_range(Sr * scale_val) and sct_col_in_range(Sg * scale_val) and sct_col_in_range(
                        Sb * scale_val)):
                scale_val /= 10

                # bail out at minimum scale if we can't find a perfect solution
                if scale_val < 1e-6:
                    break

            return scale_val

        # get the raw value from the paramset, value assigned via TC_sigma_s.load_paramset
        # will already have been clamped to (0,1)
        sct_col = [0.0, 0.0, 0.0]

        for psi in ps:
            if psi['type'] == 'color' and psi['name'] == 'sigma_s':
                sct_col = psi['value']

        scl_val = find_scale(*sct_col)
        self.scattering_scale = 1 / scl_val
        self.sigma_s_color = [c * scl_val for c in sct_col]

        # reverse the absorption_at_depth process
        def rev_aad_in_range(val):
            abs = math.e ** -val

            return abs >= 0.01 and abs <= 0.99

        def find_depth(Ar, Ag, Ab):
            depth_val = 100000.0

            # simultaneously scale all abs values to a sensible range
            while not (rev_aad_in_range(Ar * depth_val) and rev_aad_in_range(Ag * depth_val) and rev_aad_in_range(
                        Ab * depth_val)):
                depth_val /= 10

                # bail out at minimum depth if we can't find a perfect solution
                if depth_val < 1e-6:
                    break

            return depth_val

        if self.type == 'clear':
            abs_col = [1.0, 1.0, 1.0]

            # get the raw value from the paramset, value assigned via TC_absorption.load_paramset
            # will already have been clamped to (0,1)
            for psi in ps:
                if psi['type'] == 'color' and psi['name'] == 'absorption':
                    abs_col = psi['value']

            self.depth = find_depth(*abs_col)
            self.absorption_color = [math.e ** -(c * self.depth) for c in abs_col]

        if self.type == 'homogeneous':
            abs_col = [1.0, 1.0, 1.0]

            # get the raw value from the paramset, value assigned via TC_sigma_a.load_paramset
            # will already have been clamped to (0,1)

            for psi in ps:
                if psi['type'] == 'color' and psi['name'] == 'sigma_a':
                    abs_col = psi['value']

            self.depth = find_depth(*abs_col)
            self.sigma_a_color = [math.e ** -(c * self.depth) for c in abs_col]


@PBRTv3Addon.addon_register_class
class pbrtv3_volumes(declarative_property_group):
    """
    Storage class for PBRTv3 Material volumes.
    """

    ef_attach_to = ['Scene']

    controls = [
        'volumes_select',
        ['op_vol_add', 'op_vol_rem']
    ]

    visibility = {}

    properties = [
        {
            'type': 'collection',
            'ptype': pbrtv3_volume_data,
            'name': 'volumes',
            'attr': 'volumes',
            'items': []
        },
        {
            'type': 'int',
            'name': 'volumes_index',
            'attr': 'volumes_index',
        },
        {
            'type': 'template_list',
            'name': 'volumes_select',
            'attr': 'volumes_select',
            'trg': lambda sc, c: c.pbrtv3_volumes,
            'trg_attr': 'volumes_index',
            'src': lambda sc, c: c.pbrtv3_volumes,
            'src_attr': 'volumes',
        },
        {
            'type': 'operator',
            'attr': 'op_vol_add',
            'operator': 'luxrender.volume_add',
            'text': 'Add',
            'icon': 'ZOOMIN',
        },
        {
            'type': 'operator',
            'attr': 'op_vol_rem',
            'operator': 'luxrender.volume_remove',
            'text': 'Remove',
            'icon': 'ZOOMOUT',
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_lightgroup_data(declarative_property_group):
    """
    Storage class for PBRTv3 light group settings. The
    pbrtv3_lightgroups object will store 1 or more of
    these in its CollectionProperty 'lightgroups'.
    """

    ef_attach_to = []  # not attached

    controls = [
        # Drawn manually in the UI class
    ]

    properties = [
        {
            'type': 'bool',
            'attr': 'lg_enabled',
            'name': 'Enabled',
            'description': 'Enable this light group',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'show_settings',
            'name': '',
            'description': 'Show multiplier settings',
            'default': True
        },
        {
            'type': 'float',
            'attr': 'gain',
            'name': 'Gain',
            'description': 'Overall gain for this light group',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.01,
            'soft_max': 10 ** 6,
            'step': 1000,
        },
        # Additional PBRTv3Core properties of lightgroups
        {
            'type': 'bool',
            'attr': 'use_temperature',
            'name': 'Temperature:',
            'description': 'Use temperature multiplier',
            'default': False
        },
        {
            'type': 'float', # could be an int but whatever
            'attr': 'temperature',
            'name': 'Kelvin',
            'description': 'Blackbody emission color in Kelvin',
            'min': 1000,
            'max': 10000,
            'default': 4000,
            'precision': 0,
            'step': 10000,
        },
        {
            'type': 'bool',
            'attr': 'use_rgb_gain',
            'name': 'Color:',
            'description': 'Use RGB color multiplier',
            'default': False
        },
        {
            'type': 'float_vector',
            'attr': 'rgb_gain',
            'name': '',
            'description': 'RGB gain',
            'default': (1, 1, 1),
            'min': 0,
            'soft_max': 1,
            'subtype': 'COLOR',
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_lightgroups(declarative_property_group):
    """
    Storage class for PBRTv3 Light Groups.
    """

    ef_attach_to = ['Scene']

    controls = [
        # Drawn manually in ui/render_layers.py
    ]

    properties = [
        {
            'type': 'collection',
            'ptype': pbrtv3_lightgroup_data,
            'name': 'lightgroups',
            'attr': 'lightgroups',
            'items': []
        },
        {
            'type': 'int',
            'name': 'lightgroups_index',
            'attr': 'lightgroups_index',
        },
        {
            'type': 'operator',
            'attr': 'op_lg_add',
            'operator': 'luxrender.lightgroup_add',
        },
        {
            'type': 'bool',
            'attr': 'ignore',
            'name': 'Merge light groups',
            'description': 'Combine all light groups into one. Enable this for final renders, or to decrease RAM usage',
            'default': False
        },
        # Properties of the default lightgroup (PBRTv3Core only)
        {
            'type': 'bool',
            'attr': 'lg_enabled',
            'name': 'Enabled',
            'description': 'Enable this light group',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'show_settings',
            'name': '',
            'description': 'Show multiplier settings',
            'default': True
        },
        {
            'type': 'float',
            'attr': 'gain',
            'name': 'Gain',
            'description': 'Overall gain for this light group',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.01,
            'soft_max': 10 ** 6,
            'step': 1000,
        },
        {
            'type': 'bool',
            'attr': 'use_temperature',
            'name': 'Temperature:',
            'description': 'Use temperature multiplier',
            'default': False
        },
        {
            'type': 'float', # could be an int but whatever
            'attr': 'temperature',
            'name': 'Kelvin',
            'description': 'Blackbody emission color in Kelvin',
            'min': 1000,
            'max': 10000,
            'default': 4000,
            'precision': 0,
            'step': 10000,
        },
        {
            'type': 'bool',
            'attr': 'use_rgb_gain',
            'name': 'Color:',
            'description': 'Use RGB color multiplier',
            'default': False
        },
        {
            'type': 'float_vector',
            'attr': 'rgb_gain',
            'name': '',
            'description': 'RGB gain',
            'default': (1, 1, 1),
            'min': 0,
            'soft_max': 1,
            'subtype': 'COLOR',
        },
    ]

    def is_enabled(self, name):
        if name and name in self.lightgroups:
            return self.lightgroups[name].lg_enabled

        return True


@PBRTv3Addon.addon_register_class
class pbrtv3_materialgroup_data(declarative_property_group):
    """
    Storage class for PBRTv3 material group settings. The
    pbrtv3_materialgroups object will store 1 or more of
    these in its CollectionProperty 'materialgroups'.
    """

    def update_id(self, context):
        """
        Convert the 3x8bit ID to 3xfloat color
        """
        self['color'] = [
            ((self.id & 0xff0000) >> 16) / 255,
            ((self.id & 0xff00) >> 8) / 255,
            (self.id & 0xff) / 255
        ]

    def update_color(self, context):
        """
        Convert 3xfloat color to 3x8bit ID
        """
        r = int(self.color[0] * 255)
        g = int(self.color[1] * 255)
        b = int(self.color[2] * 255)

        self['id'] = (r << 16) + (g << 8) + b

    ef_attach_to = []  # not attached

    controls = [
        # Drawn manually in the UI class
    ]

    properties = [
        # TODO: material override for whole group?
        {
            'type': 'bool',
            'attr': 'show_settings',
            'name': '',
            'description': 'Show settings',
            'default': True
        },
        {
            'type': 'int',
            'attr': 'id',
            'name': 'ID',
            'description': 'Material groups with the same ID will have the same color in the MATERIAL_ID pass. '
                           'The ID is just another representation of the color.',
            'min': 0,
            'max': 0xffffff,
            'default': 0,
            'update': update_id,
        },
        {
            'type': 'float_vector',
            'attr': 'color',
            'name': '',
            'description': 'Color that is used to mask this material in the MATERIAL_ID pass',
            'default': (0, 0, 0),
            'min': 0,
            'max': 1,
            'subtype': 'COLOR',
            'update': update_color,
        },
        {
            'type': 'bool',
            'attr': 'create_MATERIAL_ID_MASK',
            'name': 'B/W mask pass',
            'description': 'Create a black/white mask for this material (additional renderpass)',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'create_BY_MATERIAL_ID',
            'name': 'Masked RGB pass',
            'description': 'Create a pass where objects with this material ID are visible, while the rest of the image '
                           'is black (additional renderpass)',
            'default': False,
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_materialgroups(declarative_property_group):
    """
    Storage class for PBRTv3 Material Groups.
    """

    ef_attach_to = ['Scene']

    controls = [
        # Drawn manually in ui/render_panels.py
    ]

    properties = [
        {
            'type': 'collection',
            'ptype': pbrtv3_materialgroup_data,
            'name': 'materialgroups',
            'attr': 'materialgroups',
            'items': []
        },
        {
            'type': 'int',
            'name': 'materialgroups_index',
            'attr': 'materialgroups_index',
        },
        {
            'type': 'operator',
            'attr': 'op_lg_add',
            'operator': 'luxrender.materialgroup_add',
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_channels(declarative_property_group):
    """
    Storage class for PBRTv3Core AOVs
    """

    ef_attach_to = ['Scene']

    controls = [
        # 'aov_label',
        ['enable_aovs', 'saveToDisk'],
        ['import_into_blender', 'import_compatible'],
        'label_unsupported_engines',
        'spacer',
        'label_info_film',
        'RGB_TONEMAPPED',
        'RGBA_TONEMAPPED',
        'RGB',
        'RGBA',
        'ALPHA',
        'label_info_material',
        'MATERIAL_ID',
        'OBJECT_ID',
        'EMISSION',
        'label_info_directlight',
        ['DIRECT_DIFFUSE', 'normalize_DIRECT_DIFFUSE'],
        ['DIRECT_GLOSSY', 'normalize_DIRECT_GLOSSY'],
        'label_info_indirectlight',
        ['INDIRECT_DIFFUSE', 'normalize_INDIRECT_DIFFUSE'],
        ['INDIRECT_GLOSSY', 'normalize_INDIRECT_GLOSSY'],
        ['INDIRECT_SPECULAR', 'normalize_INDIRECT_SPECULAR'],
        'label_info_geometry',
        ['DEPTH', 'normalize_DEPTH'],
        'POSITION',
        'SHADING_NORMAL',
        'GEOMETRY_NORMAL',
        'UV',
        'label_info_shadow',
        'DIRECT_SHADOW_MASK',
        'INDIRECT_SHADOW_MASK',
        'label_info_render',
        ['RAYCOUNT', 'normalize_RAYCOUNT'],
        'IRRADIANCE'
    ]

    visibility = {
        'label_unsupported_engines': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIDIR', 'BIDIRVM'])},
        'normalize_DIRECT_DIFFUSE': {'import_compatible': False},
        'normalize_DIRECT_GLOSSY': {'import_compatible': False},
        'normalize_INDIRECT_DIFFUSE': {'import_compatible': False},
        'normalize_INDIRECT_GLOSSY': {'import_compatible': False},
        'normalize_INDIRECT_SPECULAR': {'import_compatible': False},
        'normalize_DEPTH': {'import_compatible': False},
    }

    enabled = {
        # Menu buttons
        'saveToDisk': {'enable_aovs': True},
        'import_into_blender': {'enable_aovs': True},
        'import_compatible': {'enable_aovs': True, 'import_into_blender': True},
        'spacer': {'enable_aovs': True},
        # Info labels
        'label_unsupported_engines': {'enable_aovs': True, },
        'label_info_film': {'enable_aovs': True},
        'label_info_material': {'enable_aovs': True},
        'label_info_directlight': {'enable_aovs': True},
        'label_info_indirectlight': {'enable_aovs': True},
        'label_info_geometry': {'enable_aovs': True},
        'label_info_shadow': {'enable_aovs': True},
        'label_info_render': {'enable_aovs': True},
        # AOVs
        'RGB': {'enable_aovs': True},
        'RGBA': {'enable_aovs': True},
        'RGB_TONEMAPPED': False,
        'RGBA_TONEMAPPED': {'enable_aovs': True},
        'ALPHA': {'enable_aovs': True},
        'DEPTH': {'enable_aovs': True},
        'normalize_DEPTH': A([{'enable_aovs': True}, {'DEPTH': True}]),
        'POSITION': {'enable_aovs': True},
        'GEOMETRY_NORMAL': {'enable_aovs': True},
        'SHADING_NORMAL': {'enable_aovs': True},
        'MATERIAL_ID': {'enable_aovs': True},
        'OBJECT_ID': {'enable_aovs': True},
        'DIRECT_DIFFUSE': {'enable_aovs': True},
        'normalize_DIRECT_DIFFUSE': A([{'enable_aovs': True}, {'DIRECT_DIFFUSE': True}]),
        'DIRECT_GLOSSY': {'enable_aovs': True},
        'normalize_DIRECT_GLOSSY': A([{'enable_aovs': True}, {'DIRECT_GLOSSY': True}]),
        'EMISSION': {'enable_aovs': True},
        'INDIRECT_DIFFUSE': {'enable_aovs': True},
        'normalize_INDIRECT_DIFFUSE': A([{'enable_aovs': True}, {'INDIRECT_DIFFUSE': True}]),
        'INDIRECT_GLOSSY': {'enable_aovs': True},
        'normalize_INDIRECT_GLOSSY': A([{'enable_aovs': True}, {'INDIRECT_GLOSSY': True}]),
        'INDIRECT_SPECULAR': {'enable_aovs': True},
        'normalize_INDIRECT_SPECULAR': A([{'enable_aovs': True}, {'INDIRECT_SPECULAR': True}]),
        'DIRECT_SHADOW_MASK': {'enable_aovs': True},
        'INDIRECT_SHADOW_MASK': {'enable_aovs': True},
        'UV': {'enable_aovs': True},
        'RAYCOUNT': {'enable_aovs': True},
        'normalize_RAYCOUNT': A([{'enable_aovs': True}, {'RAYCOUNT': True}]),
        'IRRADIANCE': {'enable_aovs': True},
    }

    def toggle_shading_normal(self, context):
        context.scene.render.layers.active.use_pass_normal = self.SHADING_NORMAL

    def toggle_depth(self, context):
        context.scene.render.layers.active.use_pass_z = self.DEPTH

    def toggle_direct_diffuse(self, context):
        context.scene.render.layers.active.use_pass_diffuse_direct = self.DIRECT_DIFFUSE

    def toggle_direct_glossy(self, context):
        context.scene.render.layers.active.use_pass_glossy_direct = self.DIRECT_GLOSSY

    def toggle_emission(self, context):
        context.scene.render.layers.active.use_pass_emit = self.EMISSION

    def toggle_indirect_diffuse(self, context):
        context.scene.render.layers.active.use_pass_diffuse_indirect = self.INDIRECT_DIFFUSE

    def toggle_indirect_glossy(self, context):
        context.scene.render.layers.active.use_pass_glossy_indirect = self.INDIRECT_GLOSSY

    def toggle_indirect_specular(self, context):
        context.scene.render.layers.active.use_pass_transmission_indirect = self.INDIRECT_SPECULAR

    properties = [
        # Menu buttons
        {
            'type': 'text',
            'attr': 'aov_label',
            'name': 'PBRTv3 Passes (AOVs)',
        },
        {
            'type': 'bool',
            'attr': 'enable_aovs',
            'name': 'Enable',
            'description': 'Enable PBRTv3 Passes',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'import_into_blender',
            'name': 'Import into Blender',
            'description': 'Import passes into Blender after rendering',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'import_compatible',
            'name': 'Use Blender Passes',
            'description': 'Make compatible passes available in Blenders compositor instead of importing as images',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'saveToDisk',
            'name': 'Save',
            'description': 'Save the passes to the output path after rendering',
            'default': False
        },
        {
            'type': 'text',
            'attr': 'label_unsupported_engines',
            'name': 'Note: Bidir engines only support the Alpha and RGB passes',
        },
        {
            'type': 'separator',
            'attr': 'spacer',
        },
        # Info labels
        {
            'type': 'text',
            'attr': 'label_info_film',
            'name': 'Film Information:',
        },
        {
            'type': 'text',
            'attr': 'label_info_material',
            'name': 'Material/Object Information:',
        },
        {
            'type': 'text',
            'attr': 'label_info_directlight',
            'name': 'Direct Light Information:',
        },
        {
            'type': 'text',
            'attr': 'label_info_indirectlight',
            'name': 'Indirect Light Information:',
        },
        {
            'type': 'text',
            'attr': 'label_info_geometry',
            'name': 'Geometry Information:',
        },
        {
            'type': 'text',
            'attr': 'label_info_shadow',
            'name': 'Shadow Information:',
        },
        {
            'type': 'text',
            'attr': 'label_info_render',
            'name': 'Render Information:',
        },
        # AOVs
        {
            'type': 'bool',
            'attr': 'RGB',
            'name': 'RGB',
            'description': 'Raw RGB values (HDR)',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'RGBA',
            'name': 'RGBA',
            'description': 'Raw RGBA values (HDR)',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'RGB_TONEMAPPED',
            'name': 'RGB Tonemapped',
            'description': 'Tonemapped RGB values (LDR)',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'RGBA_TONEMAPPED',
            'name': 'RGBA Tonemapped',
            'description': 'Tonemapped RGBA values (LDR)',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'ALPHA',
            'name': 'Alpha',
            'description': 'Alpha value [0..1]',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'DEPTH',
            'name': 'Depth',
            'description': 'Distance from camera',
            'default': False,
            'update': toggle_depth
        },
        {
            'type': 'bool',
            'attr': 'normalize_DEPTH',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'POSITION',
            'name': 'Position',
            'description': 'World X, Y, Z',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'GEOMETRY_NORMAL',
            'name': 'Geometry Normal',
            'description': 'Normal vector X, Y, Z without mesh smoothing',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'SHADING_NORMAL',
            'name': 'Shading Normal',
            'description': 'Normal vector X, Y, Z with mesh smoothing',
            'default': False,
            'update': toggle_shading_normal,
        },
        {
            'type': 'bool',
            'attr': 'MATERIAL_ID',
            'name': 'Material ID',
            'description': 'Material ID (1 color per material)',
            'default': False,
            #'update': toggle_material_id
        },
        {
            'type': 'bool',
            'attr': 'OBJECT_ID',
            'name': 'Object ID',
            'description': 'Object ID (1 color per object)',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'DIRECT_DIFFUSE',
            'name': 'Diffuse',
            'description': 'Diffuse R, G, B',
            'default': False,
            'update': toggle_direct_diffuse
        },
        {
            'type': 'bool',
            'attr': 'normalize_DIRECT_DIFFUSE',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'DIRECT_GLOSSY',
            'name': 'Glossy',
            'description': 'Glossy R, G, B',
            'default': False,
            'update': toggle_direct_glossy
        },
        {
            'type': 'bool',
            'attr': 'normalize_DIRECT_GLOSSY',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'EMISSION',
            'name': 'Emission',
            'description': 'Emission R, G, B',
            'default': False,
            'update': toggle_emission
        },
        {
            'type': 'bool',
            'attr': 'INDIRECT_DIFFUSE',
            'name': 'Diffuse',
            'description': 'Indirect diffuse R, G, B',
            'default': False,
            'update': toggle_indirect_diffuse
        },
        {
            'type': 'bool',
            'attr': 'normalize_INDIRECT_DIFFUSE',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'INDIRECT_GLOSSY',
            'name': 'Glossy',
            'description': 'Indirect glossy R, G, B',
            'default': False,
            'update': toggle_indirect_glossy
        },
        {
            'type': 'bool',
            'attr': 'normalize_INDIRECT_GLOSSY',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'INDIRECT_SPECULAR',
            'name': 'Specular',
            'description': 'Indirect specular (glass) R, G, B',
            'default': False,
            'update': toggle_indirect_specular
        },
        {
            'type': 'bool',
            'attr': 'normalize_INDIRECT_SPECULAR',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'DIRECT_SHADOW_MASK',
            'name': 'Direct Shadow Mask',
            'description': 'Mask containing shadows by direct light',
            'default': False,
            #'update': toggle_direct_shadow_mask
        },
        {
            'type': 'bool',
            'attr': 'INDIRECT_SHADOW_MASK',
            'name': 'Indirect Shadow Mask',
            'description': 'Mask containing shadows by indirect light',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'UV',
            'name': 'UV',
            'description': 'Texture coordinates U, V',
            'default': False,
            #'update': toggle_uv
        },
        {
            'type': 'bool',
            'attr': 'RAYCOUNT',
            'name': 'Raycount',
            'description': 'Ray count per pixel',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'normalize_RAYCOUNT',
            'name': 'Normalize',
            'description': 'Map values to 0..1 range',
            'default': True
        },
        {
            'type': 'bool',
            'attr': 'IRRADIANCE',
            'name': 'Irradiance',
            'description': 'Surface irradiance',
            'default': False
        },

    ]
