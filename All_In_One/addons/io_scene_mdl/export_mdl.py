import bpy
import bmesh
from mathutils import Matrix, Vector

from .quake import mdl


def save(operator, context, filepath):
    mdl_file = mdl.Mdl.open(filepath, 'w')

    ob = bpy.context.active_object
    world_matrix = ob.matrix_world

    bm = bmesh.new()
    bm.from_mesh(ob.to_mesh(bpy.context.scene, True, 'PREVIEW'))
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.verts.ensure_lookup_table()

    # Apply transform
    for vert in bm.verts:
        vert.co = world_matrix * vert.co

    # Create skins
    im = ob.data.materials[0].texture_slots[0].texture.image
    width, height = im.size[:]
    pixels = im.pixels

    p = []

    for i in range(0, len(pixels), 4):
        r = int(pixels[i+0] * 255 + 0.5)
        g = int(pixels[i+1] * 255 + 0.5)
        b = int(pixels[i+2] * 255 + 0.5)

        index = nearest((r, g, b))
        p.append(index)

    # TODO: Actually export image data
    skin = mdl.Skin()
    mdl_file.skin_width = width
    mdl_file.skin_height = height
    skin.pixels = p
    mdl_file.skins.append(skin)
    mdl_file.number_of_skins = 1

    # Calculate bounds
    min_coord = bm.verts[0].co[:]
    max_coord = min_coord

    for vert in bm.verts:
        min_coord = map(lambda x: min(x[0], x[1]), zip(min_coord, vert.co[:]))
        max_coord = map(lambda x: max(x[0], x[1]), zip(max_coord, vert.co[:]))

    min_coord = list(min_coord)
    max_coord = list(max_coord)

    # Transform to 0, 0, 0 -> 255, 255, 255 local space
    size = (Vector(max_coord) - Vector(min_coord))[:]

    translation_matrix = Matrix()
    translation_matrix[0][3] = -min_coord[0]
    translation_matrix[1][3] = -min_coord[1]
    translation_matrix[2][3] = -min_coord[2]

    scale_matrix = Matrix()
    scale_matrix[0][0] = 255.0 / size[0]
    scale_matrix[1][1] = 255.0 / size[1]
    scale_matrix[2][2] = 255.0 / size[2]

    xform = scale_matrix * translation_matrix

    for vert in bm.verts:
        vert.co = xform * vert.co

    mdl_file.scale = size[0] / 255.0, size[1] / 255.0, size[2] / 255.0
    mdl_file.origin = min_coord

    # Create a frame
    frame = mdl.Frame()
    frame.name = 'frame0'

    # TODO: Fix the bounding box
    bbox_min = mdl.TriVertex()
    bbox_min[:] = 0, 0, 0
    bbox_min.light_normal_index = 0
    bbox_max = mdl.TriVertex()
    bbox_max[:] = 255, 255, 255
    bbox_max.light_normal_index = 0

    frame.bounding_box_min = bbox_min
    frame.bounding_box_max = bbox_max
    mdl_file.frames.append(frame)
    mdl_file.number_of_frames = 1

    # Determine the unique set of vertex and uv pairs
    uv_layer = bm.loops.layers.uv[0]

    vertex_uv_pairs = []
    for face in bm.faces:
        vertex_coords = [v.co[:] for v in face.verts[:]]
        uv_coords = [l[uv_layer].uv[:] for l in face.loops]
        pairs = zip(vertex_coords, uv_coords)
        vertex_uv_pairs.extend(pairs)

    vertex_uv_pairs = list(set(vertex_uv_pairs))

    # Create Vertices and UVs
    for vertex, uv in vertex_uv_pairs:
        mdl_vertex = mdl.TriVertex()
        mdl_vertex[:] = int(vertex[0]), int(vertex[1]), int(vertex[2])
        # TODO: Fix the normal calculation
        mdl_vertex.light_normal_index = 0

        st_vertex = mdl.StVertex()
        u = int(uv[0] * mdl_file.skin_width)
        v = int(uv[1] * mdl_file.skin_height)
        st_vertex[:] = u, v

        mdl_file.frames[0].vertices.append(mdl_vertex)
        mdl_file.st_vertices.append(st_vertex)

    mdl_file.number_of_vertices = len(mdl_file.frames[0].vertices)

    # Create triangles
    for face in bm.faces:
        vertex_indices = []
        for i in [0, 1, 2]:
            v = face.verts[i].co[:]
            u = face.loops[i][uv_layer].uv[:]

            index = vertex_uv_pairs.index((v, u))
            vertex_indices.append(index)

        triangle = mdl.Triangle()
        triangle.vertices = list(reversed(vertex_indices))
        mdl_file.triangles.append(triangle)

    mdl_file.number_of_triangles = len(mdl_file.triangles)

    bm.free()
    mdl_file.close()
    return {'FINISHED'}


def dot(lhs, rhs):
    return lhs[0] * rhs[0] + lhs[1] * rhs[1] + lhs[2] * rhs[2]


def sub(lhs, rhs):
    return lhs[0] - rhs[0], lhs[1] - rhs[1], lhs[2] - rhs[2]


def sqr_length(vec):
    return dot(vec, vec)

_color_map = {}


def nearest(v):
    if v in _color_map:
        return _color_map[v]

    nearest_dist = 999999
    nearest_index = -1

    for i, c in enumerate(mdl.default_palette):
        dist = sqr_length(sub(c, v))

        if dist < nearest_dist:
            nearest_dist = dist
            nearest_index = i

        if dist == 0:
            break

    _color_map[v] = nearest_index
    return nearest_index
