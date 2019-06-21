import bpy

import numpy as np
import bpy
import bmesh
import random

#import numba

import cProfile, pstats, io

def write_fast(ve, qu, tr):
    me = bpy.data.meshes.new("testmesh")

    quadcount = len(qu)
    tricount  = len(tr)

    me.vertices.add(count=len(ve))

    loopcount = quadcount * 4 + tricount * 3
    facecount = quadcount + tricount
    
    me.loops.add(loopcount)
    me.polygons.add(facecount)

    face_lengths = np.zeros(facecount, dtype=np.int)
    face_lengths[:tricount] = 3
    face_lengths[tricount:] = 4

    loops = np.concatenate((np.arange(tricount) * 3, np.arange(quadcount) * 4 + tricount * 3))
    
    v_out = np.concatenate((tr.ravel(), qu.ravel()))

    me.vertices.foreach_set("co", ve.ravel())
    me.polygons.foreach_set("loop_total", face_lengths)
    me.polygons.foreach_set("loop_start", loops)
    me.polygons.foreach_set("vertices", v_out)
    
    me.update(calc_edges=True)
    #me.validate(verbose=True)

    return me


def read_loops(mesh):
    loops = np.zeros((len(mesh.polygons)), dtype=np.int)
    mesh.polygons.foreach_get("loop_total", loops)
    return loops 

def read_loop_starts(mesh):
    loops = np.zeros((len(mesh.polygons)), dtype=np.int)
    mesh.polygons.foreach_get("loop_start", loops)
    return loops 

def read_polygon_verts(mesh):
    polys = np.zeros((len(mesh.polygons)*4), dtype=np.uint32)
    mesh.polygons.foreach_get("vertices", faces)
    return polys

def read_verts(mesh):
    mverts_co = np.zeros((len(mesh.vertices)*3), dtype=np.float)
    mesh.vertices.foreach_get("co", mverts_co)
    return np.reshape(mverts_co, (len(mesh.vertices), 3))      

def read_edges(mesh):
    fastedges = np.zeros((len(mesh.edges)*2), dtype=np.int) # [0.0, 0.0] * len(mesh.edges)
    mesh.edges.foreach_get("vertices", fastedges)
    return np.reshape(fastedges, (len(mesh.edges), 2))

def read_norms(mesh):
    mverts_no = np.zeros((len(mesh.vertices)*3), dtype=np.float)
    mesh.vertices.foreach_get("normal", mverts_no)
    return np.reshape(mverts_no, (len(mesh.vertices), 3))

def write_verts(mesh, mverts_co):
    mesh.vertices.foreach_set("co", mverts_co.ravel())

def write_edges(mesh, fastedges):
    mesh.edges.foreach_set("vertices", fastedges.ravel())

def write_norms(mesh, mverts_no):
    mesh.vertices.foreach_set("normal", mverts_no.ravel())


def safe_bincount(data, weights, dts, conn):
    """
    for i, v in enumerate(data):
        dts[v] += weights[i]
        conn[v] += 1
    return (dts, conn)
    """
    bc = np.bincount(data, weights)
    dts[:len(bc)] += bc
    bc = np.bincount(data)
    conn[:len(bc)] += bc
    return (dts, conn)


def read_bmesh(bmesh):
    bmesh.verts.ensure_lookup_table()
    bmesh.faces.ensure_lookup_table()

    verts = [(i.co[0], i.co[1], i.co[2]) for i in bmesh.verts]
    qu, tr = [], []
    for f in bmesh.faces:
        if len(f.verts) == 4:        
            qu.append([])
            for v in f.verts:
                qu[-1].append(v.index)
        if len(f.verts) == 3:        
            tr.append([])
            for v in f.verts:
                tr[-1].append(v.index)

    return (np.array(verts), np.array(tr), np.array(qu))


def read_formatted_mesh(me):     
    bm = bmesh.new()
    bm.from_mesh(me)

    loops = read_loops(me)
    if np.max(loops) >= 4:
        # Mesh has ngons/quads! Triangulate ...
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')

    nverts, ntris, nquads = read_bmesh(bm)
    bm.free()

    return nverts, ntris, nquads


def calc_curvature(fastverts, fastedges, fastnorms):
    """ Calculates curvature for specified mesh """
    edge_a, edge_b = fastedges[:,0], fastedges[:,1]
    
    tvec = fastverts[edge_b] - fastverts[edge_a]
    tvlen = np.linalg.norm(tvec, axis=1)    

    # normalize vectors
    tvec = (tvec.T / tvlen).T 

    # adjust the minimum of what is processed   
    edgelength = tvlen * 100
    edgelength = np.where(edgelength < 1, 1.0, edgelength)

    vecsums = np.zeros(fastverts.shape[0], dtype=np.float) 
    connections = np.zeros(fastverts.shape[0], dtype=np.int) 

    # calculate normal differences to the edge vector in the first edge vertex
    totdot = (np.einsum('ij,ij->i', tvec, fastnorms[edge_a]))/edgelength
    safe_bincount(edge_a, totdot, vecsums, connections)

    # calculate normal differences to the edge vector  in the second edge vertex
    totdot = (np.einsum('ij,ij->i', -tvec, fastnorms[edge_b]))/edgelength
    safe_bincount(edge_b, totdot, vecsums, connections)

    return np.arccos(vecsums/connections)/np.pi


def mesh_smooth_filter_variable(data, fastverts, fastedges, iterations):
    """ Smooths variables in data [0, 1] over the mesh topology """
    # vert indices of edges
    edge_a, edge_b = fastedges[:,0], fastedges[:,1]
    tvlen = np.linalg.norm(fastverts[edge_b] - fastverts[edge_a], axis=1)
    edgelength = np.where(tvlen<1, 1.0, tvlen)

    data_sums = np.zeros(data.shape, dtype=np.float) 
    connections = np.zeros(data.shape[0], dtype=np.float) 

    # longer the edge distance to datapoint, less it has influence

    for _ in range(iterations):
        # step 1
        data_sums = np.zeros(data_sums.shape)
        connections = np.zeros(connections.shape)

        per_vert = data[edge_b]/edgelength
        safe_bincount(edge_a, per_vert, data_sums, connections)
        eb_smooth = data_sums/connections
        
        per_vert = eb_smooth[edge_a]/edgelength
        safe_bincount(edge_b, per_vert, data_sums, connections)

        new_data = data_sums/connections

        # step 2
        data_sums = np.zeros(data_sums.shape)
        connections = np.zeros(connections.shape)

        per_vert = data[edge_a]/edgelength
        safe_bincount(edge_b, per_vert, data_sums, connections)
        ea_smooth = data_sums/connections
        
        per_vert = ea_smooth[edge_b]/edgelength
        safe_bincount(edge_a, per_vert, data_sums, connections)

        new_data += data_sums/connections
        new_data /= 2.0
        
        data = new_data

    return new_data


def get_nonmanifold_verts(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    res = np.zeros((len(bm.verts)), dtype=np.bool)
    for i, e in enumerate(bm.edges):
        if len(e.link_faces) < 2:
            res[e.verts[0].index] = True
            res[e.verts[1].index] = True

    bm.free()
    return res


# Mesh connection ops

def faces_verts(faces):
    return {v for f in faces for v in f.verts}

def verts_faces(verts):
    return {f for v in verts for f in v.link_faces}

def vert_vert(v):
    return [e.other_vert(v) for e in v.link_edges]

def con_verts(v, tfun):
    return {x for x in vert_vert(v) if tfun(x)}

def con_area(verts, tfun):
    connected = set()
    for v in verts:
        connected |= con_verts(v, tfun)
    return connected

def get_shell(clean_vert, tfun):
    previous = set([clean_vert])
    connected = con_verts(clean_vert, tfun) | previous
    res = []

    while True:
        for v in connected:
            res.append(v)

        previous = connected
        connected = con_area(connected, tfun)
        if len(connected - previous) == 0:
            break
    
    return res

def mesh_get_shells(bm):
    traversed = np.zeros((len(bm.verts)), dtype=np.bool)
    shells = []

    while np.any(traversed == False):
        location = np.nonzero(traversed == False)[0][0]
        others = [bm.verts[location]]
        
        shells.append([])
        while others != []:
            shells[-1].extend(others)
            step = []
            for v in others:
                if traversed[v.index] == False:
                    traversed[v.index] = True
                    step.extend([e.other_vert(v) for e in v.link_edges])
            others = step

    return shells


def mesh_get_edge_connection_shells(bm):
    traversed = np.zeros((len(bm.faces)), dtype=np.bool)
    shells = []

    while np.any(traversed == False):
        location = np.nonzero(traversed == False)[0][0]
        others = [bm.faces[location]]
        
        shells.append([])
        while others != []:
            shells[-1].extend(others)
            step = []
            for f in others:
                if traversed[f.index] == False:
                    traversed[f.index] = True
                    linked_faces = []
                    for e in f.edges:
                        if len(e.link_faces) > 1:
                            linked_faces.append([i for i in e.link_faces if i!=f][0])
                    step.extend(linked_faces)
            others = step
    return shells


def bmesh_get_boundary_edgeloops_from_selected(bm):
    edges = [e for e in bm.edges if e.select]
    t_edges = np.ones((len(bm.edges)), dtype=np.bool)
    for e in edges:
        t_edges[e.index] = False
    loops = []

    while np.any(t_edges == False):
        location = np.nonzero(t_edges == False)[0][0]
        others = [bm.edges[location]]
        
        loops.append([])
        while others != []:
            loops[-1].extend(others)
            step = []
            for e in others:
                if t_edges[e.index] == False:
                    t_edges[e.index] = True
                    step.extend([e for e in e.verts[0].link_edges if not e.is_manifold])
                    step.extend([e for e in e.verts[1].link_edges if not e.is_manifold])
            others = step

    return [list(set(l)) for l in loops]

def bmesh_vertloop_from_edges(edges):
    res = [edges[0]]
    verts = []
    while len(res) < len(edges) and (len(verts) < 3 or verts[-1] != verts[0] and verts[-1] != verts[-2]):
        r = res[-1]

        e0 = [e for e in r.verts[0].link_edges if e!= r and e in edges]           
        e1 = [e for e in r.verts[1].link_edges if e!= r and e in edges]

        if len(e0) > 1 or len(e1) > 1:
            pass
            #print("invalid edge in bmesh_order_edgeloop()")

        if len(e0) == 0:
            #print("not a loop")
            return None

        test = e0[0] not in res
        te = e0[0] if test else e1[0]
        res.append(te)

        # FIXME: hack
        v = r.verts[int(not test)]
        if len(verts) == 0:
            verts.append(v)
        elif verts[-1] != v:
            verts.append(v)

    verts.append(res[-1].other_vert(verts[-1]))
    #print([i.index for i in verts])

    # final sanity check
    if len(verts) != len(list(set(verts))):
        return None
    else:
        return verts


def bmesh_fill_from_loops(bm, loops):
    new_faces = []
    leftover_loops = []
    for l in loops:
        nl = bmesh_vertloop_from_edges(l)
        if nl:
            f = bm.faces.new(nl)
            f.select = True
            f.smooth = True
            new_faces.append(f)
        else:
            leftover_loops.append(l)

    return new_faces, leftover_loops


def bmesh_deselect_all(bm):
    for v in bm.verts:
        v.select = False

    for e in bm.edges:
        e.select = False



class Bmesh_from_edit():
    def __init__(self, mesh):
        self.mesh = mesh
    def __enter__(self):
        self.bm = bmesh.from_edit_mesh(self.mesh)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()
        return self.bm
    def __exit__(self, type, value, traceback):
        bmesh.update_edit_mesh(self.mesh)


def profiling_start():
    # profiling
    pr = cProfile.Profile()
    pr.enable()
    return pr

def profiling_end(pr):
    # end profile, print results
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats(sortby).print_stats(20)
    print(s.getvalue())

