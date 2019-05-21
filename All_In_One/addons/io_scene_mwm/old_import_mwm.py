import struct
import bpy


class VertexData(object):

    def __init__(self, positions, normals, uv_coords, binormals, tangents, tex_coords):
        self.positions = positions
        self.normals = normals
        self.uv_coords = uv_coords
        self.binormals = binormals
        self.tangents = tangents
        self.tex_coords = tex_coords


class Dummy(object):

    def __init__(self, name, matrix, params):
        self.name = name
        self.matrix = matrix
        self.params = params


class BoundingBox(object):

    def __init__(self, min, max):
        self.min = min
        self.max = max


class BoundingSphere(object):

    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class ModelPart(object):

    def __init__(self, faces, material):
        self.faces = faces
        self.material = material


class Material(object):

    def __init__(self, name, params, glossiness, diffuse_color, specular_color, technique):
        self.name = name
        self.params = params
        self.glossiness = glossiness
        self.diffuse_color = diffuse_color
        self.specular_color = specular_color
        self.technique = technique


def load(operator, context):

     file = open(operator.filepath, "rb")

     # reading the headder
     section = read_string(file)
     flag = read_long(file)
     version = read_string(file)

     dummies = load_dummies(file)
     vertex_data = load_vertext_data(file)
     model_params = load_model_params(file)
     model_parts = load_model_parts(file)

     file.close()

     for i in range(len(model_parts)):

          profile_mesh = bpy.data.meshes.new("Base_Profile_Data")
          profile_mesh.from_pydata(vertex_data.positions, [], model_parts[i].faces)

          profile_mesh.update()

          profile_object = bpy.data.objects.new("Base_Profile", profile_mesh)
          profile_object.data = profile_mesh

          scene = context.scene
          scene.objects.link(profile_object)
          profile_object.select = True

     return {'FINISHED'}


def load_model_params(file):

    params = {}

    # RescaleToLengthInMeters param
    key = read_string(file)
    value = read_bool(file)
    params[key] = value

    # LengthInMeters param
    key = read_string(file)
    value = read_float(file)
    params[key] = value

    # RescaleFactor param
    key = read_string(file)
    value = read_float(file)
    params[key] = value

    # Centered param
    key = read_string(file)
    value = read_bool(file)
    params[key] = value

    # UseChannelTextures param
    key = read_string(file)
    value = read_bool(file)
    params[key] = value

    # SpecularShininess param
    key = read_string(file)
    value = read_float(file)
    params[key] = value

    # SpecularPower param
    key = read_string(file)
    value = read_float(file)
    params[key] = value

    # BoundingBox param
    key = read_string(file)

    x = read_float(file)
    y = read_float(file)
    z = read_float(file)
    min = (x, y, z)

    x = read_float(file)
    y = read_float(file)
    z = read_float(file)
    max = (x, y, z)

    value = BoundingBox(min, max)
    params[key] = value

    # BounginSphere param
    key = read_string(file)

    x = read_float(file)
    y = read_float(file)
    z = read_float(file)
    pos = (x, y, z)
    radius = read_float(file)

    value = BoundingSphere(pos, radius)
    params[key] = value

    # SwapWindingOrder param
    key = read_string(file)
    value = read_bool(file)
    params[key] = value

    return params


def load_vertext_data(file):

    positions = load_positions(file)
    normals = load_normals(file)
    uv_coords = load_uv_coords(file)
    binormals = load_binormals(file)
    tangents = load_tangents(file)
    tex_coords = load_text_coord(file)

    return VertexData(positions, normals, uv_coords, binormals, tangents, tex_coords)


def load_model_parts(file):

    section = read_string(file)
    nParts = read_long(file)

    parts = []
    for i in range(nParts):
        part = load_part(file)
        parts.append(part)

    return parts


def load_part(file):

    file.read(4) # 4 bytes, Don't know what they do
    count = read_long(file)
    face_count = int(count / 3)

    faces = []
    for i in range(face_count):
        x = read_long(file)
        y = read_long(file)
        z = read_long(file)
        faces.append((x, y, z))

    hasMaterial = read_bool(file)
    material = None
    if (hasMaterial):
        material = load_material(file)

    return ModelPart(faces, material)


def load_material(file):

    name = read_string(file)
    nParams = read_long(file)

    params = {}
    for i in range(nParams):
        key = read_string(file)
        value = read_string(file)
        params[key] = value

    glossiness = read_float(file)

    x = read_float(file)
    y = read_float(file)
    z = read_float(file)
    diffuse_color = (x, y, z)

    x = read_float(file)
    y = read_float(file)
    z = read_float(file)
    specular_color = (x, y, z)

    technique = read_string(file)

    return Material(name, params, glossiness, diffuse_color, specular_color, technique)


def load_tangents(file):

    section = read_string(file)
    nTang = read_long(file)

    tangents = []
    for i in range(nTang):
        file.read(4)

    return tangents


def load_text_coord(file):

    section = read_string(file)
    nTextCoord = read_long(file)

    for i in range(nTextCoord):
        file.read(4)


def load_binormals(file):

    section = read_string(file)
    nBinormals = read_long(file)

    binormals = []
    for i in range(nBinormals):
        file.read(4) # 4 bytes of data, Don;t know what type

    return binormals


def load_uv_coords(file):

    section = read_string(file)
    nUvs = read_long(file)

    uv_coords = []
    for i in range(nUvs):
        u = read_hfloat(file)
        v = read_hfloat(file)
        uv_coords.append((u , v))

    return uv_coords


def load_normals(file):

    section = read_string(file)
    nNormals = read_long(file)

    normals = []
    for i in range(nNormals):
        file.read(4) # 4 bytes of data, Don't know what type

    return normals


def load_positions(file):

    section = read_string(file)
    nPositions = read_long(file)

    positions = []
    for i in range(nPositions):
        x = read_hfloat(file)
        y = read_hfloat(file)
        z = read_hfloat(file)
        w = read_hfloat(file)

        positions.append((x, y, z))

    return positions


def load_dummies(file):

    section = read_string(file)
    nDummies = read_long(file)

    dummies = []
    for i in range(nDummies):
        dummy = load_dummy(file)
        dummies.append(dummy)

    return dummies


def load_dummy(file):

    name = read_string(file)
    matrix = load_matrix(file)

    nParams = read_long(file)

    params = {}
    for i in range(nParams):
        key = read_string(file)
        value = read_string(file)
        params[key] = value

    return Dummy(name, matrix, params)


def load_matrix(file):

    mat = [[0 for x in range(4)] for x in range(4)]

    mat[0][0] = read_float(file)
    mat[0][1] = read_float(file)
    mat[0][2] = read_float(file)
    mat[0][3] = read_float(file)

    mat[1][0] = read_float(file)
    mat[1][1] = read_float(file)
    mat[1][2] = read_float(file)
    mat[1][3] = read_float(file)

    mat[2][0] = read_float(file)
    mat[2][1] = read_float(file)
    mat[2][2] = read_float(file)
    mat[2][3] = read_float(file)

    mat[3][0] = read_float(file)
    mat[3][1] = read_float(file)
    mat[3][2] = read_float(file)
    mat[3][3] = read_float(file)

    return mat


def read_string(file):

    byte = file.read(1)
    nChars = int.from_bytes(byte, "little")
    chars = []

    for i in range(nChars):
        byte = file.read(1)
        chars.append(chr(int.from_bytes(byte, "little")))

    return "".join(chars)


def read_hfloat(file):

    bytes = file.read(2)
    f16 = struct.unpack('h', bytes)[0]
    return f16_to_f32(f16)


def f16_to_f32(float16):

    s = int((float16 >> 15) & 0b1)    # sign
    e = int((float16 >> 10) & 0x0000001f)    # exponent
    f = int(float16 & 0x000003ff)            # fraction

    if e == 0 and f != 0:

        while not (f & 0x00000400):
            f = f << 1
            e -= 1
        e += 1
        f &= ~0x00000400

    if (not (e == 0 and f == 0)) and e != 31:

        e = e + (127 -15)
        e = e << 23

    elif (e == 31):

        e = 0x7f800000

    if not ((e == 0 or e == 31) and f == 0) :
        f = f << 13

    s = (s << 31)

    int_var = int( s | e | f )
    float_var = struct.unpack('f', struct.pack('I', int_var))[0]

    return float_var


def read_long(file):

    result = struct.unpack('l', file.read(4))
    return result[0]


def read_float(file):
    bytes = file.read(4)
    value = struct.unpack('f', bytes)[0]
    return value


def read_bool(file):
    byte = file.read(1)
    return struct.unpack('?', byte)[0]