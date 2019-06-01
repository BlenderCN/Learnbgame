import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_ray_tri
from mathutils.geometry import intersect_point_line
from mathutils.geometry import intersect_line_line as ILL
from mathutils.geometry import tessellate_polygon as tessellate


def perform_face_intersection():
    '''
    (currently) only points that are found on the face that is active, are accepted
    - In practice this means the last selected face will be used to receive
      intersection points.

    - step 2 (not implemented)
      will do the reverse... thus completing the loop.
    '''

    def rays_from_face(face):
        '''
        per edge (v1, v2) this returns the reverse edge too (v2, v1)
        in case the face intersection happens on the origin of the ray
        '''
        indices = [v.index for v in face.verts]
        indices.append(indices[0])  # makes cyclic
        edges_f = [(indices[i], indices[i + 1]) for i in range(len(indices) - 1)]  # forward
        edges_b = [(indices[i + 1], indices[i]) for i in range(len(indices) - 1)]  # backward
        return edges_f + edges_b

    def triangulated(face):
        return tessellate([[v.co for v in face.verts]])

    def get_selected_minus_active(bm_faces, active_idx):
        return [f for f in bm_faces if f.select and not (f.index == active_idx)]

    # Get the active mesh
    obj = bpy.context.edit_object
    me = obj.data

    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()  # get 2.73+
    bm_verts = bm.verts
    bm_faces = bm.faces

    # Prime Face
    active = bm_faces.active

    # triangulate face to intersect
    tris_to_intersect = triangulated(active)  # list of collections of 3 coordinates
    av = active.verts
    tris = [[av[idx1].co, av[idx2].co, av[idx3].co] for idx1, idx2, idx3 in tris_to_intersect]

    # this will hold the set of edges used to raycast, using set will avoid many duplicates of touching
    # faces that share edges.
    test_rays = set()

    # check intersection with bidirectional of all edges of all faces that are selected but not active

    # Non Prime Faces
    faces_to_intersect_with = get_selected_minus_active(bm_faces, active.index)
    for face in faces_to_intersect_with:
        rays = rays_from_face(face)
        for ray in rays:
            test_rays.add(ray)

    vert_set = set()

    for v1, v2, v3 in tris:

        for ray_idx, orig_idx in test_rays:
            orig = bm_verts[orig_idx].co
            ray_original = bm_verts[ray_idx].co
            ray = (bm_verts[ray_idx].co - orig).normalized()
            pt = intersect_ray_tri(v1, v2, v3, ray, orig)
            if pt:
                # filter new verts,
                # they must lie on the line described by (origin, ray_original) then add.
                itx_res = intersect_point_line(pt, ray_original, orig)
                if itx_res:
                    v, dist = itx_res
                    if (0.0 < dist < 1.0):
                        vert_set.add(pt[:])

    print('found {0} unique new verts'.format(len(vert_set)))

    for v in vert_set:
        bm.verts.new(v)

    bmesh.update_edit_mesh(me, True)


def do_bix2():
    obj = bpy.context.edit_object
    me = obj.data

    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm_verts = bm.verts
    bm_edges = bm.edges
    bm_faces = bm.faces

    edges = [e for e in bm_edges if e.select]

    if not len(edges) == 2:
        print('select only two edges')
        return

    itxs = [set(e.link_faces) for e in edges]
    itx = itxs[0] & itxs[1]
    if not (len(itx) == 1):
        print('two edges do not share a face..')
        return

    itx = itx.pop(); print('face idx =', itx.index)

    verts = [set(e.verts) for e in edges]
    v = verts[0] & verts[1]
    v = v.pop(); print('vertex index: ', v.index, v.co)

    vopp = verts[0] ^ verts[1]
    v1 = vopp.pop()
    v2 = vopp.pop()

    v11 = (v1.co - v.co).normalized()
    v22 = (v2.co - v.co).normalized()
    plane_no = v11 - v22
    plane_co = v.co
    dist = 0.0001

    IPL = intersect_point_line

    def find_itersected_edge(v11, v22, plane_co, face):
        v3 = v11.lerp(v22, 0.5)
        edge1 = [v3 + plane_co, plane_co]
        other_edges = list(set(edges) ^ set(face.edges))

        for e in other_edges:
            ev = e.verts
            pts = ILL(ev[0].co, ev[1].co, *edge1)
            pt = (pts[0] + pts[1]) / 2

            itx_res = IPL(pt, ev[0].co, ev[1].co)
            if itx_res:
                v, dist = itx_res
                if (0.0 < dist < 1.0):
                    return e, v, dist

        return None, None, None

    edge, vert, pos = find_itersected_edge(v11, v22, plane_co, itx)
    new_geom = bmesh.utils.edge_split(edge, edge.verts[0], pos)
    if new_geom:
        new_edge, new_vert = new_geom
        bmesh.utils.face_split(itx, v, new_vert)

    bmesh.update_edit_mesh(me, True)
