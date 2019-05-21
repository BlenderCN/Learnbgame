import os
import logging

import bpy
from bpy_extras.image_utils import load_image

from io_scene_data3d.data3d_utils import D3D

# Global Variables
C = bpy.context
D = bpy.data
O = bpy.ops

log = logging.getLogger('archilogic')


class Material:
    """
        Attributes:
            al_material_hash
            al_material
            bl_material
    """

    def __init__(self, key, al_material, import_metadata, working_dir, place_holder_images):
        """ Return a Material object. Import data3d materials and translate them to Blender Internal & Cycles materials
        Args:
            key ('str') - The hashed material key. Used for naming the material.
            al_material ('dict') - The data3d Material source.
            import_metadata ('str') - Import Archilogic json-material as blender-material metadata.
                                      Enum {'NONE', 'BASIC', 'ADVANCED' }
            working_dir ('str') - The source directory of the data3d file, used for recursive image search.
            place_holder_images ('bool') - Import place-holder images if source is not available.
        """
        self.al_material = al_material
        self.al_material_hash = key
        self.import_metadata = import_metadata
        self.bl_material = D.materials.new(key)
        #Fixme: This is a workaround for #9620
        self.add_lead_slash()

        # Create Blender Material
        create_blender_material(self.al_material, self.bl_material, working_dir, import_metadata, place_holder_images)

        # Create Cycles Material
        create_cycles_material(self.al_material, self.bl_material, working_dir, place_holder_images)

    def get_bake_nodes(self):
        add_lightmap = self.al_material[D3D.add_lightmap] if D3D.add_lightmap in self.al_material else True
        use_in_calc = self.al_material[D3D.use_in_calc] if D3D.use_in_calc in self.al_material else True
        hide_after_calc = self.al_material[D3D.hide_after_calc] if D3D.hide_after_calc in self.al_material else False
        emit_light_coef = self.al_material[D3D.coef_emit] if D3D.coef_emit in self.al_material else 0

        if not use_in_calc or hide_after_calc:
            bake_meta = {
                'type': 'NOBAKE',
                D3D.add_lightmap: False,
                D3D.use_in_calc: use_in_calc,
                D3D.hide_after_calc: hide_after_calc
            }
        elif emit_light_coef > 0:
            bake_meta = {
                'type': 'EMISSION',
                D3D.add_lightmap: False,
                D3D.use_in_calc: True,
                D3D.hide_after_calc: hide_after_calc
            }
        elif add_lightmap:
            bake_meta = {
                'type': 'BAKE',
                D3D.add_lightmap: True,
                D3D.use_in_calc: True,
                D3D.hide_after_calc: False
            }
        else:
            bake_meta = {
                'type': 'NOBAKE',
                D3D.add_lightmap: False,
                D3D.use_in_calc: use_in_calc,
                D3D.hide_after_calc: hide_after_calc
            }

        return bake_meta

    def add_lead_slash(self):
        tex_keys = [
            D3D.map_diff + D3D.map_suffix_hires, D3D.map_diff + D3D.map_suffix_source, D3D.map_diff + D3D.map_suffix_lores,
            D3D.map_spec + D3D.map_suffix_hires, D3D.map_spec + D3D.map_suffix_source, D3D.map_spec + D3D.map_suffix_lores,
            D3D.map_norm + D3D.map_suffix_hires, D3D.map_norm + D3D.map_suffix_source, D3D.map_norm + D3D.map_suffix_lores,
            D3D.map_alpha + D3D.map_suffix_hires, D3D.map_alpha + D3D.map_suffix_source, D3D.map_alpha + D3D.map_suffix_lores,
            D3D.map_light + D3D.map_suffix_hires, D3D.map_light + D3D.map_suffix_source, D3D.map_light + D3D.map_suffix_lores
        ]
        for key in self.al_material.keys():
            if key in tex_keys:
                path = self.al_material[key]
                if not path.startswith('/'):
                    self.al_material[key] = '/' + path

    def get_al_mat_node(self, key, fallback=None):
        if key in self.al_material:
            return self.al_material[key]
        else:
            return fallback


def create_blender_material(al_mat, bl_mat, working_dir, import_metadata, place_holder_images):
    """ Create the blender material
        Args:
            al_mat ('dict') - The data3d Material source.
            bl_mat ('bpy.types.Material') - The Blender Material datablock.
            working_dir ('str') - The source directory of the data3d file, used for recursive image search.
            import_metadata ('str') - Import Archilogic json-material as blender-material metadata.
                                      Enum {'NONE', 'BASIC', 'ADVANCED' }
            place_holder_images ('bool') - Import place-holder images if source is not available.
    """
    # Override default material settings
    bl_mat.diffuse_intensity = 1
    bl_mat.specular_intensity = 1

    # Import Archilogic Material Datablock (FIXME check PropertyGroup)
    if import_metadata == 'BASIC' or import_metadata == 'ADVANCED':
        bl_mat[D3D.bl_meta] = al_mat

    if D3D.col_diff in al_mat:
        bl_mat.diffuse_color = al_mat[D3D.col_diff]
    else:
        #Fixme: the documentation says 0.85 but visually this is equal
        bl_mat.diffuse_color = (1.0,)*3
    if D3D.col_spec in al_mat:
        bl_mat.specular_color = al_mat[D3D.col_spec]
    else:
        bl_mat.specular_color = (0.25,)*3
    if D3D.coef_spec in al_mat:
        bl_mat.specular_hardness = int(al_mat[D3D.coef_spec])
    else:
        bl_mat.specular_hardness = 1
    if D3D.coef_emit in al_mat:
        bl_mat.emit = float(al_mat[D3D.coef_emit])
    if D3D.opacity in al_mat:
        opacity = al_mat[D3D.opacity]
        if opacity < 1:
            bl_mat.use_transparency = True
            bl_mat.transparency_method = 'Z_TRANSPARENCY'
            bl_mat.alpha = opacity

    ref_maps = get_reference_maps(al_mat)
    for map_key in ref_maps:
        set_image_texture(bl_mat, ref_maps[map_key], map_key, working_dir, place_holder_images)

    if D3D.uv_scale in al_mat:
        scale = al_mat[D3D.uv_scale]
        for tex_slot in bl_mat.texture_slots:
            if tex_slot is not None:
                tex_slot.scale[0] = (1/scale[0] if scale[0] != 0 else 0)
                tex_slot.scale[1] = (1/scale[1] if scale[1] != 0 else 0)


def create_cycles_material(al_mat, bl_mat, working_dir, place_holder_images):
    """ Create the cycles material
        Args:
            al_mat ('dict') - The data3d Material source.
            bl_mat ('bpy.types.Material') - The Blender Material datablock.
            working_dir ('str') - The source directory of the data3d file, used for recursive image search.
            place_holder_images ('bool') - Import place-holder images if source is not available.
    """
    # This dict translates between node input names and d3d keys. (This prevents updates in the library.blend file)
    d3d_to_node = {
        D3D.map_diff: 'map-diffuse',
        D3D.map_spec: 'map-specular',
        D3D.map_norm: 'map-normal',
        D3D.map_alpha: 'map-alpha',
        D3D.map_light: 'map-light',
        D3D.col_diff: 'color-diffuse',
        D3D.col_spec: 'color-specular',
        D3D.coef_spec: 'specular-intensity',
        D3D.coef_emit: 'emission-intensity',
        D3D.opacity: 'opacity',
    }

    # Setup Cycles Material and remove all nodes.
    C.scene.render.engine = 'CYCLES'
    bl_mat.use_nodes = True
    node_tree = bl_mat.node_tree
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)

    # Material group node (The datablock is not yet assigned)
    node_group = node_tree.nodes.new('ShaderNodeGroup')
    node_group.location = (0, 0)

    # Distinguish between tree different Material types.
    # Adaptations to the nodes: node_library.blend file.
    # Basic Material (diffuse & glossy Shader) supports standard maps, fallback on neutral inputs.
    # Emission Material (emission & transparent shader) supports diffuse and alpha maps, diffuse color as emit color.
    # Transparent Material (transparent Shader) supports alpha maps and opacity additional to the basic material.

    opacity = al_mat[D3D.opacity] if D3D.opacity in al_mat else 1.0
    emission = al_mat[D3D.coef_emit] if D3D.coef_emit in al_mat else 0.0
    if emission > 0.0:
        node_group.node_tree = D.node_groups['archilogic-emission']

    elif D3D.map_alpha in al_mat or opacity < 1.0:
        node_group.node_tree = D.node_groups['archilogic-transparency']

    else:
        # Add the corresponding Material node group ('archilogic-basic')
        node_group.node_tree = D.node_groups['archilogic-basic']

    # Material Output Node
    output_node = node_tree.nodes.new('ShaderNodeOutputMaterial')
    output_node.location = (200, 0)
    # Link the group shader to the output_node
    node_tree.links.new(node_group.outputs['Shader'], output_node.inputs['Surface'])

    # Textures
    # Get the texture reference maps
    ref_maps = get_reference_maps(al_mat)

    # UV Map and UV Scale node
    uv_map_node = None
    uv2_map_node = None
    uv_scale_node = None

    if ref_maps:
        has_lightmap = D3D.map_light in ref_maps

        if has_lightmap is False or (has_lightmap and len(ref_maps) > 1):
            uv_map_node = node_tree.nodes.new('ShaderNodeUVMap')
            uv_map_node.uv_map = 'UVMap'
            uv_map_node.location = (-800, 0)
            uv_scale_node = node_tree.nodes.new('ShaderNodeMapping')
            uv_scale_node.vector_type = 'TEXTURE'
            uv_scale_node.scale = al_mat[D3D.uv_scale] + (1, ) if D3D.uv_scale in al_mat else (1, )*3
            uv_scale_node.location = (-600, 0)
            node_tree.links.new(uv_map_node.outputs['UV'], uv_scale_node.inputs['Vector'])

        if has_lightmap:
            uv2_map_node = node_tree.nodes.new('ShaderNodeUVMap')
            uv2_map_node.uv_map = 'UVLightmap'

    # Create texture map nodes
    count = 0
    for map_key in ref_maps:
        image = get_image_datablock(ref_maps[map_key], working_dir, recursive=True, place_holder_image=place_holder_images)
        if image:
            if d3d_to_node[map_key] in node_group.inputs:
                count += 1
                map_node = node_tree.nodes.new('ShaderNodeTexImage')
                map_node.image = image
                map_node.label = map_key
                # Connect the nodes
                if uv_scale_node:
                    node_tree.links.new(uv_scale_node.outputs['Vector'], map_node.inputs['Vector'])
                node_tree.links.new(map_node.outputs['Color'], node_group.inputs[d3d_to_node[map_key]])
                # Position the nodes
                x = int(count / 2) * -300 if count % 2 else int(count / 2) * 300
                map_node.location = (-200, x)

            elif map_key is D3D.map_light:
                map_node = node_tree.nodes.new('ShaderNodeTexImage')
                map_node.image = image
                map_node.label = map_key
                emission_node = node_tree.nodes.new('ShaderNodeEmission')
                add_shader_node = node_tree.nodes.new('ShaderNodeAddShader')

                node_tree.links.new(uv2_map_node.outputs['UV'], map_node.inputs['Vector'])
                node_tree.links.new(map_node.outputs['Color'], emission_node.inputs['Color'])
                node_tree.links.new(map_node.outputs['Color'], emission_node.inputs['Strength'])
                node_tree.links.new(node_group.outputs['Shader'], add_shader_node.inputs[0])
                node_tree.links.new(emission_node.outputs['Emission'], add_shader_node.inputs[1])
                node_tree.links.new(add_shader_node.outputs['Shader'], output_node.inputs['Surface'])

                # Position the nodes
                uv2_map_node.location = (-800, 600)
                map_node.location = (-200, 600)
                emission_node.location = (-0, 600)
                add_shader_node.location = (200, 0)
                output_node.location = (400, 0)

    if D3D.col_diff in al_mat and d3d_to_node[D3D.col_diff] in node_group.inputs:
        node_group.inputs[d3d_to_node[D3D.col_diff]].default_value = al_mat[D3D.col_diff] + (1, )

    if D3D.col_spec in al_mat and d3d_to_node[D3D.col_spec] in node_group.inputs:
        node_group.inputs[d3d_to_node[D3D.col_spec]].default_value = al_mat[D3D.col_spec] + (1, )

    if D3D.coef_spec in al_mat and d3d_to_node[D3D.coef_spec] in node_group.inputs:
        node_group.inputs[d3d_to_node[D3D.coef_spec]].default_value = min(max(0.0, al_mat[D3D.coef_spec]), 100.0)

    if D3D.coef_emit in al_mat and d3d_to_node[D3D.coef_emit] in node_group.inputs:
        node_group.inputs[d3d_to_node[D3D.coef_emit]].default_value = min(max(0.0, al_mat[D3D.coef_emit]), 100.0)

    if D3D.opacity in al_mat and d3d_to_node[D3D.opacity] in node_group.inputs:
        node_group.inputs[d3d_to_node[D3D.opacity]].default_value = al_mat[D3D.opacity]


def get_reference_maps(al_mat):
    """ Get all the texture maps and find the source image with the best quality.
        Args:
            al_mat ('dict') - The data3d Material source.
        Returns:
            ref_maps ('dict') - The reference maps.
    """
    map_types = [D3D.map_diff, D3D.map_spec, D3D.map_norm, D3D.map_alpha, D3D.map_light]
    ref_maps = {}
    for map_key in map_types:
        map_key_hires = map_key + D3D.map_suffix_hires
        map_key_source = map_key + D3D.map_suffix_source
        map_key_lores = map_key + D3D.map_suffix_lores

        maps = [
            al_mat[map_key_source] if map_key_source in al_mat else '',
            al_mat[map_key_hires] if map_key_hires in al_mat else '',
            al_mat[map_key_lores] if map_key_lores in al_mat else ''
        ]
        ref_map = next((m for m in maps if (m and not m.endswith('.dds'))), '')
        if ref_map:
            ref_maps[map_key] = ref_map
    return ref_maps


def set_image_texture(bl_mat, image_path, map_key, working_dir, place_holder_image):
    """ Set the texture references for the Blender Internal material
        Args:
            bl_mat ('bpy.types.Material') - The Blender Material datablock.
            image_path ('str') - The image path.
            map_key ('str') - The map key.
            working_dir ('str') - The source directory of the data3d file, used for recursive image search.
            place_holder_image ('bool') - Import place-holder image if source is not available.
    """
    # Create the blender image texture
    name = map_key + '-' + os.path.splitext(os.path.basename(image_path))[0]
    texture = bpy.data.textures.new(name=name, type='IMAGE')
    texture.use_fake_user = True
    image = get_image_datablock(image_path, working_dir, recursive=True, place_holder_image=place_holder_image)

    if image:
        texture.image = image
        tex_slot = bl_mat.texture_slots.add()
        tex_slot.texture_coords = 'UV'
        tex_slot.texture = texture
        tex_slot.use_map_color_diffuse = False

        if map_key == D3D.map_diff:
            tex_slot.use_map_color_diffuse = True
        elif map_key == D3D.map_norm:
            texture.use_normal_map = True
            tex_slot.use_map_normal = True
        elif map_key == D3D.map_spec:
            texture.use_normal_map = True
            tex_slot.use_map_specular = True
        elif map_key == D3D.map_alpha:
            texture.use_normal_map = True
            tex_slot.use_map_alpha = True
            bl_mat.use_transparency = True
            bl_mat.transparency_method = 'Z_TRANSPARENCY'
        elif map_key == D3D.map_light:
            tex_slot.uv_layer = 'UVLightmap'
            tex_slot.use_map_emit = True
            tex_slot.use_rgb_to_intensity = True
        else:
            log.error('Image Texture type not found, %s', map_key)
    else:
        log.error('Image texture could not be loaded, %s', image_path)


def get_image_datablock(image_relpath, image_directory, recursive=False, place_holder_image=True):
    """ Load the image to blender, check if image has been loaded before.
        Args:
            image_relpath ('str') - The relative path to the image.
            image_directory ('str') - The parent directory.
        Kwargs:
            recursive ('bool') - Use recursive image search.
            place_holder_image ('bool') - if True a new place holder image will be created.
        Returns:
            img ('bpy.types.Image') - The loaded image datablock.
    """
    # FIXME: make use image search optional
    image_directory = os.path.normpath(image_directory)
    img = load_image(image_relpath.strip('/'), dirname=image_directory, place_holder=place_holder_image, recursive=recursive, check_existing=True)
    if img is None:
        log.warning('Warning: Image could not be loaded: %s in directory %s ', image_relpath, image_directory)
        return None
    img.use_fake_user = True
    return img


def import_material_node_groups():
    """ Load the archilogic cycles material node groups from the node-library.blend file.
    """
    filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/node-library.blend')

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.node_groups = data_from.node_groups

    for node_group in data_to.node_groups:
        log.debug('Importing material node group: %s', node_group.name)
        node_group.use_fake_user = True


def get_al_material(bl_mat, tex_subdir, from_metadata=False):
    """ Get the json material data from Archilogic metadata or Blender Internal material.
        Args:
            bl_mat ('bpy.types.Material') - The Blender materials.
            tex_subdir ('str') - The texture export directory.
        Kwargs:
            from_metadata ('bool') - Get json from metadata.
        Returns:
            al_mat ('dict') - The parsed data3d material.
            textures ('list(bpy.types.Image)') - The list of associated textures to export.
    """
    al_mat = {}
    textures = []
    # Get Material from Archilogic MetaData
    if from_metadata and D3D.bl_meta in bl_mat:
        al_mat = bl_mat[D3D.bl_meta].to_dict()
    else:
        al_mat[D3D.col_diff] = list(bl_mat.diffuse_color)
        al_mat[D3D.col_spec] = list(bl_mat.specular_color)
        al_mat[D3D.coef_spec] = int(bl_mat.specular_hardness)

        if bl_mat.emit > 0.0:
            al_mat[D3D.coef_emit] = bl_mat.emit
        if bl_mat.use_transparency:
            al_mat[D3D.opacity] = bl_mat.alpha

        for tex_slot in bl_mat.texture_slots:
            if tex_slot is not None and tex_slot.texture.type == 'IMAGE':
                # Fixme: if type image but no filepath, abort
                # Fixme: handle packed images
                file = os.path.basename(tex_slot.texture.image.filepath)
                textures.append(tex_slot.texture.image)

                if tex_slot.use_map_color_diffuse:
                    al_mat[D3D.map_diff] = tex_subdir + file
                elif tex_slot.use_map_specular:
                    al_mat[D3D.map_spec] = tex_subdir + file
                elif tex_slot.use_map_normal:
                    al_mat[D3D.map_norm] = tex_subdir + file
                elif tex_slot.use_map_alpha:
                    al_mat[D3D.map_alpha] = tex_subdir + file
                elif tex_slot.use_map_emit:
                    al_mat[D3D.map_light + D3D.map_suffix_hires] = tex_subdir + file
                    al_mat[D3D.map_light + D3D.map_suffix_source] = tex_subdir + file
                    al_mat[D3D.map_light + D3D.map_suffix_lores] = tex_subdir + file
                # FIXME get Lightmap texture set
                else:
                    log.info('Texture type not supported for export: %s', file)

        # Fixme: export texture scale/size?

    return al_mat, textures


def get_default_al_material():
    al_mat = {D3D.col_diff: (0.85, ) * 3,
              D3D.col_spec: (0.25, ) * 3}
    return al_mat


def toggle_render_engine():
    cycles_engine = 'CYCLES'
    blender_engine = 'BLENDER_RENDER'
    use_cycles = True if C.scene.render.engine == blender_engine else False
    for mat in bpy.data.materials:
        mat.use_nodes = use_cycles
    bpy.context.scene.render.engine = cycles_engine if use_cycles else blender_engine


#################
# Setup         #
#################

def setup():
    """ Setup the material utils, load node groups.
    """
    # Import the Cycles material node groups from reference file
    log.info('Setting up material_utils.')
    import_material_node_groups()
