import pathlib
from .Reader import *  # struct + os
from .SimpleParse import *

import bpy, math
import mathutils
import bmesh
from mathutils import Vector, Matrix


def load_lvl(file_path):
    print("Starting to load level")
    scene = bpy.context.scene

    file_path = os.path.abspath(file_path)
    texture_directory = os.path.join(os.path.dirname(file_path), 'textures')
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    print("Texture_directory: " + texture_directory)

    if not pathlib.Path(os.path.join(os.path.dirname(file_path), file_basename, 'background.sgi.msb')).exists():
        raise FileNotFoundError("Missing background.sgi.msb in subfolder (don't use background.lvl)")

    with open(file_path, "r", 1, 'ascii') as f:
        content = f.readlines()

    # Note for Pointlight: Last two params are "Radius in pixels(at default screen res of 1280x720)" and nevercull
    # 4 point lights are used for effects
    # Default values: (thanks MikeZ)
    # stageSizeDefaultX = 3750
    # stageSizeDefaultY = 2000
    # defaultShadowDistance = -400 # negative is down (below the chars), positive is up (on floor behind them)
    # Guessed default values:
    # z near and far: 3,20000
    parser_instructions = [['StageSize:', 'ii'],
                           ['BottomClearance:', 'i'],
                           ['Start1:', 'i'],
                           ['Start2:', 'i'],
                           ['ShadowDir:', 'c'],  # deprecated, only U and D are allowed characters
                           ['ShadowDist:', 'i'],  # Use this instead (to convert: Default is -400)
                           ['Light:', 'siiifffis'],  # String is 'Pt',  rgbxyz...  , 8 allowed (use max 4)
                           ['Light:', 'siiifffi'],  # Pointlight without nevercull
                           ['Light:', 'siiifff'],  # String is 'Dir', rgbxyz,  4 allowed (use max 2)
                           ['Light:', 'siii'],  # String is 'Amb', rgb,     1 allowed
                           ['CAMERA', 'iii'],  # fov, znear zfar
                           ['CAMERA', 'i'],  # fov
                           ['3D', 'fii'],  # tile_rate, tilt_height1, tilt_height2
                           ['2D', 's'],  # Contains the path to the texture for the 2D level
                           ['Music_Intro', 's'],
                           ['Music_Loop', 's'],
                           ['Music_InterruptIntro', 'i'],  # If >0 loop starts even if intro hasn't finished
                           ['Music_Outro', 's'],
                           ['Replace', 'sssss'],
                           ['ForceReplace', 'i'],
                           ['ReplaceNumIfChar', 'si'],
                           ['Replace', 'ss']]  # This one is for ReplaceNumIfChar
    print("LVL data is read but not used for now")
    lvl_metadata = parse(content, parser_instructions)
    sgi = SGI(os.path.join(os.path.dirname(file_path), file_basename, 'background.sgi.msb'))
    sgi_data = sgi.get_metadata()

    sgm_data = []  # List of models

    # SGM
    print("Starting SGM import")
    print("===================")
    n_of_vertices = 0
    for element in sgi_data:
        print("Current sgm file: " + element['shape_name'] + '.sgm.msb')

        sgm = SGM(os.path.join(os.path.abspath(os.path.dirname(file_path)), file_basename,
                               element['shape_name'] + '.sgm.msb'))
        current_sgm = sgm.get_data()
        sgm_data.append(current_sgm)

        # Check if the model has any joint data, if it has load the sgs file
        # Not working correctly

        sgs_data = None
        if current_sgm['attribute_length_per_vertex'] == 44:
            sgs = SGS(os.path.join(os.path.abspath(os.path.dirname(file_path)), file_basename,
                                   element['shape_name'] + "." + SGS.FILE_EXTENSION))
            sgs_data = sgs.get_data()

        vertex_list = []
        normals = []
        uv_coords = []
        vertex_colors = []
        # Optional data
        joint_ids = []
        joint_weights = []
        for vertex in current_sgm['vertices']:
            x = struct.unpack('>f', vertex[0:4])[0]
            y = struct.unpack('>f', vertex[4:8])[0]
            z = struct.unpack('>f', vertex[8:12])[0]
            vertex_list.append(mathutils.Vector((x, y, z)))
            # Normals
            normal_x = struct.unpack('>f', vertex[12:16])[0]
            normal_y = struct.unpack('>f', vertex[16:20])[0]
            normal_z = struct.unpack('>f', vertex[20:24])[0]
            normals.append([normal_x, normal_y, normal_z])
            # UV coordinates
            u = struct.unpack('>f', vertex[24:28])[0]
            v = struct.unpack('>f', vertex[28:32])[0]
            uv_coords.append([u, v])
            # UCHAR4 ==> unsigned char x,y,z,w ==> Assuming rgba? TODO correct?
            r = struct.unpack('>B', vertex[32:33])[0]
            g = struct.unpack('>B', vertex[33:34])[0]
            b = struct.unpack('>B', vertex[34:35])[0]
            a = struct.unpack('>B', vertex[35:36])[0]
            # Blender wants the vertex color channels to be between 0 and 1
            vertex_colors.append([r / 255.0, g / 255.0, b / 255.0, a / 255.0])
            # Check if we have bone data
            if len(vertex) == 44:
                # bone id 0 = no bone, so first bone is 1
                joint_ids.append(struct.unpack('BBBB', vertex[36:40]))
                temp_joint_weights = struct.unpack('BBBB', vertex[40:44])
                # Normalize them from 0 .. 255 to 0.0 to 1.0
                joint_weights.append([temp_joint_weights[0]/255.0, temp_joint_weights[1]/255.0,
                                      temp_joint_weights[2]/255.0, temp_joint_weights[3]/255.0])
        n_of_vertices += len(vertex_list)
        mesh = bpy.data.meshes.new(element['shape_name'])
        # Edges are calculated by blender (see source for from_pydata)
        mesh.from_pydata(vertex_list, [], current_sgm['index_buffer'])

        # TODO what was this for again? (find blender forum link)
        for o in scene.objects:
            o.select = False

        mesh.update()
        mesh.validate()

        new_object = bpy.data.objects.new(element['element_name'], mesh)

        # This sets position, rotation and scale
        new_object.matrix_world = mathutils.Matrix(element['mat4'])

        current_material = get_material(texture_directory, current_sgm['texture_name'])
        new_object.data.materials.append(current_material)

        # bmesh (uvs and vertex color)
        bmesh_mesh = bmesh.new()
        bmesh_mesh.from_mesh(mesh)

        uv_layer = bmesh_mesh.loops.layers.uv.new("uv")
        tex_layer = bmesh_mesh.faces.layers.tex.new("texture")
        # http://www.macouno.com/2013/07/24/setting-vertex-colors/
        vertex_color_layer = bmesh_mesh.loops.layers.color.new("rgb")
        vertex_alpha_layer = bmesh_mesh.loops.layers.color.new("a")

        for i, f in enumerate(bmesh_mesh.faces):
            # There is only one texture slot for this material ==> [0], see get_material
            # Set image for this vertex (TODO is this necessary?)
            f[tex_layer].image = current_material.texture_slots[0].texture.image
            for j, l in enumerate(f.loops):
                # Set uv
                luv = l[uv_layer].uv
                index_of_current_vertex = current_sgm['index_buffer'][i][j]

                luv[0] = uv_coords[index_of_current_vertex][0]
                luv[1] = uv_coords[index_of_current_vertex][1]
                # Set vertex colors and alpha
                current_vc = vertex_colors[index_of_current_vertex]
                l[vertex_color_layer] = [current_vc[0], current_vc[1], current_vc[2]]
                l[vertex_alpha_layer] = [current_vc[3], current_vc[3], current_vc[3]]
        bmesh_mesh.to_mesh(mesh)
        mesh.update()
        mesh.validate()

        scene.objects.link(new_object)
        # TODO What is this needed for
        new_object.select = True
        # TODO what is this needed for
        if scene.objects.active is None or scene.objects.active.mode == 'OBJECT':
            scene.objects.active = new_object
        # Highly questionable if this is correct (also check in SGM) TODO check
        if element['is_visible'] == 0:
            new_object.hide = True

        # Now that the basic geometry is set up we add bone info if there is any

        if sgs_data is not None:
            # Solve bone dependencies (does not account for circular dependencies (can't happen))
            n_of_bones = len(sgs_data['names'])
            unsolved_dependencies = []
            # Each entry has: [name, parent_id, bone_mat, sgs_id]
            bone_table = []
            # Find root bone
            for i in range(0, n_of_bones):
                if sgs_data['parent_id'][i] == -1:
                    print("Found root bone at position" + str(i))
                    bone_table.append([sgs_data['names'][i], sgs_data['parent_id'][i], sgs_data['bone_mat'][i], i, ""])
                    unsolved_dependencies.append(i)
                    break
            else:
                raise ValueError("Malformed sgm, no root bone found")
            while len(unsolved_dependencies) != 0:
                for i in range(0, n_of_bones):
                    if unsolved_dependencies[0] == sgs_data['parent_id'][i]:
                        # Found a new dependency, add to bone table and as a new dependency
                        bone_table.append([sgs_data['names'][i], sgs_data['parent_id'][i], sgs_data['bone_mat'][i], i , sgs_data['names'][sgs_data['parent_id'][i]]])
                        unsolved_dependencies.append(i)
                unsolved_dependencies.pop(0)  # Remove element we searched for
            # Now we have a proper bone table
            print("Bonetable:")
            for single_bone in bone_table:
                print("Name:" + single_bone[0] + " ParentID:" + str(single_bone[1]) + " sgs_id:" + str(single_bone[3]) + " parent_name: " + single_bone[4])
            # With that we can make the armature (the bones)

            converted_bone_table = []
            for single_bone in bone_table:
                (trans, rot, scale) = mathutils.Matrix(single_bone[2]).decompose()
                # TODO debug stuff
                #print("==")
                #print(trans)
                #print(rot)
                #print(scale)
                #print("==")
                if single_bone[3] == -1:
                    converted_bone_table.append( (single_bone[0],None,(trans[0], trans[1], trans[2])) )
                else:
                    converted_bone_table.append( (single_bone[0],single_bone[4], (trans[0], trans[1], trans[2])))

            # TODO uncomment, add rotation
            # TODO add vertex groups, link them together
            # createRig(element['shape_name'] + "thing",Vector((0,0,0)),converted_bone_table)


            vertex_groups = {}

    print("Stage has " + str(len(sgi_data)) + " objects")
    print("Stage has " + str(n_of_vertices) + " vertices")


def get_material(path, name):
    # Check if material already exists
    # If yes: Return the old one, else make new
    try:
        return bpy.data.materials[name]
    except KeyError:  # Not found # TODO error handling!
        print("Material " + name + " not found, making a new one")
    # Load image (you are expected to have levels-textures.gfs extracted)
    texture_path = os.path.normpath(os.path.join(path, os.pardir, os.pardir, os.pardir, os.pardir,
                                                 'levels-textures', 'temp', 'levels', 'textures', name + '.dds'))
    try:
        image = bpy.data.images.load(texture_path)
    except:
        raise NameError("Can not load image at path: " + texture_path)
    # Create image texture from image
    texture = bpy.data.textures.new(name=name, type='IMAGE')
    texture.image = image
    # Disable auto mipmaps
    texture.use_mipmap = False
    # Disable interpolation
    texture.use_interpolation = False
    # Set Box filter (no blur)
    texture.filter_type = 'BOX'

    # Make material
    mat = bpy.data.materials.new(name)

    # Use transparency (if the texture has any)
    # TODO add conditional if there is no alpha in the texture
    # Is this still required?
    mat.use_transparency = True
    # Enable transparency in rendering
    mat.use_face_texture = True
    mat.use_face_texture_alpha = True
    # No lighting applied because we cannot simulate the lighting properly
    mat.use_shadeless = True
    # Set diffuse (full)
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    # Set specular (none)
    mat.specular_intensity = 0.0
    # Set ambient TODO what does this do
    mat.ambient = 1
    # Add texture slot for color texture
    color_slot = mat.texture_slots.add()
    color_slot.texture = texture
    # TODO Is this general (like searching for an input named like that) or already a specific reference?
    color_slot.texture_coords = 'UV'

    return mat


def load(operator, context, filepath=""):
    load_lvl(filepath)
    # TODO better error handling
    return {'FINISHED'}


class SGS(Reader):
    FILE_EXTENSION = "sgs.msb"
    FILE_VERSION = "2.0"

    def __init__(self, file_path):
        super().__init__(open(file_path, "rb"), os.path.getsize(file_path), BIG_ENDIAN)
        self.file_path = os.path.abspath(file_path)

    def get_data(self):
        sgs_data = {'names': [], 'parent_id': [], 'bone_mat': []}
        if self.read_pascal_string() != SGS.FILE_VERSION:
            raise ValueError("Invalid version")
        number_of_joints = self.read_int(8)
        for _ in range(0, number_of_joints):
            sgs_data['names'].append(self.read_pascal_string())
            sgs_data['parent_id'].append(self.read_int(4, is_signed=True))
            bone_mat = self.read_mat4()
            sgs_data['bone_mat'].append(bone_mat)
        return sgs_data

    def read_pascal_string(self):
        """
        Read long+ASCII String from internal file
        :return: String
        """
        return self.read_string(self.read_int(8))

    def read_mat4(self):
        mat = [self.read_float() for _ in range(0, 16)]
        # Column major, apparently
        return [[mat[0], mat[4], mat[8], mat[12]],
                [mat[1], mat[5], mat[9], mat[13]],
                [mat[2], mat[6], mat[10], mat[14]],
                [mat[3], mat[7], mat[11], mat[15]]]


class SGA(Reader):
    FILE_EXTENSION = "sga.msb"
    FILE_VERSION = "3.0"

    def __init__(self, file_path):
        super().__init__(open(file_path, "rb"), os.path.getsize(file_path, BIG_ENDIAN))
        self.file_path = os.path.abspath(file_path)

    def get_data(self):
        sga_data = {}
        if self.read_pascal_string() != SGA.FILE_VERSION:
            raise ValueError("Invalid version")
        unknown = self.read_int(4)
        n_of_elements = self.read_int(8)
        n_of_uv_tracks = self.read_int(8)
        anim_length_sec = self.read_float()


        return sga_data

    def read_pascal_string(self):
        """
        Read long+ASCII String from internal file
        :return: String
        """
        return self.read_string(self.read_int(8))

    def read_mat4(self):
        return [self.read_float() for _ in range(0, 16)]


class SGM(Reader):
    FILE_EXTENSION = "sgm.msb"
    FILE_VERSION = "2.0"

    def __init__(self, file_path):
        super().__init__(open(file_path, "rb"), os.path.getsize(file_path), BIG_ENDIAN)
        self.file_path = os.path.abspath(file_path)

    def get_data(self):
        sgm_data = {}
        if self.read_pascal_string() != SGM.FILE_VERSION:
            raise ValueError("Invalid version")
        sgm_data['texture_name'] = self.read_pascal_string()
        self.skip_bytes(52)  # TODO Unknown stuff
        sgm_data['data_format'] = self.read_pascal_string()
        sgm_data['attribute_length_per_vertex'] = self.read_int(8)
        number_of_vertices = self.read_int(8)
        number_of_triangles = self.read_int(8)
        number_of_joints = self.read_int(8)
        print("Vertices: " + str(number_of_vertices))
        print("Triangles: " + str(number_of_triangles))
        print("Joints: " + str(number_of_joints))
        # VERTICES
        vertices = []
        for _ in range(0, number_of_vertices):
            vertices.append(self.file.read(sgm_data['attribute_length_per_vertex']))
        sgm_data['vertices'] = vertices
        # TRIANGLES for an index buffer
        triangles = []
        for _ in range(0, number_of_triangles):
            triangles.append([self.read_int(2), self.read_int(2), self.read_int(2)])
        sgm_data['index_buffer'] = triangles

        # Bounding box, we don't need it for Blender, skipping it
        # Is regenerated during export anyway
        # Skip 6*4 bytes = 24 bytes
        self.skip_bytes(24)
        # Skeleton info
        joints = []
        for _ in range(0, number_of_joints):
            joints.append([self.read_pascal_string()])
        for i in range(0, number_of_joints):
            joints[i].append(self.read_mat4())
        sgm_data['joints'] = joints
        return sgm_data

    def read_pascal_string(self):
        """
        Read long+ASCII String from internal file
        :return: String
        """
        return self.read_string(self.read_int(8))

    def read_mat4(self):
        return [self.read_float() for _ in range(0, 16)]


class SGI(Reader):
    FILE_EXTENSION = "sgi.msb"
    FILE_VERSION = "2.0"

    def __init__(self, file_path):
        super().__init__(open(file_path, "rb"), os.path.getsize(file_path), BIG_ENDIAN)
        self.file_path = os.path.abspath(file_path)

    def get_metadata(self):
        """
        Read SGI file
        :raise ValueError: File integrity compromised
        """
        sgi_data = []

        if self.read_pascal_string() != SGI.FILE_VERSION:
            raise ValueError("Invalid version")
        number_of_elements = self.read_int(8)

        print("Reading SGI file (" + str(number_of_elements) + " elements)")
        print("==================================")

        for _ in range(0, number_of_elements):
            element = {'element_name': self.read_pascal_string(),
                       'shape_name': self.read_pascal_string(),
                       'mat4': self.read_mat4(),
                       'is_visible': self.read_int(1)}
            # TODO unknown if is_visible is actually is_visible
            print("Name: " + element['element_name'])
            print("Shape name" + element['shape_name'])
            self.skip_bytes(1)  # TODO unknown

            number_of_animations = self.read_int(8)
            print("This model has " + str(number_of_animations) + " animations")
            animations = []
            for _ in range(0, number_of_animations):
                current_animation = {'animation_name': self.read_pascal_string(),
                                     'animation_file_name': self.read_pascal_string()}
                print("Animation name: " + current_animation['animation_name'])
                print("Animation filename: " + current_animation['animation_file_name'])
                animations.append(current_animation)
            element['animations'] = animations
            sgi_data.append(element)
            print("================================")

        print("Reading SGI file finished")
        return sgi_data

    def read_pascal_string(self):
        """
        Read long+ASCII String from internal file
        :return: String
        """
        return self.read_string(self.read_int(8))

    def read_mat4(self):
        mat = [self.read_float() for _ in range(0, 16)]
        # Column major, apparently
        return [[mat[0], mat[4], mat[8], mat[12]],
                [mat[1], mat[5], mat[9], mat[13]],
                [mat[2], mat[6], mat[10], mat[14]],
                [mat[3], mat[7], mat[11], mat[15]]]









#TEMP
def createRig(name, origin, boneTable):
    # Create armature and object
    bpy.ops.object.add(
        type='ARMATURE',
        enter_editmode=True,
        location=origin)
    ob = bpy.context.object
    ob.show_x_ray = True
    ob.name = name
    amt = ob.data
    amt.name = name+'Amt'
    amt.show_axes = True

    # Create bones
    bpy.ops.object.mode_set(mode='EDIT')
    for (bname, pname, vector) in boneTable:
        bone = amt.edit_bones.new(bname)
        if pname:
            parent = amt.edit_bones[pname]
            bone.parent = parent
            bone.head = parent.tail
            bone.use_connect = False
            (trans, rot, scale) = parent.matrix.decompose()
        else:
            bone.head = (0,0,0)
            rot = Matrix.Translation((0,0,0))	# identity matrix
        bone.tail = rot * Vector(vector) + bone.head
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

