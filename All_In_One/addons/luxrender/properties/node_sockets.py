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

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom

from .. import LuxRenderAddon
from ..properties import (luxrender_node, luxrender_material_node, get_linked_node, check_node_export_material,
                          check_node_export_texture, check_node_get_paramset, ExportedVolumes)

from ..properties.texture import (
    import_paramset_to_blender_texture, shorten_name, refresh_preview
)

from ..export import ParamSet, process_filepath_data
from ..export.materials import (
    MaterialCounter, TextureCounter, ExportedMaterials, ExportedTextures, get_texture_from_scene
)

from ..outputs import LuxManager, LuxLog

from ..properties.material import *  # for now just the big hammer for starting autogenerate sockets

# Get all float properties
def get_props(TextureParameter, attribute):
    for prop in TextureParameter.get_properties():
        if prop['attr'].endswith('floatvalue'):
            value = prop[attribute]
    return value


# Colors are simpler, so we only get the colortuple here
def get_default(TextureParameter):
    TextureParameter = TextureParameter.default
    return TextureParameter

# Custom socket types, lookup parameters here:
# http://www.blender.org/documentation/blender_python_api_2_66a
# release/bpy.props.html?highlight=bpy.props.floatproperty#bpy.props.FloatProperty

# Store our custom socket colors here as vars, so we don't have to remember what they are on every custom socket
float_socket_color = (0.63, 0.63, 0.63, 1.0)  # Same as native NodeSocketFloat
color_socket_color = (0.9, 0.9, 0.0, 1.0)  # Same as native NodeSocketColor
fresnel_socket_color = (0.33, 0.6, 0.85, 1.0)


@LuxRenderAddon.addon_register_class
class luxrender_fresnel_socket(bpy.types.NodeSocket):
    """Fresnel texture I/O socket"""
    bl_idname = 'luxrender_fresnel_socket'
    bl_label = 'IOR socket'

    def changed_preset(self, context):
        # # connect preset -> property
        self.default_value = self.fresnel_presetvalue

    # meaningful property
    def fresnel_update(self, context):
        pass

    fresnel_presetvalue = bpy.props.FloatProperty(name='IOR-Preset', description='IOR', update=changed_preset)
    fresnel_presetstring = bpy.props.StringProperty(name='IOR_Preset Name', description='IOR')
    fresnel = bpy.props.FloatProperty(name='IOR', description='Optical dataset', default=1.52, precision=6,
                                      update=fresnel_update)
    needs_link = bpy.props.BoolProperty(name='Metal Fresnel', default=False) # for hiding inappropiate ui elements

    # helper property
    def default_value_get(self):
        return self.fresnel

    def default_value_set(self, value):
        self.fresnel = value

    default_value = bpy.props.FloatProperty(name='IOR', default=1.52, precision=6, get=default_value_get,
                                            set=default_value_set)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_linked or self.needs_link:
            layout.label(text=self.name)
        else:
            box = layout.box()

            if self.fresnel == self.fresnel_presetvalue:
                menu_text = self.fresnel_presetstring
            else:
                menu_text = '-- Choose preset --'

            box.menu('LUXRENDER_MT_ior_presets', text=menu_text)
            box.prop(self, 'fresnel', text=self.name)

    # Socket color
    def draw_color(self, context, node):
        return fresnel_socket_color

    # Export routine for this socket
    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)

        if tex_node:
            print('linked from %s' % tex_node.name)

            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)

            fresnel_params = ParamSet() \
                .add_texture('fresnel', tex_name)
        else:
            fresnel_params = ParamSet() \
                .add_float('fresnel', self.fresnel)

        return fresnel_params


# #### custom color sockets #####

@LuxRenderAddon.addon_register_class
class luxrender_TC_Ka_socket(bpy.types.NodeSocket):
    """Absorption Color socket"""
    bl_idname = 'luxrender_TC_Ka_socket'
    bl_label = 'Absorption Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Absorption Color', description='Absorption Color',
                                          default=get_default(TC_Ka), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Absorption Color', default=get_default(TC_Ka), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        print('get_paramset diffuse color')
        tex_node = get_linked_node(self)

        if tex_node:
            print('linked from %s' % tex_node.name)

            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ka_params = ParamSet().add_texture('Ka', tex_name)
        else:
            ka_params = ParamSet().add_color('Ka', self.color)

        return ka_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Kd_socket(bpy.types.NodeSocket):
    """Diffuse Color socket"""
    bl_idname = 'luxrender_TC_Kd_socket'
    bl_label = 'Diffuse Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Diffuse Color', description='Diffuse Color', default=get_default(TC_Kd),
                                          subtype='COLOR', min=0.0, max=1.0, update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Diffuse Color', default=get_default(TC_Kd), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        print('get_paramset diffuse color')
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)

            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            kd_params = ParamSet().add_texture('Kd', tex_name)
        else:
            kd_params = ParamSet().add_color('Kd', self.color)

        return kd_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Kr_socket(bpy.types.NodeSocket):
    """Reflection color socket"""
    bl_idname = 'luxrender_TC_Kr_socket'
    bl_label = 'Reflection Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Reflection Color', description='Reflection Color',
                                          default=get_default(TC_Kr), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Reflection Color', default=get_default(TC_Kr), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            kr_params = ParamSet().add_texture('Kr', tex_name)
        else:
            kr_params = ParamSet().add_color('Kr', self.color)

        return kr_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Ks_socket(bpy.types.NodeSocket):
    """Specular color socket"""
    bl_idname = 'luxrender_TC_Ks_socket'
    bl_label = 'Specular Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Specular Color', description='Specular Color',
                                          default=get_default(TC_Ks), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Specular Color', default=get_default(TC_Ks), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ks_params = ParamSet() .add_texture('Ks', tex_name)
        else:
            ks_params = ParamSet().add_color('Ks', self.color)

        return ks_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Ks1_socket(bpy.types.NodeSocket):
    """Specular color socket"""
    bl_idname = 'luxrender_TC_Ks1_socket'
    bl_label = 'Specular Color 1 socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Specular Color 1', description='Specular Color 1',
                                          default=get_default(TC_Ks1), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Specular Color 1', default=get_default(TC_Ks1), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ks1_params = ParamSet().add_texture('Ks1', tex_name)
        else:
            ks1_params = ParamSet().add_color('Ks1', self.color)

        return ks1_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Ks2_socket(bpy.types.NodeSocket):
    """Specular color socket"""
    bl_idname = 'luxrender_TC_Ks2_socket'
    bl_label = 'Specular Color 2 socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Specular Color 2', description='Specular Color 2',
                                          default=get_default(TC_Ks2), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Specular Color 2', default=get_default(TC_Ks2), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ks2_params = ParamSet().add_texture('Ks2', tex_name)
        else:
            ks2_params = ParamSet().add_color('Ks2', self.color)

        return ks2_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Ks3_socket(bpy.types.NodeSocket):
    """Specular color socket"""
    bl_idname = 'luxrender_TC_Ks3_socket'
    bl_label = 'Specular Color 3 socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Specular Color 3', description='Specular Color 3',
                                          default=get_default(TC_Ks3), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Specular Color 3', default=get_default(TC_Ks3), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ks3_params = ParamSet().add_texture('Ks3', tex_name)
        else:
            ks3_params = ParamSet().add_color('Ks3', self.color)

        return ks3_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_Kt_socket(bpy.types.NodeSocket):
    """Transmission Color socket"""
    bl_idname = 'luxrender_TC_Kt_socket'
    bl_label = 'Transmission Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Transmission Color', description='Transmission Color',
                                          default=get_default(TC_Kt), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Transmission Color', default=get_default(TC_Kt),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            kt_params = ParamSet().add_texture('Kt', tex_name)
        else:
            kt_params = ParamSet().add_color('Kt', self.color)

        return kt_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_warp_Kd_socket(bpy.types.NodeSocket):
    """Warp Diffuse Color socket"""
    bl_idname = 'luxrender_TC_warp_Kd_socket'
    bl_label = 'Warp Diffuse socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Warp Diffuse Color', description='Warp Diffuse Color',
                                          default=get_default(TC_warp_Kd), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Warp Diffuse Color', default=get_default(TC_warp_Kd),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)

            warp_kd_params = ParamSet().add_texture('warp_Kd', tex_name)
        else:
            warp_kd_params = ParamSet().add_color('warp_Kd', self.color)

        return warp_kd_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_warp_Ks_socket(bpy.types.NodeSocket):
    """Warp Diffuse Color socket"""
    bl_idname = 'luxrender_TC_warp_Ks_socket'
    bl_label = 'Warp Specular socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Warp Specular Color', description='Warp Specular Color',
                                          default=get_default(TC_warp_Ks), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Warp Specular Color', default=get_default(TC_warp_Ks),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            warp_ks_params = ParamSet().add_texture('warp_Ks', tex_name)
        else:
            warp_ks_params = ParamSet().add_color('warp_Ks', self.color)

        return warp_ks_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_weft_Kd_socket(bpy.types.NodeSocket):
    """Weft Diffuse Color socket"""
    bl_idname = 'luxrender_TC_weft_Kd_socket'
    bl_label = 'Weft Diffuse socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Weft Diffuse Color', description='Weft Diffuse Color',
                                          default=get_default(TC_weft_Kd), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Weft Diffuse Color', default=get_default(TC_weft_Kd),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)

            weft_kd_params = ParamSet().add_texture('weft_Kd', tex_name)
        else:
            weft_kd_params = ParamSet().add_color('weft_Kd', self.color)

        return weft_kd_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_weft_Ks_socket(bpy.types.NodeSocket):
    """Weft Specular Color socket"""
    bl_idname = 'luxrender_TC_weft_Ks_socket'
    bl_label = 'Weft Specular socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Weft Specular Color', description='Weft Specular Color',
                                          default=get_default(TC_weft_Ks), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Weft Specular Color', default=get_default(TC_weft_Ks),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            weft_ks_params = ParamSet().add_texture('weft_Ks', tex_name)
        else:
            weft_ks_params = ParamSet().add_color('weft_Ks', self.color)

        return weft_ks_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_backface_Ka_socket(bpy.types.NodeSocket):
    """Backface Absorption Color socket"""
    bl_idname = 'luxrender_TC_backface_Ka_socket'
    bl_label = 'Backface Absorption socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Backface Absorption Color', description='Backface Absorption Color',
                                          default=get_default(TC_backface_Ka), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Backface Absorption Color', default=get_default(TC_backface_Ka),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            backface_ka_params = ParamSet().add_texture('backface_Ka', tex_name)
        else:
            backface_ka_params = ParamSet().add_color('backface_Ka', self.color)

        return backface_ka_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_backface_Ks_socket(bpy.types.NodeSocket):
    """Backface Specular Color socket"""
    bl_idname = 'luxrender_TC_backface_Ks_socket'
    bl_label = 'Backface Specular socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Backface Specular Color', description='Backface Specular Color',
                                          default=get_default(TC_backface_Ks), subtype='COLOR', min=0.0, max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Backface Specular Color', default=get_default(TC_backface_Ks),
                                                  subtype='COLOR', get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            backface_ks_params = ParamSet().add_texture('backface_Ks', tex_name)
        else:
            backface_ks_params = ParamSet().add_color('backface_Ks', self.color)

        return backface_ks_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_L_socket(bpy.types.NodeSocket):
    """Light Color socket"""
    bl_idname = 'luxrender_TC_L_socket'
    bl_label = 'Light Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Color', description='Color', default=get_default(TC_L), subtype='COLOR',
                                          min=0.0, max=1.0, update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Color', default=get_default(TC_L), subtype='COLOR',
                                                  get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            L_params = ParamSet().add_texture('L', tex_name)
        else:
            L_params = ParamSet().add_color('L', self.color)

        return L_params


@LuxRenderAddon.addon_register_class
class luxrender_AC_absorption_socket(bpy.types.NodeSocket):
    """Volume absorption Color socket"""
    bl_idname = 'luxrender_AC_absorption_socket'
    bl_label = 'Absorption Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Absorption Color', description='Absorption Color',
                                          default=(0.0, 0.0, 0.0), subtype='COLOR', min=0.0, soft_max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Absorption Color', description='Absorption Color',
                                                  default=(0.0, 0.0, 0.0), subtype='COLOR', min=0.0, soft_max=1.0,
                                                  update=color_update)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ac_params = ParamSet().add_texture('absorption', tex_name)
        else:
            ac_params = ParamSet().add_color('absorption', self.color)

        return ac_params


@LuxRenderAddon.addon_register_class
class luxrender_SC_absorption_socket(bpy.types.NodeSocket):
    """Volume scatter absorption Color socket"""
    bl_idname = 'luxrender_SC_absorption_socket'
    bl_label = 'Scattering Absorption socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Absorption Color', description='Absorption Color',
                                          default=(0.0, 0.0, 0.0), subtype='COLOR', min=0.0, soft_max=1.0,
                                          update=color_update)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Absorption Color', description='Absorption Color',
                                                  default=(0.0, 0.0, 0.0), subtype='COLOR', min=0.0, soft_max=1.0,
                                                  update=color_update)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            ac_params = ParamSet().add_texture('sigma_a', tex_name)
        else:
            ac_params = ParamSet().add_color('sigma_a', self.color)

        return ac_params


@LuxRenderAddon.addon_register_class
class luxrender_SC_color_socket(bpy.types.NodeSocket):
    """Scattering Color socket"""
    bl_idname = 'luxrender_SC_color_socket'
    bl_label = 'Scattering Color socket'

    # meaningful property
    def color_update(self, context):
        pass

    color = bpy.props.FloatVectorProperty(name='Scattering Color', description='Scattering Color',
                                          default=(0.0, 0.0, 0.0), subtype='COLOR', min=0.0, soft_max=1.0)

    # helper property
    def default_value_get(self):
        return self.color

    def default_value_set(self, value):
        self.color = value

    default_value = bpy.props.FloatVectorProperty(name='Scattering Color', description='Scattering Color',
                                                  default=(0.0, 0.0, 0.0), subtype='COLOR', min=0.0, soft_max=1.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'color', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            sc_params = ParamSet().add_texture('sigma_s', tex_name)
        else:
            sc_params = ParamSet().add_color('sigma_s', self.color)

        return sc_params


# #### custom float sockets #####

@LuxRenderAddon.addon_register_class
class luxrender_TF_amount_socket(bpy.types.NodeSocket):
    """Amount socket"""
    bl_idname = 'luxrender_TF_amount_socket'
    bl_label = 'Amount socket'

    # meaningful property
    def amount_update(self, context):
        pass

    amount = bpy.props.FloatProperty(name=get_props(TF_amount, 'name'), description=get_props(TF_amount, 'description'),
                                     default=get_props(TF_amount, 'default'), subtype=get_props(TF_amount, 'subtype'),
                                     unit=get_props(TF_amount, 'unit'), min=get_props(TF_amount, 'min'),
                                     max=get_props(TF_amount, 'max'), soft_min=get_props(TF_amount, 'soft_min'),
                                     soft_max=get_props(TF_amount, 'soft_max'),
                                     precision=get_props(TF_amount, 'precision'), update=amount_update)

    # helper property
    def default_value_get(self):
        return self.amount

    def default_value_set(self, value):
        self.amount = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_amount, 'name'), default=get_props(TF_amount, 'default'),
                                            subtype=get_props(TF_amount, 'subtype'), unit=get_props(TF_amount, 'unit'),
                                            min=get_props(TF_amount, 'min'), max=get_props(TF_amount, 'max'),
                                            soft_min=get_props(TF_amount, 'soft_min'),
                                            soft_max=get_props(TF_amount, 'soft_max'),
                                            precision=get_props(TF_amount, 'precision'), get=default_value_get,
                                            set=default_value_set)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'amount', text=self.name)

    # Socket color
    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        print('get_paramset amount')
        tex_node = get_linked_node(self)
        if not tex_node is None:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            amount_params = ParamSet().add_texture('amount', tex_name)
        else:
            print('value %f' % self.amount)
            amount_params = ParamSet().add_float('amount', self.amount)

        return amount_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_bump_socket(bpy.types.NodeSocket):
    """Bump socket"""
    bl_idname = 'luxrender_TF_bump_socket'
    bl_label = 'Bump socket'

    # meaningful property
    def bump_update(self, context):
        pass

    bump = bpy.props.FloatProperty(name=get_props(TF_bumpmap, 'name'), description=get_props(TF_bumpmap, 'description'),
                                   default=get_props(TF_bumpmap, 'default'), subtype=get_props(TF_bumpmap, 'subtype'),
                                   unit=get_props(TF_bumpmap, 'unit'), min=get_props(TF_bumpmap, 'min'),
                                   max=get_props(TF_bumpmap, 'max'), soft_min=get_props(TF_bumpmap, 'soft_min'),
                                   soft_max=get_props(TF_bumpmap, 'soft_max'),
                                   precision=get_props(TF_bumpmap, 'precision'), update=bump_update)

    # helper property
    def default_value_get(self):
        return self.bump

    def default_value_set(self, value):
        self.bump = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_bumpmap, 'name'),
                                            description=get_props(TF_bumpmap, 'description'),
                                            default=get_props(TF_bumpmap, 'default'),
                                            subtype=get_props(TF_bumpmap, 'subtype'),
                                            unit=get_props(TF_bumpmap, 'unit'), min=get_props(TF_bumpmap, 'min'),
                                            max=get_props(TF_bumpmap, 'max'),
                                            soft_min=get_props(TF_bumpmap, 'soft_min'),
                                            soft_max=get_props(TF_bumpmap, 'soft_max'),
                                            precision=get_props(TF_bumpmap, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        bumpmap_params = ParamSet()
        tex_node = get_linked_node(self)

        if tex_node and check_node_export_texture(tex_node):
            # only export linked bumpmap sockets
            tex_name = tex_node.export_texture(make_texture)
            bumpmap_params.add_texture('bumpmap', tex_name)

        return bumpmap_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_cauchyb_socket(bpy.types.NodeSocket):
    """Cauchy B socket"""
    bl_idname = 'luxrender_TF_cauchyb_socket'
    bl_label = 'Cauchy B socket'

    # meaningful property
    def cauchyb_update(self, context):
        pass

    cauchyb = bpy.props.FloatProperty(name=get_props(TF_cauchyb, 'name'),
                                      description=get_props(TF_cauchyb, 'description'),
                                      default=get_props(TF_cauchyb, 'default'),
                                      subtype=get_props(TF_cauchyb, 'subtype'), min=get_props(TF_cauchyb, 'min'),
                                      max=get_props(TF_cauchyb, 'max'), soft_min=get_props(TF_cauchyb, 'soft_min'),
                                      soft_max=get_props(TF_cauchyb, 'soft_max'),
                                      precision=get_props(TF_cauchyb, 'precision'), update=cauchyb_update)

    # helper property
    def default_value_get(self):
        return self.cauchyb

    def default_value_set(self, value):
        self.cauchyb = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_cauchyb, 'name'),
                                            default=get_props(TF_cauchyb, 'default'),
                                            subtype=get_props(TF_cauchyb, 'subtype'), min=get_props(TF_cauchyb, 'min'),
                                            max=get_props(TF_cauchyb, 'max'),
                                            soft_min=get_props(TF_cauchyb, 'soft_min'),
                                            soft_max=get_props(TF_cauchyb, 'soft_max'),
                                            precision=get_props(TF_cauchyb, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'cauchyb', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            cauchyb_params = ParamSet().add_texture('cauchyb', tex_name)
        else:
            cauchyb_params = ParamSet().add_float('cauchyb', self.cauchyb)

        return cauchyb_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_film_ior_socket(bpy.types.NodeSocket):
    """Thin film IOR socket"""
    bl_idname = 'luxrender_TF_film_ior_socket'
    bl_label = 'Thin Film IOR socket'

    def changed_preset(self, context):
        # # connect preset -> property
        self.default_value = self.filmindex_presetvalue

    # meaningful property
    def filmindex_update(self, context):
        pass

    filmindex_presetvalue = bpy.props.FloatProperty(name='IOR-Preset', description='IOR', update=changed_preset)
    filmindex_presetstring = bpy.props.StringProperty(name='IOR_Preset Name', description='IOR')
    filmindex = bpy.props.FloatProperty(name=get_props(TF_filmindex, 'name'),
                                        description=get_props(TF_filmindex, 'description'),
                                        default=get_props(TF_filmindex, 'default'),
                                        subtype=get_props(TF_filmindex, 'subtype'), min=get_props(TF_filmindex, 'min'),
                                        max=get_props(TF_filmindex, 'max'),
                                        soft_min=get_props(TF_filmindex, 'soft_min'),
                                        soft_max=get_props(TF_filmindex, 'soft_max'),
                                        precision=get_props(TF_filmindex, 'precision'), update=filmindex_update)

    # helper property
    def default_value_get(self):
        return self.filmindex

    def default_value_set(self, value):
        self.filmindex = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_filmindex, 'name'),
                                            default=get_props(TF_filmindex, 'default'),
                                            subtype=get_props(TF_filmindex, 'subtype'),
                                            min=get_props(TF_filmindex, 'min'), max=get_props(TF_filmindex, 'max'),
                                            soft_min=get_props(TF_filmindex, 'soft_min'),
                                            soft_max=get_props(TF_filmindex, 'soft_max'),
                                            precision=get_props(TF_filmindex, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            if 'IOR' in self.node.inputs.keys():  # index/filmindex presets interfere, show simple property only then
                layout.prop(self, 'filmindex', text=self.name)
            else:  # show presetchooser for all other mat
                box = layout.box()

                if self.filmindex == self.filmindex_presetvalue:
                    menu_text = self.filmindex_presetstring
                else:
                    menu_text = '-- Choose preset --'

                box.menu('LUXRENDER_MT_ior_presets', text=menu_text)
                box.prop(self, 'filmindex', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            filmindex_params = ParamSet().add_texture('filmindex', tex_name)
        else:
            filmindex_params = ParamSet().add_float('filmindex', self.filmindex)

        return filmindex_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_film_thick_socket(bpy.types.NodeSocket):
    """Thin film thickness socket"""
    bl_idname = 'luxrender_TF_film_thick_socket'
    bl_label = 'Thin Film thickness socket'

    # meaningful property
    def film_update(self, context):
        pass

    film = bpy.props.FloatProperty(name=get_props(TF_film, 'name'), description=get_props(TF_film, 'description'),
                                   default=get_props(TF_film, 'default'), subtype=get_props(TF_film, 'subtype'),
                                   min=get_props(TF_film, 'min'), max=get_props(TF_film, 'max'),
                                   soft_min=get_props(TF_film, 'soft_min'), soft_max=get_props(TF_film, 'soft_max'),
                                   precision=get_props(TF_film, 'precision'), update=film_update)

    # helper property
    def default_value_get(self):
        return self.film

    def default_value_set(self, value):
        self.film = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_film, 'name'), default=get_props(TF_film, 'default'),
                                            subtype=get_props(TF_film, 'subtype'), min=get_props(TF_film, 'min'),
                                            max=get_props(TF_film, 'max'), soft_min=get_props(TF_film, 'soft_min'),
                                            soft_max=get_props(TF_film, 'soft_max'),
                                            precision=get_props(TF_film, 'precision'), get=default_value_get,
                                            set=default_value_set)


    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'film', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            film_params = ParamSet().add_texture('film', tex_name)
        else:
            film_params = ParamSet().add_float('film', self.film)

        return film_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_ior_socket(bpy.types.NodeSocket):
    """IOR socket"""
    bl_idname = 'luxrender_TF_ior_socket'
    bl_label = 'IOR socket'

    def changed_preset(self, context):
        # # connect preset -> property
        self.default_value = self.index_presetvalue

    # meaningful property
    def index_update(self, context):
        pass

    index_presetvalue = bpy.props.FloatProperty(name='IOR-Preset', description='IOR', update=changed_preset)
    index_presetstring = bpy.props.StringProperty(name='IOR_Preset Name', description='IOR')
    index = bpy.props.FloatProperty(name=get_props(TF_index, 'name'), description=get_props(TF_index, 'description'),
                                    default=get_props(TF_index, 'default'), subtype=get_props(TF_index, 'subtype'),
                                    min=get_props(TF_index, 'min'), max=get_props(TF_index, 'max'),
                                    soft_min=get_props(TF_index, 'soft_min'), soft_max=get_props(TF_index, 'soft_max'),
                                    precision=get_props(TF_index, 'precision'), update=index_update)

    # helper property
    def default_value_get(self):
        return self.index

    def default_value_set(self, value):
        self.index = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_index, 'name'), default=get_props(TF_index, 'default'),
                                            subtype=get_props(TF_index, 'subtype'), min=get_props(TF_index, 'min'),
                                            max=get_props(TF_index, 'max'), soft_min=get_props(TF_index, 'soft_min'),
                                            soft_max=get_props(TF_index, 'soft_max'),
                                            precision=get_props(TF_index, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            box = layout.box()

            if self.index == self.index_presetvalue:
                menu_text = self.index_presetstring
            else:
                menu_text = '-- Choose preset --'

            box.menu('LUXRENDER_MT_ior_presets', text=menu_text)
            box.prop(self, 'index', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)

            index_params = ParamSet().add_texture('index', tex_name)
        else:
            index_params = ParamSet().add_float('index', self.index)

        return index_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_uroughness_socket(bpy.types.NodeSocket):
    """U-Roughness socket"""
    bl_idname = 'luxrender_TF_uroughness_socket'
    bl_label = 'U-Roughness socket'

    # meaningful property
    def uroughness_update(self, context):
        pass

    sync_vroughness = bpy.props.BoolProperty(name='Sync V to U', default=True)
    uroughness = bpy.props.FloatProperty(name=get_props(TF_uroughness, 'name'),
                                         description=get_props(TF_uroughness, 'description'),
                                         default=get_props(TF_uroughness, 'default'),
                                         subtype=get_props(TF_uroughness, 'subtype'),
                                         min=get_props(TF_uroughness, 'min'), max=get_props(TF_uroughness, 'max'),
                                         soft_min=get_props(TF_uroughness, 'soft_min'),
                                         soft_max=get_props(TF_uroughness, 'soft_max'),
                                         precision=get_props(TF_uroughness, 'precision'), update=uroughness_update)

    # helper property
    def default_value_get(self):
        return self.uroughness

    def default_value_set(self, value):
        self.uroughness = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_uroughness, 'name'),
                                            default=get_props(TF_uroughness, 'default'),
                                            subtype=get_props(TF_uroughness, 'subtype'),
                                            min=get_props(TF_uroughness, 'min'), max=get_props(TF_uroughness, 'max'),
                                            soft_min=get_props(TF_uroughness, 'soft_min'),
                                            soft_max=get_props(TF_uroughness, 'soft_max'),
                                            precision=get_props(TF_uroughness, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'uroughness', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        print('get_paramset uroughness')
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)

            if self.sync_vroughness:
                print("Syncing V-Roughness: ")
                roughness_params = ParamSet() \
                    .add_texture('uroughness', tex_name) \
                    .add_texture('vroughness', tex_name)
            else:
                roughness_params = ParamSet() \
                    .add_texture('uroughness', tex_name)

        else:
            if self.sync_vroughness:
                print("Syncing V-Roughness: ")
                roughness_params = ParamSet() \
                    .add_float('uroughness', self.uroughness) \
                    .add_float('vroughness', self.uroughness)
            else:
                roughness_params = ParamSet() \
                    .add_float('uroughness', self.uroughness)

        return roughness_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_vroughness_socket(bpy.types.NodeSocket):
    """V-Roughness socket"""
    bl_idname = 'luxrender_TF_vroughness_socket'
    bl_label = 'V-Roughness socket'

    # meaningful property
    def vroughness_update(self, context):
        pass

    vroughness = bpy.props.FloatProperty(name=get_props(TF_vroughness, 'name'),
                                         description=get_props(TF_vroughness, 'description'),
                                         default=get_props(TF_vroughness, 'default'),
                                         subtype=get_props(TF_vroughness, 'subtype'),
                                         min=get_props(TF_vroughness, 'min'), max=get_props(TF_vroughness, 'max'),
                                         soft_min=get_props(TF_vroughness, 'soft_min'),
                                         soft_max=get_props(TF_vroughness, 'soft_max'),
                                         precision=get_props(TF_uroughness, 'precision'), update=vroughness_update)

    # helper property
    def default_value_get(self):
        return self.vroughness

    def default_value_set(self, value):
        self.vroughness = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_vroughness, 'name'),
                                            default=get_props(TF_vroughness, 'default'),
                                            subtype=get_props(TF_vroughness, 'subtype'),
                                            min=get_props(TF_vroughness, 'min'), max=get_props(TF_vroughness, 'max'),
                                            soft_min=get_props(TF_vroughness, 'soft_min'),
                                            soft_max=get_props(TF_vroughness, 'soft_max'),
                                            precision=get_props(TF_uroughness, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'vroughness', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        print('get_paramset vroughness')
        tex_node = get_linked_node(self)
        if tex_node:
            print('linked from %s' % tex_node.name)
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            roughness_params = ParamSet().add_texture('vroughness', tex_name)
        else:
            roughness_params = ParamSet().add_float('vroughness', self.vroughness)

        return roughness_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_sigma_socket(bpy.types.NodeSocket):
    """Sigma socket"""
    bl_idname = 'luxrender_TF_sigma_socket'
    bl_label = 'Sigma socket'

    # meaningful property
    def sigma_update(self, context):
        pass

    sigma = bpy.props.FloatProperty(name=get_props(TF_sigma, 'name'), description=get_props(TF_sigma, 'description'),
                                    default=get_props(TF_sigma, 'default'), subtype=get_props(TF_sigma, 'subtype'),
                                    min=get_props(TF_sigma, 'min'), max=get_props(TF_sigma, 'max'),
                                    soft_min=get_props(TF_sigma, 'soft_min'), soft_max=get_props(TF_sigma, 'soft_max'),
                                    precision=get_props(TF_sigma, 'precision'), update=sigma_update)

    # helper property
    def default_value_get(self):
        return self.sigma

    def default_value_set(self, value):
        self.sigma = value

    default_value = bpy.props.FloatProperty(name="Sigma", default=get_props(TF_sigma, 'default'),
                                            subtype=get_props(TF_sigma, 'subtype'), min=get_props(TF_sigma, 'min'),
                                            max=get_props(TF_sigma, 'max'), soft_min=get_props(TF_sigma, 'soft_min'),
                                            soft_max=get_props(TF_sigma, 'soft_max'),
                                            precision=get_props(TF_sigma, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'sigma', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            sigma_params = ParamSet().add_texture('sigma', tex_name)
        else:
            sigma_params = ParamSet().add_float('sigma', self.sigma)

        return sigma_params


@LuxRenderAddon.addon_register_class
class luxrender_SC_asymmetry_socket(bpy.types.NodeSocket):
    """Scattering asymmetry socket"""
    bl_idname = 'luxrender_SC_asymmetry_socket'
    bl_label = 'Scattering Asymmetry socket'

    # meaningful property
    def sc_asym_update(self, context):
        pass

    sc_asym = bpy.props.FloatVectorProperty(name='Asymmetry',
                                            description='Scattering asymmetry RGB. -1 means backscatter, 0 is isotropic, 1 is forwards scattering',
                                            default=(0.0, 0.0, 0.0), min=-1.0, max=1.0, precision=4,
                                            update=sc_asym_update)

    # helper property
    def default_value_get(self):
        return self.sc_asym

    def default_value_set(self, value):
        self.sc_asym = value

    default_value = bpy.props.FloatVectorProperty(name='Asymmetry', default=(0.0, 0.0, 0.0), min=-1.0, max=1.0,
                                                  precision=4, get=default_value_get, set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            col = layout.column()
            col.label(text=self.name)
            col.prop(self, 'sc_asym', text='')

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            sc_asym_params = ParamSet().add_texture('g', tex_name)
        else:
            sc_asym_params = ParamSet().add_color('g', self.sc_asym)

        return sc_asym_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_d_socket(bpy.types.NodeSocket):
    """Absorption depth socket"""
    bl_idname = 'luxrender_TF_d_socket'
    bl_label = 'Absorption Depth socket'

    # meaningful property
    def d_update(self, context):
        pass

    d = bpy.props.FloatProperty(name=get_props(TF_d, 'name'), description=get_props(TF_d, 'description'),
                                default=get_props(TF_d, 'default'), subtype=get_props(TF_d, 'subtype'),
                                min=get_props(TF_d, 'min'), max=get_props(TF_d, 'max'),
                                soft_min=get_props(TF_d, 'soft_min'), soft_max=get_props(TF_d, 'soft_max'),
                                precision=get_props(TF_d, 'precision'), update=d_update)

    # helper property
    def default_value_get(self):
        return self.d

    def default_value_set(self, value):
        self.d = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_d, 'name'), default=get_props(TF_d, 'default'),
                                            subtype=get_props(TF_d, 'subtype'), min=get_props(TF_d, 'min'),
                                            max=get_props(TF_d, 'max'), soft_min=get_props(TF_d, 'soft_min'),
                                            soft_max=get_props(TF_d, 'soft_max'),
                                            precision=get_props(TF_d, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'd', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            d_params = ParamSet().add_texture('d', tex_name)
        else:
            d_params = ParamSet().add_float('d', self.d)

        return d_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_OP1_socket(bpy.types.NodeSocket):
    """Opacity1 socket"""
    bl_idname = 'luxrender_TF_OP1_socket'
    bl_label = 'Opacity1 socket'

    # meaningful property
    def opacity1_update(self, context):
        pass

    opacity1 = bpy.props.FloatProperty(name=get_props(TF_OP1, 'name'), description=get_props(TF_OP1, 'description'),
                                       default=get_props(TF_OP1, 'default'), subtype=get_props(TF_OP1, 'subtype'),
                                       min=get_props(TF_OP1, 'min'), max=get_props(TF_OP1, 'max'),
                                       soft_min=get_props(TF_OP1, 'soft_min'), soft_max=get_props(TF_OP1, 'soft_max'),
                                       precision=get_props(TF_OP1, 'precision'), update=opacity1_update)

    # helper property
    def default_value_get(self):
        return self.opacity1

    def default_value_set(self, value):
        self.opacity1 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_OP1, 'name'), default=get_props(TF_OP1, 'default'),
                                            subtype=get_props(TF_OP1, 'subtype'), min=get_props(TF_OP1, 'min'),
                                            max=get_props(TF_OP1, 'max'), soft_min=get_props(TF_OP1, 'soft_min'),
                                            soft_max=get_props(TF_OP1, 'soft_max'),
                                            precision=get_props(TF_OP1, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'opacity1', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            opacity1_params = ParamSet().add_texture('opacity1', tex_name)
        else:
            opacity1_params = ParamSet().add_float('opacity1', self.opacity1)

        return opacity1_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_OP2_socket(bpy.types.NodeSocket):
    """Opacity2 socket"""
    bl_idname = 'luxrender_TF_OP2_socket'
    bl_label = 'Opacity2 socket'

    # meaningful property
    def opacity2_update(self, context):
        pass

    opacity2 = bpy.props.FloatProperty(name=get_props(TF_OP2, 'name'), description=get_props(TF_OP2, 'description'),
                                       default=get_props(TF_OP2, 'default'), subtype=get_props(TF_OP2, 'subtype'),
                                       min=get_props(TF_OP2, 'min'), max=get_props(TF_OP2, 'max'),
                                       soft_min=get_props(TF_OP2, 'soft_min'), soft_max=get_props(TF_OP2, 'soft_max'),
                                       precision=get_props(TF_OP2, 'precision'), update=opacity2_update)

    # helper property
    def default_value_get(self):
        return self.opacity2

    def default_value_set(self, value):
        self.opacity2 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_OP2, 'name'), default=get_props(TF_OP2, 'default'),
                                            subtype=get_props(TF_OP2, 'subtype'), min=get_props(TF_OP2, 'min'),
                                            max=get_props(TF_OP2, 'max'), soft_min=get_props(TF_OP2, 'soft_min'),
                                            soft_max=get_props(TF_OP2, 'soft_max'),
                                            precision=get_props(TF_OP2, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'opacity2', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            opacity2_params = ParamSet().add_texture('opacity2', tex_name)
        else:
            opacity2_params = ParamSet().add_float('opacity2', self.opacity2)

        return opacity2_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_OP3_socket(bpy.types.NodeSocket):
    """Opacity3 socket"""
    bl_idname = 'luxrender_TF_OP3_socket'
    bl_label = 'Opacity3 socket'

    # meaningful property
    def opacity3_update(self, context):
        pass

    opacity3 = bpy.props.FloatProperty(name=get_props(TF_OP3, 'name'), description=get_props(TF_OP3, 'description'),
                                       default=get_props(TF_OP3, 'default'), subtype=get_props(TF_OP3, 'subtype'),
                                       min=get_props(TF_OP3, 'min'), max=get_props(TF_OP3, 'max'),
                                       soft_min=get_props(TF_OP3, 'soft_min'), soft_max=get_props(TF_OP3, 'soft_max'),
                                       precision=get_props(TF_OP3, 'precision'), update=opacity3_update)

    # helper property
    def default_value_get(self):
        return self.opacity3

    def default_value_set(self, value):
        self.opacity3 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_OP3, 'name'), default=get_props(TF_OP3, 'default'),
                                            subtype=get_props(TF_OP3, 'subtype'), min=get_props(TF_OP3, 'min'),
                                            max=get_props(TF_OP3, 'max'), soft_min=get_props(TF_OP3, 'soft_min'),
                                            soft_max=get_props(TF_OP3, 'soft_max'),
                                            precision=get_props(TF_OP3, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'opacity3', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            opacity3_params = ParamSet().add_texture('opacity3', tex_name)
        else:
            opacity3_params = ParamSet().add_float('opacity3', self.opacity3)

        return opacity3_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_OP4_socket(bpy.types.NodeSocket):
    """Opacity4 socket"""
    bl_idname = 'luxrender_TF_OP4_socket'
    bl_label = 'Opacity4 socket'

    # meaningful property
    def opacity4_update(self, context):
        pass

    opacity4 = bpy.props.FloatProperty(name=get_props(TF_OP4, 'name'), description=get_props(TF_OP4, 'description'),
                                       default=get_props(TF_OP4, 'default'), subtype=get_props(TF_OP4, 'subtype'),
                                       min=get_props(TF_OP4, 'min'), max=get_props(TF_OP4, 'max'),
                                       soft_min=get_props(TF_OP4, 'soft_min'), soft_max=get_props(TF_OP4, 'soft_max'),
                                       precision=get_props(TF_OP4, 'precision'), update=opacity4_update)

    # helper property
    def default_value_get(self):
        return self.opacity4

    def default_value_set(self, value):
        self.opacity4 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_OP4, 'name'), default=get_props(TF_OP4, 'default'),
                                            subtype=get_props(TF_OP4, 'subtype'), min=get_props(TF_OP4, 'min'),
                                            max=get_props(TF_OP4, 'max'), soft_min=get_props(TF_OP4, 'soft_min'),
                                            soft_max=get_props(TF_OP4, 'soft_max'),
                                            precision=get_props(TF_OP4, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'opacity4', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            opacity4_params = ParamSet().add_texture('opacity4', tex_name)
        else:
            opacity4_params = ParamSet().add_float('opacity4', self.opacity4)

        return opacity4_params


# Sockets for carpaint nodes

@LuxRenderAddon.addon_register_class
class luxrender_TF_M1_socket(bpy.types.NodeSocket):
    """M1 socket"""
    bl_idname = 'luxrender_TF_M1_socket'
    bl_label = 'M1 socket'

    # meaningful property
    def M1_update(self, context):
        pass

    M1 = bpy.props.FloatProperty(name=get_props(TF_M1, 'name'), description=get_props(TF_M1, 'description'),
                                 default=get_props(TF_M1, 'default'), subtype=get_props(TF_M1, 'subtype'),
                                 min=get_props(TF_M1, 'min'), max=get_props(TF_M1, 'max'),
                                 soft_min=get_props(TF_M1, 'soft_min'), soft_max=get_props(TF_M1, 'soft_max'),
                                 precision=get_props(TF_M1, 'precision'), update=M1_update)

    # helper property
    def default_value_get(self):
        return self.M1

    def default_value_set(self, value):
        self.M1 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_M1, 'name'), default=get_props(TF_M1, 'default'),
                                            subtype=get_props(TF_M1, 'subtype'), min=get_props(TF_M1, 'min'),
                                            max=get_props(TF_M1, 'max'), soft_min=get_props(TF_M1, 'soft_min'),
                                            soft_max=get_props(TF_M1, 'soft_max'),
                                            precision=get_props(TF_M1, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'M1', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            M1_params = ParamSet().add_texture('M1', tex_name)
        else:
            M1_params = ParamSet().add_float('M1', self.M1)

        return M1_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_M2_socket(bpy.types.NodeSocket):
    """M2 socket"""
    bl_idname = 'luxrender_TF_M2_socket'
    bl_label = 'M2 socket'

    # meaningful property
    def M2_update(self, context):
        pass

    M2 = bpy.props.FloatProperty(name=get_props(TF_M2, 'name'), description=get_props(TF_M2, 'description'),
                                 default=get_props(TF_M2, 'default'), subtype=get_props(TF_M2, 'subtype'),
                                 min=get_props(TF_M2, 'min'), max=get_props(TF_M2, 'max'),
                                 soft_min=get_props(TF_M2, 'soft_min'), soft_max=get_props(TF_M2, 'soft_max'),
                                 precision=get_props(TF_M2, 'precision'), update=M2_update)

    # helper property
    def default_value_get(self):
        return self.M2

    def default_value_set(self, value):
        self.M2 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_M2, 'name'), default=get_props(TF_M2, 'default'),
                                            subtype=get_props(TF_M2, 'subtype'), min=get_props(TF_M2, 'min'),
                                            max=get_props(TF_M2, 'max'), soft_min=get_props(TF_M2, 'soft_min'),
                                            soft_max=get_props(TF_M2, 'soft_max'),
                                            precision=get_props(TF_M2, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'M2', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            M2_params = ParamSet().add_texture('M2', tex_name)
        else:
            M2_params = ParamSet().add_float('M2', self.M2)

        return M2_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_M3_socket(bpy.types.NodeSocket):
    """M3 socket"""
    bl_idname = 'luxrender_TF_M3_socket'
    bl_label = 'M3 socket'

    # meaningful property
    def M3_update(self, context):
        pass

    M3 = bpy.props.FloatProperty(name=get_props(TF_M3, 'name'), description=get_props(TF_M3, 'description'),
                                 default=get_props(TF_M3, 'default'), subtype=get_props(TF_M3, 'subtype'),
                                 min=get_props(TF_M3, 'min'), max=get_props(TF_M3, 'max'),
                                 soft_min=get_props(TF_M3, 'soft_min'), soft_max=get_props(TF_M3, 'soft_max'),
                                 precision=get_props(TF_M3, 'precision'), update=M3_update)

    # helper property
    def default_value_get(self):
        return self.M3

    def default_value_set(self, value):
        self.M3 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_M3, 'name'), default=get_props(TF_M3, 'default'),
                                            subtype=get_props(TF_M3, 'subtype'), min=get_props(TF_M3, 'min'),
                                            max=get_props(TF_M3, 'max'), soft_min=get_props(TF_M3, 'soft_min'),
                                            soft_max=get_props(TF_M3, 'soft_max'),
                                            precision=get_props(TF_M3, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'M3', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            M3_params = ParamSet().add_texture('M3', tex_name)
        else:
            M3_params = ParamSet().add_float('M3', self.M3)

        return M3_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_R1_socket(bpy.types.NodeSocket):
    """R1 socket"""
    bl_idname = 'luxrender_TF_R1_socket'
    bl_label = 'R1 socket'

    # meaningful property
    def R1_update(self, context):
        pass

    R1 = bpy.props.FloatProperty(name=get_props(TF_R1, 'name'), description=get_props(TF_R1, 'description'),
                                 default=get_props(TF_R1, 'default'), subtype=get_props(TF_R1, 'subtype'),
                                 min=get_props(TF_R1, 'min'), max=get_props(TF_R1, 'max'),
                                 soft_min=get_props(TF_R1, 'soft_min'), soft_max=get_props(TF_R1, 'soft_max'),
                                 precision=get_props(TF_R1, 'precision'), update=R1_update)

    # helper property
    def default_value_get(self):
        return self.R1

    def default_value_set(self, value):
        self.R1 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_R1, 'name'), default=get_props(TF_R1, 'default'),
                                            subtype=get_props(TF_R1, 'subtype'), min=get_props(TF_R1, 'min'),
                                            max=get_props(TF_R1, 'max'), soft_min=get_props(TF_R1, 'soft_min'),
                                            soft_max=get_props(TF_R1, 'soft_max'),
                                            precision=get_props(TF_R1, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'R1', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            R1_params = ParamSet().add_texture('R1', tex_name)
        else:
            R1_params = ParamSet().add_float('R1', self.R1)

        return R1_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_R2_socket(bpy.types.NodeSocket):
    """R2 socket"""
    bl_idname = 'luxrender_TF_R2_socket'
    bl_label = 'R2 socket'

    # meaningful property
    def R2_update(self, context):
        pass

    R2 = bpy.props.FloatProperty(name=get_props(TF_R2, 'name'), description=get_props(TF_R2, 'description'),
                                 default=get_props(TF_R2, 'default'), subtype=get_props(TF_R2, 'subtype'),
                                 min=get_props(TF_R2, 'min'), max=get_props(TF_R2, 'max'),
                                 soft_min=get_props(TF_R2, 'soft_min'), soft_max=get_props(TF_R2, 'soft_max'),
                                 precision=get_props(TF_R2, 'precision'), update=R2_update)

    # helper property
    def default_value_get(self):
        return self.R2

    def default_value_set(self, value):
        self.R2 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_R2, 'name'), default=get_props(TF_R2, 'default'),
                                            subtype=get_props(TF_R2, 'subtype'), min=get_props(TF_R2, 'min'),
                                            max=get_props(TF_R2, 'max'), soft_min=get_props(TF_R2, 'soft_min'),
                                            soft_max=get_props(TF_R2, 'soft_max'),
                                            precision=get_props(TF_R2, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'R2', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            R2_params = ParamSet().add_texture('R2', tex_name)
        else:
            R2_params = ParamSet().add_float('R2', self.R2)

        return R2_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_R3_socket(bpy.types.NodeSocket):
    """R3 socket"""
    bl_idname = 'luxrender_TF_R3_socket'
    bl_label = 'R3 socket'

    # meaningful property
    def R3_update(self, context):
        pass

    R3 = bpy.props.FloatProperty(name=get_props(TF_R3, 'name'), description=get_props(TF_R3, 'description'),
                                 default=get_props(TF_R3, 'default'), subtype=get_props(TF_R3, 'subtype'),
                                 min=get_props(TF_R3, 'min'), max=get_props(TF_R3, 'max'),
                                 soft_min=get_props(TF_R3, 'soft_min'), soft_max=get_props(TF_R3, 'soft_max'),
                                 precision=get_props(TF_R3, 'precision'), update=R3_update)

    # helper property
    def default_value_get(self):
        return self.R3

    def default_value_set(self, value):
        self.R3 = value

    default_value = bpy.props.FloatProperty(name=get_props(TF_R3, 'name'), default=get_props(TF_R3, 'default'),
                                            subtype=get_props(TF_R3, 'subtype'), min=get_props(TF_R3, 'min'),
                                            max=get_props(TF_R3, 'max'), soft_min=get_props(TF_R3, 'soft_min'),
                                            soft_max=get_props(TF_R3, 'soft_max'),
                                            precision=get_props(TF_R3, 'precision'), get=default_value_get,
                                            set=default_value_set)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'R3', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            R3_params = ParamSet().add_texture('R3', tex_name)
        else:
            R3_params = ParamSet().add_float('R3', self.R3)

        return R3_params


# Sockets for texture/utitlity nodes

@LuxRenderAddon.addon_register_class
class luxrender_TC_brickmodtex_socket(bpy.types.NodeSocket):
    """brickmodtex socket"""
    bl_idname = 'luxrender_TC_brickmodtex_socket'
    bl_label = 'Brick modulation texture socket'

    brickmodtex = bpy.props.FloatVectorProperty(name='Brick Modulation Texture', subtype='COLOR', min=0.0, max=1.0,
                                                default=(0.9, 0.9, 0.9))

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'brickmodtex', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            brickmodtex_params = ParamSet().add_texture('brickmodtex', tex_name)
        else:
            brickmodtex_params = ParamSet().add_color('brickmodtex', self.brickmodtex)

        return brickmodtex_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_bricktex_socket(bpy.types.NodeSocket):
    """bricktex socket"""
    bl_idname = 'luxrender_TC_bricktex_socket'
    bl_label = 'Brick texture socket'

    bricktex = bpy.props.FloatVectorProperty(name='Brick Texture', subtype='COLOR', min=0.0, max=1.0,
                                             default=(0.8, 0.8, 0.8))

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'bricktex', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            bricktex_params = ParamSet().add_texture('bricktex', tex_name)
        else:
            bricktex_params = ParamSet().add_color('bricktex', self.bricktex)

        return bricktex_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_mortartex_socket(bpy.types.NodeSocket):
    """mortartex socket"""
    bl_idname = 'luxrender_TC_mortartex_socket'
    bl_label = 'Mortar texture socket'

    mortartex = bpy.props.FloatVectorProperty(name='Mortar Texture', subtype='COLOR', min=0.0, max=1.0,
                                              default=(0.1, 0.1, 0.1))

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            row = layout.row()
            row.alignment = 'LEFT'
            row.prop(self, 'mortartex', text='')
            row.label(text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            mortartex_params = ParamSet().add_texture('mortartex', tex_name)
        else:
            mortartex_params = ParamSet().add_color('mortartex', self.mortartex)

        return mortartex_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_brickmodtex_socket(bpy.types.NodeSocket):
    """brickmodtex socket"""
    bl_idname = 'luxrender_TF_brickmodtex_socket'
    bl_label = 'Brick modulation texture socket'

    brickmodtex = bpy.props.FloatProperty(name='Brick Modulation Texture', min=0.0, max=1.0, default=0.9)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'brickmodtex', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            brickmodtex_params = ParamSet().add_texture('brickmodtex', tex_name)
        else:
            brickmodtex_params = ParamSet().add_float('brickmodtex', self.brickmodtex)

        return brickmodtex_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_bricktex_socket(bpy.types.NodeSocket):
    """bricktex socket"""
    bl_idname = 'luxrender_TF_bricktex_socket'
    bl_label = 'Brick texture socket'

    bricktex = bpy.props.FloatProperty(name='Brick Texture', min=0.0, max=1.0, default=1.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'bricktex', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            bricktex_params = ParamSet().add_texture('bricktex', tex_name)
        else:
            bricktex_params = ParamSet().add_float('bricktex', self.bricktex)

        return bricktex_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_mortartex_socket(bpy.types.NodeSocket):
    """mortartex socket"""
    bl_idname = 'luxrender_TF_mortartex_socket'
    bl_label = 'Mortar texture socket'

    mortartex = bpy.props.FloatProperty(name='Mortar Texture', min=0.0, max=1.0, default=0.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'mortartex', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            mortartex_params = ParamSet().add_texture('mortartex', tex_name)
        else:
            mortartex_params = ParamSet().add_float('mortartex', self.mortartex)

        return mortartex_params


# Custom sockets for the mix/add/scale/subtract nodes, in all 3 variants. *sigh*
# First, floats...
@LuxRenderAddon.addon_register_class
class luxrender_TF_tex1_socket(bpy.types.NodeSocket):
    """Texture 1 socket"""
    bl_idname = 'luxrender_TF_tex1_socket'
    bl_label = 'Texture 1 socket'

    tex1 = bpy.props.FloatProperty(name='Value 1', min=0.0, max=10.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'tex1', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            tex1_params = ParamSet().add_texture('tex1', tex_name)
        else:
            tex1_params = ParamSet().add_float('tex1', self.tex1)

        return tex1_params


@LuxRenderAddon.addon_register_class
class luxrender_TF_tex2_socket(bpy.types.NodeSocket):
    """Texture 2 socket"""
    bl_idname = 'luxrender_TF_tex2_socket'
    bl_label = 'Texture 2 socket'

    tex2 = bpy.props.FloatProperty(name='Value 2', min=0.0, max=10.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'tex2', text=self.name)

    def draw_color(self, context, node):
        return float_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            tex2_params = ParamSet().add_texture('tex2', tex_name)
        else:
            tex2_params = ParamSet().add_float('tex2', self.tex2)

        return tex2_params


# Now, colors:
@LuxRenderAddon.addon_register_class
class luxrender_TC_tex1_socket(bpy.types.NodeSocket):
    """Texture 1 socket"""
    bl_idname = 'luxrender_TC_tex1_socket'
    bl_label = 'Texture 1 socket'

    tex1 = bpy.props.FloatVectorProperty(name='Color 1', subtype='COLOR', min=0.0, soft_max=1.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'tex1', text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)

            tex1_params = ParamSet().add_texture('tex1', tex_name)
        else:
            tex1_params = ParamSet().add_color('tex1', self.tex1)

        return tex1_params


@LuxRenderAddon.addon_register_class
class luxrender_TC_tex2_socket(bpy.types.NodeSocket):
    """Texture 2 socket"""
    bl_idname = 'luxrender_TC_tex2_socket'
    bl_label = 'Texture 2 socket'

    tex2 = bpy.props.FloatVectorProperty(name='Color 2', subtype='COLOR', min=0.0, soft_max=1.0)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'tex2', text=self.name)

    def draw_color(self, context, node):
        return color_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            tex2_params = ParamSet().add_texture('tex2', tex_name)
        else:
            tex2_params = ParamSet().add_color('tex2', self.tex2)

        return tex2_params


# And fresnel!
@LuxRenderAddon.addon_register_class
class luxrender_TFR_tex1_socket(bpy.types.NodeSocket):
    """Texture 1 socket"""
    bl_idname = 'luxrender_TFR_tex1_socket'
    bl_label = 'Texture 1 socket'

    tex1 = bpy.props.FloatProperty(name='IOR 1', min=1.0, max=25.0, default=1.52)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'tex1', text=self.name)

    def draw_color(self, context, node):
        return fresnel_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            tex1_params = ParamSet().add_texture('tex1', tex_name)
        else:
            tex1_params = ParamSet().add_float('tex1', self.tex1)

        return tex1_params


@LuxRenderAddon.addon_register_class
class luxrender_TFR_tex2_socket(bpy.types.NodeSocket):
    """Texture 2 socket"""
    bl_idname = 'luxrender_TFR_tex2_socket'
    bl_label = 'Texture 2 socket'

    tex2 = bpy.props.FloatProperty(name='IOR 2', min=1.0, max=25.0, default=1.52)

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text=self.name)
        else:
            layout.prop(self, 'tex2', text=self.name)

    def draw_color(self, context, node):
        return fresnel_socket_color

    def get_paramset(self, make_texture):
        tex_node = get_linked_node(self)
        if tex_node:
            if not check_node_export_texture(tex_node):
                return ParamSet()

            tex_name = tex_node.export_texture(make_texture)
            tex2_params = ParamSet().add_texture('tex2', tex_name)
        else:
            tex2_params = ParamSet().add_float('tex2', self.tex2)

        return tex2_params


# 3D coordinate socket, 2D coordinates is luxrender_transform_socket. Blender does not like numbers in these names
@LuxRenderAddon.addon_register_class
class luxrender_coordinate_socket(bpy.types.NodeSocket):
    """coordinate socket"""
    bl_idname = 'luxrender_coordinate_socket'
    bl_label = 'Coordinate socket'

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    # Socket color
    def draw_color(self, context, node):
        return 0.50, 0.25, 0.60, 1.0


@LuxRenderAddon.addon_register_class
class luxrender_transform_socket(bpy.types.NodeSocket):
    """2D transform socket"""
    bl_idname = 'luxrender_transform_socket'
    bl_label = 'Transform socket'

    def draw(self, context, layout, node, text):
        layout.label(text=self.name)

    def draw_color(self, context, node):
        return 0.65, 0.55, 0.75, 1.0
