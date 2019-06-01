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

from . import create_luxcore_name, warning_luxcore_node, warning_classic_node
from .. import PBRTv3Addon

from ..export import ParamSet, process_filepath_data,  get_expanded_file_name

from ..outputs import PBRTv3Manager
from ..outputs.luxcore_api import set_prop_tex

from ..properties import pbrtv3_texture_node
from ..properties.node_material import get_socket_paramsets
from ..properties.texture import pbrtv3_tex_fresnelname


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_fresnelcolor(pbrtv3_texture_node):
    """Fresnel Color Node"""
    bl_idname = 'pbrtv3_texture_fresnelcolor_node'
    bl_label = 'Fresnel Color'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('pbrtv3_TC_Kr_socket', 'Reflection Color')
        self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
        self.outputs['Fresnel'].needs_link = True

    def export_texture(self, make_texture):
        fresnelcolor_params = ParamSet()
        fresnelcolor_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture('fresnel', 'fresnelcolor', self.name, fresnelcolor_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        kr = self.inputs['Reflection Color'].export_luxcore(properties)

        set_prop_tex(properties, luxcore_name, 'type', 'fresnelcolor')
        set_prop_tex(properties, luxcore_name, 'kr', kr)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_fresnelname(pbrtv3_texture_node):
    """Fresnel Name Node"""
    bl_idname = 'pbrtv3_texture_fresnelname_node'
    bl_label = 'Fresnel Preset'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    for prop in pbrtv3_tex_fresnelname.properties:
        if prop['attr'].startswith('name'):
            frname_presets = prop['items']

    frname_preset = bpy.props.EnumProperty(name='Preset', description='NK data presets', items=frname_presets,
                                           default='aluminium')
    frname_nkfile = bpy.props.StringProperty(name='Nk File', description='Nk file path', subtype='FILE_PATH')

    def init(self, context):
        self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
        self.outputs['Fresnel'].needs_link = True

    def draw_buttons(self, context, layout):
        layout.prop(self, 'frname_preset')

        if self.frname_preset == 'nk':
            layout.prop(self, 'frname_nkfile')

    def export_texture(self, make_texture):
        fresnelname_params = ParamSet()

        if self.frname_preset == 'nk':  # use an NK data file
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(PBRTv3Manager.CurrentScene, self, self.frname_nkfile, fresnelname_params, 'filename')

            return make_texture('fresnel', 'fresnelname', self.name, fresnelname_params)
        else:
            # use a preset name
            fresnelname_params.add_string('name', self.frname_preset)

            return make_texture('fresnel', 'preset', self.name, fresnelname_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        if self.frname_preset == 'nk':  # use an NK data file
             full_name, base_name = get_expanded_file_name(self.frname_preset, self.frname_nkfile)
             set_prop_tex(properties, luxcore_name, 'type', 'fresnelsopra')
             set_prop_tex(properties, luxcore_name, 'file', full_name)
        else:
             set_prop_tex(properties, luxcore_name, 'type', 'fresnelpreset')
             set_prop_tex(properties, luxcore_name, 'name', self.frname_preset)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_fresnelfile(pbrtv3_texture_node):
    """Fresnel Sopra/Luxpop Node"""
    bl_idname = 'pbrtv3_texture_fresnelfile_node'
    bl_label = 'Fresnel NK File'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    filepath = bpy.props.StringProperty(name='Nk File', description='Nk file path', subtype='FILE_PATH')

    type_items = [
        ('fresnelsopra', 'Sopra', 'NK file with sopra format'),
        ('fresnelluxpop', 'Luxpop', 'NK file with Luxpop format')
    ]
    type = bpy.props.EnumProperty(name='Type', items=type_items)

    def init(self, context):
        self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
        self.outputs['Fresnel'].needs_link = True

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)

        layout.prop(self, 'filepath')
        layout.prop(self, 'type', expand=True)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        full_name, base_name = get_expanded_file_name(self.type, self.filepath)
        set_prop_tex(properties, luxcore_name, 'type', self.type)
        set_prop_tex(properties, luxcore_name, 'file', full_name)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_cauchy(pbrtv3_texture_node):
    """Cauchy Node"""
    bl_idname = 'pbrtv3_texture_cauchy_node'
    bl_label = 'Cauchy'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    def changed_preset(self, context):
        # connect preset -> property
        self.default_value = cauchy_n_presetvalue

    use_ior = bpy.props.BoolProperty(name='Use IOR', default=True)
    cauchy_n_presetvalue = bpy.props.FloatProperty(name='IOR-Preset', description='IOR', update=changed_preset)
    cauchy_n_presetstring = bpy.props.StringProperty(name='IOR_Preset Name', description='IOR')
    cauchy_n = bpy.props.FloatProperty(name='IOR', default=1.52, min=1.0, max=25.0, precision=6)
    cauchy_a = bpy.props.FloatProperty(name='A', default=1.458, min=0.0, max=10.0, precision=6)
    cauchy_b = bpy.props.FloatProperty(name='B', default=0.0035, min=0.0, max=10.0, precision=6)

    def init(self, context):
        self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
        self.outputs['Fresnel'].needs_link = True

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

        layout.prop(self, 'use_ior')

        if self.use_ior:
            if self.cauchy_n == self.cauchy_n_presetvalue:
                menu_text = self.cauchy_n_presetstring
            else:
                menu_text = '-- Choose IOR preset --'

            layout.menu('PBRTv3_MT_ior_presets', text=menu_text)
            layout.prop(self, 'cauchy_n')
        else:
            layout.prop(self, 'cauchy_a')

        layout.prop(self, 'cauchy_b')

    def export_texture(self, make_texture):
        cauchy_params = ParamSet()
        cauchy_params.add_float('cauchyb', self.cauchy_b)

        if not self.use_ior:
            cauchy_params.add_float('cauchya', self.cauchy_a)
        else:
            cauchy_params.add_float('index', self.cauchy_n)

        return make_texture('fresnel', 'cauchy', self.name, cauchy_params)


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_sellmeier(pbrtv3_texture_node):
    """Sellmeier Node"""
    bl_idname = 'pbrtv3_texture_sellmeier_node'
    bl_label = 'Sellmeier'
    bl_icon = 'TEXTURE'
    bl_width_min = 200

    advanced = bpy.props.BoolProperty(name='Advanced', default=False)
    a = bpy.props.FloatProperty(name='A', default=1.0, min=0.001, max=10.0, precision=3)
    b = bpy.props.FloatVectorProperty(name='B', default=(0.696, 0.408, 0.879), min=0.0, max=100.0, precision=6)
    c = bpy.props.FloatVectorProperty(name='C', default=(0.0047, 0.0135, 97.93), min=0.0, max=100.0, precision=6)

    def init(self, context):
        self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
        self.outputs['Fresnel'].needs_link = True

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

        layout.prop(self, 'advanced')

        if self.advanced:
            layout.prop(self, 'a')

        layout.prop(self, 'b')
        layout.prop(self, 'c')

    def export_texture(self, make_texture):
        sellmeier_params = ParamSet()

        if self.advanced:
            sellmeier_params.add_float('A', self.a)

        sellmeier_params.add_float('B', tuple(self.b))
        sellmeier_params.add_float('C', tuple(self.c))

        return make_texture('fresnel', 'sellmeier', self.name, sellmeier_params)
