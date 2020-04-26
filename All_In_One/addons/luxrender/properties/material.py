# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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
import re

import bpy

from ..extensions_framework import declarative_property_group

from .. import LuxRenderAddon
from ..properties import find_node
from ..properties.texture import (
    FloatTextureParameter, ColorTextureParameter, FresnelTextureParameter,
    import_paramset_to_blender_texture, shorten_name, refresh_preview
)
from ..export import ParamSet, process_filepath_data
from ..export.materials import (
    MaterialCounter, ExportedMaterials, ExportedTextures, add_texture_parameter, get_texture_from_scene
)
from ..outputs import LuxManager, LuxLog
from ..util import dict_merge


def MaterialParameter(attr, name, property_group):
    return [
        {
            'attr': '%s_material' % attr,
            'type': 'string',
            'name': '%s_material' % attr,
            'description': '%s_material' % attr,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': attr,
            'src': lambda s, c: s.object,
            'src_attr': 'material_slots',
            'trg': lambda s, c: getattr(c, property_group),
            'trg_attr': '%s_material' % attr,
            'name': name
        },
    ]


def VolumeParameter(attr, name):
    return [
        {
            'attr': '%s_volume' % attr,
            'type': 'string',
            'name': '%s_volume' % attr,
            'description': '%s volume; leave blank to use World default' % attr,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': attr,
            'src': lambda s, c: s.scene.luxrender_volumes,
            'src_attr': 'volumes',
            'trg': lambda s, c: c.luxrender_material,
            'trg_attr': '%s_volume' % attr,
            'name': name
        },
    ]


class SubGroupFloatTextureParameter(FloatTextureParameter):
    def texture_slot_set_attr(self):
        # Looks in a different location than other FloatTextureParameters
        return lambda s, c: c.luxrender_material


def texture_append_visibility(vis_main, textureparam_object, vis_append):
    for prop in textureparam_object.properties:
        if 'attr' in prop.keys():
            if not prop['attr'] in vis_main.keys():
                vis_main[prop['attr']] = {}

            for vk, vi in vis_append.items():
                vis_main[prop['attr']][vk] = vi

    return vis_main

# Float Textures
TF_bumpmap = SubGroupFloatTextureParameter('bumpmap', 'Bump Map', add_float_value=True, min=-5.0, max=5.0, default=0.01,
                                           precision=6, multiply_float=True, ignore_unassigned=True, subtype='DISTANCE',
                                           unit='LENGTH')
TF_normalmap = SubGroupFloatTextureParameter('normalmap', 'Normal Map', add_float_value=True, min=-5.0, max=5.0,
                                             default=1.0, precision=6, multiply_float=False, ignore_unassigned=True)
TF_amount = FloatTextureParameter('amount', 'Mix amount', add_float_value=True, min=0.0, default=0.5, max=1.0)
TF_cauchyb = FloatTextureParameter('cauchyb', 'Cauchy B', add_float_value=True, default=0.0, min=0.0,
                                   max=1.0)  # default 0.0 for OFF
TF_d = FloatTextureParameter('d', 'Absorption depth (nm)', add_float_value=True, default=0.0, min=0.0,
                             max=2500.0)  # default 0.0 for OFF
TF_film = FloatTextureParameter('film', 'Thin film thickness (nm)', add_float_value=True, min=0.0, default=0.0,
                                max=2500.0)  # default 0.0 for OFF
TF_filmindex = FloatTextureParameter('filmindex', 'Film IOR', add_float_value=True, default=1.3333, min=1.0,
                                     max=6.0)  # default 1.3333 for a coating of a water-based solution

# default of something other than 1.0 so glass and roughglass render propery with defaults
TF_index = FloatTextureParameter('index', 'IOR', add_float_value=True, min=0.0, max=25.0, default=1.520)

# carpaint defaults set for a basic gray clearcoat paint job, as a "setting suggestion"
TF_M1 = FloatTextureParameter('M1', 'M1', add_float_value=True, default=0.250, min=0.0001, max=1.0)

# set m1-3 min to .0001, carpaint will take 0.0 as being max (1.0)
TF_M2 = FloatTextureParameter('M2', 'M2', add_float_value=True, default=0.100, min=0.0001, max=1.0)
TF_M3 = FloatTextureParameter('M3', 'M3', add_float_value=True, default=0.015, min=0.0001, max=1.0)
TF_R1 = FloatTextureParameter('R1', 'R1', add_float_value=True, min=0.00001, max=1.0, default=0.950)
TF_R2 = FloatTextureParameter('R2', 'R2', add_float_value=True, min=0.00001, max=1.0, default=0.90)
TF_R3 = FloatTextureParameter('R3', 'R3', add_float_value=True, min=0.00001, max=1.0, default=0.7)
TF_sigma = FloatTextureParameter('sigma', 'Sigma', add_float_value=True, min=0.0, max=45.0)
TF_uroughness = FloatTextureParameter('uroughness', 'U-Roughness', add_float_value=True, min=0.000001, max=0.8,
                                      default=0.075)
TF_uexponent = FloatTextureParameter('uexponent', 'U-Exponent', add_float_value=True, min=1.0, max=1000000000000,
                                     default=353.556)
TF_vroughness = FloatTextureParameter('vroughness', 'V-Roughness', add_float_value=True, min=0.000001, max=0.8,
                                      default=0.075)
TF_vexponent = FloatTextureParameter('vexponent', 'V-Exponent', add_float_value=True, min=1.0, max=1000000000000,
                                     default=353.556)
TF_backface_d = FloatTextureParameter('bf_d', 'Backface absorption depth (nm)', real_attr='backface_d',
                                      add_float_value=True, default=0.0, min=0.0, max=1500.0)  # default 0.0 for OFF
TF_backface_index = FloatTextureParameter('bf_index', 'Backface IOR', real_attr='backface_index', add_float_value=True,
                                          min=0.0, max=25.0, default=1.333333)

# backface roughness is high than front by default, will usually be for backs of leaves or cloth
TF_backface_uroughness = FloatTextureParameter('bf_uroughness', 'Backface U-Roughness', real_attr='backface_uroughness',
                                               add_float_value=True, min=0.00001, max=1.0, default=0.25)
TF_backface_uexponent = FloatTextureParameter('bf_uexponent', 'Backface U-Exponent', real_attr='backface_uexponent',
                                              add_float_value=True, min=1.0, max=1000000000000, default=30)
TF_backface_vroughness = FloatTextureParameter('bf_vroughness', 'Backface V-Roughness', real_attr='backface_vroughness',
                                               add_float_value=True, min=0.00001, max=1.0, default=0.25)
TF_backface_vexponent = FloatTextureParameter('bf_vexponent', 'Backface V-Exponent', real_attr='backface_vexponent',
                                              add_float_value=True, min=1.0, max=1000000000000, default=30)

# These are for the layered mat:
TF_OP1 = FloatTextureParameter('opacity1', 'Opacity 1', add_float_value=True, default=1.0, min=0.0, max=1.0)
TF_OP2 = FloatTextureParameter('opacity2', 'Opacity 2', add_float_value=True, default=1.0, min=0.0, max=1.0)
TF_OP3 = FloatTextureParameter('opacity3', 'Opacity 3', add_float_value=True, default=1.0, min=0.0, max=1.0)
TF_OP4 = FloatTextureParameter('opacity4', 'Opacity 4', add_float_value=True, default=1.0, min=0.0, max=1.0)

# Color Textures
TC_Ka = ColorTextureParameter('Ka', 'Absorption color', default=(0.0, 0.0, 0.0))
TC_Kd = ColorTextureParameter('Kd', 'Diffuse color', default=(0.64, 0.64, 0.64))

# 1.0 reflection color is not sane for mirror or shinymetal, 0.7 does not signifcantly affect glass or roughglass
TC_Kr = ColorTextureParameter('Kr', 'Reflection color', default=(0.7, 0.7, 0.7))
TC_Ks = ColorTextureParameter('Ks', 'Specular color', default=(0.04, 0.04, 0.04))
TC_Ks1 = ColorTextureParameter('Ks1', 'Specular color 1', default=(0.05, 0.05, 0.05))
TC_Ks2 = ColorTextureParameter('Ks2', 'Specular color 2', default=(0.07, 0.07, 0.07))
TC_Ks3 = ColorTextureParameter('Ks3', 'Specular color 3', default=(0.04, 0.04, 0.04))
TC_Kt = ColorTextureParameter('Kt', 'Transmission color', default=(1.0, 1.0, 1.0))
TC_backface_Ka = ColorTextureParameter('backface_Ka', 'Backface Absorption color', default=(0.0, 0.0, 0.0))

# .02 = 1.333, the IOR of water
TC_backface_Ks = ColorTextureParameter('backface_Ks', 'Backface Specular color', default=(0.02, 0.02, 0.02))
TC_warp_Kd = ColorTextureParameter('warp_Kd', 'Warp Diffuse Color', default=(0.64, 0.64, 0.64))
TC_warp_Ks = ColorTextureParameter('warp_Ks', 'Warp Specular Color', default=(0.04, 0.04, 0.04))
TC_weft_Kd = ColorTextureParameter('weft_Kd', 'Weft Diffuse Color', default=(0.64, 0.64, 0.64))
TC_weft_Ks = ColorTextureParameter('weft_Ks', 'Weft Specular Color', default=(0.04, 0.04, 0.04))

# Fresnel Textures
TFR_fresnel = FresnelTextureParameter('fresnel', 'Fresnel', add_float_value=False)

mat_names = {
    'matte': 'Matte',
    'mattetranslucent': 'Matte Translucent',
    'glossy': 'Glossy',
    'glossycoating': 'Glossy Coating',
    'glossytranslucent': 'Glossy Translucent',
    'glass': 'Glass',
    'glass2': 'Glass2',
    'roughglass': 'Rough Glass',
    'mirror': 'Mirror',
    'carpaint': 'Car Paint',
    'metal': 'Metal',
    'metal2': 'Metal2',
    'shinymetal': 'Shiny Metal',
    'velvet': 'Velvet',
    'cloth': 'Cloth',
    'scatter': 'Scatter',
    'mix': 'Mix',
    'layered': 'Layered',
    'null': 'Null',
}


@LuxRenderAddon.addon_register_class
class MATERIAL_OT_set_luxrender_type(bpy.types.Operator):
    bl_idname = 'material.set_luxrender_type'
    bl_label = 'Set LuxRender material type'

    mat_name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.material and \
               context.material.luxrender_material

    def execute(self, context):
        context.material.luxrender_material.set_type(self.properties.mat_name)
        return {'FINISHED'}


@LuxRenderAddon.addon_register_class
class MATERIAL_MT_luxrender_type(bpy.types.Menu):
    bl_label = 'Material Type'

    def draw(self, context):
        sl = self.layout

        for m_name in sorted(mat_names.keys()):
            op = sl.operator('MATERIAL_OT_set_luxrender_type', text=mat_names[m_name])
            op.mat_name = m_name


def luxrender_bumpmap_export(self, lux_context, material, bumpmap_material_name, TF_bumpmap, TF_normalmap):
    bump_params = ParamSet()
    if self.normalmap_usefloattexture:  # We have a normal map
        # Get the normal map
        texture_name = getattr(material.luxrender_material, 'normalmap_floattexturename')

        if texture_name and self.normalmap_usefloattexture:
            texture = get_texture_from_scene(LuxManager.CurrentScene, texture_name)
            lux_texture = texture.luxrender_texture
            params = ParamSet()

            if lux_texture.type in ('normalmap', 'imagemap'):
                if lux_texture.type == 'normalmap':
                    src_texture = lux_texture.luxrender_tex_normalmap
                else:
                    src_texture = lux_texture.luxrender_tex_imagemap

                process_filepath_data(LuxManager.CurrentScene, texture, src_texture.filename, params, 'filename')
                params.add_integer('discardmipmaps', src_texture.discardmipmaps)
                params.add_string('filtertype', src_texture.filtertype)
                params.add_float('maxanisotropy', src_texture.maxanisotropy)
                params.add_float('gamma', 1.0)  # Don't gamma correct normal maps
                params.add_string('wrap', src_texture.wrap)
                params.update(lux_texture.luxrender_tex_mapping.get_paramset(LuxManager.CurrentScene))
            elif lux_texture.type == 'BLENDER' and texture.type == 'IMAGE':
                src_texture = texture.image

                params = ParamSet()
                process_filepath_data(LuxManager.CurrentScene, texture, src_texture.filepath, params, 'filename')
                params.add_string('filtertype', 'bilinear')
                params.add_float('gamma', 1.0)  # Don't gamma correct normal maps
                params.update(lux_texture.luxrender_tex_mapping.get_paramset(LuxManager.CurrentScene))
            else:
                LuxLog('Texture %s is not a normal map! Greyscale height maps should be applied to \
                 the bump channel.' % texture_name)

            ExportedTextures.texture(
                lux_context,
                self.normalmap_floattexturename,
                'float',
                'normalmap',
                params
            )

            ExportedTextures.export_new(lux_context)

            if self.normalmap_multiplyfloat:
                ExportedTextures.texture(
                    lux_context,
                    '%s_scaled' % self.normalmap_floattexturename,
                    'float',
                    'scale',
                    ParamSet() \
                    .add_float('tex1', self.normalmap_floatvalue) \
                    .add_texture('tex2', self.normalmap_floattexturename)
                )
                ExportedTextures.export_new(lux_context)

                # Attach it to the bump map slot:
                bump_params.add_texture('bumpmap', '%s_scaled' % self.normalmap_floattexturename)
            else:
                # Attach the normal map directly to the bump slot
                bump_params.add_texture('bumpmap', self.normalmap_floattexturename)

    if self.bumpmap_usefloattexture:  # We have a bump map
        bump_params.update(TF_bumpmap.get_paramset(self))

    # We have both normal and bump, need to mix them
    if self.normalmap_usefloattexture and self.bumpmap_usefloattexture:
        bumpmap_texturename = self.bumpmap_floattexturename if self.bumpmap_usefloattexture else ''
        normalmap_floattexturename = self.normalmap_floattexturename if self.normalmap_usefloattexture else ''

        # Get the bump map
        texture_name = getattr(material.luxrender_material, 'bumpmap_floattexturename')
        if texture_name:
            texture = get_texture_from_scene(LuxManager.CurrentScene, texture_name)
            lux_texture = texture.luxrender_texture

            if lux_texture.type == 'BLENDER' and texture.type == 'IMAGE':
                bumpmap_texturename = '%s_float' % bumpmap_texturename

        # Build the multi-mix tex of the summed bump and normal maps
        mm_params = ParamSet() \
            .add_texture('tex1', bumpmap_texturename) \
            .add_texture('tex2', normalmap_floattexturename)

        if self.bumpmap_multiplyfloat and self.normalmap_multiplyfloat:
            weights = [self.bumpmap_floatvalue, self.normalmap_floatvalue]
        elif self.bumpmap_multiplyfloat:
            weights = [self.bumpmap_floatvalue, 1.0]
        elif self.normalmap_multiplyfloat:
            weights = [1.0, self.normalmap_floatvalue]
        else:
            weights = [1.0, 1.0]

        # In API mode need to tell Lux how many slots explicity
        if LuxManager.GetActive().lux_context.API_TYPE == 'PURE':
            mm_params.add_integer('nweights', 2)

        # Now add the actual weights
        mm_params.add_float('weights', weights)

        mm_texturename = '%s_bump_normal_mix' % bumpmap_material_name
        ExportedTextures.texture(
            lux_context,
            mm_texturename,
            'float',
            'multimix',
            mm_params
        )

        ExportedTextures.export_new(lux_context)

        # Overwrite the old maps with the combined map
        bump_params.add_texture('bumpmap', mm_texturename)

    return bump_params


@LuxRenderAddon.addon_register_class
class luxrender_material(declarative_property_group):
    """
    Storage class for LuxRender Material settings.
    """

    ef_attach_to = ['Material']
    alert = {}

    def set_viewport_properties(self, context):
        # This function is exectued when changing the material type
        # it will update several properties of the blender material so the viewport better matches the Lux material
        # Kill spec intensity for matte materials
        if self.type in ('matte', 'mattetranslucent', 'scatter'):
            context.material.specular_intensity = 0
        # Make perfectly specular mats shiny
        elif self.type in ('glass', 'glass2', 'mirror'):
            context.material.specular_intensity = 0.7
            context.material.specular_hardness = 511
        # Reset spec intensity if the mat type becomes some other mat
        else:
            context.material.specular_intensity = 0.5
            context.material.specular_hardness = 50

        # Make glass and null mats transparent
        if self.type in ('glass', 'glass2', 'roughglass'):
            context.material.use_transparency = True
            context.material.alpha = 0.8
        elif self.type == 'null':
            context.material.use_transparency = True
            context.material.alpha = 0.1
        else:
            context.material.use_transparency = False
            context.material.alpha = 1.0

        # Also refresh the preview when changing mat type
        refresh_preview(self, context)

    controls = [  # Type select Menu is drawn manually  #'nodetree', drawn manually
                  'Interior',
                  'Exterior',
                  # 'generatetangents' TODO: Make this checkbox actually do something (it has to write a line to the mesh definition)
               ] + \
               TF_normalmap.controls + \
               TF_bumpmap.controls

    visibility = dict_merge({}, TF_bumpmap.visibility, TF_normalmap.visibility)

    properties = [  # The following two items are set by the preset menu and operator.
                    {
                        'attr': 'type_label',
                        'name': 'LuxRender Type',
                        'type': 'string',
                        'default': 'Matte',
                        'save_in_preset': True
                    },
                    {
                        'type': 'string',
                        'attr': 'type',
                        'name': 'Type',
                        'default': 'matte',
                        'update': set_viewport_properties,
                        'save_in_preset': True
                    },
                    {
                        'type': 'bool',
                        'attr': 'mat_preview_flip_xz',
                        'description': 'Flip flat preview xz orientation',
                        'name': 'Flip XZ',
                        'default': False
                    },
                    {
                        'attr': 'preview_zoom',
                        'type': 'float',
                        'description': 'Zoom Factor of preview camera',
                        'name': 'Zoom Factor',
                        'min': 1.0,
                        'soft_min': 0.5,
                        'max': 2.0,
                        'soft_max': 2.0,
                        'step': 25,
                        'default': 1.0
                    },
                    {
                        'attr': 'nodetree',
                        'type': 'string',
                        'description': 'Node tree',
                        'name': 'Node Tree',
                        'default': ''
                    },
                    # {
                    # 'type': 'bool',
                    # 'attr': 'generatetangents',
                    # 'name': 'Generate Tangents',
                    # 'description': 'Generate tanget space for meshes with this material. Enable when using a bake-generated normal map',
                    # 'default': False,
                    # },
                 ] + \
                 TF_bumpmap.get_properties() + \
                 TF_normalmap.get_properties() + \
                 VolumeParameter('Interior', 'Interior') + \
                 VolumeParameter('Exterior', 'Exterior')

    def set_type(self, mat_type):
        self.type = mat_type
        self.type_label = mat_names[mat_type]

    # Decide which material property sets the viewport object
    # colour for each material type. If the property name is
    # not set, then the color won't be changed.
    master_color_map = {
        'carpaint': 'Kd',
        'cloth': 'warp_Kd',
        'glass': 'Kt',
        'roughglass': 'Kt',
        'glossy': 'Kd',
        'glossytranslucent': 'Kd',
        'matte': 'Kd',
        'mattetranslucent': 'Kr',
        'metal2': 'Kr',
        'shinymetal': 'Kr',
        'mirror': 'Kr',
        'scatter': 'Kd',
        'velvet': 'Kd',
    }


    def reset(self, prnt=None):
        super().reset()

        # Also reset sub-property groups
        for a in mat_names.keys():
            getattr(self, 'luxrender_mat_%s' % a).reset()

        if prnt:
            prnt.luxrender_emission.reset()
            prnt.luxrender_transparency.reset()
            prnt.luxrender_coating.reset()

    def set_master_color(self, blender_material):
        """
        This little function will set the blender material colour to the value
        given in the material panel.
        CAVEAT: you can only call this method in an operator context.
        """

        if blender_material is None:
            return

        if self.type in self.master_color_map.keys():
            submat = getattr(self, 'luxrender_mat_%s' % self.type)
            submat_col = getattr(submat, '%s_color' % self.master_color_map[self.type])
            if blender_material.diffuse_color != submat_col:
                blender_material.diffuse_color = submat_col

    def exportNodetree(self, scene, lux_context, material, mode):
        outputNode = find_node(material, 'luxrender_material_output_node')

        print('outputNode: ', outputNode)

        if outputNode is None:
            return set()

        return outputNode.export(scene, lux_context, material, mode)


    def export(self, scene, lux_context, material, mode='indirect'):
        mat_is_transparent = False
        if self.type in ['glass', 'glass2', 'null']:
            mat_is_transparent = True

        if scene.luxrender_testing.clay_render and not mat_is_transparent:
            return {'CLAY'}

        if self.nodetree:
            return self.exportNodetree(scene, lux_context, material, mode)

        with MaterialCounter(material.name):
            if not (mode == 'indirect' and material.name in ExportedMaterials.exported_material_names):
                if self.type == 'mix':
                    # First export the other mix mats
                    m1_name = self.luxrender_mat_mix.namedmaterial1_material
                    if not m1_name:
                        raise Exception('Unassigned mix material slot 1 on material %s' % material.name)

                    m1 = bpy.data.materials[m1_name]
                    m1.luxrender_material.export(scene, lux_context, m1, 'indirect')
                    m2_name = self.luxrender_mat_mix.namedmaterial2_material

                    if not m2_name:
                        raise Exception('Unassigned mix material slot 2 on material %s' % material.name)

                    m2 = bpy.data.materials[m2_name]
                    m2.luxrender_material.export(scene, lux_context, m2, 'indirect')

                if self.type == 'glossycoating':
                    bm_name = self.luxrender_mat_glossycoating.basematerial_material

                    if not bm_name:
                        raise Exception('No base material assigned!')

                    bm = bpy.data.materials[bm_name]
                    bm.luxrender_material.export(scene, lux_context, bm, 'indirect')

                if self.type == 'layered':
                    m1_name = self.luxrender_mat_layered.namedmaterial1_material

                    if not m1_name:
                        raise Exception('Unassigned layered material slot 1 on material %s' % material.name)

                    m1 = bpy.data.materials[m1_name]
                    m1.luxrender_material.export(scene, lux_context, m1, 'indirect')
                    m2_name = self.luxrender_mat_layered.namedmaterial2_material

                    if m2_name:  # core layered mat simply stops when finding empty slot
                        m2 = bpy.data.materials[m2_name]
                        m2.luxrender_material.export(scene, lux_context, m2, 'indirect')

                    m3_name = self.luxrender_mat_layered.namedmaterial3_material

                    if m3_name:
                        m3 = bpy.data.materials[m3_name]
                        m3.luxrender_material.export(scene, lux_context, m3, 'indirect')

                    m4_name = self.luxrender_mat_layered.namedmaterial4_material

                    if m4_name:
                        m4 = bpy.data.materials[m4_name]
                        m4.luxrender_material.export(scene, lux_context, m4, 'indirect')

                material_params = ParamSet()
                subtype = getattr(self, 'luxrender_mat_%s' % self.type)
                alpha_type = None

                # find alpha texture if material should be transparent
                if hasattr(material, 'luxrender_transparency') and material.luxrender_transparency.transparent:
                    alpha_type, alpha_amount = material.luxrender_transparency.export(lux_context, material)

                coating_params = None

                # find coating if material should be coated
                if hasattr(material, 'luxrender_coating') and material.luxrender_coating.use_coating:
                    coating_params = material.luxrender_coating.export(lux_context, material)

                # Bump and normal mapping
                if self.type not in ['mix', 'null', 'layered']:
                    material_params.update(
                        luxrender_bumpmap_export(self, lux_context, material, material.name, TF_bumpmap, TF_normalmap))

                if hasattr(subtype, 'export'):
                    subtype.export(lux_context, material)

                material_params.update(subtype.get_paramset(material))

                # DistributedPath compositing
                if scene.luxrender_integrator.surfaceintegrator == 'distributedpath':
                    material_params.update(self.luxrender_mat_compositing.get_paramset())

                mat_type = self.type

                if coating_params is not None:
                    # export coating
                    material_params.add_string('type', mat_type)

                    ExportedMaterials.makeNamedMaterial(lux_context, material.name + '_base', material_params)
                    ExportedMaterials.export_new_named(lux_context)

                    # replace material params with glossycoating
                    mat_type = 'glossycoating'
                    material_params = coating_params \
                        .add_string('basematerial', material.name + '_base')

                if alpha_type is not None:
                    # export mix for transparency
                    material_params.add_string('type', mat_type)
                    ExportedMaterials.makeNamedMaterial(lux_context, material.name + '_null',
                                                        ParamSet().add_string('type', 'null'))
                    ExportedMaterials.makeNamedMaterial(lux_context, material.name + '_mat', material_params)
                    ExportedMaterials.export_new_named(lux_context)

                    # replace material params with mix
                    mat_type = 'mix'
                    material_params = ParamSet() \
                        .add_string('namedmaterial1', material.name + '_null') \
                        .add_string('namedmaterial2', material.name + '_mat')

                    if alpha_type == 'float':
                        material_params.add_float('amount', alpha_amount)
                    else:
                        material_params.add_texture('amount', alpha_amount)

                if mode == 'indirect':
                    material_params.add_string('type', mat_type)
                    ExportedMaterials.makeNamedMaterial(lux_context, material.name, material_params)
                    ExportedMaterials.export_new_named(lux_context)
                elif mode == 'direct':
                    lux_context.material(mat_type, material_params)

        if material.luxrender_emission.use_emission:
            return {'EMITTER'}
        else:
            return set()

    def load_lbm2(self, context, lbm2, blender_mat, blender_obj):
        """
        Load LBM2 data into this material, either from LRMDB or from file
        (Includes setting up textures and volumes!)

        NOTE: this function may well overwrite material settings if the
        imported data contains objects of the same name as exists in the
        scene already.
        It will also clear and reset all material and texture slots.
        """

        # Remove all materials assigned to blender_obj
        while len(blender_obj.material_slots) > 0:
            bpy.ops.object.material_slot_remove()

        for tsi in range(18):
            blender_mat.texture_slots.clear(tsi)

        # Change the name of this material to the target material in the lbm2 data
        blender_mat.name = shorten_name(lbm2['name'])

        material_index = 0

        for lbm2_obj in lbm2['objects']:
            # Add back all the textures
            if lbm2_obj['type'] == 'Texture':
                # parse variant and type first
                vt_matches = re.match('"(.*)" "(.*)"', lbm2_obj['extra_tokens'])
                if vt_matches.lastindex != 2:
                    continue  # not a valid texture!

                variant, tex_type = vt_matches.groups()
                tex_slot = blender_mat.texture_slots.add()

                if lbm2_obj['name'] not in bpy.data.textures:
                    bpy.data.textures.new(name=shorten_name(lbm2_obj['name']), type='NONE')

                blender_tex = bpy.data.textures[shorten_name(lbm2_obj['name'])]
                tex_slot.texture = blender_tex
                lxt = bpy.data.textures[shorten_name(lbm2_obj['name'])].luxrender_texture

                # Restore default texture settings
                lxt.reset()

                if (not tex_type.startswith('blender_')) and hasattr(lxt, 'luxrender_tex_%s' % tex_type):
                    lxt.set_type(tex_type)
                    subtype = getattr(lxt, 'luxrender_tex_%s' % tex_type)
                    subtype.load_paramset(variant, lbm2_obj['paramset'])
                else:
                    lxt.set_type('BLENDER')
                    # do the reverse of export.materials.convert_texture
                    import_paramset_to_blender_texture(blender_tex, tex_type, lbm2_obj['paramset'])

                lxt.luxrender_tex_mapping.load_paramset(lbm2_obj['paramset'])
                lxt.luxrender_tex_transform.load_paramset(lbm2_obj['paramset'])

            # Add back all the materials
            if lbm2_obj['type'] == 'MakeNamedMaterial':
                if lbm2_obj['name'] not in bpy.data.materials:
                    bpy.data.materials.new(name=shorten_name(lbm2_obj['name']))

                bpy.ops.object.material_slot_add()
                blender_obj.material_slots[material_index].material = bpy.data.materials[shorten_name(lbm2_obj['name'])]

                # Update an existing material with data from lbm2
                lxm = bpy.data.materials[shorten_name(lbm2_obj['name'])].luxrender_material

                # reset this material
                lxm.reset(prnt=bpy.data.materials[shorten_name(lbm2_obj['name'])])

                # Set up bump map
                TF_bumpmap.load_paramset(lxm, lbm2_obj['paramset'])
                subtype = None

                # First iterate for the material type, because
                # we need to know which sub PropertyGroup to
                # set the other paramsetitems in
                for paramsetitem in lbm2_obj['paramset']:
                    if paramsetitem['name'] == 'type':
                        lxm.set_type(paramsetitem['value'])
                        subtype = getattr(lxm, 'luxrender_mat_%s' % paramsetitem['value'])

                if subtype is not None:
                    subtype.load_paramset(lbm2_obj['paramset'])

                material_index += 1

        for lbm2_obj in lbm2['objects']:
            # Load volume data in a separate loop to ensure
            # that any textures used have already been created
            if lbm2_obj['type'] == 'MakeNamedVolume':
                # parse volume type first
                vt_matches = re.match('"(.*)"', lbm2_obj['extra_tokens'])
                if vt_matches.lastindex != 1:
                    continue  # not a valid volume!

                scene_vols = context.scene.luxrender_volumes.volumes
                try:
                    # Use existing vol if present
                    volm = scene_vols[lbm2_obj['name']]
                except KeyError:
                    # else make a new one
                    scene_vols.add()
                    volm = scene_vols[len(scene_vols) - 1]
                    volm.name = lbm2_obj['name']

                volm.reset()
                volm.type = vt_matches.groups()[0]

                # load paramset will also assign any textures used to the world
                volm.load_paramset(context.scene.world, lbm2_obj['paramset'])

        # restore interior/exterior from metadata, if present
        if 'metadata' in lbm2.keys():
            if 'interior' in lbm2['metadata'].keys():
                self.Interior_volume = lbm2['metadata']['interior']

            if 'exterior' in lbm2['metadata'].keys():
                self.Exterior_volume = lbm2['metadata']['exterior']

        self.set_master_color(blender_mat)
        blender_mat.preview_render_type = blender_mat.preview_render_type


@LuxRenderAddon.addon_register_class
class luxrender_mat_compositing(declarative_property_group):
    """
    Storage class for LuxRender Material compositing settings
    for DistributedPath integrator.
    """

    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
        'use_compositing',
        ['visible_material',
         'visible_emission'],
        ['visible_indirect_material',
         'visible_indirect_emission'],
        'override_alpha',
        'override_alpha_value',
    ]

    visibility = {
        'visible_material': {'use_compositing': True},
        'visible_emission': {'use_compositing': True},
        'visible_indirect_material': {'use_compositing': True},
        'visible_indirect_emission': {'use_compositing': True},
        'override_alpha': {'use_compositing': True},
        'override_alpha_value': {'use_compositing': True, 'override_alpha': True},
    }

    properties = [
        {
            'type': 'bool',
            'attr': 'use_compositing',
            'name': 'Use Compositing Settings',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'visible_material',
            'name': 'Visible Material',
            'default': True,
            'description': 'Disable to render this material as a holdout (mask). The normal material will still be \
            visible in reflections and GI',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'visible_emission',
            'name': 'Visible Emission',
            'description': 'If disabled, an emitting object will not appear to shine, even when acting as a \
            light emitter',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'visible_indirect_material',
            'name': 'Visible Indirect Material',
            'description': 'Disable to hide this object from GI',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'visible_indirect_emission',
            'name': 'Visible Indirect Emission',
            'description': 'If disabled, an emitting object will not cast light, even though it appears to shine \
            when viewed directly',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'override_alpha',
            'name': 'Override Alpha',
            'description': 'If enabled along with disabling visible-direct, the resulting alpha value will the value \
            set below rather than 0',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'override_alpha_value',
            'name': 'Override Alpha Value',
            'default': 0.0,
            'description': 'Alternate alpha value to use with Override-Alpha',
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'slider': True,
            'save_in_preset': True
        },
    ]

    def get_paramset(self):
        compo_params = ParamSet()

        if self.use_compositing:
            compo_params.add_bool('compo_visible_material', self.visible_material)
            compo_params.add_bool('compo_visible_emission', self.visible_emission)
            compo_params.add_bool('compo_visible_indirect_material', self.visible_indirect_material)
            compo_params.add_bool('compo_visible_indirect_emission', self.visible_indirect_emission)
            compo_params.add_bool('compo_override_alpha', self.override_alpha)
            if self.override_alpha:
                compo_params.add_float('compo_override_alpha_value', self.override_alpha_value)

        return compo_params

    def load_paramset(self, ps):
        for psi in ps:
            for prop in self.properties:
                if prop['type'] == psi['type'] and prop['attr'] == psi['name']:
                    setattr(self, psi['name'], psi['value'])


def link_anisotropy(self, context, chan='u'):
    if not self.anisotropic and not self.use_exponent:
        if chan == 'v':
            return

        self.vroughness_floatvalue = self.uroughness_floatvalue
        self.vroughness_usefloattexture = self.uroughness_usefloattexture
        self.vroughness_floattexturename = self.uroughness_floattexturename
        self.vroughness_multiplyfloat = self.uroughness_multiplyfloat

    if not self.anisotropic and self.use_exponent:
        if chan == 'v':
            return

        self.vexponent_floatvalue = self.uexponent_floatvalue
        self.vexponent_usefloattexture = self.uexponent_usefloattexture
        self.vexponent_floattexturename = self.uexponent_floattexturename
        self.vexponent_multiplyfloat = self.uexponent_multiplyfloat


def link_backface_anisotropy(self, context, chan='u'):
    if not self.bf_anisotropic and not self.bf_exponent:
        if chan == 'v':
            return

        self.bf_vroughness_floatvalue = self.bf_uroughness_floatvalue
        self.bf_vroughness_usefloattexture = self.bf_uroughness_usefloattexture
        self.bf_vroughness_floattexturename = self.bf_uroughness_floattexturename
        self.bf_vroughness_multiplyfloat = self.bf_uroughness_multiplyfloat

    if not self.bf_anisotropic and self.bf_exponent:
        if chan == 'v':
            return

        self.bf_vexponent_floatvalue = self.bf_uexponent_floatvalue
        self.bf_vexponent_usefloattexture = self.bf_uexponent_usefloattexture
        self.bf_vexponent_floattexturename = self.bf_uexponent_floattexturename
        self.bf_vexponent_multiplyfloat = self.bf_uexponent_multiplyfloat


def gen_CB_update_exponent(chan='u'):
    def update_exponent(self, context):
        if not self.use_exponent:
            setattr(self,
                    '%sexponent_floatvalue' % chan,
                    (2.0 / (getattr(self, '%sroughness_floatvalue' % chan) ** 2) - 2.0)
            )
            setattr(self,
                    '%sexponent_usefloattexture' % chan,
                    getattr(self, '%sroughness_usefloattexture' % chan)
            )
            setattr(self,
                    '%sexponent_floattexturename' % chan,
                    getattr(self, '%sroughness_floattexturename' % chan)
            )
            setattr(self,
                    '%sexponent_multiplyfloat' % chan,
                    getattr(self, '%sroughness_multiplyfloat' % chan)
            )

            link_anisotropy(self, context, chan)
            refresh_preview(self, context)

    return update_exponent


def gen_CB_update_roughness(chan='u'):
    def update_roughness(self, context):
        if self.use_exponent:
            setattr(self,
                    '%sroughness_floatvalue' % chan,
                    (2.0 / (getattr(self, '%sexponent_floatvalue' % chan) + 2.0)) ** 0.5
            )
            setattr(self,
                    '%sroughness_usefloattexture' % chan,
                    getattr(self, '%sexponent_usefloattexture' % chan)
            )
            setattr(self,
                    '%sroughness_floattexturename' % chan,
                    getattr(self, '%sexponent_floattexturename' % chan)
            )
            setattr(self,
                    '%sroughness_multiplyfloat' % chan,
                    getattr(self, '%sexponent_multiplyfloat' % chan)
            )

            link_anisotropy(self, context, chan)
            refresh_preview(self, context)

    return update_roughness


def gen_CB_update_backface_exponent(chan='u'):
    def update_backface_exponent(self, context):
        if not self.bf_exponent:
            setattr(self,
                    'bf_%sexponent_floatvalue' % chan,
                    (2.0 / (getattr(self, 'bf_%sroughness_floatvalue' % chan) ** 2) - 2.0)
            )
            setattr(self,
                    'bf_%sexponent_usefloattexture' % chan,
                    getattr(self, 'bf_%sroughness_usefloattexture' % chan)
            )
            setattr(self,
                    'bf_%sexponent_floattexturename' % chan,
                    getattr(self, 'bf_%sroughness_floattexturename' % chan)
            )
            setattr(self,
                    'bf_%sexponent_multiplyfloat' % chan,
                    getattr(self, 'bf_%sroughness_multiplyfloat' % chan)
            )

            link_backface_anisotropy(self, context, chan)
            refresh_preview(self, context)

    return update_backface_exponent


def gen_CB_update_backface_roughness(chan='u'):
    def update_backface_roughness(self, context):
        if self.bf_exponent:
            setattr(self,
                    'bf_%sroughness_floatvalue' % chan,
                    (2.0 / (getattr(self, 'bf_%sexponent_floatvalue' % chan) + 2.0)) ** 0.5
            )
            setattr(self,
                    'bf_%sroughness_usefloattexture' % chan,
                    getattr(self, 'bf_%sexponent_usefloattexture' % chan)
            )
            setattr(self,
                    'bf_%sroughness_floattexturename' % chan,
                    getattr(self, 'bf_%sexponent_floattexturename' % chan)
            )
            setattr(self,
                    'bf_%sroughness_multiplyfloat' % chan,
                    getattr(self, 'bf_%sexponent_multiplyfloat' % chan)
            )

            link_backface_anisotropy(self, context, chan)
            refresh_preview(self, context)

    return update_backface_roughness


class TransparencyFloatTextureParameter(FloatTextureParameter):
    def texture_slot_set_attr(self):
        # Looks in a different location than other ColorTextureParameters
        return lambda s, c: c.luxrender_transparency


TF_alpha = TransparencyFloatTextureParameter('alpha', 'Alpha', add_float_value=False, default=1.0, min=0.0, max=1.0)


@LuxRenderAddon.addon_register_class
class luxrender_transparency(declarative_property_group):
    """
    Storage class for LuxRender Material alpha transparency settings.
    """
    ef_attach_to = ['Material']
    alert = {}

    controls = [
                   'alpha_source',
                   'alpha_value',
               ] + \
               TF_alpha.controls + \
               [
                   'inverse',
               ]

    visibility = dict_merge(
        {
            'alpha_source': {'transparent': True},
            'alpha_value': {'transparent': True, 'alpha_source': 'constant'},
            'inverse': {'transparent': True, 'alpha_source': 'texture'},
        },
        TF_alpha.visibility
    )
    visibility = texture_append_visibility(visibility, TF_alpha, {'transparent': True, 'alpha_source': 'texture'})

    properties = [
                     {  # Drawn in the panel header
                        'type': 'bool',
                        'attr': 'transparent',
                        'name': 'Transparent',
                        'description': 'Enable alpha transparency',
                        'default': False,
                        'save_in_preset': True
                     },
                     {
                         'type': 'enum',
                         'attr': 'alpha_source',
                         'name': 'Alpha source',
                         'default': 'diffusealpha',
                         'items': [
                             ('texture', 'texture', 'texture'),
                             ('diffuseintensity', 'diffuse/reflection intensity', 'diffuseintensity'),
                             ('diffusemean', 'diffuse/reflection mean', 'diffusemean'),
                             ('diffusealpha', 'diffuse/reflection alpha', 'diffusealpha'),
                             ('constant', 'constant', 'constant')
                         ],
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'alpha_value',
                         'name': 'Alpha value',
                         'default': 0.5,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 1.0,
                         'soft_max': 1.0,
                         'slider': True,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'inverse',
                         'name': 'Inverse',
                         'description': 'Use the inverse of the alpha source',
                         'default': False,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_alpha.get_properties()

    sourceMap = {
        'carpaint': 'Kd',
        'glass': 'Kr',
        'glossy': 'Kd',
        'glossytranslucent': 'Kd',
        'matte': 'Kd',
        'mattetranslucent': 'Kr',
        'mirror': 'Kr',
        'roughglass': 'Kr',
        'scatter': 'Kd',
        'shinymetal': 'Kr',
        'velvet': 'Kd',
        'metal2': 'Kr',
    }

    def export(self, lux_context, material):
        lux_material = getattr(material.luxrender_material, 'luxrender_mat_%s' % material.luxrender_material.type)
        alpha_type = None

        if self.alpha_source == 'texture':
            alpha_type = 'texture'
            # alpha_amount = self.alpha_floattexturename

            # export texture
            TF_alpha.get_paramset(self)

            # We take the name of the last texture exported, since
            # the texture export code may have re-written the name

            if len(ExportedTextures.exported_texture_names) < 1:
                raise Exception("Cannot get alpha texture for material %s" % material.name)

            alpha_amount = ExportedTextures.exported_texture_names[-1]

            if self.inverse:
                params = ParamSet() \
                    .add_float('tex1', 1.0) \
                    .add_float('tex2', 0.0) \
                    .add_texture('amount', alpha_amount)

                alpha_amount = alpha_amount + '_alpha'

                ExportedTextures.texture(
                    lux_context,
                    alpha_amount,
                    'float',
                    'mix',
                    params
                )

                ExportedTextures.export_new(lux_context)

        elif self.alpha_source == 'constant':
            alpha_type = 'float'
            alpha_amount = self.alpha_value
        elif material.luxrender_material.type in self.sourceMap:
            # grab base texture in case it's not diffuse channel
            texture_name = getattr(lux_material,
                                   '%s_colortexturename' % self.sourceMap[material.luxrender_material.type])
            if texture_name:
                texture = get_texture_from_scene(LuxManager.CurrentScene, texture_name)
                lux_texture = texture.luxrender_texture

                if lux_texture.type == 'imagemap':
                    src_texture = lux_texture.luxrender_tex_imagemap

                    channelMap = {
                        'diffusealpha': 'alpha',
                        'diffusemean': 'mean',
                        'diffuseintensity': 'colored_mean',
                    }

                    params = ParamSet()
                    process_filepath_data(LuxManager.CurrentScene, texture, src_texture.filename, params, 'filename')
                    params.add_string('channel', channelMap[self.alpha_source])
                    params.add_integer('discardmipmaps', src_texture.discardmipmaps)
                    params.add_string('filtertype', src_texture.filtertype)
                    params.add_float('maxanisotropy', src_texture.maxanisotropy)
                    params.add_float('gamma', 1.0)  # Don't gamma correct alpha maps
                    params.add_string('wrap', src_texture.wrap)
                    params.update(lux_texture.luxrender_tex_mapping.get_paramset(LuxManager.CurrentScene))

                    alpha_type = 'texture'
                    alpha_amount = texture_name + '_alpha'

                    ExportedTextures.texture(
                        lux_context,
                        alpha_amount,
                        'float',
                        'imagemap',
                        params
                    )

                    ExportedTextures.export_new(lux_context)
                elif texture.luxrender_texture.type == 'BLENDER' and texture.type == 'IMAGE':
                    src_texture = texture.image

                    channelMap = {
                        'diffusealpha': 'alpha',
                        'diffusemean': 'mean',
                        'diffuseintensity': 'colored_mean',
                    }

                    params = ParamSet()
                    process_filepath_data(LuxManager.CurrentScene, texture, src_texture.filepath, params, 'filename')
                    params.add_string('channel', channelMap[self.alpha_source])
                    params.add_string('filtertype', 'bilinear')
                    params.add_float('gamma', 1.0)  # Don't gamma correct alpha maps
                    params.add_string('wrap', 'repeat')
                    params.update(lux_texture.luxrender_tex_mapping.get_paramset(LuxManager.CurrentScene))

                    alpha_type = 'texture'
                    alpha_amount = texture_name + '_alpha'

                    ExportedTextures.texture(
                        lux_context,
                        alpha_amount,
                        'float',
                        'imagemap',
                        params
                    )
                    ExportedTextures.export_new(lux_context)
                else:
                    LuxLog('Texture %s is not an alpha map!' % texture_name)
        if alpha_type is None:
            LuxLog('WARNING: Invalid alpha texture for material ''%s'', disabling transparency' % material.name)
            return None, None

        return alpha_type, alpha_amount


class CoatingColorTextureParameter(ColorTextureParameter):
    def texture_slot_set_attr(self):
        # Looks in a different location than other ColorTextureParameters
        return lambda s, c: c.luxrender_coating


class CoatingFloatTextureParameter(FloatTextureParameter):
    def texture_slot_set_attr(self):
        # Looks in a different location than other ColorTextureParameters
        return lambda s, c: c.luxrender_coating

# Float Textures
TF_c_d = CoatingFloatTextureParameter('d', 'Absorption depth (nm)', add_float_value=True, default=0.0, min=0.0,
                                      max=2500.0)  # default 0.0 for OFF

# default of something other than 1.0 so glass and roughglass render propery with defaults
TF_c_index = CoatingFloatTextureParameter('index', 'IOR', add_float_value=True, min=0.0, max=25.0, default=1.520)
TF_c_uroughness = CoatingFloatTextureParameter('uroughness', 'U-Roughness', add_float_value=True, min=0.000001, max=0.8,
                                               default=0.075)
TF_c_uexponent = CoatingFloatTextureParameter('uexponent', 'U-Exponent', add_float_value=True, min=1.0,
                                              max=1000000000000, default=353.556)
TF_c_vroughness = CoatingFloatTextureParameter('vroughness', 'V-Roughness', add_float_value=True, min=0.000001, max=0.8,
                                               default=0.075)
TF_c_vexponent = CoatingFloatTextureParameter('vexponent', 'V-Exponent', add_float_value=True, min=1.0,
                                              max=1000000000000, default=353.556)
TF_c_bumpmap = CoatingFloatTextureParameter('bumpmap', 'Bump Map', add_float_value=True, min=-5.0, max=5.0,
                                            default=0.01, precision=6, multiply_float=True, ignore_unassigned=True,
                                            subtype='DISTANCE', unit='LENGTH')
TF_c_normalmap = CoatingFloatTextureParameter('normalmap', 'Normal Map', add_float_value=True, min=-5.0, max=5.0,
                                              default=1.0, precision=6, multiply_float=False, ignore_unassigned=True)

# Color Textures
TC_c_Ka = CoatingColorTextureParameter('Ka', 'Absorption color', default=(0.0, 0.0, 0.0))
TC_c_Ks = CoatingColorTextureParameter('Ks', 'Specular color', default=(0.04, 0.04, 0.04))


@LuxRenderAddon.addon_register_class
class luxrender_coating(declarative_property_group):
    """
    Storage class for LuxRender Material glossy coating settings.
    """

    ef_attach_to = ['Material']
    alert = {}

    controls = [] + \
               TF_c_normalmap.controls + \
               TF_c_bumpmap.controls + \
               [
                   'multibounce',
               ] + \
               TF_c_d.controls + \
               TC_c_Ka.controls + \
               [
                   'useior',
                   'draw_ior_menu',
               ] + \
               TF_c_index.controls + \
               TC_c_Ks.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_c_uroughness.controls + \
               TF_c_uexponent.controls + \
               TF_c_vroughness.controls + \
               TF_c_vexponent.controls

    visibility = dict_merge(
        {

            'multibounce': {'use_coating': True},

            'useior': {'use_coating': True},
            'draw_ior_menu': {'use_coating': True, 'useior': True},
            'anisotropic': {'use_coating': True},
            'use_exponent': {'use_coating': True}
        },
        TF_c_d.visibility,
        TF_c_index.visibility,
        TC_c_Ka.visibility,
        TC_c_Ks.visibility,
        TF_c_uroughness.visibility,
        TF_c_uexponent.visibility,
        TF_c_vroughness.visibility,
        TF_c_vexponent.visibility,
        TF_c_normalmap.visibility,
        TF_c_bumpmap.visibility
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_c_vroughness, {'use_coating': True, 'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_c_vexponent, {'use_coating': True, 'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_c_normalmap, {'use_coating': True})
    visibility = texture_append_visibility(visibility, TF_c_bumpmap, {'use_coating': True})
    visibility = texture_append_visibility(visibility, TF_c_uroughness, {'use_coating': True, 'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_c_vroughness, {'use_coating': True, 'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_c_uexponent, {'use_coating': True, 'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_c_vexponent, {'use_coating': True, 'use_exponent': True})

    visibility = texture_append_visibility(visibility, TC_c_Ks, {'use_coating': True, 'useior': False})
    visibility = texture_append_visibility(visibility, TF_c_index, {'use_coating': True, 'useior': True})
    visibility = texture_append_visibility(visibility, TC_c_Ka, {'use_coating': True})
    visibility = texture_append_visibility(visibility, TF_c_d, {'use_coating': True})

    properties = [
                     {  # Drawn in the panel header
                        'type': 'bool',
                        'attr': 'use_coating',
                        'name': 'Use Coating',
                        'description': 'Enable glossy coating layer',
                        'default': False,
                        'save_in_preset': True
                     },
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_coating_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'multibounce',
                         'name': 'Multibounce',
                         'description': 'Enable surface layer multibounce',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'useior',
                         'name': 'Use IOR',
                         'description': 'Use IOR/Reflective index input',
                         'default': False,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_c_normalmap.get_properties() + \
                 TF_c_bumpmap.get_properties() + \
                 TF_c_d.get_properties() + \
                 TF_c_index.get_properties() + \
                 TC_c_Ka.get_properties() + \
                 TC_c_Ks.get_properties() + \
                 TF_c_uroughness.get_properties() + \
                 TF_c_uexponent.get_properties() + \
                 TF_c_vroughness.get_properties() + \
                 TF_c_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')
        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')
        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def export(self, lux_context, material):
        glossycoating_params = ParamSet()

        glossycoating_params.add_bool('multibounce', self.multibounce)

        if self.d_floatvalue > 0:
            glossycoating_params.update(TF_c_d.get_paramset(self))
            glossycoating_params.update(TC_c_Ka.get_paramset(self))

        if self.useior:
            glossycoating_params.update(TF_c_index.get_paramset(self))
            glossycoating_params.add_color('Ks', (1.0, 1.0, 1.0))
        else:
            glossycoating_params.update(TC_c_Ks.get_paramset(self))
            glossycoating_params.add_float('index', 0.0)

        glossycoating_params.update(TF_c_uroughness.get_paramset(self))
        glossycoating_params.update(TF_c_vroughness.get_paramset(self))

        glossycoating_params.update(
            luxrender_bumpmap_export(self, lux_context, material, material.name + '_coating', TF_c_bumpmap,
                                     TF_c_normalmap))

        return glossycoating_params


@LuxRenderAddon.addon_register_class
class luxrender_mat_carpaint(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'name'
               ] + \
               TF_d.controls + \
               TC_Ka.controls + \
               TC_Kd.controls + \
               TC_Ks1.controls + \
               TC_Ks2.controls + \
               TC_Ks3.controls + \
               TF_M1.controls + \
               TF_M2.controls + \
               TF_M3.controls + \
               TF_R1.controls + \
               TF_R2.controls + \
               TF_R3.controls

    visibility = dict_merge(
        TF_d.visibility,
        TC_Ka.visibility,
        TC_Kd.visibility,
        TC_Ks1.visibility,
        TC_Ks2.visibility,
        TC_Ks3.visibility,
        TF_M1.visibility,
        TF_M2.visibility,
        TF_M3.visibility,
        TF_R1.visibility,
        TF_R2.visibility,
        TF_R3.visibility
    )

    visibility = texture_append_visibility(visibility, TC_Kd, {'name': '-'})
    visibility = texture_append_visibility(visibility, TC_Ks1, {'name': '-'})
    visibility = texture_append_visibility(visibility, TC_Ks2, {'name': '-'})
    visibility = texture_append_visibility(visibility, TC_Ks3, {'name': '-'})
    visibility = texture_append_visibility(visibility, TF_M1, {'name': '-'})
    visibility = texture_append_visibility(visibility, TF_M2, {'name': '-'})
    visibility = texture_append_visibility(visibility, TF_M3, {'name': '-'})
    visibility = texture_append_visibility(visibility, TF_R1, {'name': '-'})
    visibility = texture_append_visibility(visibility, TF_R2, {'name': '-'})
    visibility = texture_append_visibility(visibility, TF_R3, {'name': '-'})

    properties = [
                     {
                         'type': 'enum',
                         'attr': 'name',
                         'name': 'Preset',
                         'items': [
                             ('-', 'Manual settings', '-'),
                             ('2k acrylack', '2k Acrylack', '2k acrylack'),
                             ('blue', 'Blue', 'blue'),
                             ('blue matte', 'Blue Matte', 'blue matte'),
                             ('bmw339', 'BMW 339', 'bmw339'),
                             ('ford f8', 'Ford F8', 'ford f8'),
                             ('opel titan', 'Opel Titan', 'opel titan'),
                             ('polaris silber', 'Polaris Silber', 'polaris silber'),
                             ('white', 'White', 'white'),
                         ],
                         'save_in_preset': True
                     },
                 ] + \
                 TF_d.get_properties() + \
                 TC_Ka.get_properties() + \
                 TC_Kd.get_properties() + \
                 TC_Ks1.get_properties() + \
                 TC_Ks2.get_properties() + \
                 TC_Ks3.get_properties() + \
                 TF_M1.get_properties() + \
                 TF_M2.get_properties() + \
                 TF_M3.get_properties() + \
                 TF_R1.get_properties() + \
                 TF_R2.get_properties() + \
                 TF_R3.get_properties()

    def get_paramset(self, material):
        carpaint_params = ParamSet()

        if self.d_floatvalue > 0:
            carpaint_params.update(TF_d.get_paramset(self))
            carpaint_params.update(TC_Ka.get_paramset(self))

        if self.name == '-':  # Use manual settings
            carpaint_params.update(TC_Kd.get_paramset(self))
            carpaint_params.update(TC_Ks1.get_paramset(self))
            carpaint_params.update(TC_Ks2.get_paramset(self))
            carpaint_params.update(TC_Ks3.get_paramset(self))
            carpaint_params.update(TF_M1.get_paramset(self))
            carpaint_params.update(TF_M2.get_paramset(self))
            carpaint_params.update(TF_M3.get_paramset(self))
            carpaint_params.update(TF_R1.get_paramset(self))
            carpaint_params.update(TF_R2.get_paramset(self))
            carpaint_params.update(TF_R3.get_paramset(self))
        else:  # Use preset
            carpaint_params.add_string('name', self.name)

        return carpaint_params

    def load_paramset(self, ps):
        psi_accept = {
            'name': 'string'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TF_d.load_paramset(self, ps)
        TC_Ka.load_paramset(self, ps)
        TC_Kd.load_paramset(self, ps)
        TC_Ks1.load_paramset(self, ps)
        TC_Ks2.load_paramset(self, ps)
        TC_Ks3.load_paramset(self, ps)
        TF_M1.load_paramset(self, ps)
        TF_M2.load_paramset(self, ps)
        TF_M3.load_paramset(self, ps)
        TF_R1.load_paramset(self, ps)
        TF_R2.load_paramset(self, ps)
        TF_R3.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_glass(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'architectural',
               ] + \
               TF_cauchyb.controls + \
               TF_film.controls + \
               TF_filmindex.controls + \
               [
                   'draw_ior_menu'
               ] + \
               TF_index.controls + \
               TC_Kr.controls + \
               TC_Kt.controls

    visibility = dict_merge(
        TF_cauchyb.visibility,
        TF_film.visibility,
        TF_filmindex.visibility,
        TF_index.visibility,
        TC_Kr.visibility,
        TC_Kt.visibility
    )

    properties = [
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'architectural',
                         'name': 'Architectural',
                         'default': False,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_cauchyb.get_properties() + \
                 TF_film.get_properties() + \
                 TF_filmindex.get_properties() + \
                 TF_index.get_properties() + \
                 TC_Kr.get_properties() + \
                 TC_Kt.get_properties()

    def get_paramset(self, material):
        glass_params = ParamSet()

        glass_params.add_bool('architectural', self.architectural)

        glass_params.update(TF_cauchyb.get_paramset(self))
        glass_params.update(TF_film.get_paramset(self))
        glass_params.update(TF_filmindex.get_paramset(self))
        glass_params.update(TF_index.get_paramset(self))
        glass_params.update(TC_Kr.get_paramset(self))
        glass_params.update(TC_Kt.get_paramset(self))

        return glass_params

    def load_paramset(self, ps):
        psi_accept = {
            'architectural': 'bool',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TF_cauchyb.load_paramset(self, ps)
        TF_film.load_paramset(self, ps)
        TF_filmindex.load_paramset(self, ps)
        TF_index.load_paramset(self, ps)
        TC_Kr.load_paramset(self, ps)
        TC_Kt.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_glass2(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
        'architectural',
        'dispersion'
    ]

    visibility = {}

    properties = [
        {
            'type': 'bool',
            'attr': 'architectural',
            'name': 'Architectural',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'dispersion',
            'name': 'Dispersion',
            'default': False,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, material):
        glass2_params = ParamSet()

        glass2_params.add_bool('architectural', self.architectural)
        glass2_params.add_bool('dispersion', self.dispersion)

        return glass2_params

    def load_paramset(self, ps):
        psi_accept = {
            'architectural': 'bool',
            'dispersion': 'bool',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@LuxRenderAddon.addon_register_class
class luxrender_mat_roughglass(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'dispersion',
               ] + \
               TF_cauchyb.controls + \
               [
                   'draw_ior_menu',
               ] + \
               TF_index.controls + \
               TC_Kr.controls + \
               TC_Kt.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls

    visibility = dict_merge(
        TF_cauchyb.visibility,
        TF_index.visibility,
        TC_Kr.visibility,
        TC_Kt.visibility,
        TF_uroughness.visibility,
        TF_uexponent.visibility,
        TF_vroughness.visibility,
        TF_vexponent.visibility,
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})

    properties = [
                     {
                         'type': 'bool',
                         'attr': 'dispersion',
                         'name': 'Dispersion',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     },

                 ] + \
                 TF_cauchyb.get_properties() + \
                 TF_index.get_properties() + \
                 TC_Kr.get_properties() + \
                 TC_Kt.get_properties() + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def get_paramset(self, material):
        roughglass_params = ParamSet()

        roughglass_params.add_bool('dispersion', self.dispersion)
        roughglass_params.update(TF_cauchyb.get_paramset(self))
        roughglass_params.update(TF_index.get_paramset(self))
        roughglass_params.update(TC_Kr.get_paramset(self))
        roughglass_params.update(TC_Kt.get_paramset(self))
        roughglass_params.update(TF_uroughness.get_paramset(self))
        roughglass_params.update(TF_vroughness.get_paramset(self))

        return roughglass_params

    def load_paramset(self, ps):
        TF_cauchyb.load_paramset(self, ps)
        TF_index.load_paramset(self, ps)
        TC_Kr.load_paramset(self, ps)
        TC_Kt.load_paramset(self, ps)
        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)

        psi_accept = {
            'dispersion': 'bool',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])


@LuxRenderAddon.addon_register_class
class luxrender_mat_glossy(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   ['multibounce', 'separable']
               ] + \
               TC_Kd.controls + \
               TF_sigma.controls + \
               TF_d.controls + \
               TC_Ka.controls + \
               [
                   'useior',
                   'draw_ior_menu',
               ] + \
               TF_index.controls + \
               TC_Ks.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls

    visibility = dict_merge(
        {
            'draw_ior_menu': {'useior': True}
        },
        TF_d.visibility,
        TF_index.visibility,
        TC_Ka.visibility,
        TC_Kd.visibility,
        TC_Ks.visibility,
        TF_uroughness.visibility,
        TF_uexponent.visibility,
        TF_vroughness.visibility,
        TF_vexponent.visibility,
        {
            'alpha_source': {'transparent': True}
        },
        TF_alpha.visibility,
        TF_sigma.visibility
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})

    visibility = texture_append_visibility(visibility, TC_Ks, {'useior': False})
    visibility = texture_append_visibility(visibility, TF_index, {'useior': True})
    visibility = texture_append_visibility(visibility, TF_alpha, {'transparent': True, 'alpha_source': 'separate'})
    visibility = texture_append_visibility(visibility, TF_sigma, {'separable': True})

    properties = [
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'multibounce',
                         'name': 'Multibounce',
                         'description': 'Enable surface layer multibounce',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'separable',
                         'name': 'Separable',
                         'description': 'Use separable coating/base model',
                         'default': True,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'useior',
                         'name': 'Use IOR',
                         'description': 'Use IOR/Reflective index input',
                         'default': False,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_d.get_properties() + \
                 TF_index.get_properties() + \
                 TC_Ka.get_properties() + \
                 TC_Kd.get_properties() + \
                 TC_Ks.get_properties() + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties() + \
                 TF_alpha.get_properties() + \
                 TF_sigma.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def get_paramset(self, material):
        glossy_params = ParamSet()

        glossy_params.add_bool('multibounce', self.multibounce)
        glossy_params.add_bool('separable', self.separable)

        if self.d_floatvalue > 0:
            glossy_params.update(TF_d.get_paramset(self))
            glossy_params.update(TC_Ka.get_paramset(self))

        glossy_params.update(TC_Kd.get_paramset(self))

        if self.useior:
            glossy_params.update(TF_index.get_paramset(self))
            glossy_params.add_color('Ks', (1.0, 1.0, 1.0))
        else:
            glossy_params.update(TC_Ks.get_paramset(self))
            glossy_params.add_float('index', 0.0)

        glossy_params.update(TF_uroughness.get_paramset(self))
        glossy_params.update(TF_vroughness.get_paramset(self))

        if self.separable:
            glossy_params.update(TF_sigma.get_paramset(self))

        return glossy_params

    def load_paramset(self, ps):
        psi_accept = {
            'multibounce': 'bool',
            'separable': 'separable'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TF_d.load_paramset(self, ps)
        TF_index.load_paramset(self, ps)
        TC_Ka.load_paramset(self, ps)
        TC_Kd.load_paramset(self, ps)
        TC_Ks.load_paramset(self, ps)
        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)
        TF_alpha.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_matte(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
               ] + \
               TC_Kd.controls + \
               TF_sigma.controls

    visibility = dict_merge(
        TC_Kd.visibility,
        TF_sigma.visibility
    )

    properties = [
                 ] + \
                 TC_Kd.get_properties() + \
                 TF_sigma.get_properties()

    def get_paramset(self, material):
        matte_params = ParamSet()

        matte_params.update(TC_Kd.get_paramset(self))
        matte_params.update(TF_sigma.get_paramset(self))

        return matte_params

    def load_paramset(self, ps):
        TC_Kd.load_paramset(self, ps)
        TF_sigma.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_mattetranslucent(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'energyconserving'
               ] + \
               TC_Kr.controls + \
               TC_Kt.controls + \
               TF_sigma.controls

    visibility = dict_merge(
        TC_Kr.visibility,
        TC_Kt.visibility,
        TF_sigma.visibility
    )

    properties = [
                     {
                         'type': 'bool',
                         'attr': 'energyconserving',
                         'name': 'Energy conserving',
                         'description': 'Force energy conservation with regards to reflection and transmission',
                         'default': True
                     },
                 ] + \
                 TC_Kr.get_properties() + \
                 TC_Kt.get_properties() + \
                 TF_sigma.get_properties()

    def get_paramset(self, material):
        mattetranslucent_params = ParamSet()
        mattetranslucent_params.add_bool('energyconserving', self.energyconserving)
        mattetranslucent_params.update(TC_Kr.get_paramset(self))
        mattetranslucent_params.update(TC_Kt.get_paramset(self))
        mattetranslucent_params.update(TF_sigma.get_paramset(self))

        return mattetranslucent_params

    def load_paramset(self, ps):
        psi_accept = {
            'energyconserving': 'bool'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TC_Kr.load_paramset(self, ps)
        TC_Kt.load_paramset(self, ps)
        TF_sigma.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_glossytranslucent(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'multibounce',
               ] + \
               TC_Kt.controls + \
               TC_Kd.controls + \
               TF_d.controls + \
               TC_Ka.controls + \
               [
                   'useior',
                   'draw_ior_menu',
               ] + \
               TF_index.controls + \
               TC_Ks.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls + \
               [
                   'two_sided',
                   'backface_multibounce',
               ] + \
               TF_backface_d.controls + \
               TC_backface_Ka.controls + \
               [
                   'bf_useior'
               ] + \
               TF_backface_index.controls + \
               TC_backface_Ks.controls + \
               [
                   ['bf_anisotropic', 'bf_exponent'],
               ] + \
               TF_backface_uroughness.controls + \
               TF_backface_vroughness.controls + \
               TF_backface_uexponent.controls + \
               TF_backface_vexponent.controls

    visibility = dict_merge(
        TC_Kt.visibility,
        TC_Kd.visibility,
        TF_d.visibility,
        TC_Ka.visibility,
        TF_index.visibility,
        TC_Ks.visibility,
        TF_uroughness.visibility,
        TF_uexponent.visibility,
        TF_vroughness.visibility,
        TF_vexponent.visibility,

        TF_backface_d.visibility,
        TC_backface_Ka.visibility,
        TF_backface_index.visibility,
        TC_backface_Ks.visibility,
        TF_backface_uroughness.visibility,
        TF_backface_vroughness.visibility,
        TF_backface_uexponent.visibility,
        TF_backface_vexponent.visibility,
        {
            'draw_ior_menu': {'useior': True},
            'backface_multibounce': {'two_sided': True},
            'bf_useior': {'two_sided': True},
            'bf_anisotropic': {'two_sided': True},
            'bf_exponent': {'two_sided': True},
        }
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_backface_vroughness, {'bf_anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'bf_anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_backface_vexponent, {'bf_anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})

    visibility = texture_append_visibility(visibility, TF_backface_uroughness,
                                           {'two_sided': True, 'bf_exponent': False})
    visibility = texture_append_visibility(visibility, TF_backface_vroughness,
                                           {'two_sided': True, 'bf_exponent': False})
    visibility = texture_append_visibility(visibility, TF_backface_uexponent, {'two_sided': True, 'bf_exponent': True})
    visibility = texture_append_visibility(visibility, TF_backface_vexponent, {'two_sided': True, 'bf_exponent': True})

    visibility = texture_append_visibility(visibility, TC_Ks, {'useior': False})
    visibility = texture_append_visibility(visibility, TF_index, {'useior': True})
    visibility = texture_append_visibility(visibility, TC_backface_Ka, {'two_sided': True})
    visibility = texture_append_visibility(visibility, TF_backface_d, {'two_sided': True})
    visibility = texture_append_visibility(visibility, TF_backface_uroughness, {'two_sided': True})
    visibility = texture_append_visibility(visibility, TF_backface_vroughness, {'two_sided': True})
    visibility = texture_append_visibility(visibility, TC_backface_Ks, {'two_sided': True, 'bf_useior': False})
    visibility = texture_append_visibility(visibility, TF_backface_index, {'two_sided': True, 'bf_useior': True})

    properties = [
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'multibounce',
                         'name': 'Multibounce',
                         'description': 'Enable surface layer multibounce',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'two_sided',
                         'name': 'Two sided',
                         'description': 'Use different specular properties for back-face and front-face',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'backface_multibounce',
                         'name': 'Backface Multibounce',
                         'description': 'Enable back-surface layer multibounce',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'useior',
                         'name': 'Use IOR',
                         'description': 'Use IOR/Reflective index input',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'bf_useior',
                         'name': 'Backface use IOR',
                         'description': 'Use IOR/Reflective index input for backface',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'bf_anisotropic',
                         'name': 'Backface anisotropic roughness',
                         'description': 'Enable anisotropic roughness for backface',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'bf_exponent',
                         'name': 'Backface exponent',
                         'description': 'Display backface roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     }
                 ] + \
                 TC_Kt.get_properties() + \
                 TC_Kd.get_properties() + \
                 TF_d.get_properties() + \
                 TC_Ka.get_properties() + \
                 TF_index.get_properties() + \
                 TC_Ks.get_properties() + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties() + \
                 TF_backface_d.get_properties() + \
                 TC_backface_Ka.get_properties() + \
                 TF_backface_index.get_properties() + \
                 TC_backface_Ks.get_properties() + \
                 TF_backface_uroughness.get_properties() + \
                 TF_backface_vroughness.get_properties() + \
                 TF_backface_uexponent.get_properties() + \
                 TF_backface_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

        if prop['attr'].startswith('bf_uexponent'):
            prop['update'] = gen_CB_update_backface_roughness('u')

        if prop['attr'].startswith('bf_vexponent'):
            prop['update'] = gen_CB_update_backface_roughness('v')

        if prop['attr'].startswith('bf_uroughness'):
            prop['update'] = gen_CB_update_backface_exponent('u')

        if prop['attr'].startswith('bf_vroughness'):
            prop['update'] = gen_CB_update_backface_exponent('v')

    def get_paramset(self, material):
        glossytranslucent_params = ParamSet()

        if self.d_floatvalue > 0:
            glossytranslucent_params.update(TF_d.get_paramset(self))
            glossytranslucent_params.update(TC_Ka.get_paramset(self))

        glossytranslucent_params.add_bool('onesided', not self.two_sided)
        glossytranslucent_params.add_bool('multibounce', self.multibounce)

        glossytranslucent_params.update(TC_Kt.get_paramset(self))
        glossytranslucent_params.update(TC_Kd.get_paramset(self))

        if self.useior:
            glossytranslucent_params.update(TF_index.get_paramset(self))
            glossytranslucent_params.add_color('Ks', (1.0, 1.0, 1.0))
        else:
            glossytranslucent_params.update(TC_Ks.get_paramset(self))
            glossytranslucent_params.add_float('index', 0.0)

        glossytranslucent_params.update(TF_uroughness.get_paramset(self))
        glossytranslucent_params.update(TF_vroughness.get_paramset(self))

        if self.two_sided:
            glossytranslucent_params.add_bool('backface_multibounce', self.backface_multibounce)

            if self.bf_d_floatvalue > 0:
                glossytranslucent_params.update(TF_backface_d.get_paramset(self))
                glossytranslucent_params.update(TC_backface_Ka.get_paramset(self))

            if self.bf_useior:
                glossytranslucent_params.update(TF_backface_index.get_paramset(self))
                glossytranslucent_params.add_color('backface_Ks', (1.0, 1.0, 1.0))
            else:
                glossytranslucent_params.update(TC_backface_Ks.get_paramset(self))
                glossytranslucent_params.add_float('backface_index', 0.0)

            glossytranslucent_params.update(TF_backface_uroughness.get_paramset(self))
            glossytranslucent_params.update(TF_backface_vroughness.get_paramset(self))

        return glossytranslucent_params

    def load_paramset(self, ps):
        psi_accept = {
            'multibounce': 'bool',
            'backface_multibounce': 'bool',
            'onesided': 'bool'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TC_Kt.load_paramset(self, ps)
        TC_Kd.load_paramset(self, ps)
        TF_d.load_paramset(self, ps)
        TC_Ka.load_paramset(self, ps)
        TF_index.load_paramset(self, ps)
        TC_Ks.load_paramset(self, ps)
        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)
        TF_backface_d.load_paramset(self, ps)
        TC_backface_Ka.load_paramset(self, ps)
        TF_backface_index.load_paramset(self, ps)
        TC_backface_Ks.load_paramset(self, ps)
        TF_backface_uroughness.load_paramset(self, ps)
        TF_backface_vroughness.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_glossycoating(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'basematerial',
                   'multibounce',
               ] + \
               TF_d.controls + \
               TC_Ka.controls + \
               [
                   'useior',
                   'draw_ior_menu',
               ] + \
               TF_index.controls + \
               TC_Ks.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls

    visibility = dict_merge(
        {
            'draw_ior_menu': {'useior': True}
        },
        TF_d.visibility,
        TF_index.visibility,
        TC_Ka.visibility,
        TC_Ks.visibility,
        TF_uroughness.visibility,
        TF_uexponent.visibility,
        TF_vroughness.visibility,
        TF_vexponent.visibility
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})

    visibility = texture_append_visibility(visibility, TC_Ks, {'useior': False})
    visibility = texture_append_visibility(visibility, TF_index, {'useior': True})
    visibility = texture_append_visibility(visibility, TF_alpha, {'transparent': True, 'alpha_source': 'separate'})

    properties = [
                 ] + \
                 MaterialParameter('basematerial', 'Base Material', 'luxrender_mat_glossycoating') + \
                 [
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'multibounce',
                         'name': 'Multibounce',
                         'description': 'Enable surface layer multibounce',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'useior',
                         'name': 'Use IOR',
                         'description': 'Use IOR/Reflective index input',
                         'default': False,
                         'save_in_preset': True
                     },
                 ] + \
                 TF_d.get_properties() + \
                 TF_index.get_properties() + \
                 TC_Ka.get_properties() + \
                 TC_Ks.get_properties() + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def get_paramset(self, material):
        glossycoating_params = ParamSet()

        glossycoating_params.add_bool('multibounce', self.multibounce)

        if self.d_floatvalue > 0:
            glossycoating_params.update(TF_d.get_paramset(self))
            glossycoating_params.update(TC_Ka.get_paramset(self))

        if self.useior:
            glossycoating_params.update(TF_index.get_paramset(self))
            glossycoating_params.add_color('Ks', (1.0, 1.0, 1.0))
        else:
            glossycoating_params.update(TC_Ks.get_paramset(self))
            glossycoating_params.add_float('index', 0.0)

        glossycoating_params.update(TF_uroughness.get_paramset(self))
        glossycoating_params.update(TF_vroughness.get_paramset(self))
        glossycoating_params.add_string('basematerial', self.basematerial_material)

        return glossycoating_params

    def load_paramset(self, ps):
        psi_accept = {
            'multibounce': 'bool',
            'basematerial': 'string'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TF_d.load_paramset(self, ps)
        TF_index.load_paramset(self, ps)
        TC_Ka.load_paramset(self, ps)
        TC_Ks.load_paramset(self, ps)
        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_metal(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'name',
                   'filename',
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls

    visibility = dict_merge({
                                'filename': {'name': 'nk'}
                            },
                            TF_uroughness.visibility,
                            TF_uexponent.visibility,
                            TF_vroughness.visibility,
                            TF_vexponent.visibility,
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})

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
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     }
                 ] + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def get_paramset(self, material):
        metal_params = ParamSet()
        metal_params.update(TF_uroughness.get_paramset(self))
        metal_params.update(TF_vroughness.get_paramset(self))

        if self.name == 'nk':  # use an NK data file
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(LuxManager.CurrentScene, material, self.filename, metal_params, 'filename')
        else:  # use a preset name
            metal_params.add_string('name', self.name)

        return metal_params

    def load_paramset(self, ps):
        psi_accept = {
            'name': 'string',
            'filename': 'string'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_metal2(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'metaltype',
                   'filename',
                   'preset',
               ] + \
               TFR_fresnel.controls + \
               TC_Kr.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls

    visibility = dict_merge(
        TFR_fresnel.visibility,
        TC_Kr.visibility,
        TF_uroughness.visibility,
        TF_uexponent.visibility,
        TF_vroughness.visibility,
        TF_vexponent.visibility,
        {
            'filename': {'metaltype': 'nk'},
            'preset': {'metaltype': 'preset'},
        }
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TC_Kr, {'metaltype': 'fresnelcolor'})
    visibility = texture_append_visibility(visibility, TFR_fresnel, {'metaltype': 'fresneltex'})

    properties = [
                     {
                         'type': 'enum',
                         'attr': 'metaltype',
                         'name': 'Metal type',
                         'description': 'Metal type to use',
                         'items': [
                             ('fresnelcolor', 'Custom color', 'Use a custom reflection color'),
                             ('preset', 'Preset', 'Use preset metal'),
                             ('nk', 'External nk file', 'Use external nk file'),
                             ('fresneltex', 'Fresnel texture', 'Use generic fresnel input'),
                         ],
                         'default': 'preset',
                         'save_in_preset': True
                     },
                     {
                         'type': 'enum',
                         'attr': 'preset',
                         'name': 'Preset',
                         'description': 'Metal type to use',
                         'items': [
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
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     }
                 ] + \
                 TFR_fresnel.get_properties() + \
                 TC_Kr.get_properties() + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def export(self, lux_context, material):
        if self.metaltype == 'fresnelcolor':
            fresnelcolor_params = ParamSet()

            if LuxManager.GetActive() is not None:
                fresnelcolor_params.update(
                    add_texture_parameter(LuxManager.GetActive().lux_context, 'Kr', 'color', self)
                )

            ExportedTextures.texture(
                lux_context,
                '%s_nk' % material.name,
                'fresnel',
                'fresnelcolor',
                fresnelcolor_params
            )
            ExportedTextures.export_new(lux_context)

        if self.metaltype == 'preset':
            fresnelname_params = ParamSet()
            fresnelname_params.add_string('name', self.preset)

            ExportedTextures.texture(
                lux_context,
                '%s_nk' % material.name,
                'fresnel',
                'preset',
                fresnelname_params
            )
            ExportedTextures.export_new(lux_context)

        if self.metaltype == 'nk':
            fresnelname_params = ParamSet()
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(LuxManager.CurrentScene, material, self.filename, fresnelname_params, 'filename')

            ExportedTextures.texture(
                lux_context,
                '%s_nk' % material.name,
                'fresnel',
                'fresnelname',
                fresnelname_params
            )

            ExportedTextures.export_new(lux_context)

    def get_paramset(self, material):
        metal2_params = ParamSet()
        metal2_params.update(TF_uroughness.get_paramset(self))
        metal2_params.update(TF_vroughness.get_paramset(self))

        if self.metaltype == 'fresneltex':
            metal2_params.update(TFR_fresnel.get_paramset(self))
        else:
            metal2_params.add_texture('fresnel', '%s_nk' % material.name)

        return metal2_params

        TFR_fresnel.load_paramset(self, ps)
        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_scatter(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
               ] + \
               TC_Kd.controls + \
               [
                   'g'
               ]

    visibility = dict_merge(
        TC_Kd.visibility
    )

    properties = [
                     {
                         'type': 'float_vector',
                         'attr': 'g',
                         'name': 'Asymmetry',
                         'description': 'Scattering asymmetry RGB. -1 means backscatter, 0 is isotropic, 1 is \
                         forwards scattering',
                         'default': (0.0, 0.0, 0.0),
                         'min': -1.0,
                         'soft_min': -1.0,
                         'max': 1.0,
                         'soft_max': 1.0,
                         'precision': 4,
                         'save_in_preset': True
                     },
                 ] + \
                 TC_Kd.get_properties()

    def get_paramset(self, material):
        scatter_params = ParamSet()
        scatter_params.update(TC_Kd.get_paramset(self))
        scatter_params.add_color('g', self.g)

        return scatter_params

    def load_paramset(self, ps):
        psi_accept = {
            'g': 'color'
        }

        TC_Kd.load_paramset(self, ps)
        TF_g.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_shinymetal(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
               ] + \
               TF_film.controls + \
               [
                   'draw_ior_menu'
               ] + \
               TF_filmindex.controls + \
               TC_Kr.controls + \
               TC_Ks.controls + \
               [
                   ['anisotropic', 'use_exponent'],
               ] + \
               TF_uroughness.controls + \
               TF_uexponent.controls + \
               TF_vroughness.controls + \
               TF_vexponent.controls

    visibility = dict_merge(
        TF_film.visibility,
        TF_filmindex.visibility,
        TC_Kr.visibility,
        TC_Ks.visibility,
        TF_uroughness.visibility,
        TF_uexponent.visibility,
        TF_vroughness.visibility,
        TF_vexponent.visibility
    )

    enabled = {}
    enabled = texture_append_visibility(enabled, TF_vroughness, {'anisotropic': True})
    enabled = texture_append_visibility(enabled, TF_vexponent, {'anisotropic': True})

    visibility = texture_append_visibility(visibility, TF_uroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_vroughness, {'use_exponent': False})
    visibility = texture_append_visibility(visibility, TF_uexponent, {'use_exponent': True})
    visibility = texture_append_visibility(visibility, TF_vexponent, {'use_exponent': True})

    properties = [
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                     {
                         'type': 'bool',
                         'attr': 'anisotropic',
                         'name': 'Anisotropic roughness',
                         'description': 'Enable anisotropic roughness',
                         'default': False,
                         'save_in_preset': True
                     },
                     {
                         'type': 'bool',
                         'attr': 'use_exponent',
                         'name': 'Use exponent',
                         'description': 'Display roughness as a specular exponent',
                         'default': False,
                         'save_in_preset': True
                     }
                 ] + \
                 TF_film.get_properties() + \
                 TF_filmindex.get_properties() + \
                 TC_Kr.get_properties() + \
                 TC_Ks.get_properties() + \
                 TF_uroughness.get_properties() + \
                 TF_uexponent.get_properties() + \
                 TF_vroughness.get_properties() + \
                 TF_vexponent.get_properties()

    for prop in properties:
        if prop['attr'].startswith('uexponent'):
            prop['update'] = gen_CB_update_roughness('u')

        if prop['attr'].startswith('vexponent'):
            prop['update'] = gen_CB_update_roughness('v')

        if prop['attr'].startswith('uroughness'):
            prop['update'] = gen_CB_update_exponent('u')

        if prop['attr'].startswith('vroughness'):
            prop['update'] = gen_CB_update_exponent('v')

    def get_paramset(self, material):
        shinymetal_params = ParamSet()
        shinymetal_params.update(TF_film.get_paramset(self))
        shinymetal_params.update(TF_filmindex.get_paramset(self))
        shinymetal_params.update(TC_Kr.get_paramset(self))
        shinymetal_params.update(TC_Ks.get_paramset(self))
        shinymetal_params.update(TF_uroughness.get_paramset(self))
        shinymetal_params.update(TF_vroughness.get_paramset(self))

        return shinymetal_params

    def load_paramset(self, ps):
        TF_film.load_paramset(self, ps)
        TF_filmindex.load_paramset(self, ps)
        TC_Kr.load_paramset(self, ps)
        TC_Ks.load_paramset(self, ps)
        TF_uroughness.load_paramset(self, ps)
        TF_vroughness.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_mirror(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
               ] + \
               TF_film.controls + \
               [
                   'draw_ior_menu'
               ] + \
               TF_filmindex.controls + \
               TC_Kr.controls

    visibility = dict_merge(
        TF_film.visibility,
        TF_filmindex.visibility,
        TC_Kr.visibility
    )

    properties = [
                     {
                         'type': 'ef_callback',
                         'attr': 'draw_ior_menu',
                         'method': 'draw_ior_menu',
                     },
                 ] + \
                 TF_film.get_properties() + \
                 TF_filmindex.get_properties() + \
                 TC_Kr.get_properties()

    def get_paramset(self, material):
        mirror_params = ParamSet()
        mirror_params.update(TF_film.get_paramset(self))
        mirror_params.update(TF_filmindex.get_paramset(self))
        mirror_params.update(TC_Kr.get_paramset(self))

        return mirror_params

    def load_paramset(self, ps):
        TF_film.load_paramset(self, ps)
        TF_filmindex.load_paramset(self, ps)
        TC_Kr.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_mix(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'namedmaterial1',
                   'namedmaterial2',
               ] + \
               TF_amount.controls

    visibility = TF_amount.visibility

    properties = [
                 ] + \
                 TF_amount.get_properties() + \
                 MaterialParameter('namedmaterial1', 'Material 1', 'luxrender_mat_mix') + \
                 MaterialParameter('namedmaterial2', 'Material 2', 'luxrender_mat_mix')

    def get_paramset(self, material):
        mix_params = ParamSet()
        mix_params.add_string('namedmaterial1', self.namedmaterial1_material)
        mix_params.add_string('namedmaterial2', self.namedmaterial2_material)
        mix_params.update(TF_amount.get_paramset(self))

        return mix_params

    def load_paramset(self, ps):
        psi_accept = {
            'namedmaterial1': 'string',
            'namedmaterial2': 'string'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, '%s_material' % psi['name'], shorten_name(psi['value']))

        TF_amount.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_layered(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'namedmaterial1',
                   'namedmaterial2',
                   'namedmaterial3',
                   'namedmaterial4',
               ] + \
               TF_OP1.controls + \
               TF_OP2.controls + \
               TF_OP3.controls + \
               TF_OP4.controls

    visibility = dict_merge(
        TF_OP1.visibility,
        TF_OP2.visibility,
        TF_OP3.visibility,
        TF_OP4.visibility
    )

    properties = [
                 ] + \
                 MaterialParameter('namedmaterial1', 'Material 1', 'luxrender_mat_layered') + \
                 MaterialParameter('namedmaterial2', 'Material 2', 'luxrender_mat_layered') + \
                 MaterialParameter('namedmaterial3', 'Material 3', 'luxrender_mat_layered') + \
                 MaterialParameter('namedmaterial4', 'Material 4', 'luxrender_mat_layered') + \
                 TF_OP1.properties + \
                 TF_OP2.properties + \
                 TF_OP3.properties + \
                 TF_OP4.properties

    def get_paramset(self, material):
        layered_params = ParamSet()
        layered_params.add_string('namedmaterial1', self.namedmaterial1_material)
        layered_params.add_string('namedmaterial2', self.namedmaterial2_material)
        layered_params.add_string('namedmaterial3', self.namedmaterial3_material)
        layered_params.add_string('namedmaterial4', self.namedmaterial4_material)
        layered_params.update(TF_OP1.get_paramset(self))
        layered_params.update(TF_OP2.get_paramset(self))
        layered_params.update(TF_OP3.get_paramset(self))
        layered_params.update(TF_OP4.get_paramset(self))

        return layered_params

    def load_paramset(self, ps):
        psi_accept = {
            'namedmaterial1': 'string',
            'namedmaterial2': 'string',
            'namedmaterial3': 'string',
            'namedmaterial4': 'string'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, '%s_material' % psi['name'], shorten_name(psi['value']))

        TF_OP1.load_paramset(self, ps)
        TF_OP2.load_paramset(self, ps)
        TF_OP3.load_paramset(self, ps)
        TF_OP4.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_null(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = []
    visibility = {}
    properties = []

    def get_paramset(self, material):
        return ParamSet()

    def load_paramset(self, ps):
        pass


@LuxRenderAddon.addon_register_class
class luxrender_mat_velvet(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = TC_Kd.controls + [
        'thickness',
        'advanced',
        'p1', 'p2', 'p3',
    ]

    visibility = dict_merge({
                                'p1': {'advanced': True},
                                'p2': {'advanced': True},
                                'p3': {'advanced': True},
                            }, TC_Kd.visibility)

    properties = TC_Kd.get_properties() + [
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'thickness',
            'name': 'Thickness',
            'default': 0.1,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'p1',
            'name': 'p1',
            'default': -2.0,
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'p2',
            'name': 'p2',
            'default': 10.0,
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'p3',
            'name': 'p3',
            'default': 2.0,
            'min': -100.0,
            'soft_min': -100.0,
            'max': 100.0,
            'soft_max': 100.0,
            'save_in_preset': True
        },
    ]

    def get_paramset(self, material):
        velvet_params = ParamSet()
        velvet_params.update(TC_Kd.get_paramset(self))
        velvet_params.add_float('thickness', self.thickness)

        if self.advanced:
            velvet_params.add_float('p1', self.p1)
            velvet_params.add_float('p2', self.p2)
            velvet_params.add_float('p3', self.p3)

        return velvet_params

    def load_paramset(self, ps):
        psi_accept = {
            'thickness': 'float',
            'p1': 'float',
            'p2': 'float',
            'p3': 'float',
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TC_Kd.load_paramset(self, ps)


@LuxRenderAddon.addon_register_class
class luxrender_mat_cloth(declarative_property_group):
    ef_attach_to = ['luxrender_material']
    alert = {}

    controls = [
                   'presetname'
               ] + \
               TC_warp_Kd.controls + \
               TC_warp_Ks.controls + \
               TC_weft_Kd.controls + \
               TC_weft_Ks.controls + \
               [
                   ['repeat_u', 'repeat_v']
               ]

    visibility = dict_merge(
        TC_warp_Kd.visibility,
        TC_warp_Ks.visibility,
        TC_weft_Kd.visibility,
        TC_weft_Ks.visibility
    )

    properties = [
                     {
                         'type': 'enum',
                         'attr': 'presetname',
                         'name': 'Fabric Type',
                         'description': 'Fabric type to use',
                         'items': [
                             ('denim', 'Denim', 'Denim'),
                             ('silk_charmeuse', 'Silk Charmeuse', 'Silk charmeuse'),
                             ('cotton_twill', 'Cotton Twill', 'Cotton twill'),
                             ('wool_gabardine', 'Wool Gabardine', 'Wool Gabardine'),
                             ('polyester_lining_cloth', 'Polyester Lining Cloth', 'Polyester lining cloth'),
                             ('silk_shantung', 'Silk Shantung', 'Silk shantung'),
                         ],
                         'default': 'denim',
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'repeat_u',
                         'name': 'Repeat U',
                         'default': 100.0,
                         'min': 1.0,
                         'soft_min': 1.0,
                         'max': 1000.0,
                         'soft_max': 1000.0,
                         'save_in_preset': True,
                     },
                     {
                         'type': 'float',
                         'attr': 'repeat_v',
                         'name': 'Repeat V',
                         'default': 100.0,
                         'min': 1.0,
                         'soft_min': 1.0,
                         'max': 1000.0,
                         'soft_max': 1000.0,
                         'save_in_preset': True,
                     },
                 ] + \
                 TC_warp_Kd.get_properties() + \
                 TC_warp_Ks.get_properties() + \
                 TC_weft_Kd.get_properties() + \
                 TC_weft_Ks.get_properties()

    def get_paramset(self, material):
        cloth_params = ParamSet()
        cloth_params.add_string('presetname', self.presetname)
        cloth_params.update(TC_warp_Kd.get_paramset(self))
        cloth_params.update(TC_warp_Ks.get_paramset(self))
        cloth_params.update(TC_weft_Kd.get_paramset(self))
        cloth_params.update(TC_weft_Ks.get_paramset(self))
        cloth_params.add_float('repeat_u', self.repeat_u)
        cloth_params.add_float('repeat_v', self.repeat_v)

        return cloth_params

    def load_paramset(self, ps):
        psi_accept = {
            'presetname': 'string',
            'repeat_u': 'float',
            'repeat_v': 'float'
        }

        psi_accept_keys = psi_accept.keys()

        for psi in ps:
            if psi['name'] in psi_accept_keys and psi['type'].lower() == psi_accept[psi['name']]:
                setattr(self, psi['name'], psi['value'])

        TC_warp_Kd.load_paramset(self, ps)
        TC_warp_Ks.load_paramset(self, ps)
        TC_weft_Kd.load_paramset(self, ps)
        TC_weft_Ks.load_paramset(self, ps)


def EmissionLightGroupParameter():
    return [
        {
            'attr': 'lightgroup',
            'type': 'string',
            'name': 'lightgroup',
            'description': 'lightgroup; leave blank to use default',
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': 'lightgroup_chooser',
            'src': lambda s, c: s.scene.luxrender_lightgroups,
            'src_attr': 'lightgroups',
            'trg': lambda s, c: c.luxrender_emission,
            'trg_attr': 'lightgroup',
            'name': 'Light Group'
        },
    ]


class EmissionColorTextureParameter(ColorTextureParameter):
    def texture_slot_set_attr(self):
        # Looks in a different location than other ColorTextureParameters
        return lambda s, c: c.luxrender_emission


TC_L = EmissionColorTextureParameter('L', 'Emission color', default=(1.0, 1.0, 1.0))


@LuxRenderAddon.addon_register_class
class luxrender_emission(declarative_property_group):
    """
    Storage class for LuxRender Material emission settings.
    """

    ef_attach_to = ['Material']
    alert = {}

    def set_viewport_emission(self, context):
        """
        This litte function monkeys with the blender mat's emit value to sort-of show the meshlight in the viewport
        """
        if self.use_emission:
            context.material.emit = self.gain
        else:
            context.material.emit = 0

    controls = [
                   'importance',
                   'lightgroup_chooser',
                   'iesname',
               ] + \
               TC_L.controls + \
               [
                   'nsamples',
                   'gain',
                   'power',
                   'efficacy',
               ]

    visibility = {
        'importance': {'use_emission': True},
        'lightgroup_chooser': {'use_emission': True},
        'iesname': {'use_emission': True},
        'nsamples': {'use_emission': True},
        'L_colorlabel': {'use_emission': True},
        'L_color': {'use_emission': True},
        'L_usecolortexture': {'use_emission': True},
        'L_colortexture': {'use_emission': True, 'L_usecolortexture': True},
        'L_multiplycolor': {'use_emission': True, 'L_usecolortexture': True},
        'gain': {'use_emission': True},
        'power': {'use_emission': True},
        'efficacy': {'use_emission': True},
    }

    properties = [
                     {  # drawn in header
                        'type': 'bool',
                        'attr': 'use_emission',
                        'name': 'Use Emission',
                        'default': False,
                        'update': set_viewport_emission,
                        'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'importance',
                         'name': 'Importance',
                         'description': 'Light source importance',
                         'default': 1.0,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 1e3,
                         'soft_max': 1e3,
                     },
                     {
                         'type': 'string',
                         'attr': 'lightgroup',
                         'name': 'Light Group',
                         'default': 'default',
                         'save_in_preset': True
                     },
                     {
                         'type': 'string',
                         'subtype': 'FILE_PATH',
                         'attr': 'iesname',
                         'name': 'IES Data',
                         'description': 'Use IES data for this light\'s distribution'
                     },
                     {
                         'type': 'int',
                         'attr': 'nsamples',
                         'name': 'Shadow ray samples',
                         'description': 'The suggested number of shadow samples',
                         'default': 1,
                         'min': 1,
                         'soft_min': 1,
                         'max': 100,
                         'soft_max': 100,
                     },
                     {
                         'type': 'float',
                         'attr': 'gain',
                         'name': 'Gain',
                         'default': 1.0,
                         'update': set_viewport_emission,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 1e8,
                         'soft_max': 1e8,
                         'precision': 6,
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'power',
                         'name': 'Power',
                         'default': 100.0,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 1e5,
                         'soft_max': 1e5,
                         'save_in_preset': True
                     },
                     {
                         'type': 'float',
                         'attr': 'efficacy',
                         'name': 'Efficacy',
                         'default': 17.0,
                         'min': 0.0,
                         'soft_min': 0.0,
                         'max': 1e4,
                         'soft_max': 1e4,
                         'save_in_preset': True
                     }

                 ] + \
                 TC_L.get_properties() + \
                 EmissionLightGroupParameter()

    def api_output(self, obj):
        lg_gain = 1.0

        if self.lightgroup in LuxManager.CurrentScene.luxrender_lightgroups.lightgroups:
            lg_gain = LuxManager.CurrentScene.luxrender_lightgroups.lightgroups[self.lightgroup].gain

        arealightsource_params = ParamSet() \
            .add_float('importance', self.importance) \
            .add_float('gain', self.gain * lg_gain) \
            .add_float('power', self.power) \
            .add_float('efficacy', self.efficacy) \
            .add_integer('nsamples', self.nsamples)
        arealightsource_params.update(TC_L.get_paramset(self))

        if self.iesname:
            # This function resolves relative paths (even in linked library blends)
            # and optionally encodes/embeds the data if the setting is enabled
            process_filepath_data(LuxManager.CurrentScene, obj, self.iesname, arealightsource_params, 'iesname')

        return 'area', arealightsource_params
