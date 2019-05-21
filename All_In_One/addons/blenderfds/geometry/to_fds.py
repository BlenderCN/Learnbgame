"""BlenderFDS, translate Blender object geometry to FDS notation."""

import bpy
from time import time
from blenderfds.geometry.utilities import *
from blenderfds.geometry.voxelize import voxelize

DEBUG = False

### to None

def ob_to_none(context, ob):
    return None, None

### to XB

def ob_to_xbs_voxels(context, ob) -> "((x0,x1,y0,y1,z0,z1,), ...), 'Message'":
    """Transform ob solid geometry in XBs notation (voxelization)."""
    print("BFDS: geometry.ob_to_xbs_voxels:", ob.name)
    t0 = time()
    xbs, voxel_size, timing = voxelize(context, ob)
    if not xbs: return None, "No voxel created"
    msg = "{0} voxels, resolution {1:.3f} m, in {2:.0f} s".format(len(xbs), voxel_size, time()-t0)
    if DEBUG: msg += " (s:{0[0]:.0f} 1f:{0[1]:.0f}, 2g:{0[2]:.0f}, 3g:{0[3]:.0f})".format(timing)
    return xbs, msg

def ob_to_xbs_pixels(context, ob) -> "((x0,x1,y0,y1,z0,z0,), ...), 'Message'":
    """Transform ob flat geometry in XBs notation (flat voxelization)."""
    print("BFDS: geometry.ob_to_xbs_pixels:", ob.name)
    t0 = time()
    xbs, voxel_size, timing = voxelize(context, ob, flat=True)
    if not xbs: return None, "No pixel created"
    msg = "{0} pixels, resolution {1:.3f} m, in {2:.0f} s".format(len(xbs), voxel_size, time()-t0)
    if DEBUG: msg += " (s:{0[0]:.0f} 1f:{0[1]:.0f}, 2g:{0[2]:.0f}, 3g:{0[3]:.0f})".format(timing)
    return xbs, msg

def ob_to_xbs_bbox(context, ob) -> "((x0,x1,y0,y1,z0,z1,), ...), 'Message'":
    """Transform ob solid geometry in XBs notation (bounding box)."""
    x0, x1, y0, y1, z0, z1 = get_global_bbox(context, ob)
    return [(x0, x1, y0, y1, z0, z1,),], None

def ob_to_xbs_faces(context, ob) -> "((x0,x1,y0,y1,z0,z0,), ...), 'Message'":
    """Transform ob faces in XBs notation (faces)."""
    # Init
    result = list()
    me = get_global_mesh(context, ob)
    tessfaces = get_tessfaces(context, me)
    # For each tessface...
    for tessface in tessfaces:
        vertices = [me.vertices[vertex] for vertex in tessface.vertices]
        # Calc the bounding box in global coordinates
        bbminx, bbminy, bbminz = vertices[0].co
        bbmaxx, bbmaxy, bbmaxz = vertices[0].co
        for vertex in vertices[1:]:
            x, y, z = vertex.co
            bbminx, bbminy, bbminz = min(bbminx, x), min(bbminy, y), min(bbminz, z)
            bbmaxx, bbmaxy, bbmaxz = max(bbmaxx, x), max(bbmaxy, y), max(bbmaxz, z)
        bbd = [(bbmaxx - bbminx, 2), (bbmaxy - bbminy, 1), (bbmaxz - bbminz, 0)]
        bbd.sort()
        if bbd[0][1] == 2: bbmaxx = bbminx = (bbminx+bbmaxx)/2
        if bbd[0][1] == 1: bbmaxy = bbminy = (bbminy+bbmaxy)/2
        if bbd[0][1] == 0: bbmaxz = bbminz = (bbminz+bbmaxz)/2
        result.append((bbminx, bbmaxx, bbminy, bbmaxy, bbminz, bbmaxz,),)
    result.sort()
    # Clean up
    bpy.data.meshes.remove(me)
    # Return
    msg = len(result) > 1 and "{0} faces".format(len(result)) or None
    return result, msg

def ob_to_xbs_edges(context, ob) -> "((x0,x1,y0,y1,z0,z1,), ...), 'Message'":
    """Transform ob faces in XBs notation (faces)."""
    # Init
    result = list()
    me = get_global_mesh(context, ob)
    # For each edge...
    for edge in me.edges:
        pt0x, pt0y, pt0z = me.vertices[edge.vertices[0]].co
        pt1x, pt1y, pt1z = me.vertices[edge.vertices[1]].co
        result.append((pt0x, pt1x, pt0y, pt1y, pt0z, pt1z,),)
    result.sort()
    # Clean up
    bpy.data.meshes.remove(me)
    # Return
    msg = len(result) > 1 and "{0} edges".format(len(result)) or None
    return result, msg

# Caller function (ob.bf_xb)

choose_to_xbs = {
    "NONE"   : ob_to_none,
    "BBOX"   : ob_to_xbs_bbox,
    "VOXELS" : ob_to_xbs_voxels,
    "FACES"  : ob_to_xbs_faces,
    "PIXELS" : ob_to_xbs_pixels,
    "EDGES"  : ob_to_xbs_edges,
}

def ob_to_xbs(context, ob) -> "((x0,x1,y0,y1,z0,z0,), ...), 'Message'":
    """Transform Blender object geometry according to ob.bf_xb to FDS notation."""
    return choose_to_xbs[ob.bf_xb](context, ob)

### XYZ

def ob_to_xyzs_vertices(context, ob) -> "((x0,y0,z0,), ...), 'Message'":
    """Transform ob vertices in XYZs notation."""
    # Init
    result = list()
    me = get_global_mesh(context, ob)
    # For each vertex...
    for vertex in me.vertices:
        pt0x, pt0y, pt0z = vertex.co
        result.append((pt0x, pt0y, pt0z,),)
    result.sort()
    # Clean up
    bpy.data.meshes.remove(me)
    # Return
    msg = len(result) > 1 and "{0} vertices".format(len(result)) or None
    return result, msg

def ob_to_xyzs_center(context, ob) -> "((x0,y0,z0,), ...), 'Message'":
    """Transform ob center in XYZs notation."""
    return [(ob.location[0], ob.location[1], ob.location[2],),], None

# Caller function (ob.bf_xyz)

choose_to_xyzs = {
    "NONE"     : ob_to_none,
    "CENTER"   : ob_to_xyzs_center,
    "VERTICES" : ob_to_xyzs_vertices,
}

def ob_to_xyzs(context, ob):
    """Transform Blender object geometry according to ob.bf_xyz to FDS notation."""
    return choose_to_xyzs[ob.bf_xyz](context, ob)

### PB

def ob_to_pbs_planes(context, ob) -> "(('X',x3,), ('X',x7,), ('Y',y9,), ...), 'Message'":
    """Transform ob faces in PBs notation."""
    # Init
    result = list()
    xbs, msg = ob_to_xbs_faces(context, ob)
    # For each face build a plane...
    for xb in xbs:
        if   abs(xb[1] - xb[0]) < epsilon: result.append(("X", xb[0],),)
        elif abs(xb[3] - xb[2]) < epsilon: result.append(("Y", xb[2],),)
        elif abs(xb[5] - xb[4]) < epsilon: result.append(("Z", xb[4],),)
        else: raise ValueError("BFDS: Building planes impossible, problem in ob_to_xbs_faces.")
    result.sort()
    # Nothing to clean up, return
    msg = len(result) > 1 and "{0} planes".format(len(result)) or None
    return result, msg

# Caller function (ob.bf_pb)

choose_to_pbs = {
    "NONE"   : ob_to_none,
    "PLANES" : ob_to_pbs_planes,
}

def ob_to_pbs(context, ob):
    """Transform Blender object geometry according to ob.bf_pb to FDS notation."""
    return choose_to_pbs[ob.bf_pb](context, ob)

