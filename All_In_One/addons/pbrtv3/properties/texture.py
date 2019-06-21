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
import hashlib, os

import bpy, mathutils

from ..extensions_framework import declarative_property_group
from ..extensions_framework import util as efutil
from ..extensions_framework.validate import Logic_OR as O, Logic_Operator as LO, Logic_AND as A

from .. import PBRTv3Addon
from ..export import ParamSet, get_worldscale, process_filepath_data
from ..export.materials import add_texture_parameter, convert_texture
from ..outputs.luxcore_api import UsePBRTv3Core
from ..export.volumes import export_smoke
from ..outputs import PBRTv3Manager
from ..util import dict_merge, bdecode_string2file

# ------------------------------------------------------------------------------
# Texture property group construction helpers
# ------------------------------------------------------------------------------
def ObjectParameter(attr, name, description, property_group):
    return [
        {
            'attr': '%s_object' % attr,
            'type': 'string',
            'name': '%s' % name,
            'description': '%s' % description,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': attr,
            'src': lambda s, c: s.scene,
            'src_attr': 'objects',
            'trg': lambda s, c: getattr(c, property_group),
            'trg_attr': '%s_object' % attr,
            'name': name,
        },
    ]


def shorten_name(n):
    return hashlib.md5(n.encode()).hexdigest()[:21] if len(n) > 21 else n


class TextureParameterBase(object):
    real_attr = None
    attr = None
    name = None
    default = (0.8, 0.8, 0.8)
    min = 0.0
    max = 1.0

    texture_collection = 'texture_slots'

    controls = None
    visibility = None
    properties = None

    def __init__(self, attr, name, default=None, min=None, max=None, real_attr=None):
        self.attr = attr
        self.name = name
        if default is not None:
            self.default = default
        if min is not None:
            self.min = min
        if max is not None:
            self.max = max
        if real_attr is not None:
            self.real_attr = real_attr

        self.controls = self.get_controls()
        self.visibility = self.get_visibility()
        self.properties = self.get_properties()

    def texture_collection_finder(self):
        def _tcf_wrap(superctx, ctx):

            if superctx.object and len(superctx.object.material_slots) > 0 and superctx.object.material_slots[
                superctx.object.active_material_index].material:
                return superctx.object.material_slots[superctx.object.active_material_index].material
            elif superctx.lamp:  # If this is a lamp, we need to get any textures attatched to the same lamp
                return superctx.lamp
            else:
                return superctx.scene.world

                # It doesn't cost us any functionality atm, but the above function will almost certainly
                # miss particle textures. -JtheNinja

        return _tcf_wrap

    def texture_slot_set_attr(self):
        def set_attr(s, c):
            if type(c).__name__ == 'pbrtv3_material':
                return getattr(c, 'pbrtv3_mat_%s' % c.type)
            else:
                return getattr(c, 'pbrtv3_tex_%s' % c.type)

        return set_attr

    def get_controls(self):
        """
        Subclasses can override this for their own needs
        """
        return []

    def get_visibility(self):
        """
        Subclasses can override this for their own needs
        """
        return {}

    def get_properties(self):
        """
        Subclasses can override this for their own needs
        """
        return []

    def get_extra_controls(self):
        """
        Subclasses can override this for their own needs
        """
        return []

    def get_extra_visibility(self):
        """
        Subclasses can override this for their own needs
        """
        return {}

    def get_extra_properties(self):
        """
        Subclasses can override this for their own needs
        """
        return []

    def get_paramset(self, property_group):
        """
        Return a PBRTv3 ParamSet of the properties
        defined in this Texture, getting parameters
        from the property_group
        """

        return ParamSet()

    def get_real_param_name(self):
        if self.real_attr is not None:
            return self.real_attr
        else:
            return self.attr


def check_texture_variant(self, context, attr, expected_variant):
    # print('CHECK TEXTURE: self        %s' % self)
    # print('CHECK TEXTURE: context     %s' % context)
    # print('CHECK TEXTURE: attr        %s' % attr)
    # print('CHECK TEXTURE: expected    %s' % expected_variant)

    attr_name = '%s_%stexturename' % (attr, expected_variant)
    attr_alert = '%s_use%stexture' % (attr, expected_variant)

    def clear_alert():
        if attr_alert in self.alert.keys():
            del self.alert[attr_alert]

    tn = getattr(self, attr_name)
    if not tn:
        # empty assignment
        clear_alert()
        return

    valid = False

    # Disable all alerts due luxcore can handle either variant
    if UsePBRTv3Core():
        return

    if tn in bpy.data.textures:
        lt = bpy.data.textures[tn].pbrtv3_texture
        # print('CHECK TEXTURE: lt          %s' % lt)

        if lt.type == 'BLENDER':
            valid = 'float' == expected_variant
            if bpy.data.textures[tn].type == 'IMAGE':
                valid = True
        else:
            lst = getattr(lt, 'pbrtv3_tex_%s' % lt.type)
            # print('CHECK TEXTURE: lst         %s' % lst)
            # print('CHECK TEXTURE: lst.variant %s' % lst.variant)

            valid = lst.variant == expected_variant
    # else:
    # print('CHECK TEXTURE: Not a valid texture')

    if not valid:
        self.alert[attr_alert] = {attr_alert: LO({'!=': None})}
    # print('CHECK TEXTURE: Not a valid variant assigned')
    else:
        clear_alert()


def refresh_preview(self, context):
    if context.material is not None:
        context.material.preview_render_type = context.material.preview_render_type
    if context.texture is not None:
        context.texture.type = context.texture.type


class ColorTextureParameter(TextureParameterBase):
    def load_paramset(self, property_group, ps):
        for psi in ps:
            if psi['name'] == self.attr:
                setattr(property_group, '%s_multiplycolor' % self.attr, False)
                if psi['type'].lower() == 'texture':
                    setattr(property_group, '%s_usecolortexture' % self.attr, True)
                    setattr(property_group, '%s_colortexturename' % self.attr, shorten_name(psi['value']))
                else:
                    setattr(property_group, '%s_usecolortexture' % self.attr, False)
                    try:
                        setattr(property_group, '%s_color' % self.attr, psi['value'])
                    except:
                        import pdb

                        pdb.set_trace()

    def get_controls(self):
        return [
                   [0.9, [0.375, '%s_colorlabel' % self.attr, '%s_color' % self.attr],
                    '%s_usecolortexture' % self.attr],
                   [0.9, '%s_colortexture' % self.attr, '%s_multiplycolor' % self.attr],
               ] + self.get_extra_controls()

    def get_visibility(self):
        vis = {
            '%s_colortexture' % self.attr: {'%s_usecolortexture' % self.attr: True},
            '%s_multiplycolor' % self.attr: {'%s_usecolortexture' % self.attr: True},
        }
        vis.update(self.get_extra_visibility())
        return vis

    def get_properties(self):
        return [
                   {
                       'attr': self.attr,
                       'type': 'string',
                       'default': self.get_real_param_name()
                   },
                   {
                       'attr': '%s_multiplycolor' % self.attr,
                       'type': 'bool',
                       'name': 'M',
                       'description': 'Multiply texture by color',
                       'default': False,
                       'toggle': True,
                       'update': refresh_preview,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_usecolortexture' % self.attr,
                       'type': 'bool',
                       'name': 'T',
                       'description': 'Textured %s' % self.name,
                       'default': False,
                       'toggle': True,
                       'update': refresh_preview,
                       'save_in_preset': True
                   },
                   {
                       'type': 'text',
                       'attr': '%s_colorlabel' % self.attr,
                       'name': self.name
                   },
                   {
                       'type': 'float_vector',
                       'attr': '%s_color' % self.attr,
                       'name': '',
                       'description': self.name,
                       'default': self.default,
                       'min': self.min,
                       'soft_min': self.min,
                       'max': self.max,
                       'soft_max': self.max,
                       'subtype': 'COLOR',
                       'update': lambda s, c: refresh_preview(s, c) or (
                           c.material.pbrtv3_material.set_master_color(c.material)
                           if hasattr(c.material, 'pbrtv3_material') else None),
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_colortexturename' % self.attr,
                       'type': 'string',
                       'name': '%s_colortexturename' % self.attr,
                       'description': '%s texture' % self.name,
                       'update': lambda s, c: refresh_preview(s, c) or check_texture_variant(s, c, self.attr, 'color'),
                       'save_in_preset': True
                   },
                   {
                       'type': 'prop_search',
                       'attr': '%s_colortexture' % self.attr,
                       'src': self.texture_collection_finder(),
                       'src_attr': self.texture_collection,
                       'trg': self.texture_slot_set_attr(),
                       'trg_attr': '%s_colortexturename' % self.attr,
                       'name': self.name
                   },
               ] + self.get_extra_properties()

    def get_paramset(self, property_group, value_transform_function=None):
        TC_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            TC_params.update(
                add_texture_parameter(
                    PBRTv3Manager.GetActive().lux_context,
                    self.attr,
                    'color',
                    property_group,
                    value_transform_function=value_transform_function
                )
            )

        return TC_params


class FloatTextureParameter(TextureParameterBase):
    default = 0.0
    min = 0.0
    max = 1.0
    precision = 6
    texture_only = False
    multiply_float = False
    ignore_unassigned = False
    subtype = 'NONE'
    unit = 'NONE'

    def __init__(self,
                 attr, name,
                 add_float_value=True,  # True: Show float value input, and [T] button; False: Just show texture slot
                 multiply_float=False,  # Specify that when texture is in use, it should be scaled by the float value
                 ignore_unassigned=False,  # Don't export this parameter if the texture slot is unassigned
                 real_attr=None,  # translate self.attr into something else at export time (overcome 31 char RNA limit)
                 subtype='NONE',
                 unit='NONE',
                 default=0.0, min=0.0, max=1.0, precision=6
    ):
        self.attr = attr
        self.name = name
        self.texture_only = (not add_float_value)
        self.multiply_float = multiply_float
        self.ignore_unassigned = ignore_unassigned
        self.subtype = subtype
        self.unit = unit
        self.real_attr = real_attr
        self.default = default
        self.min = min
        self.max = max
        self.precision = precision

        self.controls = self.get_controls()
        self.visibility = self.get_visibility()
        self.properties = self.get_properties()

    def load_paramset(self, property_group, ps):
        for psi in ps:
            if psi['name'] == self.attr:
                setattr(property_group, '%s_multiplyfloat' % self.attr, False)
                if psi['type'].lower() == 'texture':
                    setattr(property_group, '%s_usefloattexture' % self.attr, True)
                    setattr(property_group, '%s_floattexturename' % self.attr, shorten_name(psi['value']))
                else:
                    setattr(property_group, '%s_usefloattexture' % self.attr, False)
                    setattr(property_group, '%s_floatvalue' % self.attr, psi['value'])

    def get_controls(self):
        if self.texture_only:
            return [
                       '%s_floattexture' % self.attr,
                   ] + self.get_extra_controls()
        else:
            return [
                       [0.9, '%s_floatvalue' % self.attr, '%s_usefloattexture' % self.attr],
                       [0.9, '%s_floattexture' % self.attr, '%s_multiplyfloat' % self.attr],
                   ] + self.get_extra_controls()

    def get_visibility(self):
        vis = {}
        if not self.texture_only:
            vis = {
                '%s_floattexture' % self.attr: {'%s_usefloattexture' % self.attr: True},
                '%s_multiplyfloat' % self.attr: {'%s_usefloattexture' % self.attr: True},
            }
        vis.update(self.get_extra_visibility())
        return vis

    def get_properties(self):
        return [
                   {
                       'attr': self.attr,
                       'type': 'string',
                       'default': self.get_real_param_name()
                   },
                   {
                       'attr': '%s_multiplyfloat' % self.attr,
                       'type': 'bool',
                       'name': 'M',
                       'description': 'Multiply texture by value',
                       'default': self.multiply_float,
                       'toggle': True,
                       'update': refresh_preview,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_ignore_unassigned' % self.attr,
                       'type': 'bool',
                       'default': self.ignore_unassigned,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_usefloattexture' % self.attr,
                       'type': 'bool',
                       'name': 'T',
                       'description': 'Textured %s' % self.name,
                       'default': False if not self.texture_only else True,
                       'toggle': True,
                       'update': refresh_preview,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_floatvalue' % self.attr,
                       'type': 'float',
                       'subtype': self.subtype,
                       'unit': self.unit,
                       'name': self.name,
                       'description': '%s value' % self.name,
                       'default': self.default,
                       'min': self.min,
                       'soft_min': self.min,
                       'max': self.max,
                       'soft_max': self.max,
                       'precision': self.precision,
                       'update': refresh_preview,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_presetvalue' % self.attr,
                       'type': 'float',
                       'subtype': self.subtype,
                       'default': self.default,
                       'update': refresh_preview,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_presetstring' % self.attr,
                       'type': 'string',
                       'default': '-- Choose IOR preset --',
                       'save_in_preset': True
                   },

                   {
                       'attr': '%s_floattexturename' % self.attr,
                       'type': 'string',
                       'name': '%s_floattexturename' % self.attr,
                       'description': '%s Texture' % self.name,
                       'update': lambda s, c: refresh_preview(s, c) or check_texture_variant(s, c, self.attr, 'float'),
                       'save_in_preset': True
                   },
                   {
                       'type': 'prop_search',
                       'attr': '%s_floattexture' % self.attr,
                       'src': self.texture_collection_finder(),
                       'src_attr': self.texture_collection,
                       'trg': self.texture_slot_set_attr(),
                       'trg_attr': '%s_floattexturename' % self.attr,
                       'name': self.name
                   },
               ] + self.get_extra_properties()

    def get_paramset(self, property_group):
        TC_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            TC_params.update(
                add_texture_parameter(
                    PBRTv3Manager.GetActive().lux_context,
                    self.attr,
                    'float',
                    property_group
                )
            )

        return TC_params


class FresnelTextureParameter(TextureParameterBase):
    default = 0.0
    min = 0.0
    max = 1.0
    precision = 6
    texture_only = False
    multiply_float = False
    ignore_unassigned = False

    def __init__(self,
                 attr, name,
                 add_float_value=True,  # True: Show float value input, and [T] button; False: Just show texture slot
                 multiply_float=False,  # Specify that when texture is in use, it should be scaled by the float value
                 ignore_unassigned=False,  # Don't export this parameter if the texture slot is unassigned
                 real_attr=None,  # translate self.attr into something else at export time (overcome 31 char RNA limit)
                 default=0.0, min=0.0, max=1.0, precision=6
    ):
        self.attr = attr
        self.name = name
        self.texture_only = (not add_float_value)
        self.multiply_float = multiply_float
        self.ignore_unassigned = ignore_unassigned
        self.real_attr = real_attr
        self.default = default
        self.min = min
        self.max = max
        self.precision = precision

        self.controls = self.get_controls()
        self.visibility = self.get_visibility()
        self.properties = self.get_properties()

    def load_paramset(self, property_group, ps):
        for psi in ps:
            if psi['name'] == self.attr:
                setattr(property_group, '%s_multiplyfresnel' % self.attr, False)
                if psi['type'].lower() == 'texture':
                    setattr(property_group, '%s_usefresneltexture' % self.attr, True)
                    setattr(property_group, '%s_fresneltexturename' % self.attr, shorten_name(psi['value']))
                else:
                    setattr(property_group, '%s_usefresneltexture' % self.attr, False)
                    setattr(property_group, '%s_fresnelvalue' % self.attr, psi['value'])

    def get_controls(self):
        if self.texture_only:
            return [
                       '%s_fresneltexture' % self.attr,
                   ] + self.get_extra_controls()
        else:
            return [
                       [0.9, '%s_fresnelvalue' % self.attr, '%s_usefresneltexture' % self.attr],
                       [0.9, '%s_fresneltexture' % self.attr, '%s_multiplyfresnel' % self.attr],
                   ] + self.get_extra_controls()

    def get_visibility(self):
        vis = {}

        if not self.texture_only:
            vis = {
                '%s_fresneltexture' % self.attr: {'%s_usefresneltexture' % self.attr: True},
                '%s_multiplyfresnel' % self.attr: {'%s_usefresneltexture' % self.attr: True},
            }

        vis.update(self.get_extra_visibility())

        return vis

    def get_properties(self):
        return [
                   {
                       'attr': self.attr,
                       'type': 'string',
                       'default': self.get_real_param_name()
                   },
                   {
                       'attr': '%s_multiplyfresnel' % self.attr,
                       'name': 'M',
                       'description': 'Multiply fresnel texture by fresnel value',
                       'type': 'bool',
                       'default': self.multiply_float,
                       'toggle': True,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_ignore_unassigned' % self.attr,
                       'type': 'bool',
                       'default': self.ignore_unassigned,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_usefresneltexture' % self.attr,
                       'type': 'bool',
                       'name': 'T',
                       'description': 'Textured %s' % self.name,
                       'default': False if not self.texture_only else True,
                       'toggle': True,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_fresnelvalue' % self.attr,
                       'type': 'float',
                       'name': self.name,
                       'description': '%s value' % self.name,
                       'default': self.default,
                       'min': self.min,
                       'soft_min': self.min,
                       'max': self.max,
                       'soft_max': self.max,
                       'precision': self.precision,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_presetvalue' % self.attr,
                       'type': 'float',
                       'default': self.default,
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_presetstring' % self.attr,
                       'type': 'string',
                       'default': '-- Choose IOR preset --',
                       'save_in_preset': True
                   },
                   {
                       'attr': '%s_fresneltexturename' % self.attr,
                       'type': 'string',
                       'name': '%s_fresneltexturename' % self.attr,
                       'description': '%s texture' % self.name,
                       'save_in_preset': True
                   },
                   {
                       'type': 'prop_search',
                       'attr': '%s_fresneltexture' % self.attr,
                       'src': self.texture_collection_finder(),
                       'src_attr': self.texture_collection,
                       'trg': self.texture_slot_set_attr(),
                       'trg_attr': '%s_fresneltexturename' % self.attr,
                       'name': self.name
                   },
               ] + self.get_extra_properties()

    def get_paramset(self, property_group):
        TC_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            TC_params.update(
                add_texture_parameter(
                    PBRTv3Manager.GetActive().lux_context,
                    self.attr,
                    'fresnel',
                    property_group
                )
            )

        return TC_params

# ------------------------------------------------------------------------------
# The main pbrtv3_texture property group
# ------------------------------------------------------------------------------

tex_names = (
    ('Blender Textures',
     (
         ('BLENDER', 'Use Blender Texture'),
     )),

    ('PBRTv3 Textures',
     (
         ('brick', 'Brick'),
         ('checkerboard', 'Checkerboard'),
         ('cloud', 'Cloud'),
         ('dots', 'Dots'),
         ('exponential', 'Exponential'),
         ('fbm', 'FBM'),
         ('imagemap', 'Image Map'),
         ('normalmap', 'Normal Map'),
         ('marble', 'Marble'),
         ('densitygrid', 'Smoke Data'),
         ('hitpointcolor', 'Vertex Color'),
         ('hitpointgrey', 'Vertex Grey'),
         ('hitpointalpha', 'Vertex Alpha'),
         ('pointiness', 'Pointiness'),
         ('windy', 'Windy'),
         ('wrinkled', 'Wrinkled'),
     )),

    ('Emission & Spectrum Textures',
     (
         ('blackbody', 'Blackbody'),
         ('colordepth', 'Color at Depth'),
         ('equalenergy', 'Equal Energy'),
         ('lampspectrum', 'Lamp Spectrum'),
         ('gaussian', 'Gaussian'),
         ('tabulateddata', 'Tabulated Data'),
     )),

    ('Fresnel Textures',
     (
         ('abbe', 'Abbe'),
         ('cauchy', 'Cauchy'),
         ('fresnelcolor', 'Fresnel Color'),
         ('fresnelname', 'Fresnel Name (preset/nk data)'),
         ('sellmeier', 'Sellmeier'),
         ('sopra', 'Sopra'),
         ('luxpop', 'Luxpop'),
     )),

    ('Utility Textures',
     (
         ('add', 'Add'),
         ('band', 'Band'),
         ('bilerp', 'Bilerp'),
         ('constant', 'Constant'),
         ('harlequin', 'Harlequin'),
         ('mix', 'Mix'),
         ('multimix', 'Multi Mix'),
         ('scale', 'Scale'),
         ('subtract', 'Subtract'),
         ('uv', 'UV'),
         ('uvmask', 'UV Mask'),
         ('hsv', 'HSV'),
     )),

)


@PBRTv3Addon.addon_register_class
class TEXTURE_OT_set_pbrtv3_type(bpy.types.Operator):
    bl_idname = 'texture.set_pbrtv3_type'
    bl_label = 'Set PBRTv3 texture type'

    tex_name = bpy.props.StringProperty()
    tex_label = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'texture') and context.texture and context.texture.pbrtv3_texture

    def execute(self, context):
        lux_tex = context.texture.pbrtv3_texture

        lux_tex.type = self.properties.tex_name
        lux_tex.type_label = self.properties.tex_label

        # This is what the user needs in almost all cases
        if lux_tex.type == 'densitygrid':
            lux_tex.pbrtv3_tex_transform.coordinates = 'smoke_domain'

        return {'FINISHED'}


def draw_generator(operator, m_names):
    def draw(self, context):
        sl = self.layout

        for m_name, m_label in m_names:
            op = sl.operator(operator, text=m_label)
            op.tex_name = m_name
            op.tex_label = m_label

    return draw


@PBRTv3Addon.addon_register_class
class TEXTURE_MT_pbrtv3_type(bpy.types.Menu):
    bl_label = 'Texture Type'
    submenus = []

    def draw(self, context):
        sl = self.layout
        for sm in self.submenus:
            sl.menu(sm.bl_idname)

    for tex_cat, tex_cat_list in tex_names:
        submenu_idname = 'TEXTURE_MT_pbrtv3_tex_cat%d' % len(submenus)
        submenus.append(
            PBRTv3Addon.addon_register_class(type(
                submenu_idname,
                (bpy.types.Menu,),
                {
                    'bl_idname': submenu_idname,
                    'bl_label': tex_cat,
                    'draw': draw_generator('TEXTURE_OT_set_pbrtv3_type', tex_cat_list)
                }
            ))
        )


@PBRTv3Addon.addon_register_class
class pbrtv3_texture(declarative_property_group):
    """
    Storage class for PBRTv3 Texture settings.
    """

    ef_attach_to = ['Texture']
    alert = {}

    controls = [  # Preset menu is drawn manually in the ui class
    ]

    visibility = {}

    properties = [
        {
            'attr': 'auto_generated',
            'type': 'bool',
            'default': False,
        },  # The following two items are set by the preset menu and operator.
        {
            'attr': 'type_label',
            'name': 'PBRTv3 Type',
            'type': 'string',
            'default': 'Use Blender Texture',
            'save_in_preset': True
        },
        {
            'attr': 'type',
            'name': 'PBRTv3 Type',
            'type': 'string',
            'default': 'BLENDER',
            'update': refresh_preview,
            'save_in_preset': True
        },
    ]

    def set_type(self, tex_type):
        self.type = tex_type
        for cat, texs in tex_names:
            for a, b in texs:
                if tex_type == a:
                    self.type_label = b

    def reset(self, prnt=None):
        super().reset()
        # Also reset sub-property groups
        for cat, texs in tex_names:
            for a, b in texs:
                if a != 'BLENDER':
                    getattr(self, 'pbrtv3_tex_%s' % a).reset()

    def get_paramset(self, scene, texture):
        """
        Discover the type of this PBRTv3 texture, and return its
        variant name and its ParamSet.
        We also add in the ParamSets of any panels shared by texture
        types, eg. 2D/3D mapping and transform params

        Return		tuple(string('float'|'color'|'fresnel'), ParamSet)
        """

        # this requires part of the sub-IDPropertyGroup name to be the same as the texture name
        if hasattr(self, 'pbrtv3_tex_%s' % self.type):
            lux_texture = getattr(self, 'pbrtv3_tex_%s' % self.type)
            features, params = lux_texture.get_paramset(scene, texture)

            # 2D Mapping options
            if '2DMAPPING' in features:
                params.update(self.pbrtv3_tex_mapping.get_paramset(scene))

            # 3D Mapping options
            if '3DMAPPING' in features:
                params.update(self.pbrtv3_tex_transform.get_paramset(scene))

            return lux_texture.variant, params
        else:
            variant, lux_tex_name, paramset = convert_texture(scene, texture)

            return variant, paramset

# ------------------------------------------------------------------------------
# Sub property groups of pbrtv3_texture follow
# ------------------------------------------------------------------------------

# Float Texture Parameters
TF_brickmodtex = FloatTextureParameter('brickmodtex', 'Brick modulation texture', default=0.9, min=0.0, max=1.0,
                                       precision=6)
TF_bricktex = FloatTextureParameter('bricktex', 'Brick texture', default=1.0, min=0.0, max=1.0, precision=6)
TF_mortartex = FloatTextureParameter('mortartex', 'Mortar texture', default=0.0, min=0.0, max=1.0, precision=6)
TF_tex1 = FloatTextureParameter('tex1', 'Texture 1', default=1.0, min=-1e6, max=1e6, precision=6)
TF_tex2 = FloatTextureParameter('tex2', 'Texture 2', default=0.0, min=-1e6, max=1e6, precision=6)
TF_amount = FloatTextureParameter('amount', 'Amount', default=0.5, min=0.0, max=1.0, precision=6)
TF_inside = FloatTextureParameter('inside', 'Inside', default=1.0, min=0.0, max=100.0, precision=6)
TF_outside = FloatTextureParameter('outside', 'Outside', default=0.0, min=0.0, max=100.0, precision=6)
TF_innertex = FloatTextureParameter('innertex', 'Inner texture', default=1.0, min=0.0, max=100.0, precision=6)
TF_outertex = FloatTextureParameter('outertex', 'Outer texture', default=0.0, min=0.0, max=100.0, precision=6)
TF_hue = FloatTextureParameter('hue', 'Hue', default=0.5, min=0.0, max=1.0)  # HSV texture parameters
TF_saturation = FloatTextureParameter('saturation', 'Saturation', default=1, min=0.0, max=2.0)
TF_value = FloatTextureParameter('value', 'Value', default=1, min=0.0, max=2.0)

# Color Texture Parameters
TC_brickmodtex = ColorTextureParameter('brickmodtex', 'Brick modulation texture', default=(0.9, 0.9, 0.9))
TC_bricktex = ColorTextureParameter('bricktex', 'Brick texture', default=(0.64, 0.64, 0.64))
TC_mortartex = ColorTextureParameter('mortartex', 'Mortar texture', default=(0.1, 0.1, 0.1))
TC_tex1 = ColorTextureParameter('tex1', 'Texture 1', default=(0.8, 0.8, 0.8))
TC_tex2 = ColorTextureParameter('tex2', 'Texture 2', default=(0.1, 0.1, 0.1))
TC_Kr = ColorTextureParameter('Kr', 'Reflection color',
                              default=(0.7, 0.7, 0.7))  # This parameter is used by the fresnelcolor texture
TC_Kt = ColorTextureParameter('Kt', 'Transmission color',
                              default=(1.0, 1.0, 1.0))  # This parameter is used by the color at depth texture
TC_input = ColorTextureParameter('input', 'Input Color', default=(0.8, 0.8, 0.8))  # Used by HSV texture

# Fresnel Texture Parameters
TFR_tex1 = FresnelTextureParameter('tex1', 'Texture 1', default=1.0, min=-40.0, max=40.0)
TFR_tex2 = FresnelTextureParameter('tex2', 'Texture 2', default=1.0, min=-40.0, max=40.0)

BAND_MAX_TEX = 32

TC_BAND_ARRAY = []
TF_BAND_ARRAY = []
TFR_BAND_ARRAY = []

for i in range(1, BAND_MAX_TEX + 1):
    TF_BAND_ARRAY.append(
        FloatTextureParameter('tex%d' % i, 'tex%d' % i, default=0.0, min=-1e6, max=1e6)
    )
    TC_BAND_ARRAY.append(
        ColorTextureParameter('tex%d' % i, 'tex%d' % i, default=(0.1, 0.1, 0.1))
    )
    TFR_BAND_ARRAY.append(
        FresnelTextureParameter('tex%d' % i, 'tex%d' % i, default=1.0, min=-40.0, max=40.0)
    )


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_add(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'variant',

               ] + \
               TF_tex1.controls + \
               TFR_tex1.controls + \
               TC_tex1.controls + \
               TF_tex2.controls + \
               TFR_tex2.controls + \
               TC_tex2.controls

    # Visibility we do manually because of the variant switch
    visibility = {
        'tex1_colorlabel': {'variant': 'color'},
        'tex1_color': {'variant': 'color'},
        'tex1_usecolortexture': {'variant': 'color'},
        'tex1_colortexture': {'variant': 'color', 'tex1_usecolortexture': True},
        'tex1_multiplycolor': {'variant': 'color', 'tex1_usecolortexture': True},

        'tex1_usefloattexture': {'variant': 'float'},
        'tex1_floatvalue': {'variant': 'float'},
        'tex1_floattexture': {'variant': 'float', 'tex1_usefloattexture': True},
        'tex1_multiplyfloat': {'variant': 'float', 'tex1_usefloattexture': True},

        'tex1_usefresneltexture': {'variant': 'fresnel'},
        'tex1_fresnelvalue': {'variant': 'fresnel'},
        'tex1_fresneltexture': {'variant': 'fresnel', 'tex1_usefresneltexture': True},
        'tex1_multiplyfresnel': {'variant': 'fresnel', 'tex1_usefresneltexture': True},

        'tex2_colorlabel': {'variant': 'color'},
        'tex2_color': {'variant': 'color'},
        'tex2_usecolortexture': {'variant': 'color'},
        'tex2_colortexture': {'variant': 'color', 'tex2_usecolortexture': True},
        'tex2_multiplycolor': {'variant': 'color', 'tex2_usecolortexture': True},

        'tex2_usefloattexture': {'variant': 'float'},
        'tex2_floatvalue': {'variant': 'float'},
        'tex2_floattexture': {'variant': 'float', 'tex2_usefloattexture': True},
        'tex2_multiplyfloat': {'variant': 'float', 'tex2_usefloattexture': True},

        'tex2_usefresneltexture': {'variant': 'fresnel'},
        'tex2_fresnelvalue': {'variant': 'fresnel'},
        'tex2_fresneltexture': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
        'tex2_multiplyfresnel': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
    }

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'enum',
                         'name': 'Variant',
                         'items': [
                             ('float', 'Greyscale', 'Output a floating point number'),
                             ('color', 'Color', 'Output a color value'),  # ('fresnel', 'Fresnel', 'fresnel'),
                         ],
                         'expand': True,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_tex1.properties + \
                 TFR_tex1.properties + \
                 TC_tex1.properties + \
                 TF_tex2.properties + \
                 TFR_tex2.properties + \
                 TC_tex2.properties

    def get_paramset(self, scene, texture):
        add_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            add_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex1', self.variant, self)
            )

            add_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex2', self.variant, self)
            )

        return set(), add_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color'] else 'float'

        if self.variant == 'float':
            TF_tex1.load_paramset(self, ps)
            TF_tex2.load_paramset(self, ps)

        if self.variant == 'color':
            TC_tex1.load_paramset(self, ps)
            TC_tex2.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_band(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'variant',
        'noffsets',
        [0.9, 'amount_floatvalue', 'amount_usefloattexture'],
        [0.9, 'amount_floattexture', 'amount_multiplyfloat']
    ]
    for i in range(1, BAND_MAX_TEX + 1):
        controls.extend([
            [0.9, ['offsetfloat%d' % i, 'tex%d_floatvalue' % i], 'tex%d_usefloattexture' % i],
            [0.9, 'tex%d_floattexture' % i, 'tex%d_multiplyfloat' % i],
            [0.9, ['offsetcolor%d' % i, 'tex%d_color' % i], 'tex%d_usecolortexture' % i],
            [0.9, 'tex%d_colortexture' % i, 'tex%d_multiplycolor' % i],
            [0.9, ['offsetfresnel%d' % i, 'tex%d_fresnelvalue' % i], 'tex%d_usefresneltexture' % i],
            [0.9, 'tex%d_fresneltexture' % i, 'tex%d_multiplyfresnel' % i],
        ])

    # Visibility we do manually because of the variant switch
    visibility = {
        'amount_floattexture': {'amount_usefloattexture': True},
        'amount_multiplyfloat': {'amount_usefloattexture': True},
    }

    for i in range(1, BAND_MAX_TEX + 1):
        visibility.update({
            'offsetcolor%d' % i: {'variant': 'color', 'noffsets': LO({'>=': i})},
            'tex%d_color' % i: {'variant': 'color', 'noffsets': LO({'>=': i})},
            'tex%d_usecolortexture' % i: {'variant': 'color', 'noffsets': LO({'>=': i})},
            'tex%d_colortexture' % i: {'variant': 'color', 'tex%d_usecolortexture' % i: True,
                                       'noffsets': LO({'>=': i})},
            'tex%d_multiplycolor' % i: {'variant': 'color', 'tex%d_usecolortexture' % i: True,
                                        'noffsets': LO({'>=': i})},

            'offsetfloat%d' % i: {'variant': 'float', 'noffsets': LO({'>=': i})},
            'tex%d_usefloattexture' % i: {'variant': 'float', 'noffsets': LO({'>=': i})},
            'tex%d_floatvalue' % i: {'variant': 'float', 'noffsets': LO({'>=': i})},
            'tex%d_floattexture' % i: {'variant': 'float', 'tex%d_usefloattexture' % i: True,
                                       'noffsets': LO({'>=': i})},
            'tex%d_multiplyfloat' % i: {'variant': 'float', 'tex%d_usefloattexture' % i: True,
                                        'noffsets': LO({'>=': i})},

            'offsetfresnel%d' % i: {'variant': 'fresnel', 'noffsets': LO({'>=': i})},
            'tex%d_usefresneltexture' % i: {'variant': 'fresnel', 'noffsets': LO({'>=': i})},
            'tex%d_fresnelvalue' % i: {'variant': 'fresnel', 'noffsets': LO({'>=': i})},
            'tex%d_fresneltexture' % i: {'variant': 'fresnel', 'tex%d_usefresneltexture' % i: True,
                                         'noffsets': LO({'>=': i})},
            'tex%d_multiplyfresnel' % i: {'variant': 'fresnel', 'tex%d_usefresneltexture' % i: True,
                                          'noffsets': LO({'>=': i})}
        })

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'enum',
                         'name': 'Variant',
                         'items': [
                             ('float', 'Greyscale', 'Output a floating point number'),
                             ('color', 'Color', 'Output a color value'),
                             ('fresnel', 'Fresnel', 'Output optical data'),
                         ],
                         'expand': True,
                         'save_in_preset': True
                     },
                     {
                         'attr': 'noffsets',
                         'type': 'int',
                         'name': 'Number of Offsets',
                         'default': 2,
                         'min': 2,
                         'max': BAND_MAX_TEX,
                         'save_in_preset': True
                     },
                 ] + TF_amount.properties

    for i in range(1, BAND_MAX_TEX + 1):
        properties.extend([
            {
                'attr': 'offsetfloat%d' % i,
                'type': 'float',
                'name': 'offset%d' % i,
                'default': 0.0,
                'precision': 3,
                'min': 0.0,
                'max': 1.0,
                'save_in_preset': True
            },
            {
                'attr': 'offsetcolor%d' % i,
                'type': 'float',
                'name': 'offset%d' % i,
                'default': 0.0,
                'precision': 3,
                'min': 0.0,
                'max': 1.0,
                'save_in_preset': True
            },
            {
                'attr': 'offsetfresnel%d' % i,
                'type': 'float',
                'name': 'offset%d' % i,
                'default': 0.0,
                'precision': 3,
                'min': 0.0,
                'max': 1.0,
                'save_in_preset': True
            }
        ])

    for prop in TC_BAND_ARRAY:
        properties.extend(prop.properties)

    for prop in TF_BAND_ARRAY:
        properties.extend(prop.properties)

    for prop in TFR_BAND_ARRAY:
        properties.extend(prop.properties)

    del i, prop

    def get_paramset(self, scene, texture):
        band_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            band_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'amount', 'float', self)
            )

            offsets = []
            for i in range(1, self.noffsets + 1):
                offsets.append(getattr(self, 'offset%s%d' % (self.variant, i)))

                band_params.update(
                    add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex%d' % i, self.variant, self)
                )

            # In API mode need to tell Lux how many slots explicity
            if PBRTv3Manager.GetActive().lux_context.API_TYPE == 'PURE':
                band_params.add_integer('noffsets', self.noffsets)

            band_params.add_float('offsets', offsets)

        return set(), band_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color', 'fresnel', ] else 'float'

        offsets = []
        for psi in ps:
            if psi['name'] == 'offsets' and psi['type'] == 'float':
                offsets = psi['value']
                self.noffsets = len(psi['value'])

        if self.variant == 'float':
            for i in range(self.noffsets):
                TF_BAND_ARRAY[i].load_paramset(self, ps)
                setattr(self, 'offsetfloat%d' % i, offsets[i])
        if self.variant == 'color':
            for i in range(self.noffsets):
                TC_BAND_ARRAY[i].load_paramset(self, ps)
                setattr(self, 'offsetcolor%d' % i, offsets[i])
        if self.variant == 'fresnel':
            for i in range(self.noffsets):
                TFR_BAND_ARRAY[i].load_paramset(self, ps)
                setattr(self, 'offsetfresnel%d' % i, offsets[i])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_bilerp(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'variant',
        ['v00_f', 'v10_f'],
        ['v01_f', 'v11_f'],

        ['v00_c', 'v10_c'],
        ['v01_c', 'v11_c'],

        ['v00_fr', 'v10_fr'],
        ['v01_fr', 'v11_fr'],
    ]

    visibility = {
        'v00_f': {'variant': 'float'},
        'v01_f': {'variant': 'float'},
        'v10_f': {'variant': 'float'},
        'v11_f': {'variant': 'float'},

        'v00_c': {'variant': 'color'},
        'v01_c': {'variant': 'color'},
        'v10_c': {'variant': 'color'},
        'v11_c': {'variant': 'color'},

        'v00_fr': {'variant': 'fresnel'},
        'v01_fr': {'variant': 'fresnel'},
        'v10_fr': {'variant': 'fresnel'},
        'v11_fr': {'variant': 'fresnel'},
    }

    properties = [
        {
            'attr': 'variant',
            'type': 'enum',
            'name': 'Variant',
            'items': [
                ('float', 'Greyscale', 'Output a floating point number'),
                ('color', 'Color', 'Output a color value'),
                ('fresnel', 'Fresnel', 'Output optical data'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            'attr': 'v00_f',
            'type': 'float',
            'name': '(0,0)',
            'default': 0.0,
            'save_in_preset': True
        },
        {
            'attr': 'v01_f',
            'type': 'float',
            'name': '(0,1)',
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v10_f',
            'type': 'float',
            'name': '(1,0)',
            'default': 0.0,
            'save_in_preset': True
        },
        {
            'attr': 'v11_f',
            'type': 'float',
            'name': '(1,1)',
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v00_c',
            'type': 'float_vector',
            'subtype': 'COLOR',
            'name': '(0,0)',
            'default': (0.0, 0.0, 0.0),
            'min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v01_c',
            'type': 'float_vector',
            'subtype': 'COLOR',
            'name': '(0,1)',
            'default': (1.0, 1.0, 1.0),
            'min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v10_c',
            'type': 'float_vector',
            'subtype': 'COLOR',
            'name': '(1,0)',
            'default': (0.0, 0.0, 0.0),
            'min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v11_c',
            'type': 'float_vector',
            'subtype': 'COLOR',
            'name': '(1,1)',
            'default': (1.0, 1.0, 1.0),
            'min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v00_fr',
            'type': 'float',
            'name': '(0,0)',
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v01_fr',
            'type': 'float',
            'name': '(0,1)',
            'default': 2.0,
            'save_in_preset': True
        },
        {
            'attr': 'v10_fr',
            'type': 'float',
            'name': '(1,0)',
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'attr': 'v11_fr',
            'type': 'float',
            'name': '(1,1)',
            'default': 2.0,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        if self.variant == 'float':
            params = ParamSet() \
                .add_float('v00', self.v00_f) \
                .add_float('v10', self.v10_f) \
                .add_float('v01', self.v01_f) \
                .add_float('v11', self.v11_f)

        elif self.variant == 'fresnel':
            params = ParamSet() \
                .add_float('v00', self.v00_fr) \
                .add_float('v10', self.v10_fr) \
                .add_float('v01', self.v01_fr) \
                .add_float('v11', self.v11_fr)
        else:
            params = ParamSet() \
                .add_color('v00', self.v00_c) \
                .add_color('v10', self.v10_c) \
                .add_color('v01', self.v01_c) \
                .add_color('v11', self.v11_c)

        return {'2DMAPPING'}, params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color'] else 'float'

        psi_accept = {
            'noffsets': 'integer'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        psi_accept = {
            'v00': variant,
            'v01': variant,
            'v10': variant,
            'v11': variant,
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, '%s_%s' % (psi['name'], variant[0]), psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_blackbody(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'temperature'
    ]

    visibility = {}

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color'
        },
        {
            'type': 'float',
            'attr': 'temperature',
            'name': 'Temperature',
            'default': 6500.0,
            'save_in_preset': True
        }
    ]

    def get_paramset(self, scene, texture):
        return set(), ParamSet().add_float('temperature', self.temperature)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'temperature': 'float'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_brick(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'variant',
                   'brickbond',  # 'brickbevel',
                   'brickrun',
                   'mortarsize',
                   ['brickwidth', 'brickdepth', 'brickheight'],
               ] + \
               TF_brickmodtex.controls + \
               TC_brickmodtex.controls + \
               TF_bricktex.controls + \
               TC_bricktex.controls + \
               TF_mortartex.controls + \
               TC_mortartex.controls

    # Visibility we do manually because of the variant switch
    visibility = {
        'brickmodtex_colorlabel': {'variant': 'color'},
        'brickmodtex_color': {'variant': 'color'},
        'brickmodtex_usecolortexture': {'variant': 'color'},
        'brickmodtex_colortexture': {'variant': 'color', 'brickmodtex_usecolortexture': True},
        'brickmodtex_multiplycolor': {'variant': 'color', 'brickmodtex_usecolortexture': True},

        'brickmodtex_usefloattexture': {'variant': 'float'},
        'brickmodtex_floatvalue': {'variant': 'float'},
        'brickmodtex_floattexture': {'variant': 'float', 'brickmodtex_usefloattexture': True},
        'brickmodtex_multiplyfloat': {'variant': 'float', 'brickmodtex_usefloattexture': True},

        'bricktex_colorlabel': {'variant': 'color'},
        'bricktex_color': {'variant': 'color'},
        'bricktex_usecolortexture': {'variant': 'color'},
        'bricktex_colortexture': {'variant': 'color', 'bricktex_usecolortexture': True},
        'bricktex_multiplycolor': {'variant': 'color', 'bricktex_usecolortexture': True},

        'bricktex_usefloattexture': {'variant': 'float'},
        'bricktex_floatvalue': {'variant': 'float'},
        'bricktex_floattexture': {'variant': 'float', 'bricktex_usefloattexture': True},
        'bricktex_multiplyfloat': {'variant': 'float', 'bricktex_usefloattexture': True},

        'mortartex_colorlabel': {'variant': 'color'},
        'mortartex_color': {'variant': 'color'},
        'mortartex_usecolortexture': {'variant': 'color'},
        'mortartex_colortexture': {'variant': 'color', 'mortartex_usecolortexture': True},
        'mortartex_multiplycolor': {'variant': 'color', 'mortartex_usecolortexture': True},

        'mortartex_usefloattexture': {'variant': 'float'},
        'mortartex_floatvalue': {'variant': 'float'},
        'mortartex_floattexture': {'variant': 'float', 'mortartex_usefloattexture': True},
        'mortartex_multiplyfloat': {'variant': 'float', 'mortartex_usefloattexture': True},
        'brickrun': O([{'brickbond': 'running'}, {'brickbond': 'flemish'}]),
    }

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'enum',
                         'name': 'Variant',
                         'items': [
                             ('float', 'Greyscale', 'Output a floating point number'),
                             ('color', 'Color', 'Output a color value'),
                         ],
                         'expand': True,
                         'save_in_preset': True
                     },
                     {
                         'attr': 'brickbond',
                         'type': 'enum',
                         'name': 'Bond type',
                         'items': [
                             ('running', 'Running', 'running'),
                             ('stacked', 'Stacked', 'stacked'),
                             ('flemish', 'Flemish', 'flemish'),
                             ('english', 'English', 'english'),
                             ('herringbone', 'Herringbone', 'herringbone'),
                             ('basket', 'Basket', 'basket'),
                             ('chain link', 'Chain link', 'chain Link')
                         ],
                         'save_in_preset': True
                     },
                     {
                         'attr': 'brickbevel',
                         'type': 'float',
                         'name': 'Bevel',
                         'default': 0.0,
                         'precision': 6,
                         'save_in_preset': True
                     },
                     {
                         'attr': 'brickrun',
                         'type': 'float',
                         'name': 'Brick run',
                         'default': 50.0,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 100.0,
                         'soft_max': 100.0,
                         'precision': 2,
                         'subtype': 'PERCENTAGE',
                         'unit': 'NONE',
                         'save_in_preset': True
                     },
                     {
                         'attr': 'mortarsize',
                         'type': 'float',
                         'name': 'Mortar size',
                         'default': 0.01,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 1.0,
                         'soft_max': 1.0,
                         'precision': 6,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     },
                     {
                         'attr': 'brickwidth',
                         'type': 'float',
                         'name': 'Width',
                         'default': 0.3,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 10.0,
                         'soft_max': 10.0,
                         'precision': 3,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     },
                     {
                         'attr': 'brickdepth',
                         'type': 'float',
                         'name': 'Depth',
                         'default': 0.15,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 10.0,
                         'soft_max': 10.0,
                         'precision': 3,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     },
                     {
                         'attr': 'brickheight',
                         'type': 'float',
                         'name': 'Height',
                         'default': 0.1,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 10.0,
                         'soft_max': 10.0,
                         'precision': 3,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     },
                 ] + \
                 TF_brickmodtex.properties + \
                 TC_brickmodtex.properties + \
                 TF_bricktex.properties + \
                 TC_bricktex.properties + \
                 TF_mortartex.properties + \
                 TC_mortartex.properties

    def get_paramset(self, scene, texture):
        brick_params = ParamSet() \
            .add_float('brickbevel', self.brickbevel) \
            .add_string('brickbond', self.brickbond) \
            .add_float('brickdepth', self.brickdepth) \
            .add_float('brickheight', self.brickheight) \
            .add_float('brickwidth', self.brickwidth) \
            .add_float('brickrun', self.brickrun / 100) \
            .add_float('mortarsize', self.mortarsize)

        if PBRTv3Manager.GetActive() is not None:
            brick_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'brickmodtex', self.variant, self)
            )

            brick_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'bricktex', self.variant, self)
            )

            brick_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'mortartex', self.variant, self)
            )

        return {'3DMAPPING'}, brick_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color'] else 'float'

        psi_accept = {
            'brickbevel': 'float',
            'brickbond': 'string',
            'brickdepth': 'float',
            'brickheight': 'float',
            'brickwidth': 'float',
            'brickrun': 'float',
            'mortarsize': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        if self.variant == 'float':
            TF_brickmodtex.load_paramset(self, ps)
            TF_bricktex.load_paramset(self, ps)
            TF_mortartex.load_paramset(self, ps)
        else:
            TC_brickmodtex.load_paramset(self, ps)
            TC_bricktex.load_paramset(self, ps)
            TC_mortartex.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_abbe(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'spectral_line',
        'n_d',
        'n_D',
        'n_e',
        'n_custom',
        'V_d',
        'V_D',
        'V_e',
        'V_custom',
        'lambda_D',
        'lambda_F',
        'lambda_C',
    ]

    visibility = {
        'n_d': {'spectral_line': 'd'},
        'n_D': {'spectral_line': 'D'},
        'n_e': {'spectral_line': 'e'},
        'n_custom': {'spectral_line': 'custom'},
        'V_d': {'spectral_line': 'd'},
        'V_D': {'spectral_line': 'D'},
        'V_e': {'spectral_line': 'e'},
        'V_custom': {'spectral_line': 'custom'},
        'lambda_D': {'spectral_line': 'custom'},
        'lambda_F': {'spectral_line': 'custom'},
        'lambda_C': {'spectral_line': 'custom'},
    }

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'fresnel'
        },
        {
            'attr': 'spectral_line',
            'type': 'enum',
            'name': 'Type',
            'items': [
                ('d', 'd', 'd = 587.56 nm'),
                ('D', 'D', 'D = 589.3 nm'),
                ('e', 'e', 'e = 546.073 nm'),
                ('custom', 'Custom', ''),
            ],
            'default': 'd',
            'description': 'Select emission lines used to describe the Abbe number based on the primary emission line',
            'expand': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'n_d',
            'name': 'n_d',
            'description': 'Index of Refraction at the d emission line',
            'default': 1.51680,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'n_D',
            'name': 'n_D',
            'description': 'Index of Refraction at the D emission line',
            'default': 1.51673,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'n_e',
            'name': 'n_e',
            'description': 'Index of Refraction at the e emission line',
            'default': 1.51872,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'n_custom',
            'name': 'n',
            'description': 'Index of Refraction at the specified D emission line',
            'default': 1.51680,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'V_d',
            'name': 'V_d',
            'description': 'Abbe number at the d emission line',
            'default': 64.17,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 3,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'V_D',
            'name': 'V_D',
            'description': 'Abbe number at the D emission line',
            'default': 64.161,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 3,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'V_e',
            'name': 'V_e',
            'description': 'Abbe number at the e emission line',
            'default': 63.793,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 3,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'V_custom',
            'name': 'V',
            'description': 'Abbe number at the specified D emission line',
            'default': 64.17,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 3,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'lambda_D',
            'name': 'D spectral line',
            'description': 'Wavelength (in nm) representing the D emission line in the Abbe equation',
            'default': 587.5618,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 4,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'lambda_F',
            'name': 'F spectral line',
            'description': 'Wavelength (in nm) representing the F emission line in the Abbe equation',
            'default': 486.13,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 4,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'lambda_C',
            'name': 'C spectral line',
            'description': 'Wavelength (in nm) representing the C emission line in the Abbe equation',
            'default': 656.28,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 4,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        cp = ParamSet()

        cp.add_string('type', self.spectral_line)

        cp.add_float('n', getattr(self, 'n_%s' % self.spectral_line))
        cp.add_float('V', getattr(self, 'V_%s' % self.spectral_line))

        if self.spectral_line == 'custom':
            cp.add_float('lambda_D', self.lambda_D)
            cp.add_float('lambda_F', self.lambda_F)
            cp.add_float('lambda_C', self.lambda_C)

        return set(), cp

    def load_paramset(self, variant, ps):
        psi_accept = {
            'spectral_line': 'float',
            'n': 'float',
            'V': 'float',
            'lambda_D': 'float',
            'lambda_F': 'float',
            'lambda_C': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_cauchy(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'use_index',
        'draw_ior_menu',
        'a', 'ior',
        'b'
    ]

    visibility = {
        'a': {'use_index': False},
        'draw_ior_menu': {'use_index': True},
        'ior': {'use_index': True},
    }

    properties = [
        {
            'type': 'ef_callback',
            'attr': 'draw_ior_menu',
            'method': 'draw_ior_menu',
        },
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'fresnel'
        },
        {
            'type': 'bool',
            'attr': 'use_index',
            'name': 'Use IOR',
            'default': True,
            'save_in_preset': True
        },
        {
            'attr': 'ior_presetvalue',
            'type': 'float',
            'save_in_preset': True
        },
        {
            'attr': 'ior_presetstring',
            'type': 'string',
            'default': '-- Choose IOR preset --',
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'a',
            'name': 'A',
            'default': 1.458,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'ior',
            'name': 'IOR',
            'default': 1.458,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'b',
            'name': 'B',
            'default': 0.0035,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'precision': 6,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        cp = ParamSet().add_float('cauchyb', self.b)

        if self.use_index:
            cp.add_float('index', self.ior)
        else:
            cp.add_float('cauchya', self.a)

        return set(), cp

    def load_paramset(self, variant, ps):
        psi_accept = {
            'index': 'float',
            'cauchya': 'float',
            'cauchyb': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_checkerboard(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'aamode',
                   'dimension',
               ] + \
               TF_tex1.controls + \
               TF_tex2.controls

    visibility = {
        'tex1_floattexture': {'tex1_usefloattexture': True},
        'tex1_multiplyfloat': {'tex1_usefloattexture': True},
        'tex2_floattexture': {'tex2_usefloattexture': True},
        'tex2_multiplyfloat': {'tex2_usefloattexture': True},
    }

    properties = [
                     {
                         'type': 'string',
                         'attr': 'variant',
                         'default': 'float'
                     },
                     {
                         'attr': 'aamode',
                         'type': 'enum',
                         'name': 'Anti-Alias Mode',
                         'default': 'closedform',
                         'items': [
                             ('closedform', 'Closed-form', 'closedform'),
                             ('supersample', 'Supersample', 'supersample'),
                             ('none', 'None', 'none')
                         ],
                         'save_in_preset': True
                     },
                     {
                         'attr': 'dimension',
                         'type': 'int',
                         'name': 'Dimensions',
                         'default': 3,
                         'min': 2,
                         'soft_min': 2,
                         'max': 3,
                         'soft_max': 3,
                         'save_in_preset': True
                     },

                 ] + \
                 TF_tex1.properties + \
                 TF_tex2.properties

    def get_paramset(self, scene, texture):
        checkerboard_params = ParamSet() \
            .add_string('aamode', self.aamode) \
            .add_integer('dimension', self.dimension)

        if PBRTv3Manager.GetActive() is not None:
            checkerboard_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex1', self.variant, self)
            )
            checkerboard_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex2', self.variant, self)
            )

        if self.dimension == 2:
            features = {'2DMAPPING'}
        else:
            features = {'3DMAPPING'}

        return features, checkerboard_params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'aamode': 'string',
            'dimension': 'integer',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TF_tex1.load_paramset(self, ps)
        TF_tex2.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_cloud(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'radius',
        'noisescale',
        'turbulence',
        'sharpness',
        'noiseoffset',
        'spheres',
        'octaves',
        'omega',
        'variability',
        'baseflatness',
        'spheresize'
    ]

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
        {
            'type': 'float',
            'attr': 'radius',
            'name': 'Radius',
            'precision': 2,
            'description': 'Overall cloud radius inside the base cube',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'noisescale',
            'name': 'Noise Scale',
            'precision': 2,
            'description': 'Strength of the noise',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'turbulence',
            'name': 'Turbulence',
            'precision': 2,
            'description': 'Size of the noise displacement',
            'default': 0.01,
            'min': 0.0,
            'soft_min': 0.0,
            'soft_max': 0.2,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'sharpness',
            'name': 'Sharpness',
            'precision': 2,
            'description': 'Noise sharpness - increase for more spikey appearance',
            'default': 6.0,
            'min': 0.0,
            'soft_min': 0.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'noiseoffset',
            'name': 'Noise Offset',
            'precision': 2,
            'description': 'Strength of the noise',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'spheres',
            'name': 'Spheres',
            'description': 'If greater than 0, the cloud will consist of a bunch of random spheres to mimic a \
            cumulus, this is the number of random spheres. If set to 0, the cloud will consist of single \
            displaced sphere',
            'default': 0,
            'min': 0,
            'soft_min': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'octaves',
            'name': 'Octaves',
            'description': 'Number of octaves for the noise function',
            'default': 1,
            'min': 0,
            'soft_min': 0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'omega',
            'name': 'Omega',
            'precision': 2,
            'description': 'Amount of noise per octave',
            'default': 0.75,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'variability',
            'name': 'Variability',
            'precision': 2,
            'description': 'Amount of extra noise',
            'default': 0.9,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'baseflatness',
            'name': 'Base Flatness',
            'precision': 2,
            'description': 'How much the base of the cloud is flattened',
            'default': 0.8,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'spheresize',
            'name': 'Sphere Size',
            'precision': 2,
            'description': 'Maxiumum size of cumulus spheres',
            'default': 0.15,
            'min': 0.0,
            'soft_min': 0.0,
            'save_in_preset': True
        }
    ]

    def get_paramset(self, scene, texture):
        return {'3DMAPPING'}, ParamSet().add_float('radius', self.radius) \
            .add_float('noisescale', self.noisescale) \
            .add_float('turbulence', self.turbulence) \
            .add_float('sharpness', self.sharpness) \
            .add_float('noiseoffset', self.noiseoffset) \
            .add_integer('spheres', self.spheres) \
            .add_integer('octaves', self.octaves) \
            .add_float('omega', self.omega) \
            .add_float('variability', self.variability) \
            .add_float('baseflatness', self.baseflatness) \
            .add_float('spheresize', self.spheresize)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'radius': 'float',
            'noisescale': 'float',
            'turbulence': 'float',
            'sharpness': 'float',
            'noiseoffset': 'float',
            'spheres': 'integer',
            'octaves': 'integer',
            'omega': 'float',
            'variability': 'float',
            'baseflatness': 'float',
            'spheresize': 'float'

        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_constant(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'variant',
        'floatvalue',
        'colorvalue',
        'value'
        # Just use "value" for fresnel value to avoid breaking .blend
        # files made from when this tex only had a fresnel mode
    ]

    visibility = {
        'floatvalue': {'variant': 'float'},
        'colorvalue': {'variant': 'color'},
        'value': {'variant': 'fresnel'},
    }

    properties = [
        {
            'attr': 'variant',
            'type': 'enum',
            'name': 'Variant',
            'items': [
                ('float', 'Greyscale', 'Output a floating point number'),
                ('color', 'Color', 'Output a color value'),
                ('fresnel', 'Fresnel', 'Output optical data'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            'attr': 'floatvalue',
            'type': 'float',
            'name': 'Value',
            'default': 1.00,
            'precision': 4,
            'save_in_preset': True
        },
        {
            'attr': 'colorvalue',
            'type': 'float_vector',
            'name': 'Value',
            'default': (0.64, 0.64, 0.64),
            'max': 10.0,  # Blender's color picker does not behave will with unbounded colors
            'soft_max': 10.0,
            'min': -10.0,
            'soft_min': -10.0,
            'precision': 4,
            'subtype': 'COLOR',
            'save_in_preset': True
        },
        {
            'attr': 'value',
            'type': 'float',
            'name': 'Value',
            'default': 1.52,
            'min': 1.0,  # Lux core does not properly handle lower fresnel values
            'soft_min': 1.0,
            'precision': 4,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        constant_params = ParamSet()
        if self.variant == 'float':
            constant_params.add_float('value', self.floatvalue)

        if self.variant == 'color':
            constant_params.add_color('value', self.colorvalue)

        if self.variant == 'fresnel':
            constant_params.add_float('value', self.value)

        return set(), constant_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color', 'fresnel', ] else 'float'

        psi_accept = {
            'value': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_colordepth(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'depth',
               ] + \
               TC_Kt.controls

    visibility = {
        'Kt_colortexture': {'Kt_usecolortexture': True},
        'Kt_multiplycolor': {'Kt_usecolortexture': True},
    }

    properties = [
                     {
                         'type': 'string',
                         'attr': 'variant',
                         'default': 'color'
                     },
                     {
                         'type': 'float',
                         'attr': 'depth',
                         'name': 'Depth',
                         'description': 'Transmission depth at which absorption results in the given color',
                         'default': 1.0,
                         'min': 0.00001,
                         'soft_min': 0.00001,
                         'max': 1000.0,
                         'soft_max': 1000.0,
                         'precision': 6,
                         'subtype': 'DISTANCE',
                         'unit': 'LENGTH',
                         'save_in_preset': True
                     }
                 ] + \
                 TC_Kt.properties

    def get_paramset(self, scene, texture):
        colordepth_params = ParamSet().add_float('depth', self.depth)

        if PBRTv3Manager.GetActive() is not None:
            colordepth_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'Kt', 'color', self)
            )

        return set(), colordepth_params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'depth': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TC_Kt.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_densitygrid(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}
    controls = [
        'domain',
        'source',
        'wrapping'
    ]

    properties = [
                 ] + \
                 ObjectParameter('domain', 'Domain', 'Domain object for smoke simulation',
                                 'pbrtv3_tex_densitygrid') + \
                 [
                     {
                         'attr': 'source',
                         'name': 'Source',
                         'type': 'enum',
                         'items': [
                             ('density', 'Density', ''),
                             ('fire', 'Fire', ''),
                             ('temperature', 'Temperature', ''),
                             ('velocity', 'Velocity', '')
                         ],
                         'default': 'density',
                         'save_in_preset': True
                     },
                     {
                         'attr': 'wrapping',
                         'name': 'Wrapping',
                         'type': 'enum',
                         'items': [
                             ('repeat', 'Repeat', 'repeat'),
                             ('black', 'Black', 'black'),
                             ('white', 'White', 'white'),
                             ('clamp', 'Clamp', 'clamp')
                         ],
                         'default': 'black',
                         'save_in_preset': True
                     },
                     {
                         'type': 'string',
                         'attr': 'variant',
                         'default': 'float'
                     },

                 ]

    def get_paramset(self, scene, texture):
        grid = export_smoke(self.domain_object, self.source)
        nx = grid[0]
        ny = grid[1]
        nz = grid[2]
        density = grid[3]
        # smoke_path = export_smoke(self.domain_object, self.source)
        #
        # smokedata_params = ParamSet() .add_string('wrap', self.wrapping) \
        # .add_string('filename', smoke_path)

        smokedata_params = ParamSet() \
            .add_string('wrap', self.wrapping) \
            .add_integer('nx', nx) \
            .add_integer('ny', ny) \
            .add_integer('nz', nz) \
            .add_float('density', density)

        return {'3DMAPPING'}, smokedata_params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'domain_object': 'string',
            'source': 'string',
            'wrapping': 'string'
        }
        psi_accept_keys = psi_accept.keys()
        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'].lower(), psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_dots(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [  # None
               ] + \
               TF_inside.controls + \
               TF_outside.controls

    visibility = {
        'inside_usefloattexture': {'variant': 'float'},
        'inside_floatvalue': {'variant': 'float'},
        'inside_floattexture': {'variant': 'float', 'inside_usefloattexture': True},
        'inside_multiplyfloat': {'variant': 'float', 'inside_usefloattexture': True},

        'outside_usefloattexture': {'variant': 'float'},
        'outside_floatvalue': {'variant': 'float'},
        'outside_floattexture': {'variant': 'float', 'outside_usefloattexture': True},
        'outside_multiplyfloat': {'variant': 'float', 'outside_usefloattexture': True},
    }

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'string',
                         'default': 'float'
                     },
                 ] + \
                 TF_inside.properties + \
                 TF_outside.properties

    def get_paramset(self, scene, texture):
        dots_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            dots_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'inside', self.variant, self)
            )
            dots_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'outside', self.variant, self)
            )

        return {'2DMAPPING'}, dots_params

    def load_paramset(self, variant, ps):
        TF_inside.load_paramset(self, ps)
        TF_outside.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_equalenergy(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'energy'
    ]

    visibility = {}

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color'
        },
        {
            'type': 'float',
            'attr': 'energy',
            'name': 'Energy',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        }
    ]

    def get_paramset(self, scene, texture):
        return set(), ParamSet().add_float('energy', self.energy)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'energy': 'float'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_exponential(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'origin',
        'updir',
        'decay'
    ]

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
        {
            'type': 'float_vector',
            'attr': 'updir',
            'name': 'Up Vector',
            'default': (0.0, 0.0, 1.0),
            'precision': 5,
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'origin',
            'name': 'Origin',
            'default': (0.0, 0.0, 0.0),
            'precision': 5,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'decay',
            'name': ' Decay Rate',
            'precision': 2,
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'save_in_preset': True
        }
    ]

    def get_paramset(self, scene, texture):
        return {'3DMAPPING'}, ParamSet().add_vector('updir', self.updir) \
            .add_point('origin', self.origin) \
            .add_float('decay', self.decay)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'updir': 'vector',
            'origin': 'vector',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_fbm(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'octaves',
        'roughness',
    ]

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
        {
            'type': 'int',
            'attr': 'octaves',
            'name': 'Octaves',
            'default': 8,
            'min': 1,
            'soft_min': 1,
            'max': 100,
            'soft_max': 100,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        fbm_params = ParamSet().add_integer('octaves', self.octaves) \
            .add_float('roughness', self.roughness)

        return {'3DMAPPING'}, fbm_params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'octaves': 'integer',
            'roughness': 'float'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_fresnelcolor(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
               ] + \
               TC_Kr.controls

    visibility = {
        'Kr_colortexture': {'Kr_usecolortexture': True},
        'Kr_multiplycolor': {'Kr_usecolortexture': True},
    }

    properties = [
                     {
                         'type': 'string',
                         'attr': 'variant',
                         'default': 'fresnel'
                     },
                 ] + \
                 TC_Kr.properties

    def get_paramset(self, scene, texture):
        fresnelcolor_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            fresnelcolor_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'Kr', 'color', self)
            )

        return set(), fresnelcolor_params

    def load_paramset(self, variant, ps):
        TC_Kr.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_fresnelname(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'name',
        'filename',
    ]

    visibility = {
        'filename': {'name': 'nk'},
    }

    properties = [
        {
            'type': 'enum',
            'attr': 'name',
            'name': 'Preset',
            'description': 'Metal type to use, select "Use NK file" to input external metal data',
            'items': [
                ('nk', 'Use NK file', 'nk'),
                ('amorphous carbon', 'Amorphous carbon', 'amorphous carbon'),
                ('copper', 'Copper', 'copper'),
                ('gold', 'Gold', 'gold'),
                ('silver', 'Silver', 'silver'),
                ('aluminium', 'Aluminium', 'aluminium')
            ],
            'default': 'aluminium',
            'save_in_preset': True
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'filename',
            'name': 'NK file',
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'fresnel'
        },
    ]

    def get_paramset(self, scene, texture):
        fresnelname_params = ParamSet()

        if self.name == 'nk':  # use an NK data file
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(scene, texture, self.filename, fresnelname_params, 'filename')
        else:  # use a preset name
            fresnelname_params.add_string('name', self.name)

        return set(), fresnelname_params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'name': 'string',
            'filename': 'string'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_gaussian(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'energy',
        'wavelength',
        'width',
    ]

    visibility = {}

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color'
        },
        {
            'type': 'float',
            'attr': 'energy',
            'name': 'Energy',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'wavelength',
            'name': 'Wavelength (nm)',
            'default': 550.0,
            'min': 380.0,
            'soft_min': 380.0,
            'max': 720.0,
            'soft_max': 720.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'width',
            'name': 'Width (nm)',
            'default': 50.0,
            'min': 20.0,
            'soft_min': 20.0,
            'max': 300.0,
            'soft_max': 300.0,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        return set(), ParamSet().add_float('energy', self.energy) \
            .add_float('wavelength', self.wavelength) \
            .add_float('width', self.width)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'energy': 'float',
            'wavelength': 'float',
            'width': 'float'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_harlequin(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [  # None
    ]

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'color'
        },
    ]

    def get_paramset(self, scene, texture):
        harlequin_params = ParamSet()

        return set(), harlequin_params

    def load_paramset(self, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_hitpointcolor(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = []

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'color'
        },
    ]

    def get_paramset(self, scene, texture):
        hitpointcolor_params = ParamSet()

        return set(), hitpointcolor_params

    def load_paramset(self, variant, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_hitpointgrey(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = []

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
    ]

    def get_paramset(self, scene, texture):
        hitpointgrey_params = ParamSet()

        return set(), hitpointgrey_params

    def load_paramset(self, variant, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_hitpointalpha(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = []

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
    ]

    def get_paramset(self, scene, texture):
        hitpointalpha_params = ParamSet()

        return set(), hitpointalpha_params

    def load_paramset(self, variant, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_imagemap(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'variant',
        'filename',
        'channel',
        'gain',
        'gamma',
        'filtertype',
        'discardmipmaps',
        'maxanisotropy',
        'wrap',
    ]

    visibility = {
        'channel': {'variant': 'float'},
        'discardmipmaps': {'filtertype': O(['mipmap_trilinear', 'mipmap_ewa'])},
        'maxanisotropy': {'filtertype': O(['mipmap_trilinear', 'mipmap_ewa'])},
    }

    properties = [
        {
            'attr': 'variant',
            'type': 'enum',
            'name': 'Variant',
            'items': [
                ('float', 'Greyscale', 'Output a floating point number'),
                ('color', 'Color', 'Output a color value'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'filename',
            'name': 'File Name',
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'channel',
            'name': 'Channel',
            'items': [
                ('mean', 'Mean', 'mean'),
                ('red', 'Red', 'red'),
                ('green', 'Green', 'green'),
                ('blue', 'Blue', 'blue'),
                ('alpha', 'Alpha', 'alpha'),
                ('colored_mean', 'Colored Mean', 'colored_mean')
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'discardmipmaps',
            'name': 'Discard MipMaps below',
            'description': 'Set to 0 to disable',
            'default': 0,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'filtertype',
            'name': 'Filter type',
            'items': [
                ('bilinear', 'Bilinear', 'bilinear'),
                ('mipmap_trilinear', 'MipMap Trilinear', 'mipmap_trilinear'),
                ('mipmap_ewa', 'MipMap EWA', 'mipmap_ewa'),
                ('nearest', 'Nearest Neighbor', 'nearest'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'gain',
            'name': 'Gain',
            'default': 1.0,
            'description': 'Scale texture value by this amount',
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'gamma',
            'name': 'Gamma',
            'description': 'Gamma correction setting. Use 1 to get the actual values in the texture, \
            otherwise use your screen gamma',
            'default': 2.2,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 6.0,
            'soft_max': 6.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'maxanisotropy',
            'name': 'Max. Anisotropy',
            'default': 8.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'wrap',
            'name': 'Wrapping',
            'items': [
                ('repeat', 'Repeat', 'repeat'),
                ('black', 'Black', 'black'),
                ('white', 'White', 'white'),
                ('clamp', 'Clamp', 'clamp')
            ],
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        params = ParamSet()

        # This function resolves relative paths (even in linked library blends)
        # and optionally encodes/embeds the data if the setting is enabled
        process_filepath_data(scene, texture, self.filename, params, 'filename')

        params.add_integer('discardmipmaps', self.discardmipmaps) \
            .add_string('filtertype', self.filtertype) \
            .add_float('gain', self.gain) \
            .add_float('gamma', self.gamma) \
            .add_float('maxanisotropy', self.maxanisotropy) \
            .add_string('wrap', self.wrap)

        if self.variant == 'float':
            params.add_string('channel', self.channel)

        return {'2DMAPPING'}, params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color'] else 'float'

        psi_accept = {
            'filename': 'string',
            'discardmipmaps': 'integer',
            'filtertype': 'string',
            'gain': 'float',
            'gamma': 'float',
            'maxanisotropy': 'float',
            'wrap': 'string',
            'channel': 'string',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        # Use a 2nd loop to ensure that self.filename has been set
        for psi in ps:
            # embedded data decode
            if psi['name'] == 'filename_data':
                filename_data = '\n'.join(psi['value'])
                self.filename = '//%s' % self.filename
                fn = efutil.filesystem_path(self.filename)
                bdecode_string2file(filename_data, fn)


# This class holds the parameters for the image sampling panel
# which exposes Lux params when blender's image texture is selected
@PBRTv3Addon.addon_register_class
class pbrtv3_tex_imagesampling(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'channel',
        'channel_luxcore',  # PBRTv3Core needs special channel because it needs the extra "rgb" default option
        'gain',
        'gamma',
        'filtertype',
        'discardmipmaps',
        'maxanisotropy',
        'wrap',
        'wrap_info',  # PBRTv3Core only
        'is_normalmap',  # PBRTv3Core only
    ]

    # varient is auto-detected for blender image, and file path is supplied from blender tex

    visibility = {
        'channel': lambda: not UsePBRTv3Core(),
        'channel_luxcore': lambda: UsePBRTv3Core(),
        'discardmipmaps': A([{'filtertype': O(['mipmap_trilinear', 'mipmap_ewa'])}, lambda: not UsePBRTv3Core()]),
        'maxanisotropy': A([{'filtertype': O(['mipmap_trilinear', 'mipmap_ewa'])}, lambda: not UsePBRTv3Core()]),
        'filtertype': lambda: not UsePBRTv3Core(),
        # Show an info message about unsupported wrapping modes in PBRTv3Core API mode
        'wrap_info': lambda: UsePBRTv3Core(),
    }

    enabled = {
        # wrap modes are not yet supported by PBRTv3Core
        'wrap': lambda: not UsePBRTv3Core(),
    }

    properties = [
        {
            'attr': 'variant',
            'type': 'enum',
            'name': 'Variant',
            'items': [
                ('float', 'Greyscale', 'Output a floating point number'),
                ('color', 'Color', 'Output a color value'),
            ],
            'expand': True,
            'save_in_preset': True
        },  # all textures need to have a varient defined, no exceptions!
        {
            'type': 'enum',
            'attr': 'channel',
            'name': 'Channel',
            'description': 'Channel to sample for grayscale textures',
            'items': [
                ('mean', 'Mean', 'mean'),
                ('red', 'Red', 'red'),
                ('green', 'Green', 'green'),
                ('blue', 'Blue', 'blue'),
                ('alpha', 'Alpha', 'alpha'),
                ('colored_mean', 'Colored mean', 'colored_mean')
            ],
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'channel_luxcore',
            'name': 'Channel',
            'description': 'Channel to sample',
            'items': [
                ('rgb', 'RGB', 'Default, use all color channels'),
                ('red', 'Red', 'Use only the red color channel'),
                ('green', 'Green', 'Use only the green color channel'),
                ('blue', 'Blue', 'Use only the blue color channel'),
                ('alpha', 'Alpha', 'Use only the alpha channel'),
                ('mean', 'Mean', 'Greyscale'),
                ('colored_mean', 'Colored Mean', 'Greyscale'),
            ],
            'default': 'rgb',
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'discardmipmaps',
            'name': 'Discard MipMaps below',
            'description': 'Set to 0 to disable',
            'default': 0,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'filtertype',
            'name': 'Filter type',
            'items': [
                ('bilinear', 'Bilinear', 'bilinear'),
                ('mipmap_trilinear', 'MipMap trilinear', 'mipmap_trilinear'),
                ('mipmap_ewa', 'MipMap EWA', 'mipmap_ewa'),
                ('nearest', 'Nearest Neighbor', 'nearest'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'gain',
            'name': 'Gain',
            'default': 1.0,
            'description': 'Scale texture value by this amount',
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'gamma',
            'name': 'Gamma',
            'description': 'Gamma correction setting. Use 1 to get the actual values in the texture, otherwise use \
            your screen gamma',
            'default': 2.2,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 6.0,
            'soft_max': 6.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'maxanisotropy',
            'name': 'Max. Anisotropy',
            'default': 8.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'wrap',
            'name': 'Wrapping',
            'items': [
                ('repeat', 'Repeat', 'repeat'),
                ('black', 'Black', 'black'),
                ('white', 'White', 'white'),
                ('clamp', 'Clamp', 'clamp')
            ],
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'wrap_info',
            'name': 'Only "Repeat" wrapping supported by PBRTv3Core',
            'icon': 'INFO',
        },
    ]


# We do not build a paramset for imagesampling, that is handled by convert_texture in export/materials.py
@PBRTv3Addon.addon_register_class
class pbrtv3_tex_normalmap(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'filename',
        'filtertype',
        'discardmipmaps',
        'maxanisotropy',
        'wrap',
    ]

    visibility = {
        'discardmipmaps': {'filtertype': O(['mipmap_trilinear', 'mipmap_ewa'])},
        'maxanisotropy': {'filtertype': O(['mipmap_trilinear', 'mipmap_ewa'])},
    }

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'float'
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'filename',
            'name': 'File Name',
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'discardmipmaps',
            'name': 'Discard MipMaps below',
            'description': 'Set to 0 to disable',
            'default': 0,
            'min': 0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'filtertype',
            'name': 'Filter type',
            'items': [
                ('bilinear', 'Bilinear', 'bilinear'),
                ('mipmap_trilinear', 'MipMap Trilinear', 'mipmap_trilinear'),
                ('mipmap_ewa', 'MipMap EWA', 'mipmap_ewa'),
                ('nearest', 'Nearest Neighbor', 'nearest'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'maxanisotropy',
            'name': 'Max. Anisotropy',
            'default': 8.0,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'wrap',
            'name': 'Wrapping',
            'items': [
                ('repeat', 'Repeat', 'repeat'),
                # ('black', 'Black', 'black'),
                #				('white', 'White', 'white'),
                ('clamp', 'Clamp', 'clamp')
            ],
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        params = ParamSet()
        # This function resolves relative paths (even in linked library blends)
        # and optionally encodes/embeds the data if the setting is enabled
        process_filepath_data(scene, texture, self.filename, params, 'filename')

        params.add_integer('discardmipmaps', self.discardmipmaps) \
            .add_string('filtertype', self.filtertype) \
            .add_float('maxanisotropy', self.maxanisotropy) \
            .add_float('gamma', 1.0) \
            .add_string('wrap', self.wrap)
        # Don't gamma correct normal maps^

        return {'2DMAPPING'}, params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'filename': 'string',
            'discardmipmaps': 'integer',
            'filtertype': 'string',
            'maxanisotropy': 'float',
            'wrap': 'string',
        }

        psi_accept_keys = psi_accept.keys()
        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        # Use a 2nd loop to ensure that self.filename has been set
        for psi in ps:
            # embedded data decode
            if psi['name'] == 'filename_data':
                filename_data = '\n'.join(psi['value'])
                self.filename = '//%s' % self.filename
                fn = efutil.filesystem_path(self.filename)
                bdecode_string2file(filename_data, fn)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_lampspectrum(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [  # Preset menu is drawn manually in the ui class
    ]

    visibility = {}

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color'
        },  # The following two items are set by the preset menu and operator.
        {
            'type': 'string',
            'attr': 'preset',
            'name': 'Name',
            'save_in_preset': True,
        },
        {
            'type': 'string',
            'attr': 'label',
            'name': 'Name',
            'default': '-- Choose preset --',
            'update': refresh_preview,
            'save_in_preset': True,
        }
    ]

    def get_paramset(self, scene, texture):
        return set(), ParamSet().add_string('name', self.preset)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'name': 'string',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, 'preset', psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_mapping(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'type',
        ['uscale', 'vscale'],
        ['udelta', 'vdelta'],
        'v1', 'v2',
        'center_map',
    ]

    visibility = {
        'v1': {'type': 'planar'},
        'v2': {'type': 'planar'},
        'uscale': {'type': O(['uv', 'spherical', 'cylindrical'])},
        'vscale': {'type': O(['uv', 'spherical'])},  # 'udelta': # always visible
        'vdelta': {'type': O(['uv', 'spherical', 'planar'])},
        'center_map': {'type': O(['uv'])},
    }

    properties = [
        {
            'attr': 'type',
            'type': 'enum',
            'name': 'Mapping Type',
            'items': [
                ('uv', 'UV', 'uv'),
                ('planar', 'Planar', 'planar'),
                ('spherical', 'Spherical', 'spherical'),
                ('cylindrical', 'Cylindrical', 'cylindrical'),
            ],
            'save_in_preset': True
        },
        {
            'attr': 'uscale',
            'type': 'float',
            'name': 'U Scale',
            'default': 1.0,
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'precision': 5,
            'save_in_preset': True
        },
        {
            'attr': 'vscale',
            'type': 'float',
            'name': 'V Scale',
            'default': 1.0,  # gets corrected in export
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'precision': 5,
            'save_in_preset': True
        },
        {
            'attr': 'udelta',
            'type': 'float',
            'name': 'U Offset',
            'default': 0.0,
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'precision': 5,
            'save_in_preset': True
        },
        {
            'attr': 'vdelta',
            'type': 'float',
            'name': 'V Offset',
            'default': 0.0,
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'precision': 5,
            'save_in_preset': True
        },
        {
            'attr': 'v1',
            'type': 'float_vector',
            'name': 'V1',
            'default': (1.0, 0.0, 0.0),
            'precision': 5,
            'save_in_preset': True
        },
        {
            'attr': 'v2',
            'type': 'float_vector',
            'name': 'V2',
            'default': (0.0, 1.0, 0.0),
            'precision': 5,
            'save_in_preset': True
        },
        {
            'attr': 'center_map',
            'type': 'bool',
            'name': 'Center Map',
            'default': False,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene):
        mapping_params = ParamSet()

        mapping_params.add_string('mapping', self.type)

        if self.type == 'planar':
            mapping_params.add_vector('v1', self.v1)
            mapping_params.add_vector('v2', self.v2)
            mapping_params.add_float('udelta', self.udelta)
            mapping_params.add_float('vdelta', self.vdelta)

        if self.type == 'cylindrical':
            mapping_params.add_float('uscale', self.uscale)
            mapping_params.add_float('udelta', self.udelta)

        if self.type == 'spherical':
            mapping_params.add_float('uscale', self.uscale)
            mapping_params.add_float('vscale', self.vscale)
            mapping_params.add_float('udelta', self.udelta)
            mapping_params.add_float('vdelta', self.vdelta)

        if self.type == 'uv':
            mapping_params.add_float('uscale', self.uscale)
            mapping_params.add_float('vscale', self.vscale * -1)  # flip to match blender

            if not self.center_map:
                mapping_params.add_float('udelta', self.udelta)
                mapping_params.add_float('vdelta',
                                         self.vdelta + 1)  # correction for clamped types, does not harm repeat type
            else:
                mapping_params.add_float('udelta', self.udelta + 0.5 * (1.0 - self.uscale))  # auto-center the mapping
                mapping_params.add_float('vdelta',
                                         self.vdelta * -1 + 1 - (0.5 * (1.0 - self.vscale)))  # auto-center the mapping

        return mapping_params

    def load_paramset(self, ps):
        psi_accept = {
            'mapping': 'string',
            'udelta': 'float',
            'vdelta': 'float',
            'uscale': 'float',
            'vscale': 'float',
            'v1': 'vector',
            'v2': 'vector',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'] if psi['name'] != 'mapping' else 'type', psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_marble(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'octaves',
        'roughness',
        'scale',
        'variation',
    ]

    visibility = {}

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color',
            'update': refresh_preview,
        },
        {
            'type': 'int',
            'attr': 'octaves',
            'name': 'Octaves',
            'default': 8,
            'min': 1,
            'soft_min': 1,
            'max': 100,
            'soft_max': 100,
            'save_in_preset': True,
            'update': refresh_preview,
        },
        {
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'save_in_preset': True,
            'update': refresh_preview,
        },
        {
            'type': 'float',
            'attr': 'scale',
            'name': 'Scale',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 100.0,
            'soft_max': 100.0,
            'save_in_preset': True,
            'update': refresh_preview,
        },
        {
            'type': 'float',
            'attr': 'variation',
            'name': 'Variation',
            'default': 0.2,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 100.0,
            'soft_max': 100.0,
            'save_in_preset': True,
            'update': refresh_preview,
        },
    ]

    def get_paramset(self, scene, texture):
        return {'3DMAPPING'}, ParamSet().add_integer('octaves', self.octaves) \
            .add_float('roughness', self.roughness) \
            .add_float('scale', self.scale) \
            .add_float('variation', self.variation)

    def load_paramset(self, variant, ps):
        psi_accept = {
            'octaves': 'integer',
            'roughness': 'float',
            'scale': 'float',
            'variation': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_mix(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'variant',

               ] + \
               TF_amount.controls + \
               TF_tex1.controls + \
               TC_tex1.controls + \
               TFR_tex1.controls + \
               TF_tex2.controls + \
               TC_tex2.controls + \
               TFR_tex2.controls

    # Visibility we do manually because of the variant switch
    visibility = {
        'amount_floattexture': {'amount_usefloattexture': True},
        'amount_multiplyfloat': {'amount_usefloattexture': True},

        'tex1_colorlabel': {'variant': 'color'},
        'tex1_color': {'variant': 'color'},
        'tex1_usecolortexture': {'variant': 'color'},
        'tex1_colortexture': {'variant': 'color', 'tex1_usecolortexture': True},
        'tex1_multiplycolor': {'variant': 'color', 'tex1_usecolortexture': True},

        'tex1_usefloattexture': {'variant': 'float'},
        'tex1_floatvalue': {'variant': 'float'},
        'tex1_floattexture': {'variant': 'float', 'tex1_usefloattexture': True},
        'tex1_multiplyfloat': {'variant': 'float', 'tex1_usefloattexture': True},

        'tex1_usefresneltexture': {'variant': 'fresnel'},
        'tex1_fresnelvalue': {'variant': 'fresnel'},
        'tex1_fresneltexture': {'variant': 'fresnel', 'tex1_usefresneltexture': True},
        'tex1_multiplyfresnel': {'variant': 'fresnel', 'tex1_usefresneltexture': True},

        'tex2_colorlabel': {'variant': 'color'},
        'tex2_color': {'variant': 'color'},
        'tex2_usecolortexture': {'variant': 'color'},
        'tex2_colortexture': {'variant': 'color', 'tex2_usecolortexture': True},
        'tex2_multiplycolor': {'variant': 'color', 'tex2_usecolortexture': True},

        'tex2_usefloattexture': {'variant': 'float'},
        'tex2_floatvalue': {'variant': 'float'},
        'tex2_floattexture': {'variant': 'float', 'tex2_usefloattexture': True},
        'tex2_multiplyfloat': {'variant': 'float', 'tex2_usefloattexture': True},

        'tex2_usefresneltexture': {'variant': 'fresnel'},
        'tex2_fresnelvalue': {'variant': 'fresnel'},
        'tex2_fresneltexture': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
        'tex2_multiplyfresnel': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
    }

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'enum',
                         'name': 'Variant',
                         'items': [
                             ('float', 'Greyscale', 'Output a floating point number'),
                             ('color', 'Color', 'Output a color value'),
                             ('fresnel', 'Fresnel', 'Output optical data'),
                         ],
                         'expand': True,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_amount.properties + \
                 TF_tex1.properties + \
                 TC_tex1.properties + \
                 TFR_tex1.properties + \
                 TF_tex2.properties + \
                 TC_tex2.properties + \
                 TFR_tex2.properties

    def get_paramset(self, scene, texture):
        mix_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            mix_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'amount', 'float', self)
            )
            mix_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex1', self.variant, self)
            )
            mix_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex2', self.variant, self)
            )

        return set(), mix_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color', 'fresnel', ] else 'float'

        TF_amount.load_paramset(self, ps)

        if variant == 'float':
            TF_tex1.load_paramset(self, ps)
            TF_tex2.load_paramset(self, ps)

        if variant == 'color':
            TC_tex1.load_paramset(self, ps)
            TC_tex2.load_paramset(self, ps)

        if variant == 'fresnel':
            TFR_tex1.load_paramset(self, ps)
            TFR_tex2.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_multimix(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'variant',
        'nslots',
    ]

    for i in range(1, BAND_MAX_TEX + 1):
        controls.extend([
            [0.9, ['weightfloat%d' % i, 'tex%d_floatvalue' % i], 'tex%d_usefloattexture' % i],
            [0.9, 'tex%d_floattexture' % i, 'tex%d_multiplyfloat' % i],
            [0.9, ['weightcolor%d' % i, 'tex%d_color' % i], 'tex%d_usecolortexture' % i],
            [0.9, 'tex%d_colortexture' % i, 'tex%d_multiplycolor' % i],
            [0.9, ['weightfresnel%d' % i, 'tex%d_fresnelvalue' % i], 'tex%d_usefresneltexture' % i],
            [0.9, 'tex%d_fresneltexture' % i, 'tex%d_multiplyfresnel' % i],
        ])

    # Visibility we do manually because of the variant switch
    visibility = {}

    for i in range(1, BAND_MAX_TEX + 1):
        visibility.update({
            'weightcolor%d' % i: {'variant': 'color', 'nslots': LO({'>=': i})},
            'tex%d_color' % i: {'variant': 'color', 'nslots': LO({'>=': i})},
            'tex%d_usecolortexture' % i: {'variant': 'color', 'nslots': LO({'>=': i})},
            'tex%d_colortexture' % i: {'variant': 'color', 'nslots': LO({'>=': i}), 'tex%d_usecolortexture' % i: True},
            'tex%d_multiplycolor' % i: {'variant': 'color', 'nslots': LO({'>=': i}), 'tex%d_usecolortexture' % i: True},

            'weightfloat%d' % i: {'variant': 'float', 'nslots': LO({'>=': i})},
            'tex%d_usefloattexture' % i: {'variant': 'float', 'nslots': LO({'>=': i})},
            'tex%d_floatvalue' % i: {'variant': 'float', 'nslots': LO({'>=': i})},
            'tex%d_floattexture' % i: {'variant': 'float', 'nslots': LO({'>=': i}), 'tex%d_usefloattexture' % i: True},
            'tex%d_multiplyfloat' % i: {'variant': 'float', 'nslots': LO({'>=': i}), 'tex%d_usefloattexture' % i: True},

            'weightfresnel%d' % i: {'variant': 'fresnel', 'nslots': LO({'>=': i})},
            'tex%d_usefresneltexture' % i: {'variant': 'fresnel', 'nslots': LO({'>=': i})},
            'tex%d_fresnelvalue' % i: {'variant': 'fresnel', 'nslots': LO({'>=': i})},
            'tex%d_fresneltexture' % i: {'variant': 'fresnel', 'nslots': LO({'>=': i}),
                                         'tex%d_usefresneltexture' % i: True},
            'tex%d_multiplyfresnel' % i: {'variant': 'fresnel', 'nslots': LO({'>=': i}),
                                          'tex%d_usefresneltexture' % i: True},
        })

    properties = [
        {
            'attr': 'variant',
            'type': 'enum',
            'name': 'Variant',
            'items': [
                ('float', 'Greyscale', 'Output a floating point number'),
                ('color', 'Color', 'Output a color value'),
                ('fresnel', 'Fresnel', 'Output optical data'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            'attr': 'nslots',
            'type': 'int',
            'name': 'Texture count',
            'default': 2,
            'min': 2,
            'max': BAND_MAX_TEX,
            'save_in_preset': True
        },
    ]

    for i in range(1, BAND_MAX_TEX + 1):
        properties.extend([
            {
                'attr': 'weightfloat%d' % i,
                'type': 'float',
                'name': 'weight%d' % i,
                'default': 0.0,
                'precision': 3,
                'min': 0.0,
                'max': 1.0,
                'save_in_preset': True
            },
            {
                'attr': 'weightcolor%d' % i,
                'type': 'float',
                'name': 'weight%d' % i,
                'default': 0.0,
                'precision': 3,
                'min': 0.0,
                'max': 1.0,
                'save_in_preset': True
            },
            {
                'attr': 'weightfresnel%d' % i,
                'type': 'float',
                'name': 'weight%d' % i,
                'default': 0.0,
                'precision': 3,
                'min': 0.0,
                'max': 1.0,
                'save_in_preset': True
            }
        ])

    for prop in TC_BAND_ARRAY:
        properties.extend(prop.properties)

    for prop in TF_BAND_ARRAY:
        properties.extend(prop.properties)

    for prop in TFR_BAND_ARRAY:
        properties.extend(prop.properties)

    def get_paramset(self, scene, texture):
        mm_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            weights = []

            for i in range(1, self.nslots + 1):
                weights.append(getattr(self, 'weight%s%d' % (self.variant, i)))
                mm_params.update(
                    add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex%d' % i, self.variant, self)
                )

            # In API mode need to tell Lux how many slots explicity
            if PBRTv3Manager.GetActive().lux_context.API_TYPE == 'PURE':
                mm_params.add_integer('nweights', self.nslots)

            mm_params.add_float('weights', weights)

        return set(), mm_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color', 'fresnel', ] else 'float'

        weights = []
        for psi in ps:
            if psi['name'] == 'weights' and psi['type'] == 'float':
                weights = psi['value']
                self.nslots = len(psi['value'])

        if self.variant == 'float':
            for i in range(self.nslots):
                TF_BAND_ARRAY[i].load_paramset(self, ps)
                setattr(self, 'weightfloat%d' % i, weights[i])

        if self.variant == 'color':
            for i in range(self.nslots):
                TC_BAND_ARRAY[i].load_paramset(self, ps)
                setattr(self, 'weightcolor%d' % i, weights[i])

        if self.variant == 'fresnel':
            for i in range(self.nslots):
                TF_BAND_ARRAY[i].load_paramset(self, ps)
                setattr(self, 'weightfresnel%d' % i, weights[i])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_sellmeier(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'advanced',
        'a',
        'b',
        'c',
    ]

    visibility = {
        'a': {'advanced': True},
    }

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'fresnel'
        },
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'a',
            'name': 'A',
            'default': 1.0,
            'min': 0.001,
            'soft_min': 0.001,
            'max': 10.0,
            'soft_max': 10.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'b',
            'name': 'B',
            'default': (0.696, 0.408, 0.879),
            'min': 0.0,
            'soft_min': 0.0,
            'max': 100.0,
            'soft_max': 100.0,
            'precision': 6,
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'c',
            'name': 'C',
            'default': (0.0047, 0.0135, 97.93),
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 6,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, scene, texture):
        sp = ParamSet() \
            .add_float('A', self.a) \
            .add_float('B', tuple(self.b)) \
            .add_float('C', tuple(self.c))

        return set(), sp

    def load_paramset(self, variant, ps):
        psi_accept = {
            'A': 'float',
            'B': 'float',
            'C': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'].lower(), psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_scale(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'variant',

               ] + \
               TF_tex1.controls + \
               TFR_tex1.controls + \
               TC_tex1.controls + \
               TF_tex2.controls + \
               TFR_tex2.controls + \
               TC_tex2.controls

    # Visibility we do manually because of the variant switch
    visibility = {
        'tex1_colorlabel': {'variant': 'color'},
        'tex1_color': {'variant': 'color'},
        'tex1_usecolortexture': {'variant': 'color'},
        'tex1_colortexture': {'variant': 'color', 'tex1_usecolortexture': True},
        'tex1_multiplycolor': {'variant': 'color', 'tex1_usecolortexture': True},

        'tex1_usefloattexture': {'variant': 'float'},
        'tex1_floatvalue': {'variant': 'float'},
        'tex1_floattexture': {'variant': 'float', 'tex1_usefloattexture': True},
        'tex1_multiplyfloat': {'variant': 'float', 'tex1_usefloattexture': True},

        'tex1_usefresneltexture': {'variant': 'fresnel'},
        'tex1_fresnelvalue': {'variant': 'fresnel'},
        'tex1_fresneltexture': {'variant': 'fresnel', 'tex1_usefresneltexture': True},
        'tex1_multiplyfresnel': {'variant': 'fresnel', 'tex1_usefresneltexture': True},

        'tex2_colorlabel': {'variant': 'color'},
        'tex2_color': {'variant': 'color'},
        'tex2_usecolortexture': {'variant': 'color'},
        'tex2_colortexture': {'variant': 'color', 'tex2_usecolortexture': True},
        'tex2_multiplycolor': {'variant': 'color', 'tex2_usecolortexture': True},

        'tex2_usefloattexture': {'variant': 'float'},
        'tex2_floatvalue': {'variant': 'float'},
        'tex2_floattexture': {'variant': 'float', 'tex2_usefloattexture': True},
        'tex2_multiplyfloat': {'variant': 'float', 'tex2_usefloattexture': True},

        'tex2_usefresneltexture': {'variant': 'fresnel'},
        'tex2_fresnelvalue': {'variant': 'fresnel'},
        'tex2_fresneltexture': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
        'tex2_multiplyfresnel': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
    }

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'enum',
                         'name': 'Variant',
                         'items': [
                             ('float', 'Greyscale', 'Output a floating point number'),
                             ('color', 'Color', 'Output a color value'),  # ('fresnel', 'Fresnel', 'fresnel'),
                         ],
                         'expand': True,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_tex1.properties + \
                 TFR_tex1.properties + \
                 TC_tex1.properties + \
                 TF_tex2.properties + \
                 TFR_tex2.properties + \
                 TC_tex2.properties

    def get_paramset(self, scene, texture):
        scale_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            scale_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex1', self.variant, self)
            )
            scale_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex2', self.variant, self)
            )

        return set(), scale_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color'] else 'float'

        if self.variant == 'float':
            TF_tex1.load_paramset(self, ps)
            TF_tex2.load_paramset(self, ps)

        if self.variant == 'color':
            TC_tex1.load_paramset(self, ps)
            TC_tex2.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_subtract(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
                   'variant',

               ] + \
               TF_tex1.controls + \
               TFR_tex1.controls + \
               TC_tex1.controls + \
               TF_tex2.controls + \
               TFR_tex2.controls + \
               TC_tex2.controls

    # Visibility we do manually because of the variant switch
    visibility = {
        'tex1_colorlabel': {'variant': 'color'},
        'tex1_color': {'variant': 'color'},
        'tex1_usecolortexture': {'variant': 'color'},
        'tex1_colortexture': {'variant': 'color', 'tex1_usecolortexture': True},
        'tex1_multiplycolor': {'variant': 'color', 'tex1_usecolortexture': True},

        'tex1_usefloattexture': {'variant': 'float'},
        'tex1_floatvalue': {'variant': 'float'},
        'tex1_floattexture': {'variant': 'float', 'tex1_usefloattexture': True},
        'tex1_multiplyfloat': {'variant': 'float', 'tex1_usefloattexture': True},

        'tex1_usefresneltexture': {'variant': 'fresnel'},
        'tex1_fresnelvalue': {'variant': 'fresnel'},
        'tex1_fresneltexture': {'variant': 'fresnel', 'tex1_usefresneltexture': True},
        'tex1_multiplyfresnel': {'variant': 'fresnel', 'tex1_usefresneltexture': True},

        'tex2_colorlabel': {'variant': 'color'},
        'tex2_color': {'variant': 'color'},
        'tex2_usecolortexture': {'variant': 'color'},
        'tex2_colortexture': {'variant': 'color', 'tex2_usecolortexture': True},
        'tex2_multiplycolor': {'variant': 'color', 'tex2_usecolortexture': True},

        'tex2_usefloattexture': {'variant': 'float'},
        'tex2_floatvalue': {'variant': 'float'},
        'tex2_floattexture': {'variant': 'float', 'tex2_usefloattexture': True},
        'tex2_multiplyfloat': {'variant': 'float', 'tex2_usefloattexture': True},

        'tex2_usefresneltexture': {'variant': 'fresnel'},
        'tex2_fresnelvalue': {'variant': 'fresnel'},
        'tex2_fresneltexture': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
        'tex2_multiplyfresnel': {'variant': 'fresnel', 'tex2_usefresneltexture': True},
    }

    properties = [
                     {
                         'attr': 'variant',
                         'type': 'enum',
                         'name': 'Variant',
                         'items': [
                             ('float', 'Greyscale', 'Output a floating point number'),
                             ('color', 'Color', 'Output a color value'),  # ('fresnel', 'Fresnel', 'fresnel'),
                         ],
                         'expand': True,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_tex1.properties + \
                 TFR_tex1.properties + \
                 TC_tex1.properties + \
                 TF_tex2.properties + \
                 TFR_tex2.properties + \
                 TC_tex2.properties

    def get_paramset(self, scene, texture):
        subtract_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            subtract_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex1', self.variant, self)
            )

            subtract_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'tex2', self.variant, self)
            )

        return set(), subtract_params

    def load_paramset(self, variant, ps):
        self.variant = variant if variant in ['float', 'color'] else 'float'

        if self.variant == 'float':
            TF_tex1.load_paramset(self, ps)
            TF_tex2.load_paramset(self, ps)

        if self.variant == 'color':
            TC_tex1.load_paramset(self, ps)
            TC_tex2.load_paramset(self, ps)


class tabulatedbase(declarative_property_group):
    controls = [
        'filename'
    ]

    def get_paramset(self, scene, texture):
        td = ParamSet()
        # This function resolves relative paths (even in linked library blends)
        # and optionally encodes/embeds the data if the setting is enabled
        process_filepath_data(scene, texture, self.filename, td, 'filename')

        return set(), td

    def load_paramset(self, variant, ps):
        psi_accept = {
            'filename': 'string',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'].lower(), psi['value'])


class tabulatedcolor(tabulatedbase):
    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color'
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'filename',
            'name': 'File name',
            'save_in_preset': True
        },
    ]


class tabulatedfresnel(tabulatedbase):
    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'fresnel'
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'filename',
            'name': 'File name',
            'save_in_preset': True
        },
    ]


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_tabulateddata(tabulatedcolor):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_luxpop(tabulatedfresnel):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_sopra(tabulatedfresnel):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_transform(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'coordinates',
        'translate',
        'rotate',
        'scale',
        'lbl_smoke_domain',
    ]

    visibility = {
        'translate': {'coordinates': O(['global', 'globalnormal', 'local', 'localnormal', 'uv'])},
        'rotate': {'coordinates': O(['global', 'globalnormal', 'local', 'localnormal', 'uv'])},
        'scale': {'coordinates': O(['global', 'globalnormal', 'local', 'localnormal', 'uv'])},
        'lbl_smoke_domain': {'coordinates': 'smoke_domain'},
    }

    properties = [
        {
            'type': 'enum',
            'attr': 'coordinates',
            'name': 'Coordinates',
            'items': [
                ('global', 'Global', 'Use global 3D coordinates'),
                ('globalnormal', 'Global Normal', 'Use Global surface normals'),
                ('local', 'Object', 'Use object local 3D coordinates'),
                ('localnormal', 'Object Normal', 'Use object local surface normals'),
                ('uv', 'UV', 'Use UV coordinates (x=u y=v z=0)'),
                ('smoke_domain', 'Smoke Domain', 'Use Smoke Domain Coordinates'),
            ],
            'default': 'global',
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'translate',
            'name': 'Translate',
            'default': (0.0, 0.0, 0.0),
            'precision': 5,
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'rotate',
            'name': 'Rotate',
            'default': (0.0, 0.0, 0.0),
            'precision': 5,
            # 'subtype': 'DIRECTION',
            'unit': 'ROTATION',
            'save_in_preset': True
        },
        {
            'type': 'float_vector',
            'attr': 'scale',
            'name': 'Scale',
            'default': (1.0, 1.0, 1.0),
            'precision': 5,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'lbl_smoke_domain',
            'name': 'Auto Using Smoke Domain Data'
        },
    ]

    def get_paramset(self, scene):
        transform_params = ParamSet()
        ws = get_worldscale(as_scalematrix=False)
        transform_params.add_vector('rotate', self.rotate)

        if self.coordinates == 'smoke_domain':
            for tex in bpy.data.textures:
                if bpy.data.textures[tex.name].pbrtv3_texture.type == 'densitygrid':
                    domain = bpy.data.textures[tex.name].pbrtv3_texture.pbrtv3_tex_densitygrid.domain_object

            obj = bpy.context.scene.objects[domain]
            vloc = mathutils.Vector((obj.bound_box[0][0], obj.bound_box[0][1], obj.bound_box[0][2]))
            vloc_global = obj.matrix_world * vloc
            d_dim = bpy.data.objects[domain].dimensions
            transform_params.add_string('coordinates', 'global')
            transform_params.add_vector('translate', vloc_global)
            transform_params.add_vector('scale', d_dim)
        else:
            transform_params.add_string('coordinates', self.coordinates)
            transform_params.add_vector('translate', [i * ws for i in self.translate])
            transform_params.add_vector('scale', [i * ws for i in self.scale])

        return transform_params

    def load_paramset(self, ps):
        psi_accept = {
            'coordinates': 'string',
            'translate': 'vector',
            'rotate': 'vector',
            'scale': 'vector',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_uv(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = []

    visibility = {}

    properties = [
        {
            'type': 'string',
            'attr': 'variant',
            'default': 'color'
        },
    ]

    def get_paramset(self, scene, texture):
        uv_params = ParamSet()

        return {'2DMAPPING'}, uv_params

    def load_paramset(self, variant, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_uvmask(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = \
        TF_innertex.controls + \
        TF_outertex.controls

    visibility = dict_merge(
        TF_innertex.visibility,
        TF_outertex.visibility,
    )

    properties = [
                     {
                         'type': 'string',
                         'attr': 'variant',
                         'default': 'float'
                     },
                 ] + \
                 TF_innertex.properties + \
                 TF_outertex.properties

    def get_paramset(self, scene, texture):
        uvmask_params = ParamSet()

        if PBRTv3Manager.GetActive() is not None:
            uvmask_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'innertex', self.variant, self)
            )
            uvmask_params.update(
                add_texture_parameter(PBRTv3Manager.GetActive().lux_context, 'outertex', self.variant, self)
            )

        return {'2DMAPPING'}, uvmask_params

    def load_paramset(self, variant, ps):
        TF_innertex.load_paramset(self, ps)
        TF_outertex.load_paramset(self, ps)


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_windy(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = []

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
    ]

    def get_paramset(self, scene, texture):
        windy_params = ParamSet()

        return {'3DMAPPING'}, windy_params

    def load_paramset(self, variant, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_wrinkled(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'octaves',
        'roughness',
    ]

    visibility = {}

    properties = [
        {
            'attr': 'variant',
            'type': 'string',
            'default': 'float'
        },
        {
            'type': 'int',
            'attr': 'octaves',
            'name': 'Octaves',
            'default': 8,
            'min': 1,
            'soft_min': 1,
            'max': 100,
            'soft_max': 100,
            'save_in_preset': True,
            'update': refresh_preview,
        },
        {
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True,
            'update': refresh_preview,
        },
    ]

    def get_paramset(self, scene, texture):
        wrinkled_params = ParamSet().add_integer('octaves', self.octaves) \
            .add_float('roughness', self.roughness)

        return {'3DMAPPING'}, wrinkled_params

    def load_paramset(self, variant, ps):
        psi_accept = {
            'octaves': 'integer',
            'roughness': 'float',
        }
        psi_accept_keys = psi_accept.keys()
        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_hsv(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = (
        TC_input.controls +
        TF_hue.controls +
        TF_saturation.controls +
        TF_value.controls
    )

    visibility = dict_merge(
        TC_input.visibility,
        TF_hue.visibility,
        TF_saturation.visibility,
        TF_value.visibility,
    )

    properties = (
        TC_input.properties +
        TF_hue.properties +
        TF_saturation.properties +
        TF_value.properties
    )

    def get_paramset(self, scene, texture):
        # Not supported by Classic API
        return set(), ParamSet()

    def load_paramset(self, variant, ps):
        pass


@PBRTv3Addon.addon_register_class
class pbrtv3_tex_pointiness(declarative_property_group):
    ef_attach_to = ['pbrtv3_texture']
    alert = {}

    controls = [
        'curvature_mode',
        'warning_luxcore_tex',
    ]

    visibility = {
        'warning_luxcore_tex': lambda: not UsePBRTv3Core(),
    }

    properties = [
        {
            'attr': 'curvature_mode',
            'type': 'enum',
            'name': 'Curvature',
            'default': 'both',
            'items': [
                ('both', 'Both', 'Use both dents and hills'),
                ('concave', 'Concave', 'Only use dents'),
                ('convex', 'Convex', 'Only use hills'),
            ],
            'expand': True,
        },
        {
            'attr': 'warning_luxcore_tex',
            'type': 'text',
            'name': 'Not supported in Classic API mode!',
            'icon': 'ERROR',
        }
    ]

    def get_paramset(self, scene, texture):
        # Not supported by Classic API
        return set(), ParamSet()

    def load_paramset(self, variant, ps):
        pass


def import_paramset_to_blender_texture(texture, tex_type, ps):
    """
    This function is derived from, and ought to do the exact
    reverse of export.materials.convert_texture
    """

    # Some paramset item names might need to be changed to
    # blender texture parameter names
    def psi_translate(psi_name, xlate):
        if psi_name in xlate.keys():
            return xlate[psi_name]
        else:
            return psi_name

    # Some paramset item values might need to be remapped to
    # blender texture parameter values
    def psi_remap(psi_name, psi_value, xmap):
        if psi_name in xmap.keys():
            xm = xmap[psi_name]

            if type(xm) == type(lambda: None):
                return xm(psi_value)
            elif type(xm) == dict:
                if psi_value in xm.keys():
                    return xmap[psi_name][psi_value]
                else:
                    return psi_value
            else:
                return psi_value
        else:
            return psi_value

    # Process the paramset items specified in accept, and run them
    # through the translate and remap filters
    def import_ps(accept, xl={}, xmap={}):
        accept_keys = accept.keys()

        for psi in ps:
            if psi['name'] in accept_keys and psi['type'].lower() == accept[psi['name']]:
                setattr(texture, psi_translate(psi['name'], xl), psi_remap(psi['name'], psi['value'], xmap))

    import_ps({
                  'bright': 'float',
                  'contrast': 'float'
              }, {
                  'bright': 'intensity'
              })

    # Set the Blender texture type
    blender_tex_type = tex_type.replace('blender_', '').upper()
    blender_type_xlate = {
        'DISTORTEDNOISE': 'DISTORTED_NOISE'
    }

    if blender_tex_type in blender_type_xlate.keys():
        blender_tex_type = blender_type_xlate[blender_tex_type]

    texture.type = blender_tex_type

    # Get a new reference to the texture, since changing the type
    # needs to re-cast the blender texture as a subtype
    tex_name = texture.name
    texture = bpy.data.textures[tex_name]

    if texture.type == 'BLEND':
        progression_map = {
            'LINEAR': 'lin',
            'QUADRATIC': 'quad',
            'EASING': 'ease',
            'DIAGONAL': 'diag',
            'SPHERICAL': 'sphere',
            'QUADRATIC_SPHERE': 'halo',
            'RADIAL': 'radial',
        }

        import_ps({
                      'flipxy': 'bool',
                      'type': 'string'
                  }, {
                      'flipxy': 'use_flip_axis',
                      'type': 'progression'
                  }, {
                      'type': {v: k for k, v in progression_map.items()}
                  })

    if texture.type == 'CLOUDS':
        import_ps({
                      'noisetype': 'string',
                      'noisebasis': 'string',
                      'noisesize': 'float',
                      'noisedepth': 'integer'
                  },
                  {
                      'noisetype': 'noise_type',
                      'noisebasis': 'noise_basis',
                      'noisesize': 'noise_scale',
                      'noisedepth': 'noise_depth'
                  },
                  {
                      'noisetype': lambda x: x.upper(),
                      'noisebasis': lambda x: x.upper(),
                  })

    if texture.type == 'DISTORTED_NOISE':
        import_ps({
                      'type': 'string',
                      'noisebasis': 'string',
                      'distamount': 'float',
                      'noisesize': 'float',
                      'nabla': 'float'
                  }, {
                      'type': 'noise_distortion',
                      'noisebasis': 'noise_basis',
                      'distamount': 'distortion',
                      'noisesize': 'noise_scale'
                  }, {
                      'type': lambda x: x.upper(),
                      'noisebasis': lambda x: x.upper()
                  })

    if texture.type == 'MAGIC':
        import_ps({
                      'noisedepth': 'integer',
                      'turbulence': 'float'
                  }, {
                      'noisedepth': 'noise_depth'
                  })

    if texture.type == 'MARBLE':
        import_ps({
                      'type': 'string',
                      'noisetype': 'string',
                      'noisebasis': 'string',
                      'noisebasis2': 'string',
                      'noisesize': 'float',
                      'turbulence': 'float',
                      'noisedepth': 'integer'
                  }, {
                      'type': 'marble_type',
                      'noisetype': 'noise_type',
                      'noisebasis': 'noise_basis',
                      'noisebasis2': 'noise_basis_2',
                      'noisesize': 'noise_scale',
                      'noisedepth': 'noise_depth'
                  }, {
                      'type': lambda x: x.upper(),
                      'noisetype': lambda x: x.upper(),
                      'noisebasis': lambda x: x.upper(),
                      'noisebasis2': lambda x: x.upper(),
                  })

    if texture.type == 'MUSGRAVE':
        import_ps({
                      'type': 'string',
                      'h': 'float',
                      'lacu': 'float',
                      'noisebasis': 'string',
                      'noisesize': 'float',
                      'octs': 'float'
                  }, {
                      'type': 'musgrave_type',
                      'h': 'dimension_max',
                      'lacu': 'lacunarity',
                      'noisebasis': 'noise_basis',
                      'noisesize': 'noise_scale',
                      'octs': 'octaves'
                  }, {
                      'type': lambda x: x.upper(),
                      'noisebasis': lambda x: x.upper(),
                  })

    # NOISE shows no params ?

    if texture.type == 'STUCCI':
        import_ps({
                      'type': 'string',
                      'noisetype': 'string',
                      'noisebasis': 'string',
                      'noisesize': 'float',
                      'turbulence': 'float'
                  }, {
                      'type': 'stucci_type',
                      'noisetype': 'noise_type',
                      'noisebasis': 'noise_basis',
                      'noisesize': 'noise_scale'
                  }, {
                      'type': lambda x: x.upper(),
                      'noisetype': lambda x: x.upper(),
                      'noisebasis': lambda x: x.upper(),
                  })

    if texture.type == 'VORONOI':
        distancem_map = {
            'DISTANCE': 'actual_distance',
            'DISTANCE_SQUARED': 'distance_squared',
            'MANHATTAN': 'manhattan',
            'CHEBYCHEV': 'chebychev',
            'MINKOVSKY_HALF': 'minkovsky_half',
            'MINKOVSKY_FOUR': 'minkovsky_four',
            'MINKOVSKY': 'minkovsky'
        }
        import_ps({
                      'distmetric': 'string',
                      'minkovsky_exp': 'float',
                      'noisesize': 'float',
                      'nabla': 'float',
                      'w1': 'float',
                      'w2': 'float',
                      'w3': 'float',
                      'w4': 'float',
                  }, {
                      'distmetric': 'distance_metric',
                      'minkovsky_exp': 'minkovsky_exponent',
                      'noisesize': 'noise_scale',
                      'w1': 'weight_1',
                      'w2': 'weight_1',
                      'w3': 'weight_1',
                      'w4': 'weight_1',
                  }, {
                      'distmetric': {v: k for k, v in distancem_map.items()}
                  })

    if texture.type == 'WOOD':
        import_ps({
                      'noisebasis': 'string',
                      'noisebasis2': 'string',
                      'noisesize': 'float',
                      'noisetype': 'string',
                      'turbulence': 'float',
                      'type': 'string'
                  }, {
                      'noisebasis': 'noise_basis',
                      'noisebasis2': 'noise_basis_2',
                      'noisesize': 'noise_scale',
                      'noisetype': 'noise_type',
                      'type': 'wood_type'
                  }, {
                      'noisebasis': lambda x: x.upper(),
                      'noisebasis2': lambda x: x.upper(),
                      'noisetype': lambda x: x.upper(),
                      'type': lambda x: x.upper(),
                  })
