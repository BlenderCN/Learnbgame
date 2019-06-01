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

import os
import tempfile
import math

from ..export.cycles import cycles_material_to_dict
from ..outputs.file_api import FileExportContext
from ..outputs import MtsLog


class MaterialCounter:
    stack = []

    @classmethod
    def reset(cls):
        cls.stack = []

    def __init__(self, name):
        self.ident = name

    def __enter__(self):
        if self.ident in MaterialCounter.stack:
            raise Exception("Recursion in material assignment: %s -- %s" % (self.ident, ' -> '.join(MaterialCounter.stack)))

        MaterialCounter.stack.append(self.ident)

    def __exit__(self, exc_type, exc_val, exc_tb):
        MaterialCounter.stack.pop()


class ExportedMaterials:
    # Static class variables
    exported_materials_dict = {}

    @staticmethod
    def clear():
        MaterialCounter.reset()
        ExportedMaterials.exported_materials_dict = {}

    @staticmethod
    def addExportedMaterial(name, params):
        if name not in ExportedMaterials.exported_materials_dict:
            ExportedMaterials.exported_materials_dict.update({name: params})


class ExportedTextures:
    # Static class variables
    exported_textures_dict = {}
    exported_textures_not_found = set()
    warning_not_exported = True

    @staticmethod
    def clear():
        ExportedTextures.exported_textures_dict = {}
        ExportedTextures.exported_textures_not_found = set()
        ExportedTextures.warning_not_exported = True

    @staticmethod
    def addExportedTexture(name, params):
        if name not in ExportedTextures.exported_textures_dict:
            ExportedTextures.exported_textures_dict.update({name: params})

    @staticmethod
    def ensureWarningTexture(export_ctx, tex_id):
        if ExportedTextures.warning_not_exported:
            export_ctx.data_add({
                'type': 'checkerboard',
                'id': 'warning_bitmap_not_found',
                'color0': export_ctx.spectrum(0.0),
                'color1': export_ctx.spectrum([0.8, 0, 0.8]),
            })
            ExportedTextures.warning_not_exported = False

        ExportedTextures.exported_textures_not_found.add(tex_id)


def get_texture_id(texture):
    exported_textures = ExportedTextures.exported_textures_dict
    tex_name = 'Texture'

    if 'image' in texture:
        tex_name = texture['image'].name

        if tex_name not in exported_textures or exported_textures[tex_name] == texture:
            return tex_name

    for tex_id, tex_params in exported_textures.items():
        if tex_params == texture:
            return tex_id

    return '%s_%i' % (tex_name, len(ExportedTextures.exported_textures_dict))


def export_image(export_ctx, image):
    tex_image = ''

    if image.source in {'GENERATED', 'FILE'}:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        tex_image = temp_file.name

        if image.source == 'GENERATED':
            image.save_render(tex_image)

        if image.source == 'FILE':
            if image.packed_file:
                image.save_render(tex_image)

            else:
                tex_image = export_ctx.get_export_path(image.filepath, id_data=image)

    return tex_image


def export_textures(export_ctx, params):
    if not isinstance(params, (dict)):
        return

    for key, elem in params.items():
        if not isinstance(elem, (dict)):
            continue

        if 'type' in elem and elem['type'] in {'bitmap'}:
            tex_id = get_texture_id(elem)

            if tex_id not in ExportedTextures.exported_textures_dict:
                tex_params = elem.copy()
                tex_params['id'] = tex_id
                tex_image = tex_params.get('filename', '')

                if 'image' in tex_params:
                    image = tex_params.pop('image')
                    tex_image = export_image(export_ctx, image)

                if tex_image and os.path.exists(tex_image) and os.path.isfile(tex_image):
                    tex_params['filename'] = tex_image
                    export_ctx.data_add(tex_params)

                else:
                    ExportedTextures.ensureWarningTexture(export_ctx, tex_id)

                ExportedTextures.addExportedTexture(tex_id, elem)

            if tex_id in ExportedTextures.exported_textures_not_found:
                tex_id = 'warning_bitmap_not_found'

            params[key] = {'type': 'ref', 'id': tex_id}

        else:
            export_textures(export_ctx, elem)


def get_instance_materials(ob):
    obmats = []

    # Grab materials attached to object instances ...
    if hasattr(ob, 'material_slots'):
        for ms in ob.material_slots:
            obmats.append(ms.material)

    # ... and to the object's mesh data
    if hasattr(ob.data, 'materials'):
        for m in ob.data.materials:
            obmats.append(m)

    # per instance materials will take precedence
    # over the base mesh's material definition.
    return obmats


def internal_material_to_dict(export_ctx, blender_mat):
    ''' Converting one material from Blender to Mitsuba dict'''
    params = {}

    if (blender_mat.use_transparency and blender_mat.transparency_method != 'MASK'):

        if blender_mat.transparency_method == 'Z_TRANSPARENCY':
            params.update({
                'type': 'thindielectric',
                'intIOR': 1.0,
                'specularReflectance': export_ctx.spectrum(blender_mat.specular_color * blender_mat.specular_intensity),
                'specularTransmittance': export_ctx.spectrum(blender_mat.diffuse_color * blender_mat.diffuse_intensity),
            })

        else:
            # the RayTracing from blender
            specular_mul = (math.sqrt(blender_mat.specular_intensity * (1 - blender_mat.specular_alpha))) % 1
            diffuse_mul = (math.sqrt(blender_mat.diffuse_intensity * (1 - blender_mat.alpha))) % 1
            params.update({
                'type': 'dielectric',
                'intIOR': blender_mat.raytrace_transparency.ior,
                'specularReflectance': export_ctx.spectrum(blender_mat.specular_color * specular_mul),
                'specularTransmittance': export_ctx.spectrum(blender_mat.diffuse_color * diffuse_mul),
            })

    elif blender_mat.raytrace_mirror.use:
        # a mirror part is used

        if (blender_mat.diffuse_intensity < 0.01 and blender_mat.specular_intensity < 0.01):
            # simple conductor material
            params.update({
                'type': 'conductor',
                'material': 'none',
                'specularReflectance': export_ctx.spectrum(blender_mat.mirror_color),
            })

        else:
            spec_inte = blender_mat.specular_intensity
            #diff_inte = blender_mat.diffuse_intensity

            cond_params = {
                'type': 'conductor',
                'material': 'none',
                'specularReflectance': export_ctx.spectrum(blender_mat.mirror_color),
            }

            if blender_mat.specular_intensity > 0.01:
                mat1_params = OrderedDict([
                    ('type', 'blendbsdf'),
                    ('weight', (1.0 - spec_inte)),
                    ('bsdf1', cond_params),
                    ('bsdf2', {
                        'type': 'phong',
                        'specularReflectance': export_ctx.spectrum(blender_mat.specular_color * spec_inte),
                        'exponent': blender_mat.specular_hardness * 1.9,
                    }),
                ])

            else:
                mat1_params = cond_params

            params = OrderedDict([
                ('type', 'blendbsdf'),
                ('weight', (1.0 - blender_mat.raytrace_mirror.reflect_factor)),
                ('bsdf1', mat1_params),
                ('bsdf2', {
                    'type': 'diffuse',
                    'reflectance': export_ctx.spectrum(blender_mat.diffuse_color),
                }),
            ])

    elif blender_mat.specular_intensity == 0:
        params.update({
            'type': 'diffuse',
            'reflectance': export_ctx.spectrum(blender_mat.diffuse_color),
        })

    else:
        roughness = math.exp(-blender_mat.specular_hardness / 50)  # by eyeballing rule of Bartosz Styperek :/

        if roughness:
            params.update({
                'type': 'roughplastic',
                'alpha': roughness,
                'distribution': 'beckmann',
            })

        else:
            params.update({
                'type': 'plastic',
            })

        params.update({
            'diffuseReflectance': export_ctx.spectrum(blender_mat.diffuse_color * blender_mat.diffuse_intensity),
            'specularReflectance': export_ctx.spectrum(blender_mat.specular_color * blender_mat.specular_intensity),
        })

    # === Blender texture conversion
    for tex in blender_mat.texture_slots:
        if (tex and tex.use and tex.texture.type == 'IMAGE'):
            if params['type'] in {'diffuse', 'roughdiffuse'}:
                params['reflectance'] = {
                    'type': 'bitmap',
                    'image': tex.texture.image
                }

            elif params['type'] in {'plastic', 'roughplastic'}:
                if tex.use_map_color_diffuse:
                    params['diffuseReflectance'] = {
                        'type': 'bitmap',
                        'image': tex.texture.image
                    }

                elif tex.use_map_color_spec:
                    params['specularReflectance'] = {
                        'type': 'bitmap',
                        'image': tex.texture.image
                    }

    mat_params = {}

    if params:
        mat_params.update({
            'bsdf': params
        })

    if blender_mat.emit > 0 and params['type'] not in {'dielectric', 'thindielectric'}:
        mat_params.update({
            'emitter': {
                'type': 'area',
                'radiance': export_ctx.spectrum(blender_mat.diffuse_color * blender_mat.emit * 10),
            }
        })

    return mat_params


def blender_material_to_dict(export_ctx, blender_mat):
    ''' Converting one material from Blender / Cycles to Mitsuba'''
    if export_ctx is None:
        export_ctx = FileExportContext()

    mat_params = {}

    if blender_mat.use_nodes:
        try:
            output_node = blender_mat.node_tree.nodes["Material Output"]
            surface_node = output_node.inputs["Surface"].links[0].from_node
            mat_params = cycles_material_to_dict(export_ctx, surface_node)

        except Exception as err:
            MtsLog("Could not convert nodes!!", str(err))

    else:
        mat_params = internal_material_to_dict(export_ctx, blender_mat)

    return mat_params


def export_material(export_ctx, material):
    mat_params = {}

    if material is None:
        return mat_params

    ntree = material.mitsuba_nodes.get_node_tree()

    if ntree:
        name = "%s-mts_ntree" % ntree.name

    else:
        name = "%s-bl_mat" % material.name

    if name in ExportedMaterials.exported_materials_dict:
        return ExportedMaterials.exported_materials_dict[name]

    if ntree:
        mat_params = ntree.get_nodetree_dict(export_ctx, ntree)

    else:
        mat_params = blender_material_to_dict(export_ctx, material)

    export_textures(export_ctx, mat_params)

    if 'emitter' in mat_params:
        try:
            hide_emitters = export_ctx.scene_data['integrator']['hideEmitters']

        except:
            hide_emitters = False

        if hide_emitters:
            mat_params.update({'bsdf': {'type': 'null'}})

    if 'bsdf' in mat_params and mat_params['bsdf']['type'] != 'null':
        bsdf_params = OrderedDict([('id', '%s-bsdf' % name)])
        bsdf_params.update(mat_params['bsdf'])
        export_ctx.data_add(bsdf_params)
        mat_params.update({'bsdf': {'type': 'ref', 'id': '%s-bsdf' % name}})

    if 'interior' in mat_params:
        interior_params = {'id': '%s-medium' % name}
        interior_params.update(mat_params['interior'])

        if interior_params['type'] == 'ref':
            mat_params.update({'interior': interior_params})

        else:
            export_ctx.data_add(interior_params)
            mat_params.update({'interior': {'type': 'ref', 'id': '%s-medium' % name}})

    ExportedMaterials.addExportedMaterial(name, mat_params)

    return mat_params
