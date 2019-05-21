import bpy, gpu, os, base64, struct, zlib, re
from json import loads, dumps
from pprint import pprint
from random import random
from .shader_lib_extractor import *
from . import mat_binternal
from . import mat_nodes
from . import mat_code_generator

def mat_to_json(mat, scn, used_data):
    layers = used_data['material_layers'][mat.name]
    if scn.render.engine != 'CYCLES' and not mat_nodes.is_blender_pbr_material(mat):
        # Blender internal or Blender game

        # We'll disable "this layer only" lights,
        # and restore them all unconditionally
        lamps = []
        try:
            # TODO: optimize making a list of lamps per layer?
            # TODO: update scene only when necessary?
            # export materials ordered by update requirements?
            for ob in scn.objects:
                if ob.type == 'LAMP':
                    lamp = ob.data
                    if lamp.use_own_layer and \
                            not any(a and b for a,b in zip(ob.layers, layers)):
                        lamps.append([lamp, lamp.use_diffuse, lamp.use_specular])
                        lamp.use_diffuse = lamp.use_specular = False
            scn.update()
            r = mat_binternal.mat_to_json_try(mat, scn)
        finally:
            for lamp, use_diffuse, use_specular in lamps:
                lamp.use_diffuse = use_diffuse
                lamp.use_specular = use_specular
        r['ramps'] = {}
        return r
    else:
        # Blender Cycles or PBR branch

        # NodeTreeShaderGenerator uses platform-agnostic data
        # so we convert the tree and the lamps
        tree = mat_nodes.export_nodes_of_material(mat)
        ramps = tree['ramps']
        lamps = []
        for ob in scn.objects:
            if ob.type == 'LAMP' and ob.data and ob.data.type not in ['AREA', 'SPOT']:
                use_shadow = False
                shadow_buffer_type = ''
                if ob.data.type != 'HEMI':
                    use_shadow = ob.data.use_shadow
                    shadow_buffer_type = ob.data.ge_shadow_buffer_type
                lamps.append(dict(
                    name=ob.name,
                    lamp_type=ob.data.type,
                    use_diffuse=ob.data.use_diffuse,
                    use_specular=ob.data.use_specular,
                    use_shadow=use_shadow,
                    shadow_buffer_type=shadow_buffer_type,
                ))

        gen = mat_code_generator.NodeTreeShaderGenerator(tree, lamps)

        code = gen.get_code()
        uniforms = gen.get_uniforms()
        varyings = gen.get_varyings()
        # pprint(uniforms)
        material_type = 'BLENDER_CYCLES_PBR'
        return dict(
            type='MATERIAL',
            name=mat.name,
            material_type=material_type,
            fragment=code,
            uniforms=uniforms,
            varyings=varyings,
            ramps=ramps, # To be removed and converted to textures in exporter.py
        )


def world_material_to_json(scn):
    if mat_nodes.is_blender_pbr_material(scn.world) and scn.world.use_nodes:
        tree = mat_nodes.export_nodes_of_material(scn.world)
        tree['is_background'] = True
        ramps = tree['ramps']
        gen = mat_code_generator.NodeTreeShaderGenerator(tree, [])

        code = gen.get_code()
        uniforms = gen.get_uniforms()
        varyings = gen.get_varyings()
        # pprint(uniforms)
        material_type = 'BLENDER_CYCLES_PBR'
        return dict(
            type='MATERIAL',
            name=scn.name+'_world_background',
            material_type=material_type,
            fragment=code,
            uniforms=uniforms,
            varyings=varyings,
            ramps=ramps, # To be removed and converted to textures in exporter.py
            fixed_z=1,
        )
    return None

def has_node(tree, type):
    for node in tree.nodes:
        if node.type == type:
            return True
        elif node.type == '':
            if has_node(node.node_tree, type):
                return True
    return False

def get_pass_of_material(mat, scn):
    pass_ = 0
    if not mat_nodes.is_blender_pbr_material(mat):
        # Blender internal or Blender game
        if mat.use_transparency and \
            mat.transparency_method == 'RAYTRACE':
                pass_ = 2
        elif mat.use_transparency and \
                mat.game_settings.alpha_blend != 'CLIP':
            pass_ = 1
    else:
        # PBR branch
        if mat.use_transparency and \
            mat.game_settings.alpha_blend != 'CLIP':
                pass_ = 1
        if mat.use_nodes:
            if has_node(mat.node_tree, 'BSDF_TRANSPARENT'):
                pass_ = 1
            elif has_node(mat.node_tree, 'BSDF_REFRACTION'):
                pass_ = 2
    return pass_
