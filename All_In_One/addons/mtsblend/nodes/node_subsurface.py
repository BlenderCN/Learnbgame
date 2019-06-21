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

from bpy.types import Node
from bpy.props import BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, StringProperty

from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


class mitsuba_subsurface_node(mitsuba_node):
    bl_width_min = 160
    shader_type_compat = {'OBJECT'}
    mitsuba_nodetype = 'SUBSURFACE'

    def draw_ior_menu_box(self, layout, attr, name, menu):
        box = layout.box()
        box.context_pointer_set("node", self)

        if attr == 'intIOR' and self.intIOR == self.intIOR_presetvalue:
            menu_text = self.intIOR_presetstring

        elif attr == 'extIOR' and self.extIOR == self.extIOR_presetvalue:
            menu_text = self.extIOR_presetstring

        else:
            menu_text = '-- Choose %s preset --' % name

        box.menu('MITSUBA_MT_%s_ior_presets' % menu, text=menu_text)
        box.prop(self, attr)

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


@MitsubaNodeTypes.register
class MtsNodeSubsurface_dipole(mitsuba_subsurface_node, Node):
    '''Dipole Subsurface node'''
    bl_idname = 'MtsNodeSubsurface_dipole'
    bl_label = 'Dipole'
    plugin_types = {'dipole'}

    def changed_int_ior_preset(self, context):
        # # connect preset -> property
        self.intIOR = self.intIOR_presetvalue

    def changed_ext_ior_preset(self, context):
        # # connect preset -> property
        self.extIOR = self.extIOR_presetvalue

    def update_visibility(self, context):
        self.inputs['Scattering Coefficient'].enabled = not self.useAlbSigmaT
        self.inputs['Absorption Coefficient'].enabled = not self.useAlbSigmaT
        self.inputs['Anisotropy'].enabled = not self.useAlbSigmaT
        self.inputs['Extinction Coefficient'].enabled = self.useAlbSigmaT
        self.inputs['Albedo'].enabled = self.useAlbSigmaT

    def draw_buttons(self, context, layout):
        self.draw_material_menu(layout)
        layout.prop(self, 'scale')
        self.draw_ior_menu_box(layout, 'intIOR', 'Int. IOR', 'interior')
        self.draw_ior_menu_box(layout, 'extIOR', 'Ext. IOR', 'exterior')

    material = StringProperty(name='Material Name', description='Material Name', update=update_visibility)

    preset_material = StringProperty(name='material preset', default='')
    preset_sigmaS = FloatVectorProperty(name='sigmaS preset', default=(0.0, 0.0, 0.0))
    preset_sigmaA = FloatVectorProperty(name='sigmaA preset', default=(0.0, 0.0, 0.0))
    preset_g = FloatVectorProperty(name='g preset', default=(0.0, 0.0, 0.0), min=-0.999999, max=0.999999)

    useAlbSigmaT = BoolProperty(name='Use Albedo & SigmaT', description='Use Albedo & SigmaT instead SigmatS & SigmaA', default=False, update=update_visibility)

    intIOR_presetvalue = FloatProperty(name='Int. IOR-Preset', description='Int. IOR', update=changed_int_ior_preset)
    intIOR_presetstring = StringProperty(name='Int. IOR-Preset Name', description='Int. IOR')
    intIOR = FloatProperty(name='Int IOR', default=1.49, min=1.0, max=10.0, precision=6)

    extIOR_presetvalue = FloatProperty(name='Ext. IOR-Preset', description='Ext. IOR', update=changed_ext_ior_preset)
    extIOR_presetstring = StringProperty(name='Ext. IOR-Preset Name', description='Ext. IOR')
    extIOR = FloatProperty(name='Ext IOR', default=1.000277, min=1.0, max=10.0, precision=6)

    scale = FloatProperty(name='Scale', description='Density Scale', default=1, min=0.0001, max=50000.0)
    irrSamples = IntProperty(name='irrSamples', description='Number of Samples', default=16, min=-2, max=128)

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_sigmaS', 'name': 'Scattering Coefficient'},
        {'type': 'MtsSocketSpectrum_sigmaA', 'name': 'Absorption Coefficient'},
        {'type': 'MtsSocketSpectrum_g', 'name': 'Anisotropy'},
        {'type': 'MtsSocketSpectrum_sigmaT', 'name': 'Extinction Coefficient'},
        {'type': 'MtsSocketSpectrum_albedo', 'name': 'Albedo'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketSubsurface', 'name': 'Subsurface'},
    ]

    def get_subsurface_dict(self, export_ctx):
        params = {
            'type': 'dipole',
            'scale': self.scale,
            'irrSamples': self.irrSamples,
            'intIOR': self.intIOR,
            'extIOR': self.extIOR,
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

        return params

    def set_from_dict(self, ntree, params):
        if 'scale' in params:
            self.scale = params['scale']

        if 'irrSamples' in params:
            self.irrSamples = params['irrSamples']

        if 'intIOR' in params:
            self.intIOR = params['intIOR']

        if 'extIOR' in params:
            self.extIOR = params['extIOR']

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


@MitsubaNodeTypes.register
class MtsNodeSubsurface_singlescatter(mitsuba_subsurface_node, Node):
    '''Single Scattering Subsurface node'''
    bl_idname = 'MtsNodeSubsurface_singlescatter'
    bl_label = 'Single Scattering'
    plugin_types = {'singlescatter'}

    def update_visibility(self, context):
        self.inputs['Scattering Coefficient'].enabled = not self.useAlbSigmaT
        self.inputs['Absorption Coefficient'].enabled = not self.useAlbSigmaT
        self.inputs['Anisotropy'].enabled = not self.useAlbSigmaT
        self.inputs['Extinction Coefficient'].enabled = self.useAlbSigmaT
        self.inputs['Albedo'].enabled = self.useAlbSigmaT

    def draw_buttons(self, context, layout):
        layout.prop(self, 'fastSingleScatter')
        layout.prop(self, 'fssSamples')
        layout.prop(self, 'singleScatterDepth')
        #layout.prop(self, 'singleScatterShadowRays')
        #layout.prop(self, 'singleScatterTransmittance')
        self.draw_material_menu(layout)

    material = StringProperty(name='Material Name', description='Material Name', update=update_visibility)

    preset_material = StringProperty(name='material preset', default='')
    preset_sigmaS = FloatVectorProperty(name='sigmaS preset', default=(0.0, 0.0, 0.0))
    preset_sigmaA = FloatVectorProperty(name='sigmaA preset', default=(0.0, 0.0, 0.0))
    preset_g = FloatVectorProperty(name='g preset', default=(0.0, 0.0, 0.0), min=-0.999999, max=0.999999)

    useAlbSigmaT = BoolProperty(name='Use Albedo & SigmaT', description='Use Albedo & SigmaT instead SigmatS & SigmaA', default=False, update=update_visibility)

    fastSingleScatter = BoolProperty(name='Use Fast Single Scatter', description='Use Fast Single Scatter', default=True)
    fssSamples = IntProperty(name='FSS Samples', description='Number of samples along the inside ray', default=2, min=2, max=128)
    singleScatterDepth = IntProperty(name='Single Scatter Depth', description='Number of total internal reflexions', default=4, min=2, max=128)
    #singleScatterShadowRays = BoolProperty(name='Use Shadow Rays', description='Use Shadow Rays', default=True)
    #singleScatterTransmittance = BoolProperty(name='Compute Transmittance', description='Compute Transmittance', default=True)

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_sigmaS', 'name': 'Scattering Coefficient'},
        {'type': 'MtsSocketSpectrum_sigmaA', 'name': 'Absorption Coefficient'},
        {'type': 'MtsSocketSpectrum_g', 'name': 'Anisotropy'},
        {'type': 'MtsSocketSpectrum_sigmaT', 'name': 'Extinction Coefficient'},
        {'type': 'MtsSocketSpectrum_albedo', 'name': 'Albedo'},
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketSubsurface', 'name': 'Subsurface'},
    ]

    def get_subsurface_dict(self, export_ctx):
        params = {
            'type': 'singlescatter',
            'fastSingleScatter': self.fastSingleScatter,
            'fssSamples': self.fssSamples,
            'singleScatterDepth': self.singleScatterDepth,
            #'singleScatterShadowRays': self.singleScatterShadowRays,
            #'singleScatterTransmittance': self.singleScatterTransmittance,
        }

        bsdf_node = self.inputs['Bsdf'].get_linked_node()

        if bsdf_node:
            params.update({'bsdf': bsdf_node.get_bsdf_dict(export_ctx)})

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

        return params

    def set_from_dict(self, ntree, params):
        if 'fastSingleScatter' in params:
            self.fastSingleScatter = params['fastSingleScatter']

        if 'fssSamples' in params:
            self.fssSamples = params['fssSamples']

        if 'singleScatterDepth' in params:
            self.singleScatterDepth = params['singleScatterDepth']

        if 'bsdf' in params:
            ntree.new_node_from_dict(params['bsdf'], self.inputs['Bsdf'])

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
