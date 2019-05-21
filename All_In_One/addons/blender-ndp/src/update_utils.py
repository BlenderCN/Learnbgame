import bpy
import bmesh
import mathutils

def _edge_pos(edge : bmesh.types.BMEdge):
    verts : bmesh.types.BMElemSeq = edge.verts
    vert_a : bmesh.types.BMVert = verts[0]
    vert_b : bmesh.types.BMVert = verts[1]
    return (vert_a.co + vert_b.co)*0.5

def _edge_loop_insert(bm, edge_ring, cuts):
    if (cuts <= 0):
        return
    bmesh.ops.subdivide_edgering(
        bm,
        edges = edge_ring,
        interp_mode = 'LINEAR',
        smooth = 0,
        cuts = cuts,
        profile_shape = 'LINEAR',
        profile_shape_factor = 0
    )

def _select_edge_ring(all_edges, axis):
    result = []
    for edge in all_edges:
        pos = _edge_pos(edge)
        if (abs(pos[axis]) < 0.0001):
            result.append(edge)
    return result

def _recreate_mesh(context, obj, func):
    ndp_props = obj.data.ndp_props
    mesh = obj.data
    size_policy = ndp_props.size_policy
    if not size_policy:
        size_policy = 'DEFAULT'

    bm = bmesh.new()
    bm = func(
        obj = obj,
        bm = bm,
        matrix = obj.matrix_world,
        divisions = ndp_props.divisions,
        size = ndp_props.size,
        radius = ndp_props.radius,
        fill_type = ndp_props.fill_type,
        calculate_uvs = ndp_props.calculate_uvs,
        size_policy = size_policy,
        identity = mathutils.Matrix.Identity(4))
    bm.to_mesh(mesh)
    bm.free()

def _create_plane(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    bmesh.ops.create_grid(
        bm,
        x_segments = 1+divisions[0],
        y_segments = 1+divisions[1],
        size = 1.0,
        matrix = identity,
        calc_uvs = calculate_uvs)
    verts = bm.verts[:]
    actual_size = []
    for i in range(0, 3):
        actual_size.append(size[i]*.5)
    bmesh.ops.scale(bm, vec=actual_size, space=identity, verts=verts)
    return bm

def _create_box(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    bmesh.ops.create_cube(
        bm,
        size = 1.0,
        matrix = identity,
        calc_uvs = calculate_uvs)

    bm.select_mode = {'EDGE'}
    all_edges : bmesh.types.BMEdgeSeq = bm.edges
    edge_rings = [[], [], []]
    for i in range(0, 3):
        _edge_loop_insert(bm, _select_edge_ring(bm.edges, i), divisions[i])

    bmesh.ops.scale(bm, vec=size, space=identity, verts=bm.verts[:])
    return bm

def _create_circle(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    should_cap_ends = (fill_type == 'NGONS' or fill_type == 'TRIANGLE_FAN')
    should_cap_w_tris = (fill_type == 'TRIANGLE_FAN')
    bmesh.ops.create_circle(
        bm,
        cap_ends = should_cap_ends,
        cap_tris = should_cap_w_tris,
        segments = 3+divisions[0],
        radius = radius[0],
        matrix = identity,
        calc_uvs = calculate_uvs)
    if (size_policy == 'AXIS_SCALE'):
        bmesh.ops.scale(bm, vec=size, space=identity, verts=bm.verts[:])
    return bm
    
def _create_uvsphere(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    bmesh.ops.create_uvsphere(
        bm,
        u_segments = 3+divisions[0],
        v_segments = 3+divisions[1],
        diameter = radius[0],
        matrix = identity,
        calc_uvs = calculate_uvs)
    if (size_policy == 'AXIS_SCALE'):
        bmesh.ops.scale(bm, vec=size, space=identity, verts=bm.verts[:])
    return bm
    
def _create_icosphere(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    bmesh.ops.create_icosphere(
        bm,
        subdivisions = 1+divisions[0],
        diameter = radius[0],
        matrix = identity,
        calc_uvs = calculate_uvs)
    if (size_policy == 'AXIS_SCALE'):
        bmesh.ops.scale(bm, vec=size, space=identity, verts=bm.verts[:])
    return bm
    
def _create_cylinder(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    should_cap_ends = (fill_type == 'NGONS' or fill_type == 'TRIANGLE_FAN')
    should_cap_w_tris = (fill_type == 'TRIANGLE_FAN')
    bmesh.ops.create_cone(
        bm,
        cap_ends = should_cap_ends,
        cap_tris = should_cap_w_tris,
        segments = 3+divisions[0],
        diameter1 = radius[0],
        diameter2 = radius[0],
        depth = size[2],
        matrix = identity,
        calc_uvs = calculate_uvs)
    if (size_policy == 'AXIS_SCALE'):
        size = (size[0], size[1], 1)
        bmesh.ops.scale(bm, vec=size, space=identity, verts=bm.verts[:])
    return bm
    
def _create_cone(obj:bpy.types.Object, bm:bmesh.types.BMesh,
    matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy, identity):
    should_cap_ends = (fill_type == 'NGONS' or fill_type == 'TRIANGLE_FAN')
    should_cap_w_tris = (fill_type == 'TRIANGLE_FAN')
    bmesh.ops.create_cone(
        bm,
        cap_ends = should_cap_ends,
        cap_tris = should_cap_w_tris,
        segments = 3+divisions[0],
        diameter1 = radius[0],
        diameter2 = radius[1],
        depth = size[2],
        matrix = identity,
        calc_uvs = calculate_uvs)
    bmesh.ops.remove_doubles(
        bm,
        verts = bm.verts[:],
        dist = .0000001
    )
    if (size_policy == 'AXIS_SCALE'):
        size = (size[0], size[1], 1)
        bmesh.ops.scale(bm, vec=size, space=identity, verts=bm.verts[:])
    return bm
    
# def _create_torus(obj:bpy.types.Object, bm:bmesh.types.BMesh,
#     matrix, divisions, size, radius, fill_type, calculate_uvs, size_policy):
#     bmesh.ops
#     return bm


from . enums import PrimType
update_func = {
    PrimType.Plane.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_plane),
    PrimType.Box.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_box),
    PrimType.Circle.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_circle),
    PrimType.UvSphere.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_uvsphere),
    PrimType.IcoSphere.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_icosphere),
    PrimType.Cylinder.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_cylinder),
    PrimType.Cone.name.upper() :
        lambda op, context, obj: _recreate_mesh(context, obj, _create_cone),
    # PrimType.Torus.name.upper() : _create_torus,
}