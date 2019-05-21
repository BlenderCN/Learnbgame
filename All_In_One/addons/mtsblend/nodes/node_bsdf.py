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

from collections import OrderedDict

from bpy.types import Node
from bpy.props import BoolProperty, FloatProperty, FloatVectorProperty, StringProperty, EnumProperty

from ..data.materials import conductor_material_items
from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


microfacet_distribution_items = [
    ('beckmann', 'Beckmann', 'beckmann'),
    ('ggx', 'Ggx', 'ggx'),
    ('phong', 'Phong', 'phong'),
]


class mitsuba_bsdf_node(mitsuba_node):
    bl_icon = 'MATERIAL'
    bl_width_min = 180
    shader_type_compat = {'OBJECT'}
    mitsuba_nodetype = 'BSDF'

    def draw_ior_menu_box(self, layout, attr, name, menu):
        box = layout.box()
        box.context_pointer_set("node", self)

        if attr == 'intIOR' and self.intIOR == self.intIOR_presetvalue:
            menu_text = self.intIOR_presetstring

        elif attr == 'extIOR' and self.extIOR == self.extIOR_presetvalue:
            menu_text = self.extIOR_presetstring

        elif attr == 'extEta' and self.extEta == self.extEta_presetvalue:
            menu_text = self.extEta_presetstring

        else:
            menu_text = '-- Choose %s preset --' % name

        box.menu('MITSUBA_MT_%s_ior_presets' % menu, text=menu_text)
        box.prop(self, attr)


@MitsubaNodeTypes.register
class MtsNodeBsdf_diffuse(mitsuba_bsdf_node, Node):
    '''Diffuse material node'''
    bl_idname = 'MtsNodeBsdf_diffuse'
    bl_label = 'Diffuse'
    plugin_types = {'diffuse', 'roughdiffuse'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'useFastApprox')

    useFastApprox = BoolProperty(
        name='Use Fast Approximation',
        description='This parameter selects between the full version of the model or a fast approximation that still retains most qualitative features.',
        default=False
    )

    custom_inputs = [
        {'type': 'MtsSocketFloat_alpha', 'name': 'Roughness'},
        {'type': 'MtsSocketColor_diffuseReflectance', 'name': 'Diffuse Reflectance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'diffuse',
            'reflectance': self.inputs['Diffuse Reflectance'].get_color_dict(export_ctx),
        }

        alpha = self.inputs['Roughness'].get_float_dict(export_ctx)

        if alpha:
            params.update({
                'alpha': alpha,
                'useFastApprox': self.useFastApprox,
                'type': 'roughdiffuse',
            })

        return params

    def set_from_dict(self, ntree, params):
        if 'reflectance' in params:
            self.inputs['Diffuse Reflectance'].set_color_socket(ntree, params['reflectance'])

        if params['type'] == 'roughdiffuse':
            if 'alpha' in params:
                self.inputs['Roughness'].set_float_socket(ntree, params['alpha'])

            if 'useFastApprox' in params:
                self.useFastApprox = params['useFastApprox']

        else:
            self.inputs['Roughness'].default_value = 0


@MitsubaNodeTypes.register
class MtsNodeBsdf_dielectric(mitsuba_bsdf_node, Node):
    '''Dielectric material node'''
    bl_idname = 'MtsNodeBsdf_dielectric'
    bl_label = 'Dielectric'
    plugin_types = {'dielectric', 'thindielectric', 'roughdielectric'}

    def changed_int_ior_preset(self, context):
        # # connect preset -> property
        self.intIOR = self.intIOR_presetvalue

    def changed_ext_ior_preset(self, context):
        # # connect preset -> property
        self.extIOR = self.extIOR_presetvalue

    def update_visibility(self, context):
        try:
            self.inputs['Roughness'].enabled = not self.thin
            self.inputs['Roughness'].name = 'Roughness U' if self.anisotropic else 'Roughness'

        except:
            self.inputs['Roughness U'].enabled = not self.thin
            self.inputs['Roughness U'].name = 'Roughness U' if self.anisotropic else 'Roughness'

        self.inputs['Roughness V'].enabled = not self.thin and self.anisotropic

    def draw_buttons(self, context, layout):
        layout.prop(self, 'thin')

        self.draw_ior_menu_box(layout, 'intIOR', 'Int. IOR', 'interior')
        self.draw_ior_menu_box(layout, 'extIOR', 'Ext. IOR', 'exterior')

        if not self.thin:
            layout.prop(self, 'distribution')
            layout.prop(self, 'anisotropic')

    intIOR_presetvalue = FloatProperty(name='Int. IOR-Preset', description='Int. IOR', update=changed_int_ior_preset)
    intIOR_presetstring = StringProperty(name='Int. IOR-Preset Name', description='Int. IOR')
    intIOR = FloatProperty(
        name='Int IOR',
        description='Interior index of refraction specified numerically or using a material preset.',
        default=1.49, min=1.0, max=10.0,
        precision=6
    )

    extIOR_presetvalue = FloatProperty(name='Ext. IOR-Preset', description='Ext. IOR', update=changed_ext_ior_preset)
    extIOR_presetstring = StringProperty(name='Ext. IOR-Preset Name', description='Ext. IOR')
    extIOR = FloatProperty(
        name='Ext IOR',
        description='Interior index of refraction specified numerically or using a material preset.',
        default=1.000277,
        min=1.0, max=10.0,
        precision=6
    )

    thin = BoolProperty(name='Thin Dielectric', description='Use thin dielectric material', default=False, update=update_visibility)

    anisotropic = BoolProperty(
        name='Anisotropic Roughness',
        description='Use anisotropy. Allows setting different roughness values for tangent and bitangent directions.',
        default=False,
        update=update_visibility
    )

    distribution = EnumProperty(
        name='Roughness Model',
        description='Specifies the type of microfacet normal distribution used to model the surface roughness.',
        items=microfacet_distribution_items,
        default='beckmann',
        update=update_visibility
    )

    custom_inputs = [
        {'type': 'MtsSocketFloat_alphaU', 'name': 'Roughness U'},
        {'type': 'MtsSocketFloat_alphaV', 'name': 'Roughness V'},
        {'type': 'MtsSocketColor_specularReflectance', 'name': 'Specular Reflectance'},
        {'type': 'MtsSocketColor_specularTransmittance', 'name': 'Specular Transmittance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'dielectric',
            'intIOR': self.intIOR,
            'extIOR': self.extIOR,
            'specularReflectance': self.inputs['Specular Reflectance'].get_color_dict(export_ctx),
            'specularTransmittance': self.inputs['Specular Transmittance'].get_color_dict(export_ctx),
        }

        if self.thin:
            params.update({'type': 'thindielectric'})

        else:
            if self.anisotropic:
                alphaU = self.inputs['Roughness U'].get_float_dict(export_ctx)
                alphaV = self.inputs['Roughness V'].get_float_dict(export_ctx)
                if alphaU or alphaV:
                    params.update({
                        'alphaU': alphaU,
                        'alphaV': alphaV,
                        'distribution': self.distribution,
                        'type': 'roughdielectric',
                    })

            else:
                alpha = self.inputs['Roughness'].get_float_dict(export_ctx)
                if alpha:
                    params.update({
                        'alpha': alpha,
                        'distribution': self.distribution,
                        'type': 'roughdielectric',
                    })

        return params

    def set_from_dict(self, ntree, params):
        if 'intIOR' in params:
            self.intIOR = params['intIOR']

        if 'extIOR' in params:
            self.extIOR = params['extIOR']

        if 'specularReflectance' in params:
            self.inputs['Specular Reflectance'].set_color_socket(ntree, params['specularReflectance'])

        if 'specularTransmittance' in params:
            self.inputs['Specular Transmittance'].set_color_socket(ntree, params['specularTransmittance'])

        if params['type'] == 'thindielectric':
            self.thin = True

        elif params['type'] == 'roughdielectric':
            if 'distribution' in params:
                self.distribution = params['distribution']

            if 'alphaU' in params or 'alphaV' in params:
                self.anisotropic = True

                if 'alphaU' in params:
                    self.inputs['Roughness U'].set_float_socket(ntree, params['alphaU'])

                if 'alphaV' in params:
                    self.inputs['Roughness V'].set_float_socket(ntree, params['alphaV'])

            elif 'alpha' in params:
                self.anisotropic = False
                self.inputs['Roughness'].set_float_socket(ntree, params['alpha'])

        else:
            self.anisotropic = False
            self.inputs['Roughness'].default_value = 0


@MitsubaNodeTypes.register
class MtsNodeBsdf_conductor(mitsuba_bsdf_node, Node):
    '''Conductor material node'''
    bl_idname = 'MtsNodeBsdf_conductor'
    bl_label = 'Conductor'
    plugin_types = {'conductor', 'roughconductor'}

    def changed_ext_eta_preset(self, context):
        # # connect preset -> property
        self.extEta = self.extEta_presetvalue

    def update_visibility(self, context):
        try:
            self.inputs['Roughness'].name = 'Roughness U' if self.anisotropic else 'Roughness'

        except:
            self.inputs['Roughness U'].name = 'Roughness U' if self.anisotropic else 'Roughness'

        self.inputs['Roughness V'].enabled = self.anisotropic
        self.inputs['IOR'].enabled = self.material in {'', 'custom'}
        self.inputs['Absorption Coefficient'].enabled = self.material in {'', 'custom'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'material')

        self.draw_ior_menu_box(layout, 'extEta', 'Ext. Eta', 'exterior')

        layout.prop(self, 'distribution')
        layout.prop(self, 'anisotropic')

    material = EnumProperty(
        name='Material',
        description='Choose material preset',
        items=conductor_material_items,
        default='custom',
        update=update_visibility
    )

    eta = FloatVectorProperty(name='IOR', default=(0.37, 0.37, 0.37), min=0.10, max=10.0)
    k = FloatVectorProperty(name='Absorption Coefficient', default=(2.82, 2.82, 2.82), min=1.0, max=10.0)

    extEta_presetvalue = FloatProperty(name='Ext. Eta-Preset', description='Ext. Eta', update=changed_ext_eta_preset)
    extEta_presetstring = StringProperty(name='Ext. Eta-Preset Name', description='Ext. Eta')
    extEta = FloatProperty(name='Ext Eta', default=1.000277, min=1.0, max=10.0, precision=6)

    anisotropic = BoolProperty(
        name='Anisotropic Roughness',
        description='Use anisotropy. Allows setting different roughness values for tangent and bitangent directions.',
        default=False,
        update=update_visibility
    )

    distribution = EnumProperty(
        name='Roughness Model',
        description='Specifies the type of microfacet normal distribution used to model the surface roughness.',
        items=microfacet_distribution_items,
        default='beckmann',
        update=update_visibility
    )

    custom_inputs = [
        {'type': 'MtsSocketFloat_alphaU', 'name': 'Roughness U'},
        {'type': 'MtsSocketFloat_alphaV', 'name': 'Roughness V'},
        {'type': 'MtsSocketColor_specularReflectance', 'name': 'Specular Reflectance'},
        {'type': 'MtsSocketSpectrum_eta', 'name': 'IOR'},
        {'type': 'MtsSocketSpectrum_k', 'name': 'Absorption Coefficient'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'conductor',
            'extEta': self.extEta,
            'specularReflectance': self.inputs['Specular Reflectance'].get_color_dict(export_ctx),
        }

        if self.material in {'', 'custom'}:
            params.update({
                'eta': self.inputs['IOR'].get_spectrum_dict(export_ctx),
                'k': self.inputs['Absorption Coefficient'].get_spectrum_dict(export_ctx),
            })

        else:
            params.update({'material': self.material})

        if self.anisotropic:
            alphaU = self.inputs['Roughness U'].get_float_dict(export_ctx)
            alphaV = self.inputs['Roughness V'].get_float_dict(export_ctx)

            if alphaU or alphaV:
                params.update({
                    'alphaU': alphaU,
                    'alphaV': alphaV,
                    'distribution': self.distribution,
                    'type': 'roughconductor',
                })

        else:
            alpha = self.inputs['Roughness'].get_float_dict(export_ctx)

            if alpha:
                params.update({
                    'alpha': alpha,
                    'distribution': self.distribution,
                    'type': 'roughconductor',
                })

        return params

    def set_from_dict(self, ntree, params):
        if 'extEta' in params:
            self.extEta = params['extEta']

        if 'specularReflectance' in params:
            self.inputs['Specular Reflectance'].set_color_socket(ntree, params['specularReflectance'])

        if 'eta' in params or 'k' in params:
            if 'eta' in params:
                self.inputs['IOR'].set_spectrum_socket(ntree, params['eta'])

            if 'k' in params:
                self.inputs['Absorption Coefficient'].set_spectrum_socket(ntree, params['k'])

        elif 'material' in params:
            self.material = params['material']

        if params['type'] == 'roughconductor':
            if 'distribution' in params:
                self.distribution = params['distribution']

            if 'alphaU' in params or 'alphaV' in params:
                self.anisotropic = True

                if 'alphaU' in params:
                    self.inputs['Roughness U'].set_float_socket(ntree, params['alphaU'])

                if 'alphaV' in params:
                    self.inputs['Roughness V'].set_float_socket(ntree, params['alphaV'])

            elif 'alpha' in params:
                self.anisotropic = False
                self.inputs['Roughness'].set_float_socket(ntree, params['alpha'])

        else:
            self.anisotropic = False
            self.inputs['Roughness'].default_value = 0


@MitsubaNodeTypes.register
class MtsNodeBsdf_plastic(mitsuba_bsdf_node, Node):
    '''Plastic material node'''
    bl_idname = 'MtsNodeBsdf_plastic'
    bl_label = 'Plastic'
    plugin_types = {'plastic', 'roughplastic'}

    def changed_int_ior_preset(self, context):
        # # connect preset -> property
        self.intIOR = self.intIOR_presetvalue

    def changed_ext_ior_preset(self, context):
        # # connect preset -> property
        self.extIOR = self.extIOR_presetvalue

    def draw_buttons(self, context, layout):
        self.draw_ior_menu_box(layout, 'intIOR', 'Int. IOR', 'interior')
        self.draw_ior_menu_box(layout, 'extIOR', 'Ext. IOR', 'exterior')

        layout.prop(self, 'nonlinear')
        layout.prop(self, 'distribution')

    intIOR_presetvalue = FloatProperty(name='Int. IOR-Preset', description='Int. IOR', update=changed_int_ior_preset)
    intIOR_presetstring = StringProperty(name='Int. IOR-Preset Name', description='Int. IOR')
    intIOR = FloatProperty(name='Int IOR', default=1.49, min=1.0, max=10.0, precision=6)

    extIOR_presetvalue = FloatProperty(name='Ext. IOR-Preset', description='Ext. IOR', update=changed_ext_ior_preset)
    extIOR_presetstring = StringProperty(name='Ext. IOR-Preset Name', description='Ext. IOR')
    extIOR = FloatProperty(name='Ext IOR', default=1.000277, min=1.0, max=10.0, precision=6)

    nonlinear = BoolProperty(name='Use Internal Scattering', description='Use Internal Scattering', default=False)
    distribution = EnumProperty(name='Roughness Model', description='Roughness Model', items=microfacet_distribution_items, default='beckmann')

    custom_inputs = [
        {'type': 'MtsSocketFloat_alpha', 'name': 'Roughness'},
        {'type': 'MtsSocketColor_diffuseReflectance', 'name': 'Diffuse Reflectance'},
        {'type': 'MtsSocketColor_specularReflectance', 'name': 'Specular Reflectance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'plastic',
            'intIOR': self.intIOR,
            'extIOR': self.extIOR,
            'nonlinear': self.nonlinear,
            'diffuseReflectance': self.inputs['Diffuse Reflectance'].get_color_dict(export_ctx),
            'specularReflectance': self.inputs['Specular Reflectance'].get_color_dict(export_ctx),
        }

        alpha = self.inputs['Roughness'].get_float_dict(export_ctx)

        if alpha:
            params.update({
                'alpha': alpha,
                'distribution': self.distribution,
                'type': 'roughplastic',
            })

        return params

    def set_from_dict(self, ntree, params):
        if 'intIOR' in params:
            self.intIOR = params['intIOR']

        if 'extIOR' in params:
            self.extIOR = params['extIOR']

        if 'nonlinear' in params:
            self.nonlinear = params['nonlinear']

        if 'diffuseReflectance' in params:
            self.inputs['Diffuse Reflectance'].set_color_socket(ntree, params['diffuseReflectance'])

        if 'specularReflectance' in params:
            self.inputs['Specular Reflectance'].set_color_socket(ntree, params['specularReflectance'])

        if params['type'] == 'roughplastic':
            if 'distribution' in params:
                self.distribution = params['distribution']

            if 'alpha' in params:
                self.inputs['Roughness'].set_float_socket(ntree, params['alpha'])

        else:
            self.inputs['Roughness'].default_value = 0


@MitsubaNodeTypes.register
class MtsNodeBsdf_coating(mitsuba_bsdf_node, Node):
    '''Dielectric Coating material node'''
    bl_idname = 'MtsNodeBsdf_coating'
    bl_label = 'Dielectric Coating'
    plugin_types = {'coating', 'roughcoating'}

    def changed_int_ior_preset(self, context):
        # # connect preset -> property
        self.intIOR = self.intIOR_presetvalue

    def changed_ext_ior_preset(self, context):
        # # connect preset -> property
        self.extIOR = self.extIOR_presetvalue

    def draw_buttons(self, context, layout):
        self.draw_ior_menu_box(layout, 'intIOR', 'Int. IOR', 'interior')
        self.draw_ior_menu_box(layout, 'extIOR', 'Ext. IOR', 'exterior')

        layout.prop(self, 'thickness')
        layout.prop(self, 'distribution')

    intIOR_presetvalue = FloatProperty(name='Int. IOR-Preset', description='Int. IOR', update=changed_int_ior_preset)
    intIOR_presetstring = StringProperty(name='Int. IOR-Preset Name', description='Int. IOR')
    intIOR = FloatProperty(name='Int IOR', default=1.49, min=1.0, max=10.0, precision=6)

    extIOR_presetvalue = FloatProperty(name='Ext. IOR-Preset', description='Ext. IOR', update=changed_ext_ior_preset)
    extIOR_presetstring = StringProperty(name='Ext. IOR-Preset Name', description='Ext. IOR')
    extIOR = FloatProperty(name='Ext IOR', default=1.000277, min=1.0, max=10.0, precision=6)

    thickness = FloatProperty(name='Thickness', default=1.0, min=0.0, max=15.0)
    distribution = EnumProperty(name='Roughness Model', description='Roughness Model', items=microfacet_distribution_items, default='beckmann')

    custom_inputs = [
        {'type': 'MtsSocketFloat_alpha', 'name': 'Roughness'},
        {'type': 'MtsSocketColor_sigmaA', 'name': 'Absorption Coefficient'},
        {'type': 'MtsSocketColor_specularReflectance', 'name': 'Specular Reflectance'},
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'coating',
            'intIOR': self.intIOR,
            'extIOR': self.extIOR,
            'thickness': self.thickness,
            'sigmaA': self.inputs['Absorption Coefficient'].get_color_dict(export_ctx),
            'specularReflectance': self.inputs['Specular Reflectance'].get_color_dict(export_ctx),
        }

        alpha = self.inputs['Roughness'].get_float_dict(export_ctx)

        if alpha:
            params.update({
                'alpha': alpha,
                'distribution': self.distribution,
                'type': 'roughcoating',
            })

        bsdf = self.inputs['Bsdf'].get_linked_node()

        if bsdf:
            params.update({
                'bsdf': bsdf.get_bsdf_dict(export_ctx),
            })

        else:
            params.update({
                'bsdf': {'type': 'diffuse'},
            })

        return params

    def set_from_dict(self, ntree, params):
        if 'intIOR' in params:
            self.intIOR = params['intIOR']

        if 'extIOR' in params:
            self.extIOR = params['extIOR']

        if 'thickness' in params:
            self.thickness = params['thickness']

        if 'sigmaA' in params:
            self.inputs['Absorption Coefficient'].set_color_socket(ntree, params['sigmaA'])

        if 'specularReflectance' in params:
            self.inputs['Specular Reflectance'].set_color_socket(ntree, params['specularReflectance'])

        if params['type'] == 'roughcoating':
            if 'distribution' in params:
                self.distribution = params['distribution']

            if 'alpha' in params:
                self.inputs['Roughness'].set_float_socket(ntree, params['alpha'])

        else:
            self.inputs['Roughness'].default_value = 0

        if 'bsdf' in params:
            ntree.new_node_from_dict(params['bsdf'], self.inputs['Bsdf'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_bumpmap(mitsuba_bsdf_node, Node):
    '''Bumpmap material node'''
    bl_idname = 'MtsNodeBsdf_bumpmap'
    bl_label = 'Bumpmap'
    plugin_types = {'bumpmap'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'scale')

    scale = FloatProperty(name='Scale', default=1.0, min=0.001, max=100.0)

    custom_inputs = [
        {'type': 'MtsSocketTexture', 'name': 'Bumpmap Texture'},
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        texture = self.inputs['Bumpmap Texture'].get_linked_node()
        bsdf = self.inputs['Bsdf'].get_linked_node()

        if not bsdf or not texture:
            return {}

        params = {
            'type': 'bumpmap',
            'texture': {
                'type': 'scale',
                'scale': self.scale,
                'bumpmap': texture.get_texture_dict(export_ctx),
            },
            'bsdf': bsdf.get_bsdf_dict(export_ctx),
        }

        return params

    def set_from_dict(self, ntree, params):

        if 'texture' in params:
            tex = params['texture']
            bumpmap = params['texture']

            if tex['type'] == 'scale':
                if 'scale' in tex:
                    self.scale = tex['scale']

                if 'bumpmap' in tex:
                    bumpmap = tex['bumpmap']

            ntree.new_node_from_dict(bumpmap, self.inputs['Bumpmap Texture'])

        if 'bsdf' in params:
            ntree.new_node_from_dict(params['bsdf'], self.inputs['Bsdf'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_phong(mitsuba_bsdf_node, Node):
    '''Phong material node'''
    bl_idname = 'MtsNodeBsdf_phong'
    bl_label = 'Phong'
    plugin_types = {'phong'}

    custom_inputs = [
        {'type': 'MtsSocketFloat_exponent', 'name': 'Exponent'},
        {'type': 'MtsSocketColor_diffuseReflectance', 'name': 'Diffuse Reflectance'},
        {'type': 'MtsSocketColor_specularReflectance', 'name': 'Specular Reflectance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'phong',
            'exponent': self.inputs['Exponent'].get_float_dict(export_ctx),
            'diffuseReflectance': self.inputs['Diffuse Reflectance'].get_color_dict(export_ctx),
            'specularReflectance': self.inputs['Specular Reflectance'].get_color_dict(export_ctx),
        }

        return params

    def set_from_dict(self, ntree, params):
        if 'exponent' in params:
            self.inputs['Exponent'].set_float_socket(ntree, params['exponent'])

        if 'diffuseReflectance' in params:
            self.inputs['Diffuse Reflectance'].set_color_socket(ntree, params['diffuseReflectance'])

        if 'specularReflectance' in params:
            self.inputs['Specular Reflectance'].set_color_socket(ntree, params['specularReflectance'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_ward(mitsuba_bsdf_node, Node):
    '''Ward material node'''
    bl_idname = 'MtsNodeBsdf_ward'
    bl_label = 'Ward'
    plugin_types = {'ward'}

    def update_visibility(self, context):
        try:
            self.inputs['Roughness'].name = 'Roughness U' if self.anisotropic else 'Roughness'

        except:
            self.inputs['Roughness U'].name = 'Roughness U' if self.anisotropic else 'Roughness'

        self.inputs['Roughness V'].enabled = self.anisotropic

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')
        layout.prop(self, 'anisotropic')

    variant = EnumProperty(
        name='Ward Model',
        description='Ward Model',
        items=[
            ('ward', 'Ward', 'ward'),
            ('ward-duer', 'Ward-duer', 'ward-duer'),
            ('balanced', 'Balanced', 'balanced')
        ],
        default='balanced'
    )

    anisotropic = BoolProperty(
        name='Anisotropic Roughness',
        description='Use anisotropy. Allows setting different roughness values for tangent and bitangent directions.',
        default=False,
        update=update_visibility
    )

    custom_inputs = [
        {'type': 'MtsSocketFloat_alphaU', 'name': 'Roughness U'},
        {'type': 'MtsSocketFloat_alphaV', 'name': 'Roughness V'},
        {'type': 'MtsSocketColor_diffuseReflectance', 'name': 'Diffuse Reflectance'},
        {'type': 'MtsSocketColor_specularReflectance', 'name': 'Specular Reflectance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'ward',
            'variant': self.variant,
            'diffuseReflectance': self.inputs['Diffuse Reflectance'].get_color_dict(export_ctx),
            'specularReflectance': self.inputs['Specular Reflectance'].get_color_dict(export_ctx),
        }

        if self.anisotropic:
            alphaU = self.inputs['Roughness U'].get_float_dict(export_ctx, minval=0.0001)
            alphaV = self.inputs['Roughness V'].get_float_dict(export_ctx, minval=0.0001)
            params.update({
                'alphaU': alphaU,
                'alphaV': alphaV,
            })

        else:
            alpha = self.inputs['Roughness'].get_float_dict(export_ctx, minval=0.0001)
            params.update({
                'alpha': alpha,
            })

        return params

    def set_from_dict(self, ntree, params):
        if 'variant' in params:
            self.variant = params['variant']

        if 'diffuseReflectance' in params:
            self.inputs['Diffuse Reflectance'].set_color_socket(ntree, params['diffuseReflectance'])

        if 'specularReflectance' in params:
            self.inputs['Specular Reflectance'].set_color_socket(ntree, params['specularReflectance'])

        if 'alphaU' in params or 'alphaV' in params:
            self.anisotropic = True

            if 'alphaU' in params:
                self.inputs['Roughness U'].set_float_socket(ntree, params['alphaU'])

            if 'alphaV' in params:
                self.inputs['Roughness V'].set_float_socket(ntree, params['alphaV'])

        elif 'alpha' in params:
            self.anisotropic = False
            self.inputs['Roughness'].set_float_socket(ntree, params['alpha'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_blendbsdf(mitsuba_bsdf_node, Node):
    '''Blend material node'''
    bl_idname = 'MtsNodeBsdf_blendbsdf'
    bl_label = 'Blend'
    plugin_types = {'blendbsdf'}

    custom_inputs = [
        {'type': 'MtsSocketFloat_weight', 'name': 'Blending Factor'},
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf 1'},
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf 2'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = OrderedDict([
            ('type', 'blendbsdf'),
            ('weight', self.inputs['Blending Factor'].get_float_dict(export_ctx)),
        ])

        bsdf1 = self.inputs['Bsdf 1'].get_linked_node()

        if bsdf1:
            params.update([(
                'bsdf1', bsdf1.get_bsdf_dict(export_ctx),
            )])

        bsdf2 = self.inputs['Bsdf 2'].get_linked_node()

        if bsdf2:
            params.update([(
                'bsdf2', bsdf2.get_bsdf_dict(export_ctx),
            )])

        return params

    def set_from_dict(self, ntree, params):
        if 'weight' in params:
            self.inputs['Blending Factor'].set_float_socket(ntree, params['weight'])

        if 'bsdf1' in params:
            ntree.new_node_from_dict(params['bsdf1'], self.inputs['Bsdf 1'])

        if 'bsdf2' in params:
            ntree.new_node_from_dict(params['bsdf2'], self.inputs['Bsdf 2'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_mask(mitsuba_bsdf_node, Node):
    '''Mask material node'''
    bl_idname = 'MtsNodeBsdf_mask'
    bl_label = 'Mask'
    plugin_types = {'mask'}

    custom_inputs = [
        {'type': 'MtsSocketColor_opacity', 'name': 'Opacity Mask'},
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'mask',
            'opacity': self.inputs['Opacity Mask'].get_color_dict(export_ctx),
        }

        bsdf = self.inputs['Bsdf'].get_linked_node()

        if bsdf:
            params.update({
                'bsdf': bsdf.get_bsdf_dict(export_ctx),
            })

        return params

    def set_from_dict(self, ntree, params):
        if 'opacity' in params:
            self.inputs['Opacity Mask'].set_color_socket(ntree, params['opacity'])

        if 'bsdf' in params:
            ntree.new_node_from_dict(params['bsdf'], self.inputs['Bsdf'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_twosided(mitsuba_bsdf_node, Node):
    '''Two-sided material node'''
    bl_idname = 'MtsNodeBsdf_twosided'
    bl_label = 'Two-sided'
    plugin_types = {'twosided'}

    custom_inputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Front Bsdf'},
        {'type': 'MtsSocketBsdf', 'name': 'Back Bsdf'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = OrderedDict([
            ('type', 'twosided'),
        ])

        front_bsdf = self.inputs['Front Bsdf'].get_linked_node()

        if front_bsdf:
            params.update([(
                'bsdf1', front_bsdf.get_bsdf_dict(export_ctx),
            )])

        back_bsdf = self.inputs['Back Bsdf'].get_linked_node()

        if back_bsdf:
            params.update([(
                'bsdf2', back_bsdf.get_bsdf_dict(export_ctx),
            )])

        return params

    def set_from_dict(self, ntree, params):
        if 'bsdf1' in params:
            ntree.new_node_from_dict(params['bsdf1'], self.inputs['Bsdf 1'])

        if 'bsdf2' in params:
            ntree.new_node_from_dict(params['bsdf2'], self.inputs['Bsdf 2'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_difftrans(mitsuba_bsdf_node, Node):
    '''Diffuse Transmitter material node'''
    bl_idname = 'MtsNodeBsdf_difftrans'
    bl_label = 'Diffuse Transmitter'
    plugin_types = {'difftrans'}

    custom_inputs = [
        {'type': 'MtsSocketColor_transmittance', 'name': 'Diffuse Transmittance'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'difftrans',
            'transmittance': self.inputs['Diffuse Transmittance'].get_color_dict(export_ctx),
        }

        return params

    def set_from_dict(self, ntree, params):
        if 'transmittance' in params:
            self.inputs['Diffuse Transmittance'].set_color_socket(ntree, params['transmittance'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_hk(mitsuba_bsdf_node, Node):
    '''Hanrahan-Krueger material node'''
    bl_idname = 'MtsNodeBsdf_hk'
    bl_label = 'Hanrahan-Krueger'
    plugin_types = {'hk'}

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

    def draw_buttons(self, context, layout):
        self.draw_material_menu(layout)
        layout.prop(self, 'thickness')

    material = StringProperty(name='Material Name', description='Material Name')

    preset_material = StringProperty(name='material preset', default='')
    preset_sigmaS = FloatVectorProperty(name='sigmaS preset', default=(0.0, 0.0, 0.0))
    preset_sigmaA = FloatVectorProperty(name='sigmaA preset', default=(0.0, 0.0, 0.0))
    preset_g = FloatVectorProperty(name='g preset', default=(0.0, 0.0, 0.0), min=-0.999999, max=0.999999)

    useAlbSigmaT = BoolProperty(name='Use Albedo & SigmaT', description='Use Albedo & SigmaT instead SigmatS & SigmaA', default=False, update=update_visibility)

    thickness = FloatProperty(name='Thickness', default=1, min=0.0, max=15.0)

    custom_inputs = [
        {'type': 'MtsSocketColor_sigmaS', 'name': 'Scattering Coefficient'},
        {'type': 'MtsSocketColor_sigmaA', 'name': 'Absorption Coefficient'},
        {'type': 'MtsSocketSpectrum_g', 'name': 'Anisotropy'},
        {'type': 'MtsSocketColor_sigmaT', 'name': 'Extinction Coefficient'},
        {'type': 'MtsSocketColor_albedo', 'name': 'Albedo'},
    ]

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'hk',
            'thickness': self.thickness,
        }

        if self.useAlbSigmaT:
            params.update({
                'sigmaT': self.inputs['Extinction Coefficient'].get_color_dict(export_ctx),
                'albedo': self.inputs['Albedo'].get_color_dict(export_ctx),
            })

        else:
            params.update({
                'sigmaS': self.inputs['Scattering Coefficient'].get_color_dict(export_ctx),
                'sigmaA': self.inputs['Absorption Coefficient'].get_color_dict(export_ctx),
                'g': self.inputs['Anisotropy'].get_spectrum_dict(export_ctx),
            })

        #if self.g == 0:
            #params.update({'phase': {'type': 'isotropic'}})
        #else:
            #params.update({
                #'phase': {
                    #'type': 'hg',
                    #'g': self.g,
                #}
            #})

        return params

    def set_from_dict(self, ntree, params):
        if 'thickness' in params:
            self.thickness = params['thickness']

        if 'sigmaT' in params or 'albedo' in params:
            self.useAlbSigmaT = True

            if 'sigmaT' in params:
                self.inputs['Extinction Coefficient'].set_color_socket(ntree, params['sigmaT'])

            if 'albedo' in params:
                self.inputs['Albedo'].set_color_socket(ntree, params['albedo'])

        elif 'sigmaS' in params or 'sigmaA' in params:
            self.useAlbSigmaT = False

            if 'sigmaS' in params:
                self.inputs['Scattering Coefficient'].set_color_socket(ntree, params['sigmaS'])

            if 'sigmaA' in params:
                self.inputs['Absorption Coefficient'].set_color_socket(ntree, params['sigmaA'])

            if 'g' in params:
                self.inputs['Anisotropy'].set_spectrum_socket(ntree, params['g'])


@MitsubaNodeTypes.register
class MtsNodeBsdf_null(mitsuba_bsdf_node, Node):
    '''Null material node'''
    bl_idname = 'MtsNodeBsdf_null'
    bl_label = 'Null'
    plugin_types = {'null'}

    custom_outputs = [
        {'type': 'MtsSocketBsdf', 'name': 'Bsdf'},
    ]

    def get_bsdf_dict(self, export_ctx):
        params = {
            'type': 'null',
        }

        return params

    def set_from_dict(self, ntree, params):
        pass
