#!/usr/bin/env python
from . import byte_functions as read
from . import mwm_datatypes as mwm
import time


def load_mesh_sections(index_dict, file):
    params = {}

    # RescaleToLengthInMeters param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    # LengthInMeters param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # RescaleFactor param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # Centered param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    # UseChannelTextures param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    # SpecularShininess param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # SpecularPower param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # BoundingBox param
    key = read.read_string(file)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    min = (x, y, z)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    max = (x, y, z)

    value = mwm.BoundingBox(min, max)
    params[key] = value

    # BoungingSphere param
    key = read.read_string(file)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    pos = (x, y, z)
    radius = read.read_float(file)

    value = mwm.BoundingSphere(pos, radius)
    params[key] = value

    # SwapWindingOrder param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    return params


def load_mesh_data(index_dict, file):
    vertices = load_vertices(index_dict, file)
    normals = load_normals(index_dict, file)
    uv_coords = load_uv_coords(index_dict, file)
    binormals = load_binormals(index_dict, file)
    tangents = load_tangents(index_dict, file)
    tex_coords = load_text_coord(index_dict, file)

    return mwm.VertexData(vertices, normals, uv_coords, binormals, tangents, tex_coords)


# Check for class "MyMeshPartInfo" in SE Code, should be in
# Sources/VRage.Render/Import/MyImportUtils.cs
def load_mesh_parts(index_dict, file, version):
    section = read.read_string(file)
    nParts = read.read_long(file)

    parts = []
    for i in range(nParts):
        part = load_part(file, version)
        parts.append(part)

    return parts


def load_part(file, version):
    m_MaterialHash = read.read_long(file)

    if version < 1052001:
        print("Older part version detected")
        draw_technique = read.read_long(file)

    count = read.read_long(file)
    print("Count is %s" % count)
    face_count = int(count / 3)
    print("Got %s faces." % face_count)

    faces = []
    for i in range(face_count):
        try:
            x = read.read_long(file)
            y = read.read_long(file)
            z = read.read_long(file)
            faces.append((x, y, z))
        except:
            print("%s / %s" % (i, face_count))
            exit(1)


    hasMaterial = read.read_bool(file)
    material = None
    if (hasMaterial):
        material = load_material(file)

    return mwm.MeshPart(faces, material)


def load_material(file):
    name = read.read_string(file)
    nParams = read.read_long(file)

    params = {}
    for i in range(nParams):
        key = read.read_string(file)
        value = read.read_string(file)
        params[key] = value

    glossiness = read.read_float(file)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    diffuse_color = (x, y, z)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    specular_color = (x, y, z)

    technique = read.read_string(file)

    return mwm.Material(name, params, glossiness, diffuse_color, specular_color, technique)


def load_tangents(index_dict, file):
    seek_loc = index_dict['Tangents']
    file.seek(seek_loc)

    section = read.read_string(file)
    nTang = read.read_long(file)

    tangents = []
    for i in range(nTang):
        file.read(4)

    return tangents


def load_text_coord(index_dict, file):
    seek_loc = index_dict['TexCoords1']
    file.seek(seek_loc)
    section = read.read_string(file)
    nTextCoord = read.read_long(file)

    for i in range(nTextCoord):
        file.read(4)

    return None


def load_binormals(index_dict, file):
    seek_loc = index_dict['Binormals']
    file.seek(seek_loc)
    section = read.read_string(file)
    nBinormals = read.read_long(file)

    binormals = []
    for i in range(nBinormals):
        file.read(4)  # 4 bytes of data, Don;t know what type

    return binormals


def load_uv_coords(index_dict, file):
    seek_loc = index_dict['TexCoords0']
    file.seek(seek_loc)
    section = read.read_string(file)
    nUvs = read.read_long(file)

    uv_coords = []
    for i in range(nUvs):
        u = read.read_hfloat(file)
        v = read.read_hfloat(file)
        uv_coords.append((u, v))

    return uv_coords


def load_normals(index_dict, file):
    seek_loc = index_dict['Normals']
    file.seek(seek_loc)

    section = read.read_string(file)
    nNormals = read.read_long(file)

    normals = []
    for i in range(nNormals):
        file.read(4)  # 4 bytes of data, Don't know what type

    return normals


def load_vertices(index_dict, file):
    seek_loc = index_dict['Vertices']
    file.seek(seek_loc)

    section = read.read_string(file)
    nPositions = read.read_long(file)

    positions = []
    for i in range(nPositions):
        x = read.read_hfloat(file)
        y = read.read_hfloat(file)
        z = read.read_hfloat(file)
        w = read.read_hfloat(file)

        positions.append((x, y, z))

    return positions


def load_dummies(file):
    section = read.read_string(file)
    nDummies = read.read_long(file)

    dummies = []
    for i in range(nDummies):
        dummy = load_dummy(file)
        dummies.append(dummy)

    return dummies


def load_dummy(file):
    name = read.read_string(file)
    matrix = load_matrix(file)

    nParams = read.read_long(file)

    params = {}
    for i in range(nParams):
        key = read.read_string(file)
        value = read.read_string(file)
        params[key] = value

    return mwm.Dummy(name, matrix, params)


def load_matrix(file):
    mat = [[0 for x in range(4)] for x in range(4)]

    mat[0][0] = read.read_float(file)
    mat[0][1] = read.read_float(file)
    mat[0][2] = read.read_float(file)
    mat[0][3] = read.read_float(file)

    mat[1][0] = read.read_float(file)
    mat[1][1] = read.read_float(file)
    mat[1][2] = read.read_float(file)
    mat[1][3] = read.read_float(file)

    mat[2][0] = read.read_float(file)
    mat[2][1] = read.read_float(file)
    mat[2][2] = read.read_float(file)
    mat[2][3] = read.read_float(file)

    mat[3][0] = read.read_float(file)
    mat[3][1] = read.read_float(file)
    mat[3][2] = read.read_float(file)
    mat[3][3] = read.read_float(file)

    return mat


def load_mwm_header(file):
    # reading the headder
    section = read.read_string(file)
    print("Section: %s" % section)
    flag = read.read_long(file)
    print("Flag: %s" % flag)
    version = read.read_string(file)
    if version[:8] != "Version:":
        time.sleep(0.25)
        err_msg = "Uht-oh.  Version string did not parse.\n" \
                  "Expected value to start with Version: instead got:\n%s" \
                  % version
        raise ValueError(err_msg)
    version_number = int(version[8:])
    return version_number


def load_index(file):
    total_items = read.read_long(file)
    item_dictionary = dict()
    item_count = 0
    print("Item count: %s" % total_items)
    while item_count < total_items:
        tagName = read.read_string(file)
        index = read.read_long(file)
        item_dictionary[tagName] = index
        item_count += 1

    return item_dictionary

