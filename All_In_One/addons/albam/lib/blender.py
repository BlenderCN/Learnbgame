from collections import deque, namedtuple
import os


def get_bounding_box(blender_object):
    bounding_box = namedtuple('bounding_box', ('min_x', 'min_y', 'min_z', 'min_w',
                                               'max_x', 'max_y', 'max_z', 'max_w',
                                               'width',
                                               'height',
                                               'length'))

    x = {b[0] for b in blender_object.bound_box}
    y = {b[1] for b in blender_object.bound_box}
    z = {b[2] for b in blender_object.bound_box}

    min_x = min(x)
    min_y = min(y)
    min_z = min(z)

    max_x = max(x)
    max_y = max(y)
    max_z = max(z)

    width = abs(min_x) + abs(max_x)
    height = abs(min_y) + abs(max_y)
    length = abs(min_z) + abs(max_z)

    return bounding_box(min_x, min_y, min_z, 0.0,
                        max_x, max_y, max_z, 0.0,
                        width,
                        height,
                        length)


def strip_triangles_to_triangles_list(strip_indices_array):
    indices = []
    offset = min(strip_indices_array)

    for i in range(2, len(strip_indices_array)):
        a = strip_indices_array[i - 2]
        b = strip_indices_array[i - 1]
        c = strip_indices_array[i]
        if a != b and a != c and b != c:
            if i % 2 == 0:
                indices.extend((a - offset, b - offset, c - offset))
            else:
                indices.extend((c - offset, b - offset, a - offset))
    if not indices:
        return list(strip_indices_array)
    return indices


def triangles_list_to_triangles_strip(blender_mesh):
    """
    Export triangle strips from a blender mesh.
    It assumes the mesh is all triangulated.
    Based on a paper by Pierre Terdiman: http://www.codercorner.com/Strips.htm
    """
    # TODO: Fix changing of face orientation in some cases (see tests)
    edges_faces = {}
    current_strip = []
    strips = []
    joined_strips = []
    faces_indices = deque(p.index for p in blender_mesh.polygons)
    done_faces_indices = set()
    current_face_index = faces_indices.popleft()
    process_faces = True

    for polygon in blender_mesh.polygons:
        for edge in polygon.edge_keys:
            edges_faces.setdefault(edge, set()).add(polygon.index)

    while process_faces:
        current_face = blender_mesh.polygons[current_face_index]
        current_face_verts = current_face.vertices[:]
        strip_indices = [v for v in current_face_verts if v not in current_strip[-2:]]
        if current_strip:
            face_to_add = tuple(current_strip[-2:]) + tuple(strip_indices)
            if face_to_add != current_face_verts and face_to_add != tuple(reversed(current_face_verts)):
                # we arrived here because the current face shares and edge with the face in the strip
                # however, if we just add the verts, we would be changing the direction of the face
                # so we create a degenerate triangle before adding to it to the strip
                current_strip.append(current_strip[-2])
        current_strip.extend(strip_indices)
        done_faces_indices.add(current_face_index)

        next_face_index = None
        possible_face_indices = {}
        for edge in current_face.edge_keys:
            if edge not in edges_faces:
                continue
            checked_edge = {face_index: edge for face_index in edges_faces[edge]
                            if face_index != current_face_index and face_index not in done_faces_indices}
            possible_face_indices.update(checked_edge)
        for face_index, edge in possible_face_indices.items():
            if not current_strip:
                next_face_index = face_index
                break
            elif edge == tuple(current_strip[-2:]) or edge == tuple(reversed(current_strip[-2:])):
                next_face_index = face_index
                break
            elif edge == (current_strip[-1], current_strip[-2]):
                if len(current_strip) % 2 != 0:
                    # create a degenerate triangle to join them
                    current_strip.append(current_strip[-2])
                next_face_index = face_index

        if next_face_index:
            faces_indices.remove(next_face_index)
            current_face_index = next_face_index
        else:
            strips.append(current_strip)
            current_strip = []
            try:
                current_face_index = faces_indices.popleft()
            except IndexError:
                process_faces = False

    prev_strip_len = 0
    # join strips with degenerate triangles
    for strip in strips:
        if not prev_strip_len:
            joined_strips.extend(strip)
            prev_strip_len = len(strip)
        elif prev_strip_len % 2 == 0:
            joined_strips.extend((joined_strips[-1], strip[0]))
            joined_strips.extend(strip)
            prev_strip_len = len(strip)
        else:
            joined_strips.extend((joined_strips[-1], strip[0], strip[0]))
            joined_strips.extend(strip)
            prev_strip_len = len(strip)

    return joined_strips


def create_mesh_name(mesh, index, file_path):
    return '{}_{}_LOD_{}'.format(os.path.basename(file_path),
                                 str(index).zfill(4),
                                 mesh.level_of_detail)


def get_textures_from_blender_objects(blender_objects):
    """
    Only counting the first material of the mesh
    """
    textures = set()
    meshes = {ob.data for ob in blender_objects if ob.type == 'MESH'}
    for ob in meshes:
        if not ob.materials:
            continue
        for ts in ob.materials[0].texture_slots:
            if ts and ts.texture and ts.texture.image:
                textures.add(ts.texture)
    return sorted(textures, key=lambda t: t.name)


def get_materials_from_blender_objects(blender_objects):
    """
    Only counting the first material of the mesh
    """
    materials = set()
    meshes = {ob.data for ob in blender_objects if ob.type == 'MESH'}
    for ob in meshes:
        if not ob.materials:
            continue
        materials.add(ob.materials[0])
    return sorted(materials, key=lambda m: m.name)


def get_vertex_count_from_blender_objects(blender_objects):
    return sum([len(ob.data.vertices) for ob in blender_objects if ob.type == 'MESH'])


def get_bone_indices_and_weights_per_vertex(blender_object):
    """
    Return {vertex_index: [(bone_index, weight_value), ...]}
    """
    vertex_groups = blender_object.vertex_groups
    modifiers = {m.type: m for m in blender_object.modifiers}
    weights_per_vertex = {}
    if blender_object.type != 'MESH':
        raise TypeError('Blender object is not a mesh')
    if not vertex_groups or 'ARMATURE' not in modifiers:
        return weights_per_vertex
    armature = modifiers['ARMATURE'].object.data
    bone_names_to_index = {b.name: i for i, b in enumerate(armature.bones)}
    # https://www.blender.org/api/blender_python_api_current/bpy.types.VertexGroupElement.html
    vertex_groups = blender_object.vertex_groups
    for vertex in blender_object.data.vertices:
        for group in vertex.groups:
            weights_per_vertex.setdefault(vertex.index, [])
            if not group.weight:
                continue
            # avoiding list comprehensions for readability
            # bones in blender are matched to vertex group only by name
            vgroup_name = vertex_groups[group.group].name
            bone_index = bone_names_to_index[vgroup_name]
            pair = (bone_index, group.weight)
            weights_per_vertex[vertex.index].append(pair)
    return weights_per_vertex


def get_uvs_per_vertex(blender_mesh_object):
    vertices = {}  # vertex_index: (uv_x, uv_y)
    try:
        uv_layer = blender_mesh_object.data.uv_layers[0]
    except IndexError:
        return vertices
    uvs_per_loop = uv_layer.data
    for i, loop in enumerate(blender_mesh_object.data.loops):
        vertex_index = loop.vertex_index
        if vertex_index in vertices:
            continue
        else:
            uvs = uvs_per_loop[i].uv
            vertices[vertex_index] = (uvs[0], uvs[1])
    return vertices
