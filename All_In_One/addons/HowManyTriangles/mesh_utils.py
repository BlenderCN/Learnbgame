import bpy
import math

def unselect_mesh(bmesh):
    for ver in bmesh.verts:
        ver.select = False
    
    for edge in bmesh.edges:
        edge.select = False
    
    for face in bmesh.faces:
        face.select = False

    # trigger viewport update
    bpy.context.scene.objects.active = bpy.context.scene.objects.active

def get_next_verts(vert):
    next_verts = [];
    
    for edge in vert.link_edges:
        for next_vert in edge.verts:
            if next_vert is not vert:
                next_verts.append(next_vert)
    
    return next_verts

def get_edge_from_verts(vertex1, vertex2):
    if vertex1 is vertex2:
        return None
    
    for edge in vertex1.link_edges:
        if vertex2 in edge.verts:
            return edge
    
    return None

def calc_edges_angle(edge1, edge2):
    if edge1 is edge2:
        return 0
    
    common_vertex_set = list(set(edge1.verts) & set(edge2.verts))
    if len(common_vertex_set) != 1:
        raise ValueError("Both edge must share only one vertex!")
    
    common_vertex = common_vertex_set[0]
    
    vector1 = list(set(edge1.verts) - set([common_vertex]))[0].co - common_vertex.co
    vector2 = list(set(edge2.verts) - set([common_vertex]))[0].co - common_vertex.co
    
    internal = vector1.normalized() * vector2.normalized()
    
    if internal < -1:
        internal = -1
    if internal > 1:
        internal = 1
    
    return math.acos(internal)
