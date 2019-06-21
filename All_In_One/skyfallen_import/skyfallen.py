import struct


def read_struct(fmt, file):
    data = file.read(struct.calcsize(fmt))
    result = struct.unpack(fmt, data)
    if len(result) == 1:
        return result[0]
    return result


def calc_label(string):
    result = 0
    for index, char in enumerate(string.lower()):
        byte = ord(char) << index
        result = result ^ byte
    return result


def read_header(header, file):
    header_label = calc_label(header)
    label, count = read_struct('II', file)
    if label != header_label:
        raise Exception('Missing header: {}'.format(header))
    return count


def read_string(file):
    strlen = read_struct('I', file)
    struct_format = '{}s'.format(strlen)
    string = read_struct(struct_format, file)
    terminator = read_struct('B', file)
    if terminator != 0x00:
        print('No terminator for string', string)
    return string.decode('cp1251')


def read_vector(file):
    return read_struct('fff', file)


def read_packed_vector(is_normal, file):
    packed = read_struct('I', file)

    pos_x = (packed & 0x00FF0000) >> 16
    pos_y = (packed & 0x0000FF00) >> 8
    pos_z = (packed & 0x000000FF)

    pos_x = (pos_x / 127.5) - 1
    pos_y = (pos_y / 127.5) - 1
    pos_z = (pos_z / 127.5) - 1

    if is_normal:
        mirror = bool(packed & 0xFF000000)
        if mirror:
            pos_x, pos_y, pos_z = -pos_x, -pos_y, -pos_z

    return (pos_x, pos_y, pos_z)


def read_matrix4(file):
    data = read_struct('16f', file)
    return (
        (data[0], data[1], data[2], data[3]),
        (data[4], data[5], data[6], data[7]),
        (data[8], data[9], data[10], data[11]),
        (data[12], data[13], data[14], data[15]),
    )


# ------------------------------------------------------------------------------
# Versions
# ------------------------------------------------------------------------------
def v_num(major, minor):
    return major * 1000 + minor


class SFVersionHeader:
    def __init__(self, file):
        self.minor, self.major = read_struct('2H', file)
        self.v_num = v_num(self.major, self.minor)

    def __str__(self):
        return 'Version {}.{}'.format(self.major, self.minor)


class SFExportMeshVersion(SFVersionHeader):
    known = [v_num(4, 4), v_num(4, 5)]

    def __init__(self, file):
        super(SFExportMeshVersion, self).__init__(file)
        if self.v_num not in self.known:
            raise Exception('Unknown file version')

    def __str__(self):
        ver = super(SFExportMeshVersion, self).__str__()
        return 'Exported Mesh {}'.format(ver)


# ------------------------------------------------------------------------------
# Mesh Format
# ------------------------------------------------------------------------------
class SFMeshFormat:
    def __init__(self, file, version_number):
        self.v_num = version_number

        flags = read_header('MeshHeader', file)

        self.skinned = bool(flags & (1 << 0))
        self.tiled = bool(flags & (1 << 1))
        self.stripped = bool(flags & (1 << 2))
        self.scaled = bool(flags & (1 << 29))

        if self.scaled:
            self.scale = read_struct('f', file)
        else:
            self.scale = 512

    def __str__(self):
        string = 'SFMeshFormat:\n'
        string += '\tSkinned  = {}\n'.format(self.skinned)
        string += '\tTiled    = {}\n'.format(self.tiled)
        string += '\tStripped = {}\n'.format(self.stripped)
        string += '\tScaled   = {}'.format(self.scaled)
        string += '\t--------'
        string += '\tScale   = {}'.format(self.scale)
        return string


# ------------------------------------------------------------------------------
# Materials
# ------------------------------------------------------------------------------
class SFMaterial:
    def __init__(self, file):
        self.name = read_string(file)
        if not self.name:
            self.name = '__noname'
        self.texture = read_string(file)

        # Unknown string fields, always have value 'none'
        read_string(file)
        read_string(file)
        read_string(file)
        read_string(file)

        # Other material settings in unknown format
        read_struct('120s', file)

    def __str__(self):
        string = 'MeshMaterial: name = {}, texture = {}'
        return string.format(self.name, self.texture)


# ------------------------------------------------------------------------------
# Fragments
# ------------------------------------------------------------------------------
class SFVertexFormat:
    def __init__(self, flags):
        self.packed = bool(flags & (1 << 0)) # Has position packing
        self.bones = bool(flags & (1 << 1))  # Has bone indices
        self.bump = bool(flags & (1 << 2))   # Has binormal and tangent vectors
        self.color = bool(flags & (1 << 3))  # Has vertex colors
        self.uv2 = bool(flags & (1 << 4))    # Has second set of UV coordinates

    def __str__(self):
        string = 'SFVertexFormat:\n'
        string += '\tPos packing   = {}\n'.format(self.packed)
        string += '\tBone indices  = {}\n'.format(self.bones)
        string += '\tS/T vectors   = {}\n'.format(self.bump)
        string += '\tVertex colors = {}\n'.format(self.color)
        string += '\tSet of UVs    = {}'.format(self.uv2)
        return string


class SFMeshFragment:
    def __init__(self, file, mesh_fmt):
        vertex_fmt_raw = read_struct('I', file)
        self.vertex_format = SFVertexFormat(vertex_fmt_raw)

        self.mat_id = read_struct('i', file)
        self.facees_offset = read_struct('i', file) // 3
        self.facees_length = read_struct('i', file) // 3

        if mesh_fmt.v_num >= v_num(4, 6):
            self.vertex_offset = read_struct('i', file)
        else:
            self.vertex_offset = 0

        if mesh_fmt.skinned:
            self.vertex_bones = read_struct('i', file)
            self.bone_remap = read_struct('16B', file)
        else:
            self.vertex_bones = 0
            self.bone_remap = ()

    def __str__(self):
        string = 'MeshFragment:\n'
        string += '\tMaterial ID      = {}\n'.format(self.mat_id)
        string += '\tFaces offset     = {}\n'.format(self.facees_offset)
        string += '\tFaces length     = {}\n'.format(self.facees_length)
        string += '\tVertex offset    = {}\n'.format(self.vertex_offset)
        string += '\tBones per vertex = {}\n'.format(self.vertex_bones)
        string += '\tBone remap: {}'.format(self.bone_remap)
        return string


# ------------------------------------------------------------------------------
# Vertices
# ------------------------------------------------------------------------------
class SFVertex:
    def __init__(self, file, vertex_fmt, mesh_fmt):
        # Read position
        pos_x, pos_y, pos_z = 0, 0, 0
        if vertex_fmt.packed:
            pos_x, pos_y, pos_z, scale = read_struct('4h', file)
            if vertex_fmt.bones:
                pos_x = pos_x / scale
                pos_y = pos_y / scale
                pos_z = pos_z / scale
            else:
                pos_x = (pos_x - 0.5) * 2.0 / mesh_fmt.scale - 1.0
                pos_y = (pos_y - 0.5) * 2.0 / mesh_fmt.scale - 1.0
                pos_z = (pos_z - 0.5) * 2.0 / mesh_fmt.scale - 1.0
        else:
            pos_x, pos_y, pos_z = read_struct('fff', file)

        self.pos = (pos_x, pos_y, pos_z)

        # Read normal
        self.normal = read_packed_vector(True, file)

        # Binormal and tangent vectors
        if vertex_fmt.bump:
            self.bump_s = read_packed_vector(False, file)
            self.bump_t = read_packed_vector(False, file)

        # Texture coordinates
        tex_u = read_struct('h', file) / 2048.0
        tex_v = 1.0 - (read_struct('h', file) / 2048.0)
        self.tex_uv = (tex_u, tex_v)
        if vertex_fmt.uv2:
            read_struct('i', file)

        # Bones
        if vertex_fmt.bones:
            self.bones = read_struct('4B', file)
            weights = read_struct('4B', file)
            self.weights = (
                weights[0] / 255,
                weights[1] / 255,
                weights[2] / 255,
                weights[3] / 255
            )
        else:
            self.bones = ()
            self.weights = ()

        if vertex_fmt.color:
            read_struct('I', file)

    def __str__(self):
        string = 'Vertex: p = {}; uv = {}; n = {}'
        return string.format(self.pos, self.tex_uv, self.normal)


# ------------------------------------------------------------------------------
# Faces
# ------------------------------------------------------------------------------
class SFMeshFace:
    def __init__(self, file):
        self.ids = read_struct('hhh', file)

    def get_mapped_indices(self, id_map):
        vertex_id1 = id_map.index(self.ids[0])
        vertex_id2 = id_map.index(self.ids[1])
        vertex_id3 = id_map.index(self.ids[2])
        return (vertex_id1, vertex_id2, vertex_id3)

    def __str__(self):
        string = 'MeshFace: {}'
        return string.format(self.ids)


# ------------------------------------------------------------------------------
# SkyFallen 3D Geometry
# ------------------------------------------------------------------------------
class SFBone:
    def __init__(self, bone_id,  file):
        self.id = bone_id

        self.name = read_string(file)
        self.parent_id = read_struct('i', file)

        self.pos_start = read_vector(file)
        self.pos_end = read_vector(file)

        self.bs_pos = read_vector(file)
        self.bs_range = read_struct('f', file)

        flags = read_struct('i', file)
        self.collision = bool(flags & (1 << 0))

        # Bone transform
        self.matrix = read_matrix4(file)

    def __str__(self):
        string = 'Bone:\n'
        string += '\tName: \'{}\'\n'.format(self.name)
        string += '\tParent ID: {}\n'.format(self.parent_id)
        string += '\tStart: {}\n'.format(self.pos_start)
        string += '\tEnd: {}\n'.format(self.pos_end)
        string += '\tBounding Sphere center: {}\n'.format(self.bs_pos)
        string += '\tBounding Sphere range: {}\n'.format(self.bs_range)
        string += '\tCollisions: {}\n'.format(self.collision)
        return string



# ------------------------------------------------------------------------------
# SkyFallen 3D Geometry
# ------------------------------------------------------------------------------
class SFGeometry:
    def __init__(self, file):
        self.version = SFExportMeshVersion(file)

        self.mesh_format = SFMeshFormat(file, self.version.v_num)
        if self.mesh_format.tiled or self.mesh_format.stripped:
            raise Exception('Mesh format is not supproted')

        # Bones
        self.bones = []
        if self.mesh_format.skinned:
            bone_count = read_header('Skeleton2', file)
            for bone_id in range(bone_count):
                bone = SFBone(bone_id, file)
                self.bones.append(bone)

        # Materials
        material_count = read_header('MeshMaterials', file)
        self.materials = []
        for _ in range(material_count):
            self.materials.append(SFMaterial(file))

        # Fragments
        self.fragments = []
        frg_count = 0
        if self.mesh_format.skinned:
            frg_count = read_header('MeshFragmentsSkinned', file)
        else:
            frg_count = read_header('MeshFragmentsStatic', file)

        for _ in range(frg_count):
            fragment = SFMeshFragment(file, self.mesh_format)
            self.fragments.append(fragment)

        # Vertices
        self.vertex_format = self.fragments[0].vertex_format
        self.vertices = []
        vtx_count = 0
        if self.mesh_format.skinned:
            vtx_count = read_header('MeshVerticesSkinned', file)
        else:
            vtx_count = read_header('MeshVerticesStatic', file)

        for _ in range(vtx_count):
            vertex = SFVertex(file, self.vertex_format, self.mesh_format)
            self.vertices.append(vertex)

        # Faces
        index_count = read_header('MeshIndices', file)
        self.faces = []
        for _ in range(index_count // 3):
            face = SFMeshFace(file)
            self.faces.append(face)

    def get_indices(self, offset, length):
        uniq = []
        for i in range(offset, offset + length):
            for indice in self.faces[i].ids:
                if indice not in uniq:
                    uniq.append(indice)
        return uniq
