# stdlib imports
import os.path as op
import xml.etree.ElementTree as ET
import struct
from math import radians
from tempfile import TemporaryDirectory
import subprocess
import shutil

# Blender imports
import bpy  # pylint: disable=import-error
from mathutils import Matrix, Vector  # pylint: disable=import-error

# Internal imports
from ..serialization.formats import (bytes_to_half, bytes_to_ubyte,  # noqa pylint: disable=relative-beyond-top-level
                                     bytes_to_int_2_10_10_10_rev)
from ..serialization.utils import read_list_header  # noqa pylint: disable=relative-beyond-top-level
from ..NMS.LOOKUPS import VERTS, NORMS, UVS, COLOUR  # noqa pylint: disable=relative-beyond-top-level
from ..NMS.LOOKUPS import DIFFUSE, MASKS, NORMAL, DIFFUSE2  # noqa pylint: disable=relative-beyond-top-level
from .readers import read_material, read_metadata, read_gstream  # noqa pylint: disable=relative-beyond-top-level
from .utils import element_to_dict  # noqa pylint: disable=relative-beyond-top-level
from .SceneNodeData import SceneNodeData  # noqa pylint: disable=relative-beyond-top-level
from ..utils.io import get_NMS_dir  # noqa pylint: disable=relative-beyond-top-level

VERT_TYPE_MAP = {5121: {'size': 1, 'func': bytes_to_ubyte},
                 5131: {'size': 2, 'func': bytes_to_half},
                 36255: {'size': 1, 'func': bytes_to_int_2_10_10_10_rev}}
ROT_MATRIX = Matrix.Rotation(radians(90), 4, 'X')

TYPE_MAP = {'MESH': 'Mesh', 'LOCATOR': 'Locator', 'REFERENCE': 'Reference',
            'JOINT': 'Joint'}


class ImportScene():
    """ Load a scene into blender.

    Parameters
    ----------
    fpath : string
        Filepath to the scene file to be loaded.
    parent_obj : obj
        The parent object. For a first-class scene this will always be none
        and an empty NMS_SCENE node will be generated for the scene to be
        placed in.
        For scenes that are referenced by another scene this will be that
        reference object.
    ref_scenes : dict
        A dictionary with the path to another scene as the key, and the blender
        object that has already been loaded as the value.
    """
    def __init__(self, fpath, parent_obj=None, ref_scenes=dict()):
        self.local_directory = op.dirname(fpath)

        self.parent_obj = parent_obj
        self.ref_scenes = ref_scenes
        # When scenes contain reference nodes there can be clashes with names.
        # To ensure correct parenting of objects in blender, we will keep track
        # of what objects exist within a scene as there will be no name clashes
        # within each scene.
        self.local_objects = dict()

        self.requires_render = True
        self.scn = bpy.context.scene

        # Find the local name of the scene (relative to the NMS PCBANKS dir)
        with open(fpath, 'rb') as fobj:
            fobj.seek(0x60)
            self.scene_name = fobj.read(0x80).decode().replace('\x00', '')
        print('Loading {0}'.format(self.scene_name))

        # To optimise loading of referenced scenes, check to see if the current
        # scene has already been loaded into blender. If so, simply make a copy
        # of the mesh object and place it appropriately.
        if self.scene_name in self.ref_scenes:
            self._add_existing_to_scene()
            self.requires_render = False
            return

        self.ref_scenes[self.scene_name] = list()

        # check to see if there already exists an exml file with the same name
        if op.exists(fpath.upper().replace('.MBIN', '.EXML')):
            fpath = fpath.upper().replace('.MBIN', '.EXML')

        ext = op.splitext(fpath)[1]

        self.data = None
        self.vertex_elements = list()
        self.bh_data = list()
        self.materials = dict()

        # change to render with cycles
        self.scn.render.engine = 'CYCLES'

        if ext.lower() == '.mbin':
            # Determine if the current NMSDK setting require the exml to be
            # cached
            cache = bpy.context.scene.NMSDK_import_settings.cache_exml
            if not cache:
                with TemporaryDirectory() as temp_dir:
                    fpath_dst = op.join(temp_dir, op.basename(fpath))
                    shutil.copy(fpath, fpath_dst)
                    retcode = subprocess.call(
                        ["MBINCompiler", '-q', fpath_dst],
                        shell=True)
                    if retcode != 0:
                        print('MBINCompiler failed to run. Please ensure it '
                              'is registered on the path.')
                        print('Import failed')
                        return
                    fpath = fpath_dst.replace('.MBIN', '.EXML')
                    self._load_scene(fpath)
            else:
                retcode = subprocess.call(["MBINCompiler", '-q', fpath],
                                          shell=True)
                if retcode != 0:
                    print('MBINCompiler failed to run. Please ensure it is '
                          'registered on the path.')
                    print('Import failed')
                    return
                fpath = fpath.replace('.MBIN', '.EXML')
                self._load_scene(fpath)
        elif ext.lower() != '.exml':
            raise TypeError('Selected file is of the wrong format.')
        else:
            self._load_scene(fpath)

        if self.data is None:
            raise ValueError('Cannot load scene file...')
        self.scene_node_data = SceneNodeData(self.data)
        self.directory = op.dirname(self.scene_node_data.Name)
        # remove the name of the top level object
        self.scene_node_data.info['Name'] = None
        self.geometry_file = op.join(
            self.local_directory,
            op.relpath(
                self.scene_node_data.Attribute('GEOMETRY'),
                self.directory) + '.PC')
        self.geometry_stream_file = self.geometry_file.replace('GEOMETRY',
                                                               'GEOMETRY.DATA')

        # get the information about what data the geometry file contains
        with open(self.geometry_file, 'rb') as f:
            f.seek(0x140)
            self.count, self.stride = struct.unpack('<II', f.read(0x8))
            # skip platform data
            f.seek(0x8, 1)
            list_offset, list_count = read_list_header(f)
            f.seek(list_offset, 1)
            # jump to the actual TkVertexElement data
            for _ in range(list_count):
                data = dict()
                data['semID'], data['size'], data['type'], data['offset'] = \
                    struct.unpack('<IIII', f.read(0x10))
                f.seek(0x10, 1)
                self.vertex_elements.append(data)

        # load all the bounded hull data
        self._load_bounded_hulls()

        # load all the mesh metadata
        self.mesh_metadata = read_metadata(self.geometry_file)

# region public methods

    def load_mesh(self, mesh_node):
        """ Load the mesh.
        This will load the mesh data into memory then deserialize the actual
        vertex and index data from the gstream mbin.
        """
        self._load_mesh(mesh_node)
        self._deserialize_vertex_data(mesh_node)
        self._deserialize_index_data(mesh_node)
        mesh_node._generate_geometry()
        mesh_node._generate_bounded_hull(self.bh_data)

    def render_mesh(self, mesh_ID):
        """Render the specified mesh in the blender view. """
        obj = self.scene_node_data.get(mesh_ID)
        if obj.Type == 'MESH':
            obj.metadata = self.mesh_metadata.get(mesh_ID.upper())
            self.load_mesh(obj)
            self._add_mesh_to_scene(obj, standalone=True)
        elif obj.Type == 'LOCATOR' or obj.Type == 'JOINT':
            self._add_empty_to_scene(obj, standalone=True)
        self.state = {'FINISHED'}

    def render_scene(self):
        """ Render the scene in the blender view. """
        # First, add the empty NMS_SCENE object that everything will be a
        # child of
        if self.parent_obj is None:
            # First, remove everything else in the scene
            self._clear_prev_scene()
            self._add_empty_to_scene('NMS_SCENE')
        for obj in self.scene_node_data.iter():
            if obj.Type == 'MESH':
                obj.metadata = self.mesh_metadata.get(obj.Name.upper())
                self.load_mesh(obj)
                self._add_mesh_to_scene(obj)
            elif (obj.Type == 'LOCATOR' or obj.Type == 'JOINT'
                  or obj.Type == 'REFERENCE'):
                self._add_empty_to_scene(obj)
        self.state = {'FINISHED'}

# region private methods

    def _add_empty_to_scene(self, scene_node, standalone=False):
        """ Adds the given scene node data to the Blender scene.

        Parameters
        ----------
        standalone : bool
            Whether or not the scene_node is provided by itself and not part
            of a complete scene. This is used to indicate that a single mesh
            part is being rendered.
        """
        if scene_node == 'NMS_SCENE' and self.parent_obj is None:
            # If the scene_node is simply 'NMS_SCENE' just add an empty and
            # return
            empty_mesh = bpy.data.meshes.new('NMS_SCENE')
            empty_obj = bpy.data.objects.new('NMS_SCENE', empty_mesh)
            empty_obj.matrix_world = ROT_MATRIX
            self.scn.objects.link(empty_obj)
            self.scn.objects.active = empty_obj
            bpy.ops.object.mode_set(mode='OBJECT')
            # check if the scene is proc-gen
            descriptor_name = op.basename(self.scene_name) + '.DESCRIPTOR.MBIN'
            if op.exists(op.join(self.local_directory, descriptor_name)):
                empty_obj.NMSScene_props.is_proc = True
            self.local_objects['NMS_SCENE'] = empty_obj
            return

        # Otherwise just assign everything as usual...
        name = scene_node.Name

        # create a new empty instance
        empty_mesh = bpy.data.meshes.new(name)
        empty_obj = bpy.data.objects.new(name, empty_mesh)
        empty_obj.NMSNode_props.node_types = TYPE_MAP[scene_node.Type]

        # get transform and apply
        transform = scene_node.Transform['Trans']
        empty_obj.location = Vector(transform)
        # get rotation and apply
        rotation = scene_node.Transform['Rot']
        empty_obj.rotation_mode = 'ZXY'
        empty_obj.rotation_euler = rotation
        # get scale and apply
        scale = scene_node.Transform['Scale']
        empty_obj.scale = Vector(scale)

        self.local_objects[name] = empty_obj

        if not standalone:
            if self.parent_obj is not None and scene_node.parent.Name is None:
                # Direct child of the reference node
                empty_obj.parent = self.parent_obj
                self.ref_scenes[self.scene_name].append(empty_obj)
            elif scene_node.parent.Name is not None:
                # Other child
                empty_obj.parent = self.local_objects[scene_node.parent.Name]
            else:
                # Direct child of loaded scene
                empty_obj.parent = self.local_objects['NMS_SCENE']
        else:
            empty_obj.matrix_world = ROT_MATRIX * empty_obj.matrix_world

        # link the object then update the scene so that the above transforms
        # can be applied before we do the NMS -> blender scene rotation
        self.scn.objects.link(empty_obj)
        self.scn.update()

        if scene_node.Type == 'REFERENCE':
            # TODO: requires optimisation to re-use already loaded mesh data
            # if a scene is referenced multiple times
            mod_dir = get_NMS_dir(self.local_directory)
            empty_obj.NMSReference_props.reference_path = scene_node.Attribute(
                'SCENEGRAPH')
            ref_scene_path = op.join(mod_dir,
                                     scene_node.Attribute('SCENEGRAPH'))
            sub_scene = ImportScene(ref_scene_path, empty_obj, self.ref_scenes)
            if sub_scene.requires_render:
                sub_scene.render_scene()

    def _add_existing_to_scene(self):
        # existing is a list of child objects to the reference
        existing = self.ref_scenes[self.scene_name]
        # for each object
        for obj in existing:
            new_obj = obj.copy()
            new_obj.parent = self.parent_obj
            self.scn.objects.link(new_obj)

    def _add_mesh_to_scene(self, scene_node, standalone=False):
        """ Adds the given scene node data to the Blender scene.

        Parameters
        ----------
        standalone : bool
            Whether or not the scene_node is provided by itself and not part
            of a complete scene. This is used to indicate that a single mesh
            part is being rendered.
        """
        name = scene_node.Name
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(scene_node.verts[VERTS],
                         scene_node.edges,
                         scene_node.faces)
        # add normals
        for i, vert in enumerate(mesh.vertices):
            vert.normal = scene_node.verts[NORMS][i]

        mesh_obj = bpy.data.objects.new(name, mesh)
        mesh_obj.NMSNode_props.node_types = 'Mesh'

        # get transform and apply
        transform = scene_node.Transform['Trans']
        mesh_obj.location = Vector(transform)
        # get rotation and apply
        rotation = scene_node.Transform['Rot']
        mesh_obj.rotation_mode = 'ZXY'
        mesh_obj.rotation_euler = rotation
        # get scale and apply
        scale = scene_node.Transform['Scale']
        mesh_obj.scale = Vector(scale)

        self.local_objects[name] = mesh_obj

        # give object correct parent
        if not standalone:
            if self.parent_obj is not None and scene_node.parent.Name is None:
                # Direct child of reference node
                mesh_obj.parent = self.parent_obj
                self.ref_scenes[self.scene_name].append(mesh_obj)
            elif scene_node.parent.Name is not None:
                # Other child
                parent_obj = self.local_objects[scene_node.parent.Name]
                mesh_obj.parent = parent_obj
            else:
                # Direct child of loaded scene
                mesh_obj.parent = self.local_objects['NMS_SCENE']
        else:
            mesh_obj.matrix_world = ROT_MATRIX * mesh_obj.matrix_world

        # link the object then update the scene so that the above transforms
        # can be applied before we do the NMS -> blender scene rotation
        self.scn.objects.link(mesh_obj)
        self.scn.update()

        # ensure the newly created object is the active one in the scene
        self.scn.objects.active = mesh_obj
        mesh = mesh_obj.data
        # Add UV's
        bpy.ops.object.mode_set(mode='EDIT')
        if not mesh.uv_textures:
            mesh.uv_textures.new()
        bpy.ops.object.mode_set(mode='OBJECT')

        uvs = scene_node.verts[UVS]
        uv_layers = mesh.uv_layers.active.data
        for idx, loop in enumerate(mesh.loops):
            uv = uvs[loop.vertex_index]
            uv_layers[idx].uv = (uv[0], 1 - uv[1])

        # Add vertex colour
        if COLOUR in scene_node.verts.keys():
            colours = scene_node.verts[COLOUR]
            if not mesh.vertex_colors:
                mesh.vertex_colors.new()
            colour_loops = mesh.vertex_colors.active.data
            for idx, loop in enumerate(mesh.loops):
                colour = colours[loop.vertex_index]
                colour_loops[idx].color = (colour[0]/255,
                                           colour[1]/255,
                                           colour[2]/255)

        # sort out materials
        mat_path = self._get_material_path(scene_node)
        material = None
        if mat_path is not None:
            material = self._create_material(mat_path)
            mesh_obj.NMSMesh_props.material_path = scene_node.Attribute('MATERIAL')  # noqa
        if material is not None:
            mesh_obj.data.materials.append(material)
            mesh_obj.active_material = material

        if bpy.context.scene.NMSDK_import_settings.draw_hulls:
            # create child object for bounded hull
            name = 'BH' + name
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(scene_node.bounded_hull, [], [])
            bh_obj = bpy.data.objects.new(name, mesh)
            # Don't show the bounded hull
            bh_obj.hide = True
            bh_obj.parent = mesh_obj
            self.scn.objects.link(bh_obj)

    def _clear_prev_scene(self):
        """ Remove any existing data in the blender scene. """
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        for mat in bpy.data.materials:
            bpy.data.materials.remove(mat)
        for img in bpy.data.images:
            bpy.data.images.remove(img)

    def _create_material(self, mat_path):
        # retrieve a cached copy if it exists
        if mat_path in self.materials:
            return self.materials[mat_path]
        # Read the material data directly from the material MBIN
        mat_data = read_material(mat_path)
        if mat_data is None or mat_data == dict():
            # no texture data so just exit this function.
            return
        # create a new material
        mat_name = mat_data.pop('Name')
        mat = bpy.data.materials.new(name=mat_name)

        uniforms = mat_data['Uniforms']

        # Since we are using cycles we want to have node-based materials
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        # clear any existing nodes just to be safe.
        nodes.clear()
        # Now add all the nodes we need.
        output_material = nodes.new(type='ShaderNodeOutputMaterial')
        output_material.location = (500, 0)
        principled_BSDF = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_BSDF.location = (200, 150)
        principled_BSDF.inputs['Roughness'].default_value = 1.0

        # Set up some constants
        if 61 in mat_data['Flags']:
            kfAlphaThreshold = 0.1
        elif 10 in mat_data['Flags']:
            kfAlphaThreshold = 0.45
        else:
            kfAlphaThreshold = 0.0001

        # create the diffuse, mask and normal nodes and give them their images
        for tex_type, tex_path in mat_data['Samplers'].items():
            img = None
            if tex_type == DIFFUSE:
                # texture
                _path = self._get_path(tex_path)
                if op.exists(_path):
                    img = bpy.data.images.load(_path)
                diffuse_texture = nodes.new(type='ShaderNodeTexImage')
                diffuse_texture.name = diffuse_texture.label = 'Texture Image - Diffuse'  # noqa
                diffuse_texture.image = img
                diffuse_texture.location = (-600, 300)
                lColourVec4 = diffuse_texture.outputs['Color']
                if 15 in mat_data['Flags']:
                    # #ifdef _F16_DIFFUSE2MAP
                    if 16 not in mat_data['Flags']:
                        # #ifndef _F17_MULTIPLYDIFFUSE2MAP
                        diffuse2_path = self._get_path(
                            mat_data['Samplers'][DIFFUSE2])
                        if op.exists(diffuse2_path):
                            img = bpy.data.images.load(diffuse2_path)
                        diffuse2_texture = nodes.new(type='ShaderNodeTexImage')
                        diffuse2_texture.name = diffuse_texture.label = 'Texture Image - Diffuse2'  # noqa
                        diffuse2_texture.image = img
                        diffuse2_texture.location = (-400, 300)
                        mix_diffuse = nodes.new(type='ShaderNodeMixRGB')
                        mix_diffuse.location = (-200, 300)
                        links.new(mix_diffuse.inputs['Color1'],
                                  lColourVec4)
                        links.new(mix_diffuse.inputs['Color2'],
                                  diffuse2_texture.outputs['Color'])
                        links.new(mix_diffuse.inputs['Fac'],
                                  diffuse2_texture.outputs['Alpha'])
                        lColourVec4 = mix_diffuse.outputs['Color']
                    else:
                        print('Note: Please post on discord the model you are'
                              ' importing so I can fix this!!!')

                if 20 in mat_data['Flags'] or 28 in mat_data['Flags']:
                    # #ifdef _F21_VERTEXCOLOUR
                    # lColourVec4 *= IN( mColourVec4 );
                    col_attribute = nodes.new(type='ShaderNodeAttribute')
                    col_attribute.attribute_name = 'Col'
                    mix_colour = nodes.new(type='ShaderNodeMixRGB')
                    links.new(mix_colour.inputs['Color1'],
                              lColourVec4)
                    links.new(mix_colour.inputs['Color2'],
                              col_attribute.outputs['Color'])
                    links.new(principled_BSDF.inputs['Base Color'],
                              mix_colour.outputs['Color'])
                else:
                    links.new(principled_BSDF.inputs['Base Color'],
                              lColourVec4)
                # #ifndef _F44_IMPOSTER
                if 43 not in mat_data['Flags']:
                    # #ifdef _F39_METALLIC_MASK
                    if 38 in mat_data['Flags']:
                        links.new(principled_BSDF.inputs['Metallic'],
                                  diffuse_texture.outputs['Alpha'])
                    else:
                        # use the default value from the file
                        if 'gMaterialParamsVec4' in uniforms:
                            principled_BSDF.inputs['Metallic'].default_value = uniforms['gMaterialParamsVec4'][2]  # noqa
                if (8 in mat_data['Flags'] or 10 in mat_data['Flags'] or
                        21 in mat_data['Flags']):
                    # Handle transparency
                    alpha_mix = nodes.new(type='ShaderNodeMixShader')
                    alpha_shader = nodes.new(type='ShaderNodeBsdfTransparent')
                    discard_node = nodes.new(type="ShaderNodeMath")
                    discard_node.operation = 'LESS_THAN'
                    discard_node.inputs[1].default_value = kfAlphaThreshold
                    links.new(discard_node.inputs[0],
                              diffuse_texture.outputs['Alpha'])
                    links.new(alpha_mix.inputs['Fac'],
                              discard_node.outputs['Value'])
                    links.new(alpha_mix.inputs[1],
                              principled_BSDF.outputs['BSDF'])
                    links.new(alpha_mix.inputs[2],
                              alpha_shader.outputs['BSDF'])
                    FRAGMENT_COLOUR0 = alpha_mix.outputs['Shader']
                else:
                    FRAGMENT_COLOUR0 = principled_BSDF.outputs['BSDF']
            elif tex_type == MASKS:
                # texture
                _path = self._get_path(tex_path)
                if op.exists(_path):
                    img = bpy.data.images.load(_path)
                mask_texture = nodes.new(type='ShaderNodeTexImage')
                mask_texture.name = mask_texture.label = 'Texture Image - Mask'
                mask_texture.image = img
                mask_texture.location = (-600, 0)
                mask_texture.color_space = 'NONE'
                if 43 not in mat_data['Flags']:
                    # #ifndef _F44_IMPOSTER
                    if 24 in mat_data['Flags']:
                        # #ifdef _F25_ROUGHNESS_MASK
                        # lfRoughness = 1 - lMasks.g
                        # RGB separation node
                        separate_rgb = nodes.new(type='ShaderNodeSeparateRGB')
                        separate_rgb.location = (-400, 0)
                        # subtract the green channel from 1:
                        sub_1 = nodes.new(type="ShaderNodeMath")
                        sub_1.operation = 'SUBTRACT'
                        sub_1.location = (-200, 0)
                        sub_1.inputs[0].default_value = 1.0
                        lfRoughness = sub_1.outputs['Value']
                        # link them up
                        links.new(separate_rgb.inputs['Image'],
                                  mask_texture.outputs['Color'])
                        links.new(sub_1.inputs[1], separate_rgb.outputs['G'])
                    else:
                        roughness_value = nodes.new(type='ShaderNodeValue')
                        roughness_value.outputs[0].default_value = 1.0
                        lfRoughness = roughness_value.outputs['Value']
                    # lfRoughness *= lUniforms.mpCustomPerMaterial->gMaterialParamsVec4.x;  # noqa
                    mult_param_x = nodes.new(type="ShaderNodeMath")
                    mult_param_x.operation = 'MULTIPLY'
                    mult_param_x.inputs[1].default_value = uniforms[
                        'gMaterialParamsVec4'][0]
                    links.new(mult_param_x.inputs[0], lfRoughness)
                    lfRoughness = mult_param_x.outputs['Value']
                links.new(principled_BSDF.inputs['Roughness'],
                          lfRoughness)

                # gMaterialParamsVec4.x
                # from shader: #ifdef _F40_SUBSURFACE_MASK
                if 39 in mat_data['Flags']:
                    links.new(principled_BSDF.inputs['Subsurface'],
                              separate_rgb.outputs['R'])
                if 43 in mat_data['Flags']:
                    # lfMetallic = lMasks.b;
                    links.new(principled_BSDF.inputs['Metallic'],
                              separate_rgb.outputs['B'])

            elif tex_type == NORMAL:
                # texture
                _path = self._get_path(tex_path)
                if op.exists(_path):
                    img = bpy.data.images.load(_path)
                normal_texture = nodes.new(type='ShaderNodeTexImage')
                normal_texture.name = normal_texture.label = 'Texture Image - Normal'  # noqa
                normal_texture.image = img
                normal_texture.location = (-600, -300)
                normal_texture.color_space = 'NONE'
                # separate xyz then recombine
                normal_sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
                normal_sep_xyz.location = (-400, -300)
                normal_com_xyz = nodes.new(type='ShaderNodeCombineXYZ')
                normal_com_xyz.location = (-200, -300)
                # swap X and Y channels
                links.new(normal_com_xyz.inputs['X'],
                          normal_sep_xyz.outputs['Y'])
                links.new(normal_com_xyz.inputs['Y'],
                          normal_sep_xyz.outputs['X'])
                links.new(normal_com_xyz.inputs['Z'],
                          normal_sep_xyz.outputs['Z'])

                # normal map
                normal_map = nodes.new(type='ShaderNodeNormalMap')
                normal_map.location = (0, -300)
                # link them up
                links.new(normal_sep_xyz.inputs['Vector'],
                          normal_texture.outputs['Color'])
                links.new(normal_map.inputs['Color'],
                          normal_com_xyz.outputs['Vector'])
                links.new(principled_BSDF.inputs['Normal'],
                          normal_map.outputs['Normal'])

                if 42 in mat_data['Flags']:
                    # lTexCoordsVec4.xy *= lUniforms.mpCustomPerMesh->gCustomParams01Vec4.z;  # noqa
                    normal_scale = nodes.new(type='ShaderNodeMapping')
                    normal_scale.location = (-1000, -300)
                    scale = uniforms['gCustomParams01Vec4'][2]
                    normal_scale.scale = (scale, scale, scale)
                    tex_coord = nodes.new(type='ShaderNodeTexCoord')
                    tex_coord.location = (-1200, -300)
                    tex_coord.object = self.scn.objects.active
                    links.new(normal_scale.inputs['Vector'],
                              tex_coord.outputs['Generated'])
                    links.new(normal_texture.inputs['Vector'],
                              normal_scale.outputs['Vector'])

        # Apply some fnial transforms to the data before connecting it to the
        # Material output node
        if 50 in mat_data['Flags']:
            # #ifdef _F51_DECAL_DIFFUSE
            # FRAGMENT_COLOUR0 = vec4( lOutColours0Vec4.xyz, lColourVec4.a );
            alpha_mix_decal = nodes.new(type='ShaderNodeMixShader')
            alpha_shader = nodes.new(type='ShaderNodeBsdfTransparent')
            links.new(alpha_mix_decal.inputs['Fac'],
                      diffuse_texture.outputs['Alpha'])
            links.new(alpha_mix_decal.inputs[1],
                      alpha_shader.outputs['BSDF'])
            links.new(alpha_mix_decal.inputs[2],
                      FRAGMENT_COLOUR0)
            FRAGMENT_COLOUR0 = alpha_mix_decal.outputs['Shader']

        # FInally, link the fragment colour to the output material
        links.new(output_material.inputs['Surface'],
                  FRAGMENT_COLOUR0)

        # link some nodes up according to the uberfragment.bin shader
        if 6 in mat_data['Flags']:
            mat.use_shadeless = True
        self.materials[mat_path] = mat

        return mat

    def _deserialize_index_data(self, mesh):
        """ Take the raw index data and generate a list of actual index data.

        Parameters
        ----------
        mesh : SceneNodeData
            SceneNodeData of type MESH to get the vertex data of.
        """
        idx_count = int(mesh.Attribute('BATCHCOUNT'))
        size = mesh.metadata.idx_size // idx_count
        if size == 4:
            fmt = '<I'
        elif size == 2:
            fmt = '<H'
        else:
            raise ValueError('Something has gone wrong!!')
        with open(self.geometry_stream_file, 'rb') as f:
            f.seek(mesh.metadata.idx_off)
            for _ in range(idx_count):
                mesh.idxs.append(struct.unpack(fmt, f.read(size))[0])

    def _deserialize_vertex_data(self, mesh):
        """ Take the raw vertex data and generate a list of actual vertex data.

        Parameters
        ----------
        mesh : SceneNodeData
            SceneNodeData of type MESH to get the vertex data of.
        """
        semIDs = list()
        read_sizes = list()
        read_funcs = list()
        for ve in self.vertex_elements:
            mesh.verts[ve['semID']] = list()
            semIDs.append(ve['semID'])
            read_sizes.append(ve['size'] * VERT_TYPE_MAP[ve['type']]['size'])
            read_funcs.append(VERT_TYPE_MAP[ve['type']]['func'])
        num_verts = mesh.metadata.vert_size / self.stride
        if not num_verts % 1 == 0:
            raise ValueError('Something has gone wrong!!!')
        with open(self.geometry_stream_file, 'rb') as f:
            f.seek(mesh.metadata.vert_off)
            for _ in range(int(num_verts)):
                for i in range(self.count):
                    # Skip 't' component.
                    mesh.verts[semIDs[i]].append(
                        read_funcs[i](f.read(read_sizes[i]))[:-1])

    def _get_material_path(self, scene_node):
        real_path = None
        raw_path = scene_node.Attribute('MATERIAL')
        if raw_path is not None:
            real_path = self._get_path(raw_path)
        return real_path

    def _get_path(self, fpath):
        return op.normpath(
            op.join(self.local_directory, op.relpath(fpath, self.directory)))

    def _load_bounded_hulls(self):
        with open(self.geometry_file, 'rb') as f:
            f.seek(0x130)
            list_offset, list_count = read_list_header(f)
            f.seek(list_offset, 1)
            for _ in range(list_count):
                self.bh_data.append(struct.unpack('<fff', f.read(0xC)))
                # Skip 't' component.
                f.seek(0x4, 1)

    def _load_mesh(self, mesh):
        """ Load the mesh data from the geometry stream file."""
        mesh.raw_verts, mesh.raw_idxs = read_gstream(self.geometry_stream_file,
                                                     mesh.metadata)

    def _load_scene(self, fpath):
        tree = ET.parse(fpath)
        root = tree.getroot()
        self.data = element_to_dict(root)
