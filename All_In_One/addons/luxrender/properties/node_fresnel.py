# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Jens Verwiebe, Jason Clarke, Asbjørn Heid
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

import re

import bpy

from ..extensions_framework import declarative_property_group

from .. import LuxRenderAddon
from ..properties import (
    luxrender_texture_node, get_linked_node, check_node_export_texture, check_node_get_paramset
)
from ..properties.texture import (
    import_paramset_to_blender_texture, shorten_name, refresh_preview
)
from ..export import ParamSet, process_filepath_data
from ..export.materials import (
    ExportedTextures, add_texture_parameter, get_texture_from_scene
)
from ..outputs import LuxManager, LuxLog

from ..properties.node_sockets import (
    luxrender_fresnel_socket, luxrender_TC_Kr_socket
)

from ..properties.node_material import get_socket_paramsets
from ..properties.texture import luxrender_tex_fresnelname


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_fresnelcolor(luxrender_texture_node):
    """Fresnel Color Node"""
    bl_idname = 'luxrender_texture_fresnelcolor_node'
    bl_label = 'Fresnel Color'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('luxrender_TC_Kr_socket', 'Reflection Color')
        self.outputs.new('luxrender_fresnel_socket', 'Fresnel')

    def export_texture(self, make_texture):
        fresnelcolor_params = ParamSet()
        fresnelcolor_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture('fresnel', 'fresnelcolor', self.name, fresnelcolor_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_cauchy(luxrender_texture_node):
    """Cauchy Node"""
    bl_idname = 'luxrender_texture_cauchy_node'
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
        self.outputs.new('luxrender_fresnel_socket', 'Fresnel')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'use_ior')

        if self.use_ior:
            if self.cauchy_n == self.cauchy_n_presetvalue:
                menu_text = self.cauchy_n_presetstring
            else:
                menu_text = '-- Choose preset --'

            layout.menu('LUXRENDER_MT_ior_presets', text=menu_text)
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


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_fresnelname(luxrender_texture_node):
    """Fresnel Name Node"""
    bl_idname = 'luxrender_texture_fresnelname_node'
    bl_label = 'Fresnel Name'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    for prop in luxrender_tex_fresnelname.properties:
        if prop['attr'].startswith('name'):
            frname_presets = prop['items']

    frname_preset = bpy.props.EnumProperty(name='Preset', description='NK data presets', items=frname_presets,
                                           default='aluminium')
    frname_nkfile = bpy.props.StringProperty(name='Nk File', description='Nk file path', subtype='FILE_PATH')

    def init(self, context):
        self.outputs.new('luxrender_fresnel_socket', 'Fresnel')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'frname_preset')

        if self.frname_preset == 'nk':
            layout.prop(self, 'frname_nkfile')

    def export_texture(self, make_texture):
        fresnelname_params = ParamSet()

        if self.frname_preset == 'nk':  # use an NK data file
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(LuxManager.CurrentScene, self, self.frname_nkfile, fresnelname_params, 'filename')

            return make_texture('fresnel', 'fresnelname', self.name, fresnelname_params)
        else:
            # use a preset name
            fresnelname_params.add_string('name', self.frname_preset)

            return make_texture('fresnel', 'preset', self.name, fresnelname_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_sellmeier(luxrender_texture_node):
    """Sellmeier Node"""
    bl_idname = 'luxrender_texture_sellmeier_node'
    bl_label = 'Sellmeier'
    bl_icon = 'TEXTURE'
    bl_width_min = 200

    advanced = bpy.props.BoolProperty(name='Advanced', default=False)
    a = bpy.props.FloatProperty(name='A', default=1.0, min=0.001, max=10.0, precision=3)
    b = bpy.props.FloatVectorProperty(name='B', default=(0.696, 0.408, 0.879), min=0.0, max=100.0, precision=6)
    c = bpy.props.FloatVectorProperty(name='C', default=(0.0047, 0.0135, 97.93), min=0.0, max=100.0, precision=6)

    def init(self, context):
        self.outputs.new('luxrender_fresnel_socket', 'Fresnel')

    def draw_buttons(self, context, layout):
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
