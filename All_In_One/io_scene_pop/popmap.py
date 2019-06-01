import bpy
from mathutils import Matrix
from io_scene_pop.binary_reader import BinaryReader
import os
import struct

class GameObject:
    def __init__(self, name, hash, center, bounding_box, rot_matrix, scale,
                 mesh_hash, material_pack_hash, extra_hash, group):
        self.name = name
        self.hash = hash
        self.center = center
        self.bounding_box = bounding_box
        self.rotation = rot_matrix
        self.scale = scale
        self.mesh_hash = mesh_hash
        self.material_pack_hash = material_pack_hash
        self.extra_hash = extra_hash
        self.group = group


def get_dds_header(width, height, num_mipmaps, compression):
    b_height = struct.pack("<I", height)
    b_width = struct.pack("<I", width)
    b_num_mipmaps = struct.pack("<I", num_mipmaps + 1)
    if num_mipmaps == 0:
        if compression == 0 or compression == 1:
            flags1 = b'\x0F\x10\x00\x00'
        else:
            flags1 = b'\x07\x10\x08\x00'
        flags2 = b'\x00\x10\x00\x00'
    else:
        if compression == 0 or compression == 1:
            flags1 = b'\x0F\x10\x02\x00'
        else:
            flags1 = b'\x07\x10\x0A\x00'
        flags2 = b'\x08\x10\x40\x00'

    if compression == 0 or compression == 1:
        # header for no compression
        return (b'\x44\x44\x53\x20\x7c\x00\x00\x00' + flags1 + b_height +
                b_width +
                b'\x00\x00\x00\x00\x00\x00\x00\x00' +
                b_num_mipmaps + b'\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x20\x00\x00\x00\x41\x00' +
                b'\x00\x00\x00\x00\x00\x00\x20\x00\x00' +
                b'\x00\x00\x00\xFF\x00\x00\xFF\x00\x00' +
                b'\xFF\x00\x00\x00\x00\x00\x00\xFF' + flags2 +
                b'\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    elif compression == 2 or compression == 5 or compression == 11:
        # header for dxt1 compression
        return (b'\x44\x44\x53\x20\x7c\x00\x00\x00' + flags1 + b_height +
                b_width +
                b'\x00\x00\x00\x00\x00\x00\x00\x00' +
                b_num_mipmaps + b'\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x20\x00\x00\x00\x04\x00' +
                b'\x00\x00\x44\x58\x54\x31\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00' + flags2 +
                b'\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    elif compression == 7:
        # header for dxt5 compression
        return (b'\x44\x44\x53\x20\x7c\x00\x00\x00' + flags1 + b_height +
                b_width +
                b'\x00\x00\x00\x00\x00\x00\x00\x00' +
                b_num_mipmaps + b'\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x20\x00\x00\x00\x04\x00' +
                b'\x00\x00\x44\x58\x54\x35\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00' + flags2 +
                b'\x00\x00\x00\x00\x00\x00' +
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    else:
        raise ValueError("Unknown texture compression: " +
                         str(compression))


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def blender_add_texture(blend_data, name, path):
    if not name in blend_data.textures:
        image = blend_data.images.load(path)
        texture = blend_data.textures.new(name, type='IMAGE')
        texture.image = image


def blender_add_material(blend_data, name, texture_name):
    if not name in blend_data.materials:
        material = blend_data.materials.new(name)
        material["texture_name"] = texture_name # to add it later on
        material.use_transparency = True
        material.alpha = 0
        material.specular_alpha = 0
        material.diffuse_intensity = 1
        material.specular_intensity = 0


def blender_add_mesh(blend_data, name, vertices, faces, uvs, uv_indices,
                     material_ids):
    if not name in blend_data.meshes:
        mesh = blend_data.meshes.new(name)
        mesh.from_pydata(vertices, [], faces)

        # add uvs to mesh
        if len(uvs) > 0:
            mesh.uv_textures.new().name = "UVMap"
            uv_data = mesh.uv_layers[0].data
            if len(uv_indices) > 0:
                for face_index, face in enumerate(mesh.polygons):
                    for vert_index, loop_index in zip([0, 1, 2],
                                                      face.loop_indices):
                        uv_index = uv_indices[face_index][vert_index]
                        uv_data[loop_index].uv = uvs[uv_index]
            else:
                for face in mesh.polygons:
                    for vert_index, loop_index in zip(face.vertices,
                                                      face.loop_indices):
                        uv_data[loop_index].uv = uvs[vert_index]

        mesh["material_ids"] = material_ids
    else:
        blend_data.meshes[name].materials.clear()


def add_materials_to_mesh(blend_data, mesh, material_pack, material_ids):
    if len(mesh.materials) > 0:
        # this mesh already got materials, should be fine
        return

    assigned_faces = 0
    curr_id = 0
    for material_id, num in material_ids:
        if num == 0:
            continue

        if material_id >= 0 and material_id < len(material_pack):
            material_hash = material_pack[material_id]
            try:
                material = blend_data.materials[material_hash]
                mesh.materials.append(material)

                for face_index in range(assigned_faces,
                                        assigned_faces + num):
                    mesh.polygons[face_index].material_index = curr_id
                curr_id += 1
                assigned_faces += num
            except KeyError:
                print("Missing material", material_hash, "!")
        else:
            print("Material id", material_id, "out of bounds!")


def add_bounding_box_material(blend_data, mesh, group_name):
    color = None
    if group_name == "Trigger":
        color = (0, 1, 1)
    elif group_name == "Portal":
        color = (0, 1, 0)
    elif group_name == "Set Position":
        color = (0, 0, 1)
    elif group_name == "Loading Trigger":
        color = (1, 0.5, 0)

    if color is not None:
        try:
            material = blend_data.materials[group_name]
        except KeyError:
            material = blend_data.materials.new(group_name)
            material.diffuse_color = color
            material.diffuse_intensity = 1
            material.specular_intensity = 0
            material.use_transparency = True
            material.alpha = 0.3
        mesh.materials.append(material)
        return True
    return False


def get_group(name):
    if "TEC" in name:
        return "Trigger"
    elif "ini_pos" in name.lower():
        return "Set Position"
    elif ("SND" in name) or ("SFX" in name):
        return "Sound"
    elif "PORTAL" in name:
        return "Portal"
    elif "SECTOR" in name:
        return "Sector"
    elif "CAM" in name:
        return "Camera Position"
    elif "TUT" in name:
        return "Descriptive Text"
    elif (("NET" in name) or ("FRH" in name) or ("NAV" in name) or
          ("GUY" in name)):
        return "AI Position"
    elif ("LUM" in name) or ("Lampe" in name) or ("Lanterne" in name):
        return "Lightning"
    elif "OBJ" in name:
        return "Movable Object"
    elif (("GFX" in name) or ("Particule" in name) or ("GP11" in name) or
          ("FOG" in name)):
        return "Graphics"
    elif "trigger" in name.lower():
        return "Trigger"
    else:
        return "Other"


def create_wowlist(directory):

    file_hashes = {}

    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if (os.path.isfile(path) and path.endswith(".dec") and
            "wow" in path):
            with open(path, 'rb') as f:
                f.read(8)
                reader = BinaryReader(f.read(4))
                file_hashes[reader.read_hex()] = file
    return file_hashes


def import_wol(path, context, wow_hashes):
    wow_list = []
    with open(path, 'rb') as f:
        f.read(12)  # block length, 99C0FFEE and wol hash, not needed
        reader = BinaryReader(f.read())
        while not reader.end_of_stream():
            wow_hash = reader.read_hex()
            if wow_hash in wow_hashes:
                wow_list.append(wow_hashes[wow_hash])
            else:
                ValueError("Unknown wow hash")
            assert reader.read_string(4) == ".wow"

    directory = os.path.dirname(path)
    for wow_path in [os.path.join(directory, wow) for wow in wow_list]:
        import_wow(wow_path, context, False, wow_hashes)


def import_wow(path, context, textures_only, wow_hashes):

    blend_data = context.blend_data
    scene = context.scene


    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]
    texture_directory = os.path.join(os.path.dirname(path), "textures")
    if not os.path.exists(texture_directory):
        os.makedirs(texture_directory)


    object_hashes = set()
    game_objects = []

    material_packs = {}
    material_hashes = set()
    textures = set()
    color_palettes = {}

    modellist_hash = None
    unknown_mesh_types_hash = None
    unknown_mesh_types = set()

    extra_hashes = {}
    what_to_load = {}


    # read file and split data blocks by the separator "99C0FFEE"
    # yep, it's 99 coffee^^
    with open(path, 'rb') as f:
        blocks = f.read().split(b'\x99\xC0\xFF\xEE')


    for block in  blocks:

        reader = BinaryReader(block)

        hash = reader.read_hex()
        if hash == "000000B0":
            # this is the first dword of every file
            continue
        elif hash == "0FF7C0DE":
            # this is the terminator sequence
            break
        elif hash == modellist_hash:
            # hashes of the models, not all models of the file
            # are listed here though
            while not reader.end_of_stream():
                object_hashes.add(reader.read_hex())
            continue
        elif hash == unknown_mesh_types_hash:
            for _ in range((reader.length - reader.pos - 4) // 4):
                unknown_mesh_types.add(reader.read_hex())
            reader.read_int()
            continue
        elif hash in extra_hashes.values():
            reader.pos = reader.length - 36  # don't hate me
            what_to_load[hash] = (reader.read_hex(), reader.read_hex(),
                                  reader.read_hex())


        type = reader.read_hex()
        if textures_only and type != hash:
            continue

        if type == "776F772E":
            # .wow
            reader.read_int()
            reader.read_int()
            reader.read_string(60)

            empty_hash = reader.read_hex()
            reader.read_float(20)
            unknown_hash1 = reader.read_hex()
            unknown_hash2 = reader.read_hex()
            modellist_hash = reader.read_hex()
            unknown_mesh_types_hash = reader.read_hex()
            unknown_hash4 = reader.read_hex()
            unknown_hash5 = reader.read_hex()


        elif type == "6F61672E":
            # GameObject (.gao)
            reader.read_int() # ten
            reader.read_int() # eight
            flags = reader.read_int()
            reader.read_int()
            name = reader.read_string()
            reader.read_int() # some more flags
            reader.read_short() # always 4096?

            reader.read_float() # always 0?

            # Rotation and scale of the object
            rot_x = reader.read_float(3)
            scale_x = reader.read_float()
            rot_y = reader.read_float(3)
            scale_y = reader.read_float()
            rot_z = reader.read_float(3)
            scale_z = reader.read_float()
            rot_matrix = Matrix((rot_x, rot_y, rot_z)).transposed()
            if scale_x == 0:
                scale_x = 1
            if scale_y == 0:
                scale_y = 1
            if scale_z == 0:
                scale_z = 1
            scale = (scale_x, scale_y, scale_z)

            # position of the center of the object
            center = reader.read_float(3)

            if flags & 0x10000:
                reader.read_hex()
            else:
                reader.read_float()

            reader.read_int()

            if flags & 0x80000:
                reader.read_float(6)

            bounding_box = reader.read_float(6)

            if flags & 0x4000:
                mesh_hash = reader.read_hex()
                material_pack_hash = reader.read_hex()
                reader.read_byte(10) # something magic, always the same?
                amount = reader.read_int()
                reader.read_int(amount)
                reader.read_int() # seems to always be 10
                reader.read_hex() # pretty much FFFFFFFF
                reader.read_hex()
                reader.read_hex()
                extra_hash = ""
            else:
                reader.pos = reader.length - 8
                extra_hash = reader.read_hex()
                mesh_hash = ""
                material_pack_hash = None

            game_objects.append(GameObject(name, hash, center,
                                           bounding_box, rot_matrix, scale,
                                           mesh_hash, material_pack_hash,
                                           extra_hash, get_group(name)))


        elif type == "00000001":
            # mesh data
            version = reader.read_hex()

            if version == "00000007" or version == "00000008":
                flags = reader.read_int()
                has_second_mesh = (reader.read_int() != 0)

                num_vertices = reader.read_int()
                num_unknown = reader.read_int()
                has_unknown = (reader.read_int() != 0)
                num_uvs = reader.read_int()
                num_materials = reader.read_int()
                bool2 = False

                if flags & 0x8 or flags & 0x10:
                    reader.read_float()
                    has_normals = (reader.read_short() != 0)
                    num4 = reader.read_short()
                    for _ in range(num4):
                        unknown = reader.read_short()
                        num_floats = reader.read_short()
                        reader.read_float(16)
                        reader.read_hex()
                        reader.read_float(num_floats)
                    if num4 > 0:
                        has_normals = ((reader.read_int() != 0) or
                                       has_normals)
                else:
                    bool2 = (reader.read_int() != 0)
                    has_normals = (reader.read_int() != 0)

                # vertex coordinates
                vert_data = reader.read_float(3 * num_vertices)
                vertices = chunks(vert_data, 3)

                # no idea what this is, maybe weights for bones?
                if has_unknown:
                    reader.read_float(1 * num_unknown)

                # most likely normals
                if has_normals:
                    normal_data = reader.read_float(3 * num_vertices)
                    normals = chunks(normal_data, 3)

                # uv coordinates
                uv_data = reader.read_float(2 * num_uvs)
                uvs = chunks(uv_data, 2)

                # faces
                num_faces = 0
                material_ids = []
                for _ in range(num_materials):
                    num_curr_matid = reader.read_int()
                    num_faces += num_curr_matid
                    material_id = reader.read_int()
                    material_ids.append((material_id, num_curr_matid))

                faces = []
                uv_indices = []
                for _ in range(num_faces):
                    faces.append(reader.read_short(3))
                    uv_indices.append(reader.read_short(3))
                    reader.read_short(2) # no idea what that is

                # add mesh to blender
                mesh_name = hash
                blender_add_mesh(blend_data, mesh_name, vertices, faces,
                                 uvs, uv_indices, material_ids)

                # no idea what this data is, only in T2T files
                # unknown will be something else than 0 though,
                # also i've only seen unknown == 5 yet
                reader.read_int()
                unknown = reader.read_int()
                while unknown != 0:
                    amount = reader.read_int()
                    for _ in range(amount):
                        size = reader.read_short()
                        reader.read_short() # always 0x8000 ?
                        reader.read_short(2 * size)
                    unknown = reader.read_int()
                reader.read_int()

                # second object, no idea what it's purpose is, as it has
                # afaik always the same geometry as the first one
                if has_second_mesh:

                    num_faces = 0
                    material_ids = []
                    for _ in range(num_materials):
                        num_curr_matid = reader.read_int()
                        num_faces += num_curr_matid
                        material_id = reader.read_int()
                        material_ids.append((material_id, num_curr_matid))

                    size = reader.read_int()
                    unknown = reader.read_int()
                    num_vertices = reader.read_int()
                    block_length = reader.read_int()

                    # vertex data
                    vertices = []
                    uvs = []
                    uv_ids = []
                    if block_length == 20:
                        for _ in range(num_vertices):
                            # coordinates, uv
                            vertices.append(reader.read_float(3))
                            uvs.append(reader.read_float(2))
                    elif block_length == 32:
                        for _ in range(num_vertices):
                            # coordinates, normals, uv
                            vertices.append(reader.read_float(3))
                            reader.read_float(3)
                            uvs.append(reader.read_float(2))
                    elif block_length == 44:
                        for _ in range(num_vertices):
                            # coordinates, normals, uv, ?
                            vertices.append(reader.read_float(3))
                            reader.read_float(3)
                            uvs.append(reader.read_float(2))
                            reader.read_float(3)
                    elif block_length == 52:
                        for _ in range(num_vertices):
                            # coordinates, normals, ..., uv ?
                            vertices.append(reader.read_float(3))
                            reader.read_float(3)
                            reader.read_short(2)
                            reader.read_int()
                            reader.read_float(3)
                            uvs.append(reader.read_float(2))
                    elif block_length == 64:
                        for _ in range(num_vertices):
                            # coordinates, normals, ..., uv ?
                            vertices.append(reader.read_float(3))
                            reader.read_float(3)
                            reader.read_short(2)
                            reader.read_int()
                            reader.read_float(3)
                            uvs.append(reader.read_float(2))
                            reader.read_int()
                            reader.read_float(2)
                    else:
                        raise ValueError("Unknown vertex data size " +
                                         str(block_length) + " for "
                                         "second mesh at hash '" + hash +
                                         "'!")

                    # faces
                    size = reader.read_int()
                    face_data = reader.read_short(size // 2)
                    faces = chunks(face_data, 3)

                    blender_add_mesh(blend_data, mesh_name + "_second",
                                     vertices, faces, uvs, uv_ids,
                                     material_ids)

                    reader.read_int()

            else:
                pass


        elif type == "0000000B":
            # the "mesh" (rather call it data) mostly for objects with
            # "GFX" in it
            reader.read_int()
            reader.read_int()
            reader.read_hex()
            reader.read_int()
            reader.read_short()
            reader.read_float(24)
            # then maybe 4 hashes and then a lot of zeros, no idea


        elif type == "00000004":
            # material pack
            if reader.end_of_stream():
                # uh well, nice material pack...
                continue
            elif reader.read_int() != 0:
                # no idea what this is then, but it's not a texture pack
                continue

            num_materials = reader.read_int()
            if num_materials > 1000:
                # stupid way to decide this, but there doesn't seem to be
                # another one for 100_AileNord_wow_ff08941d.dec
                continue
            elif num_materials == 0:
                while reader.pos + 4 != reader.length:
                    assert reader.read_int() == 0

            mat_hashes = []
            for _ in range(num_materials):
                mat_hashes.append(reader.read_hex())
            material_packs[hash] = mat_hashes
            reader.read_int()
            assert reader.end_of_stream()


        elif type == "00000005":
            # material
            version = reader.read_int()
            if version >= 3 and version <= 9:
                reader.read_hex()
                if version >= 8:
                    reader.read_hex()
                    reader.read_hex()
                reader.read_int()
                reader.read_hex() # so far always FFFFFFFF
                reader.read_int()

                # when figured out which texture to use for what
                # (diffuse map, normal map etc.) use while again
                #while reader.pos + 4 != reader.length:
                if reader.pos + 4 == reader.length:
                    # empty material
                    continue

                reader.read_int() # flags
                if version >= 8:
                    reader.read_short()
                reader.read_int() # more flags, most interesting one
                specular_intensity = reader.read_float()
                diffuse_intensity = reader.read_float()
                reader.read_int() # even more flags
                if version == 9:
                    reader.read_byte(9)
                    reader.read_hex()
                texture_hash = reader.read_hex()

                material_name = hash
                texture_name = texture_hash
                blender_add_material(blend_data, material_name,
                                     texture_name)
                material_hashes.add(material_name)

            else:
                if version >= 22 or version == 0:
                    # no idea what that data this is, but they are all
                    # pretty similar
                    continue
                raise ValueError("unknown material version '" +
                                 str(version) + "' at '" + hash + "'!")


        elif type == "0D0024F1":
            # points to some hopefully important info
            extra_hashes[hash] = reader.read_hex()
            reader.read_int()
            assert reader.end_of_stream()


        elif type == hash:
            # texture
            if reader.read_hex() != "FFFFFFFF":
                if reader.read_hex() == "11111111":
                    # 11111111, 22222222, 33333333, ...
                    # what is this even?
                    pass
                else:
                    # this is a color palatte for a texture
                    reader.seek(-8, 1)
                    color_data = reader.read(4 * 256)
                    color_palettes[hash] = chunks(color_data, 4)
                    if not reader.pos + 4 == reader.length:
                        # another palette? o.O
                        reader.read_int(24)
                        reader.read(4 * 256)
                        reader.read_int(8)
                    reader.read_int()
                    assert reader.end_of_stream()
            else:
                # this is a real texture, not a color palette
                texture_type = reader.read_int()
                if texture_type == 286331153:
                    # 11111111, 22222222, ... what?
                    continue
                if hash not in textures:
                    textures.add(hash)
                    # for whatever reason there are always two data blocks
                    # for each texture, the first entry is only the
                    # texture information like width, height and so on
                    # though. therefore note which textures we've already
                    # seen and if have seen it twice import it
                else:
                    uses_palette = (texture_type & 0x40000000 and
                                    texture_type & 0x1)

                    (width, height) = reader.read_short(2)
                    reader.read_hex()
                    reader.read_hex() # some id?
                    reader.read_hex() # CAD01234
                    reader.read_hex() # 00FF00FF
                    reader.read_hex() # C0DEC0DE

                    if texture_type & 0x80000:
                        bool = (reader.read_int() != 1)
                        compression = reader.read_int()
                        assert width == reader.read_int() # width again
                        assert height == reader.read_int() # height again
                        num_mipmaps = reader.read_int()
                        if bool:
                            reader.read_int()
                    elif texture_type & 0x40000:
                        compression = 7
                        num_mipmaps = 0
                    else:
                        reader.read_short()
                        compression = reader.read_short()
                        reader.read_int()
                        reader.read_int()
                        reader.read_short()
                        reader.read_short()
                        num_mipmaps = reader.read_short()

                    dds_path = os.path.join(texture_directory,
                                            hash + ".dds")
                    dds = open(dds_path, 'bw')
                    dds.write(get_dds_header(width, height, num_mipmaps,
                                             compression))
                    if uses_palette:
                        if not texture_type & 0x40000:
                            palette = color_palettes[reader.read_hex()]
                        size = reader.length - reader.pos - 4
                        dds.write(b''.join([palette[i] for i in
                                            reader.read_byte(size)]))
                    else:
                        dds.write(reader.read(reader.length -
                                              reader.pos - 4))

                    # add texture to blender
                    blender_add_texture(blend_data, hash, dds_path)

        else:
            assert hash not in object_hashes


    if textures_only:
        return


    if not "PoP_Lamp1" in blend_data.objects:
        lamp1 = blend_data.lamps.new("PoP_Lamp1", 'HEMI')
        lamp1.energy = 0.5
        lamp2 = blend_data.lamps.new("PoP_Lamp2", 'HEMI')
        lamp2.energy = 0.3
        object = blend_data.objects.new("PoP_Lamp1", lamp1)
        scene.objects.link(object)
        object = blend_data.objects.new("PoP_Lamp2", lamp2)
        object.rotation_euler = (0, 3.14159, 0)
        scene.objects.link(object)
    scene.game_settings.material_mode = 'GLSL'


    for material_hash in material_hashes:
        material = blend_data.materials[material_hash]
        texture_name = material["texture_name"]
        try:
            texture = blend_data.textures[texture_name]
        except KeyError:
            try:
                texture_path = os.path.join(texture_directory,
                                            texture_name + ".dds")
                texture = blender_add_texture(blend_data, texture_name,
                                              texture_path)
            except:
                print("Missing texture", texture_name, "for material",
                      material_hash, "!")
                continue
        if material.texture_slots[0] is None:
            mat_texture = material.texture_slots.add()
            mat_texture.texture = texture
            mat_texture.texture_coords = 'UV'
            mat_texture.use_map_color_diffuse = True
            mat_texture.use_map_alpha = True
            mat_texture.mapping = 'FLAT'
            mat_texture.uv_layer = "UVMap"
            mat_texture.scale = (1, -1, 1)


    for game_object in game_objects:

        if not game_object.hash in object_hashes:
            game_object.group = "Not on map"

        if game_object.mesh_hash in blend_data.meshes:
            game_object.group = "Model"

            mesh = blend_data.meshes[game_object.mesh_hash]
            if game_object.mesh_hash + "_second" in blend_data.meshes:
                mesh_second = blend_data.meshes[game_object.mesh_hash +
                                                "_second"]
            else:
                mesh_second = None

            if game_object.material_pack_hash is not None:
                if game_object.material_pack_hash in material_packs:
                    material_pack = material_packs[
                        game_object.material_pack_hash]
                    material_ids = mesh["material_ids"]

                    add_materials_to_mesh(blend_data, mesh,
                                          material_pack, material_ids)
                    if mesh_second is not None:
                        add_materials_to_mesh(blend_data,
                                              mesh_second,
                                              material_pack,
                                              material_ids)
                elif (game_object.material_pack_hash in
                      blend_data.materials):
                    material_hash = game_object.material_pack_hash
                    face_count = len(mesh.polygons)
                    add_materials_to_mesh(blend_data, mesh,
                                          [material_hash],
                                          [(0, face_count)])
                    if mesh_second is not None:
                        face_count = len(mesh.polygons)
                        add_materials_to_mesh(blend_data, mesh_second,
                                              [material_hash],
                                              [(0, face_count)])
                else:
                    print("Missing material pack",
                          game_object.material_pack_hash,
                          "for object", game_object.hash, "!")

            # create object
            object = blend_data.objects.new(game_object.name, mesh)
            object.location = game_object.center
            object.rotation_euler = game_object.rotation.to_euler()
            object.scale = game_object.scale
            scene.objects.link(object)
            scene.objects.active = object

            if mesh_second is not None:
                # create object
                #object = blend_data.objects.new(game_object.name +
                #                                "_second",
                #                                mesh_second)
                #object.location = game_object.center
                #object.rotation_euler = game_object.rotation.to_euler()
                #object.scale = game_object.scale
                #scene.objects.link(object)
                #scene.objects.active = object
                pass
        else:
            if game_object.mesh_hash != "":
                print("Missing mesh", game_object.mesh_hash, "for object",
                      game_object.hash, "!")

            if game_object.hash in blend_data.meshes:
                mesh = blend_data.meshes[game_object.hash]
                mesh.materials.clear()
            else:
                mesh = blend_data.meshes.new(game_object.hash)
                (x_min, y_min, z_min, x_max, y_max, z_max) = game_object.bounding_box
                cub_verts = [(x_min, y_min, z_min), (x_min, y_min, z_max),
                             (x_min, y_max, z_min), (x_min, y_max, z_max),
                             (x_max, y_min, z_min), (x_max, y_min, z_max),
                             (x_max, y_max, z_min), (x_max, y_max, z_max)]
                cub_faces = [(0, 1, 3, 2), (0, 4, 5, 1), (4, 6, 7, 5),
                             (6, 7, 3, 2), (0, 2, 6, 4), (1, 3, 7, 5)]
                mesh.from_pydata(cub_verts, [], cub_faces)

            if game_object.extra_hash in extra_hashes:
                game_object.group = "Loading Trigger"
            has_material = add_bounding_box_material(blend_data, mesh,
                                                     game_object.group)

            # create object
            object = blend_data.objects.new(game_object.name, mesh)
            object.location = game_object.center
            object.rotation_euler = game_object.rotation.to_euler()
            object.scale = game_object.scale
            object.hide_render = True

            if game_object.extra_hash in extra_hashes:
                to_loads = what_to_load[extra_hashes[
                                       game_object.extra_hash]]
                count = 0
                for to_load in to_loads:
                    if to_load in wow_hashes:
                        if count == 1:
                            raise ValueError("trigger importing several wols")
                        wow_to_load = wow_hashes[to_load]

                        search_name = wow_to_load.split("wow_")[0]
                        for file in os.listdir(directory):
                            file_path = os.path.join(directory, file)
                            if (os.path.isfile(file_path) and
                                file_path.endswith(".dec") and
                                (search_name + "wol_") in file):
                                object["wol_to_load"] = file_path
                        count += 1

            if has_material:
                object.show_transparent = True
                object.show_wire = True
            else:
                object.draw_type = 'BOUNDS'

            scene.objects.link(object)
            scene.objects.active = object

        object["out_of_file"] = filename

        try:
            group = blend_data.groups[game_object.group]
        except KeyError:
            group = blend_data.groups.new(game_object.group)
        group.objects.link(object)
        if (game_object.group != "Trigger" and
            game_object.group != "Model" and
            game_object.group != "Other" and
            game_object.group != "Portal" and
            game_object.group != "Loading Trigger"):
            object.hide = True


