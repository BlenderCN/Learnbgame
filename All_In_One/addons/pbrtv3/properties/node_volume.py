# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Jens Verwiebe, Jason Clarke, Asbjørn Heid, Simon Wendsche
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

import bpy
from ..outputs.luxcore_api import set_prop_vol, set_prop_tex

from ..properties.node_sockets import *
from ..properties.node_material import get_socket_paramsets

from . import (create_luxcore_name_vol, create_luxcore_name, export_emission_luxcore,
               warning_luxcore_node, export_volume_luxcore, pbrtv3_node, pbrtv3_material_node)


@PBRTv3Addon.addon_register_class
class pbrtv3_volume_output_node(pbrtv3_node):
    """Volume output node"""
    bl_idname = 'pbrtv3_volume_output_node'
    bl_label = 'Volume Output'
    bl_icon = 'WORLD'
    bl_width_min = 120

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Volume')
        self.inputs.new('pbrtv3_color_socket', 'Emission Color')
        self.inputs['Emission Color'].default_value = [0, 0, 0]

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        if UsePBRTv3Core():
            current_vol_index = context.scene.pbrtv3_volumes.volumes_index
            if current_vol_index >= 0 and context.scene.pbrtv3_volumes.volumes:
                current_vol = context.scene.pbrtv3_volumes.volumes[current_vol_index]

                layout.prop(current_vol, 'priority', text='Priority')

    def export_luxcore(self, volume, properties, blender_scene):
        tree_name = volume.nodetree
        print('Converting volume: %s (Nodetree: %s)' % (volume.name, tree_name))

        # Export emission color (backwards compatible)
        if 'Emission Color' in self.inputs:
            emission = self.inputs['Emission Color'].export_luxcore(properties)

            if emission == [0, 0, 0]:
                emission = None
        else:
            emission = None

        # Export the volume tree
        luxcore_name = export_volume_luxcore(properties, self.inputs[0], volume.name)

        # Set emission color (backwards compatible)
        if emission:
            set_prop_vol(properties, luxcore_name, 'emission', emission)

        set_prop_vol(properties, luxcore_name, 'priority', volume.priority)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_volume_type_node_clear(pbrtv3_material_node):
    """Clear volume node"""
    bl_idname = 'pbrtv3_volume_clear_node'
    bl_label = 'Clear Volume'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def init(self, context):
        self.inputs.new('pbrtv3_fresnel_socket', 'IOR')
        self.inputs.new('pbrtv3_AC_absorption_socket', 'Absorption Color')

        self.outputs.new('NodeSocketShader', 'Volume')

    def export_volume(self, make_volume, make_texture):
        vol_type = 'clear'

        clear_params = ParamSet()
        clear_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_volume(self.name, vol_type, clear_params)

    def export_luxcore(self, properties, name=None):
        luxcore_name = create_luxcore_name_vol(self, name)

        ior = self.inputs['IOR'].export_luxcore(properties)
        absorption = self.inputs['Absorption Color'].export_luxcore(properties)

        set_prop_vol(properties, luxcore_name, 'type', 'clear')
        set_prop_vol(properties, luxcore_name, 'ior', ior)
        set_prop_vol(properties, luxcore_name, 'absorption', absorption)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_volume_type_node_homogeneous(pbrtv3_material_node):
    '''Homogeneous volume node'''
    bl_idname = 'pbrtv3_volume_homogeneous_node'
    bl_label = 'Homogeneous Volume'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    use_multiscattering = bpy.props.BoolProperty(name='Multiscattering', description='Compute multiple scattering '
                                                 'events in this volume (recommended for volumes with high scattering '
                                                 'scale)', default=False)

    def init(self, context):
        self.inputs.new('pbrtv3_fresnel_socket', 'IOR')
        self.inputs.new('pbrtv3_SC_absorption_socket', 'Absorption Color')
        self.inputs.new('pbrtv3_SC_color_socket', 'Scattering Color')
        self.inputs.new('pbrtv3_float_socket', 'Scattering Scale')
        self.inputs['Scattering Scale'].default_value = 1
        self.inputs.new('pbrtv3_SC_asymmetry_socket', 'Asymmetry')

        self.outputs.new('NodeSocketShader', 'Volume')

    def draw_buttons(self, context, layout):
        if UsePBRTv3Core():
            layout.prop(self, 'use_multiscattering')

    def export_volume(self, make_volume, make_texture):
        vol_type = 'homogeneous'

        homogeneous_params = ParamSet()
        homogeneous_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_volume(self.name, vol_type, homogeneous_params)

    def export_luxcore(self, properties, name=None):
        luxcore_name = create_luxcore_name_vol(self, name)

        ior = self.inputs['IOR'].export_luxcore(properties)
        absorption = self.inputs['Absorption Color'].export_luxcore(properties)
        scattering = self.inputs['Scattering Color'].export_luxcore(properties)
        asymmetry = self.inputs['Asymmetry'].export_luxcore(properties)

        if self.inputs['Scattering Scale'] != 1:
            scale = self.inputs['Scattering Scale'].export_luxcore(properties)

            scale_name = create_luxcore_name(self, suffix='scattering_scale')
            set_prop_tex(properties, scale_name, 'type', 'scale')
            set_prop_tex(properties, scale_name, 'texture1', scattering)
            set_prop_tex(properties, scale_name, 'texture2', scale)
            scattering = scale_name

        set_prop_vol(properties, luxcore_name, 'type', 'homogeneous')
        set_prop_vol(properties, luxcore_name, 'ior', ior)
        set_prop_vol(properties, luxcore_name, 'absorption', absorption)
        set_prop_vol(properties, luxcore_name, 'scattering', scattering)
        set_prop_vol(properties, luxcore_name, 'asymmetry', asymmetry)
        set_prop_vol(properties, luxcore_name, 'multiscattering', self.use_multiscattering)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_volume_type_node_heterogeneous(pbrtv3_material_node):
    """Heterogeneous volume node"""
    bl_idname = 'pbrtv3_volume_heterogeneous_node'
    bl_label = 'Heterogeneous Volume'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    stepsize = bpy.props.FloatProperty(name='Step Size', default=0.1, min=0.0, soft_min=0.001, max=1000, soft_max=10,
                                       subtype='DISTANCE', unit='LENGTH', precision=3,
                                       description='Length of ray marching steps, smaller values resolve more detail, but are slower')
    max_steps = bpy.props.IntProperty(name='Max. Steps', description='Maximum number of steps for a ray in this volume',
                                      default=32, min=1)
    use_multiscattering = bpy.props.BoolProperty(name='Multiscattering', description='Compute multiple scattering events in '
                                                 'this volume (recommended for volumes with high scattering scale)',
                                                 default=False)

    def init(self, context):
        self.inputs.new('pbrtv3_fresnel_socket', 'IOR')
        self.inputs.new('pbrtv3_SC_absorption_socket', 'Absorption Color')
        self.inputs.new('pbrtv3_SC_color_socket', 'Scattering Color')
        self.inputs.new('pbrtv3_float_socket', 'Scattering Scale')
        self.inputs['Scattering Scale'].default_value = 1
        self.inputs.new('pbrtv3_SC_asymmetry_socket', 'Asymmetry')

        self.outputs.new('NodeSocketShader', 'Volume')

    def draw_buttons(self, context, layout):
        if UsePBRTv3Core():
            column = layout.column(align=True)
            column.prop(self, 'stepsize')
            column.prop(self, 'max_steps')

            layout.prop(self, 'use_multiscattering')
        else:
            layout.prop(self, 'stepsize')

    def export_volume(self, make_volume, make_texture):
        vol_type = 'heterogeneous'

        heterogeneous_params = ParamSet()
        heterogeneous_params.update(get_socket_paramsets(self.inputs, make_texture))
        heterogeneous_params.add_float('stepsize', self.stepsize)

        return make_volume(self.name, vol_type, heterogeneous_params)

    def export_luxcore(self, properties, name=None):
        luxcore_name = create_luxcore_name_vol(self, name)

        ior = self.inputs['IOR'].export_luxcore(properties)
        absorption = self.inputs['Absorption Color'].export_luxcore(properties)
        scattering = self.inputs['Scattering Color'].export_luxcore(properties)
        asymmetry = self.inputs['Asymmetry'].export_luxcore(properties)

        if self.inputs['Scattering Scale'] != 1:
            scale = self.inputs['Scattering Scale'].export_luxcore(properties)

            scale_name = create_luxcore_name(self, suffix='scattering_scale')
            set_prop_tex(properties, scale_name, 'type', 'scale')
            set_prop_tex(properties, scale_name, 'texture1', scattering)
            set_prop_tex(properties, scale_name, 'texture2', scale)
            scattering = scale_name

        set_prop_vol(properties, luxcore_name, 'type', 'heterogeneous')
        set_prop_vol(properties, luxcore_name, 'ior', ior)
        set_prop_vol(properties, luxcore_name, 'absorption', absorption)
        set_prop_vol(properties, luxcore_name, 'scattering', scattering)
        set_prop_vol(properties, luxcore_name, 'asymmetry', asymmetry)
        set_prop_vol(properties, luxcore_name, 'multiscattering', self.use_multiscattering)
        set_prop_vol(properties, luxcore_name, 'steps.size', self.stepsize)
        set_prop_vol(properties, luxcore_name, 'steps.maxcount', self.max_steps)

        return luxcore_name

