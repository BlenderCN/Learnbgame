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
from bpy.props import BoolProperty, FloatProperty, FloatVectorProperty, StringProperty, EnumProperty

from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


class mitsuba_medium_node(mitsuba_node):
    bl_width_min = 160
    shader_type_compat = {'OBJECT', 'WORLD'}
    mitsuba_nodetype = 'MEDIUM'


@MitsubaNodeTypes.register
class MtsNodeMedium_reference(mitsuba_medium_node, Node):
    '''Medium Reference node'''
    bl_idname = 'MtsNodeMedium_reference'
    bl_label = 'Medium Reference'
    plugin_types = {'medium_reference'}

    ref_type = EnumProperty(
        name='Reference Type',
        description='Specifies the reference type.',
        items=[
            ('nodegroup', 'Node Group', 'nodegroup'),
            ('object', 'Object', 'object'),
        ],
        default='nodegroup',
    )

    ref_nodegroup = StringProperty(name='Node Group', description='Node Group')
    ref_object = StringProperty(name='Object', description='Object')

    custom_outputs = [
        {'type': 'MtsSocketMedium', 'name': 'Medium'},
    ]

    def draw_buttons(self, context, layout):
        layout.prop(self, 'ref_type')

        if self.ref_type == 'object':
            layout.prop_search(self, 'ref_object', bpy.data, 'objects')

        else:
            layout.prop_search(self, 'ref_nodegroup', context.scene.mitsuba_nodegroups, 'medium')

    def get_medium_dict(self, export_ctx):
        try:
            ntree = bpy.data.node_groups[self.reference]
            output_node = ntree.find_node('MtsNodeMaterialOutput')
            material = output_node.get_output_dict(export_ctx, ntree)
            params = material['interior']

        except:
            params = {}

        return params


@MitsubaNodeTypes.register
class MtsNodeMedium_homogeneous(mitsuba_medium_node, Node):
    '''Homogeneous Medium node'''
    bl_idname = 'MtsNodeMedium_homogeneous'
    bl_label = 'Homogeneous Medium'
    plugin_types = {'homogeneous'}

    def update_visibility(self, context):
        self.inputs['Scattering Coefficient'].enabled = not self.useAlbSigmaT
        self.inputs['Absorption Coefficient'].enabled = not self.useAlbSigmaT
        self.inputs['Anisotropy'].enabled = not self.useAlbSigmaT
        self.inputs['Extinction Coefficient'].enabled = self.useAlbSigmaT
        self.inputs['Albedo'].enabled = self.useAlbSigmaT

    def draw_material_menu(self, layout):
        iss = self.inputs['Scattering Coefficient'].default_value[:]
        isa = self.inputs['Absorption Coefficient'].default_value[:]
        isg = self.inputs['Anisotropy'].default_value[:]
        pss = self.preset_sigmaS[:]
        psa = self.preset_sigmaA[:]
        psg = self.preset_g[:]
        if self.material == self.preset_material and \
                iss == pss and isa == psa and isg == psg:
            menu_text = self.material
        else:
            menu_text = '-- Choose Material preset --'

        layout.menu('MITSUBA_MT_material_presets', text=menu_text)

        row = layout.row()
        row.enabled = self.material != menu_text
        row.prop(self, 'useAlbSigmaT')

    material = StringProperty(name='Material Name', description='Material Name')

    preset_material = StringProperty(name='material preset', default='')
    preset_sigmaS = FloatVectorProperty(name='sigmaS preset', default=(0.0, 0.0, 0.0))
    preset_sigmaA = FloatVectorProperty(name='sigmaA preset', default=(0.0, 0.0, 0.0))
    preset_g = FloatVectorProperty(name='g preset', default=(0.0, 0.0, 0.0), min=-0.999999, max=0.999999)

    useAlbSigmaT = BoolProperty(name='Use Albedo & SigmaT', description='Use Albedo & SigmaT instead SigmatS & SigmaA', default=False, update=update_visibility)

    scale = FloatProperty(name='Scale', description='Density Scale', default=1, min=0.0001, max=50000.0)

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_sigmaS', 'name': 'Scattering Coefficient'},
        {'type': 'MtsSocketSpectrum_sigmaA', 'name': 'Absorption Coefficient'},
        {'type': 'MtsSocketSpectrum_g', 'name': 'Anisotropy'},
        {'type': 'MtsSocketSpectrum_sigmaT', 'name': 'Extinction Coefficient'},
        {'type': 'MtsSocketSpectrum_albedo', 'name': 'Albedo'},
        #{'type': 'MtsSocketPhase', 'name': 'Phase'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketMedium', 'name': 'Medium'},
    ]

    def draw_buttons(self, context, layout):
        self.draw_material_menu(layout)
        layout.prop(self, 'scale')

    def get_medium_dict(self, export_ctx):
        params = {
            'type': 'homogeneous',
            'scale': self.scale,
        }

        if self.useAlbSigmaT:
            params.update({
                'sigmaT': self.inputs['Extinction Coefficient'].get_spectrum_dict(export_ctx),
                'albedo': self.inputs['Albedo'].get_spectrum_dict(export_ctx),
            })

        else:
            params.update({
                'sigmaS': self.inputs['Scattering Coefficient'].get_spectrum_dict(export_ctx),
                'sigmaA': self.inputs['Absorption Coefficient'].get_spectrum_dict(export_ctx),
                'g': self.inputs['Anisotropy'].get_spectrum_dict(export_ctx),
            })

        # TODO: phase

        return params

    def set_from_dict(self, ntree, params):
        if 'scale' in params:
            self.scale = params['scale']

        if 'sigmaT' in params or 'albedo' in params:
            self.useAlbSigmaT = True

            if 'sigmaT' in params:
                self.inputs['Extinction Coefficient'].set_spectrum_socket(ntree, params['sigmaT'])

            if 'albedo' in params:
                self.inputs['Albedo'].set_spectrum_socket(ntree, params['albedo'])

        elif 'sigmaS' in params or 'sigmaA' in params:
            self.useAlbSigmaT = False

            if 'sigmaS' in params:
                self.inputs['Scattering Coefficient'].set_spectrum_socket(ntree, params['sigmaS'])

            if 'sigmaA' in params:
                self.inputs['Absorption Coefficient'].set_spectrum_socket(ntree, params['sigmaA'])

            if 'g' in params:
                self.inputs['Anisotropy'].set_spectrum_socket(ntree, params['g'])
