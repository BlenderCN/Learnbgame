from functools import reduce
from operator import add
from mathutils import Vector, Matrix
import math


def get_loop(edges, vert=None):
    if vert is None:
        edge = edges[0]
        edges.remove(edge)
        success_0, is_boundary_0, verts_0, edges_0 = get_loop(edges, edge.verts[0])
        success_1, is_boundary_1, verts_1, edges_1 = get_loop(edges, edge.verts[1])
        if len(verts_0) > 0:
            edges_0.reverse()
            verts_0.reverse()
            verts_0 = verts_0 + [v for v in edge.verts if v not in verts_0]
        if len(verts_1) > 0:
            if len(verts_0) == 0:
                verts_1 = verts_1 + [v for v in edge.verts if v not in verts_1]
        is_boundary = is_boundary_0 and is_boundary_1
        success = success_0 and success_1
        if edge.is_boundary:
            is_boundary = True
        return success, is_boundary, verts_0 + verts_1, edges_0 + [edge] + edges_1

    link_edges = [e for e in vert.link_edges if e in edges]

    if len(link_edges) == 1:
        edge = link_edges[0]
        vert, = set(edge.verts) - {vert}
        edges.remove(edge)
        success, is_boundary, verts_, edges_ = get_loop(edges, vert)
        if edge.is_boundary:
            is_boundary = True
        return success, is_boundary, [vert] + verts_, [edge] + edges_

    elif len(link_edges) > 1:
        for edge in link_edges:
            edges.remove(edge)
        return False, False, [], []

    return True, False, [], []


def get_loops(edges, faces=None):
    edges = edges[:]
    loops = []

    if faces:
        for group in get_boundary_edges(faces[:]):
            success, is_boundary, loop_verts, loop_edges = get_loop(group[0])
            is_cyclic = any((v for v in loop_edges[0].verts if v in loop_edges[-1].verts))
            loops.append(((loop_verts, loop_edges, group[1]), is_cyclic, is_boundary))

        for face in faces:
            for face_edge in face.edges:
                if face_edge.select and face_edge in edges:
                    edges.remove(face_edge)

    while len(edges) > 0:
        success, is_boundary, loop_verts, loop_edges = get_loop(edges)
        if success:
            if len(loop_verts) < 2:
                is_cyclic = False
            else:
                is_cyclic = any((v for v in loop_edges[0].verts if v in loop_edges[-1].verts))
            loops.append(((loop_verts, loop_edges, []), is_cyclic, is_boundary))

    return loops


def is_clockwise(forward, center, verts):
    return forward.dot((verts[0].co - center).cross(verts[1].co - center)) > 0


def get_parallel_edges(edges, verts, perpendicular=False):
    """
    Return parallel (or perpendicular) edges from given sorted edges and vertices
    :param edges: Sorted edges
    :param verts: Sorted vertices
    :param perpendicular: If True return perpendicular edges
    :return: tuple of loop edges, first smaller, second bigger
    """
    sides = ([], [])
    side_verts = []
    sides_faces = []
    len_a = 0
    len_b = 0

    parallels = []
    lost = []

    for vert in verts:
        for face in vert.link_faces:
            if face in sides_faces:
                continue
            sides_faces.append(face)
            for edge in face.edges:
                if edge not in parallels:
                    parallels.append(edge)
                    test = len([v for v in edge.verts if v not in verts])
                    if test == 2:
                        if not sides[0] or any((v for v in edge.verts if v in side_verts)):
                            sides[0].append(edge)
                            side_verts.extend(edge.verts[:])
                            len_a += edge.calc_length()
                        else:
                            lost.append(edge)
    processed = []
    while True:
        counter = 0
        for edge in lost:
            if edge not in processed and any((v for v in edge.verts if v in side_verts)):
                sides[0].append(edge)
                side_verts.extend(edge.verts[:])
                len_a += edge.calc_length()
                counter += 1
                processed.append(edge)
        if counter == 0:
            break

    for edge in lost:
        if edge not in processed:
            sides[1].append(edge)
            len_b += edge.calc_length()

    return sides if len_a <= len_b else (sides[1], sides[0])


def get_inner_faces(edges, verts, limit_edges):
    """
    Return inner faces from loop
    :param edges: Sorted edges
    :param verts: Sorted vertices
    :return: Inner loop-faces
    """
    def search_faces(faces, limit_edges, processed=None):
        if processed is None:
            processed = []
        result = []
        for face in faces:
            for edge in face.edges:
                if edge not in limit_edges:
                    for search_face in edge.link_faces:
                        if search_face not in processed and search_face not in result:
                            result.append(search_face)
        if result:
            processed.extend(result)
        else:
            return []

        return search_faces(result, limit_edges, processed)

    parallels = get_parallel_edges(edges, verts)
    inner_faces = []

    parallel_verts = []
    for e in parallels[1]:
        parallel_verts.extend(e.verts[:])

    for edge in edges:
        if edge in limit_edges:
            continue
        for face in edge.link_faces:
            if face not in inner_faces and not any((v for v in face.verts if v in parallel_verts)):
                inner_faces.append(face)

    if not parallels[0]:
        return inner_faces

    return inner_faces + search_faces([f for f in reduce(add,
                                                         [v.link_faces[:] for v in
                                                          reduce(add, [e.verts[:] for e in parallels[0]])])
                                       if f not in inner_faces], limit_edges, inner_faces)


def get_boundary_edges(faces):
    result = []

    def get_group(face, faces):
        group = []
        for edge in face.edges:
            tree = [[], []]
            for idx, edge_face in enumerate(edge.link_faces):
                if edge_face not in group and edge_face in faces:
                    group.append(edge_face)
                    faces.remove(edge_face)
                    if faces:
                        tree[idx] = get_group(edge_face, faces)
            group.extend(tree[0])
            group.extend(tree[1])

        return group

    while len(faces) > 0:
        group = get_group(faces[0], faces)
        edges = []
        for face in group:
            for edge in face.edges:
                for edge_face in edge.link_faces:
                    if edge_face not in group:
                        edges.append(edge)
        result.append((edges, group))
    return result
