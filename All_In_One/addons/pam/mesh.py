import bpy
import mathutils

import numpy

from . import constants
from .utils import quadtree

def compute_path_length(path):
    """Compute for an array of 3d-vectors their combined length in space
    :param path: A sequence of mathutils.Vector, defining the points of the path
    :type path: Sequence of mathutils.Vector

    :return: The length of the path
    :rtype: float"""
    return sum([(path[i] - path[i - 1]).length for i in range(1, len(path))])

def checkPointInObject(obj, point):
    """Checks if a given point is inside or outside of the given geometry

    Uses a ray casting algorithm to count intersections

    :param obj: The object whose geometry will be used to check
    :type obj: bpy.types.Object 
    :param point: The point to be checked
    :type point: mathutils.Vector (should be 3d)

    :return: True if the point is inside of the geometry, False if outside
    :rtype: bool"""

    m = obj.data
    ray = mathutils.Vector((0.0,0.0,1.0))

    world_matrix = obj.matrix_world
    m.calc_tessface()
    ray_hit_count = 0

    for f, face in enumerate(m.tessfaces):
        verts = face.vertices
        if len(verts) == 3:
            v1 = world_matrix * m.vertices[face.vertices[0]].co.xyz
            v2 = world_matrix * m.vertices[face.vertices[1]].co.xyz
            v3 = world_matrix * m.vertices[face.vertices[2]].co.xyz
            vr = mathutils.geometry.intersect_ray_tri(v1, v2, v3, ray, point)
            if vr is not None:
                ray_hit_count += 1
        elif len(verts) == 4:
            v1 = world_matrix * m.vertices[face.vertices[0]].co.xyz
            v2 = world_matrix * m.vertices[face.vertices[1]].co.xyz
            v3 = world_matrix * m.vertices[face.vertices[2]].co.xyz
            v4 = world_matrix * m.vertices[face.vertices[3]].co.xyz
            vr1 = mathutils.geometry.intersect_ray_tri(v1, v2, v3, ray, point)
            vr2 = mathutils.geometry.intersect_ray_tri(v1, v3, v4, ray, point)
            if vr1 is not None:
                ray_hit_count += 1
            if vr2 is not None:
                ray_hit_count += 1

    return ray_hit_count % 2 == 1


def map3dPointToUV(obj, obj_uv, point, normal=None):
    """Convert a given 3d-point into uv-coordinates,
    obj for the 3d point and obj_uv must have the same topology
    if normal is not None, the normal is used to detect the point on obj, otherwise
    the closest_point_on_mesh operation is used

    :param obj: The source 3d-object on which to project the point before mapping
    :type obj: bpy.types.Object
    :param obj_uv: The object with the uv-map on which to project the point
    :type obj_uv: bpy.types.Object
    :param point: The 3d point which to project onto uv
    :type point: mathutils.Vector (should be 3d)

    :return: The transformed point in uv-space
    :rtype: mathutils.Vector (2d)
    """

    
    if normal:
        normal_scaled = normal * constants.RAY_FAC
        p, n, f = obj.ray_cast(point + normal_scaled, point - normal_)
        # if no collision could be detected, return None
        if f == -1:
            return None
    else:
        # get point, normal and face of closest point to a given point
        p, n, f = obj.closest_point_on_mesh(point)

    # get the uv-coordinate of the first triangle of the polygon
    A = obj.data.vertices[obj.data.polygons[f].vertices[0]].co
    B = obj.data.vertices[obj.data.polygons[f].vertices[1]].co
    C = obj.data.vertices[obj.data.polygons[f].vertices[2]].co

    # and the uv-coordinates of the first triangle
    uvs = [obj_uv.data.uv_layers.active.data[li] for li in obj_uv.data.polygons[f].loop_indices]
    U = uvs[0].uv.to_3d()
    V = uvs[1].uv.to_3d()
    W = uvs[2].uv.to_3d()

    # convert 3d-coordinates of point p to uv-coordinates
    p_uv = mathutils.geometry.barycentric_transform(p, A, B, C, U, V, W)

    p_uv_2d = p_uv.to_2d()

    # if the point is not within the first triangle, we have to repeat the calculation
    # for the second triangle
    if (mathutils.geometry.intersect_point_tri_2d(p_uv_2d, uvs[0].uv, uvs[1].uv, uvs[2].uv) == 0) & (len(uvs) == 4):
        A = obj.data.vertices[obj.data.polygons[f].vertices[0]].co
        B = obj.data.vertices[obj.data.polygons[f].vertices[2]].co
        C = obj.data.vertices[obj.data.polygons[f].vertices[3]].co

        U = uvs[0].uv.to_3d()
        V = uvs[2].uv.to_3d()
        W = uvs[3].uv.to_3d()

        p_uv_new = mathutils.geometry.barycentric_transform(p, A, B, C, U, V, W)

    else:
        return p_uv_2d

    p_uv_2d_new = p_uv_new.to_2d()

    if (mathutils.geometry.intersect_point_tri_2d(p_uv_2d_new, uvs[0].uv, uvs[2].uv, uvs[3].uv) == 0) & (len(uvs) == 4):
        
        delta1 = checkPointOnLine(p_uv_2d,uvs[0].uv,uvs[1].uv)
        delta2 = checkPointOnLine(p_uv_2d,uvs[0].uv,uvs[2].uv)
        delta3 = checkPointOnLine(p_uv_2d,uvs[1].uv,uvs[2].uv)
        delta = min(delta1,delta2,delta3)
        
        delta1 = checkPointOnLine(p_uv_2d_new,uvs[0].uv,uvs[2].uv)
        delta2 = checkPointOnLine(p_uv_2d_new,uvs[0].uv,uvs[3].uv)
        delta3 = checkPointOnLine(p_uv_2d_new,uvs[2].uv,uvs[3].uv)
        delta_new = min(delta1,delta2,delta3)
        
        if delta_new > delta:
            return p_uv_2d
    return p_uv_2d_new

QUADTREE_CACHE = {}

def mapUVPointTo3d(obj_uv, uv_list, check_edges = False, cleanup=True):
    """Convert a list of uv-points into 3d. 
    This function is mostly used by interpolateUVTrackIn3D. Note, that 
    therefore, not all points can and have to be converted to 3d points. 
    The return list can therefore have less points than the uv-list. 
    This cleanup can be deactivated by setting cleanup = False. Then, 
    the return-list may contain some [] elements.

    This function makes use of a quadtree cache managed in pam.model.

    :param obj_uv: The object with the uv-map
    :type obj_uv: bpy.types.Object
    :param uv_list: The list of uv-coordinates to convert
    :type uv_list: List of mathutils.Vector (Vectors should be 2d)
    :param check_edges: If set to True, the edges of the mesh are 
        specifically checked again to ensure accuracy when points 
        are directly on the edge of a mesh. This slows the function 
        down, so use with care.
    :type check_edges: bool
    :param cleanup: If set to False, unmapped uv-coordinates are 
        removed from the return list
    :type cleanup: bool

    :return: List of converted 3d-points
    :rtype: list of mathutils.Vector (Vectors are 3d) or []
    """

    uv_list_range_container = range(len(uv_list))

    points_3d = [[] for _ in uv_list_range_container]
    point_indices = [i for i in uv_list_range_container]

    # Build new quadtree to cache objects if no chache exists
    if obj_uv.name not in QUADTREE_CACHE:
        qtree = quadtree.buildUVQuadtreeFromObject(obj_uv, constants.CACHE_QUADTREE_DEPTH)
        QUADTREE_CACHE[obj_uv.name] = qtree
    else:
        qtree = QUADTREE_CACHE[obj_uv.name]

    for i in point_indices:
        point = uv_list[i]
        for polygon in qtree.getPolygons(point):
            uvs = polygon[0]
            p3ds = polygon[1]

            result = mathutils.geometry.intersect_point_tri_2d(
                point,
                uvs[0],
                uvs[1],
                uvs[2]
            )

            if (result != 0):
                points_3d[i] = mathutils.geometry.barycentric_transform(
                    point.to_3d(),
                    uvs[0].to_3d(),
                    uvs[1].to_3d(),
                    uvs[2].to_3d(),
                    p3ds[0],
                    p3ds[1],
                    p3ds[2]
                )
                break

            else:
                result = mathutils.geometry.intersect_point_tri_2d(
                    point,
                    uvs[0],
                    uvs[2],
                    uvs[3]
                )
                if (result != 0):
                    points_3d[i] = mathutils.geometry.barycentric_transform(
                        point.to_3d(),
                        uvs[0].to_3d(),
                        uvs[2].to_3d(),
                        uvs[3].to_3d(),
                        p3ds[0],
                        p3ds[2],
                        p3ds[3]
                    )
                    break
            if check_edges:
                # Sometimes the point is directly on the edge of a tri and intersect_point_tri_2d doesn't recognize it
                # So we check for all possible edges
                edges = [(0, 1),
                         (1, 2),
                         (2, 3),
                         (3, 0),
                         (0, 2)]
                for edge in edges:
                    point_on_line, percentage = mathutils.geometry.intersect_point_line(point, uvs[edge[0]], uvs[edge[1]])
                    if (point_on_line - point).length <= constants.UV_THRESHOLD and percentage >= 0. and percentage <= 1.:
                        points_3d[i] = p3ds[edge[0]].lerp(p3ds[edge[1]], percentage)
                        break

    if cleanup:
        points_3d = [p for p in points_3d if p]

    return points_3d


# TODO(MP): triangle check could be made more efficient
# TODO(MP): check the correct triangle order !!!
def map3dPointTo3d(o1, o2, point, normal=None):
    """Map a 3d-point on a given object on another object. Both objects must have the
    same topology. The closest point on the mesh of the first object is projected onto 
    the mesh of the second object.

    :param o1: The source object
    :type o1: bpy.types.Object
    :param o2: The target object
    :type o2: bpy.types.Object
    :param point: The point to transform
    :type point: mathutils.Vector
    :param normal: If a normal is given, the point on the target mesh is not determined 
        by the closest point on the mesh, but by raycast along the normal
    :type normal: mathutils.Vector

    :return: The transformed point
    :rtype: mathutils.Vector
    """

    # if normal is None, we don't worry about orthogonal projections
    if normal is None:
        # get point, normal and face of closest point to a given point
        p, n, f = o1.closest_point_on_mesh(point)
    else:
        p, n, f = o1.ray_cast(point + normal * constants.RAY_FAC, point - normal * constants.RAY_FAC)
        # if no collision could be detected, return None
        if f == -1:
            return None

    # if o1 and o2 are identical, there is nothing more to do
    if (o1 == o2):
        return p

    # get the vertices of the first triangle of the polygon from both objects
    A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
    B1 = o1.data.vertices[o1.data.polygons[f].vertices[1]].co
    C1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co

    # project the point on a 2d-surface and check, whether we are in the right triangle
    t1 = mathutils.Vector()
    t2 = mathutils.Vector((1.0, 0.0, 0.0))
    t3 = mathutils.Vector((0.0, 1.0, 0.0))

    p_test = mathutils.geometry.barycentric_transform(p, A1, B1, C1, t1, t2, t3)

    # if the point is on the 2d-triangle, proceed with the real barycentric_transform
    if mathutils.geometry.intersect_point_tri_2d(p_test.to_2d(), t1.xy, t2.xy, t3.xy) == 1:
        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[1]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co

        # convert 3d-coordinates of the point
        p_new = mathutils.geometry.barycentric_transform(p, A1, B1, C1, A2, B2, C2)

    else:
        # use the other triangle
        A1 = o1.data.vertices[o1.data.polygons[f].vertices[0]].co
        B1 = o1.data.vertices[o1.data.polygons[f].vertices[2]].co
        C1 = o1.data.vertices[o1.data.polygons[f].vertices[3]].co

        A2 = o2.data.vertices[o2.data.polygons[f].vertices[0]].co
        B2 = o2.data.vertices[o2.data.polygons[f].vertices[2]].co
        C2 = o2.data.vertices[o2.data.polygons[f].vertices[3]].co

        # convert 3d-coordinates of the point
        p_new = mathutils.geometry.barycentric_transform(p, A1, B1, C1, A2, B2, C2)

    return p_new

def checkPointOnLine(p,a1,a2):
    """Checks if a point p is on the line between the points a1 and a2
    returns the qualitative distance of the point from the line, 0 if the point is on the line with tolerance
    """
    EPSILON = 0.0001     #tolerance value for being able to work with floats
    d1 = p-a1
    d2 = a2-p
    dot = numpy.dot(d1,d2)
    #print('dot',dot)
    cross = numpy.cross(d1,d2)
    #print('cross',cross)
    norma1a2 = numpy.linalg.norm(a2-a1)
    #print('norma1a2',norma1a2)
    delta = numpy.linalg.norm(cross) - EPSILON
    if delta > 0:        #greater than 0, with tolerance
        #print('First false')
        return delta
    delta = -EPSILON-dot
    if delta > 0:                   #lesser than 0, with tolerance
        #print('Second false')
        return delta
    delta = dot-norma1a2*norma1a2+EPSILON
    if delta > 0:       #greater that squared norm, with tolerance
        #print('Third false')
        return delta
    return 0


# TODO(SK): Rephrase docstring, add parameter/return values
def interpolateUVTrackIn3D(p1_3d, p2_3d, layer):
    """Create a 3D-path along given 3d-coordinates p1_3d and p2_3d on layer"""
    # get 2d-coordinates
    p1_2d = map3dPointToUV(layer, layer, p1_3d)
    p2_2d = map3dPointToUV(layer, layer, p2_3d)

    uv_p_2d = []

    for step in range(1, constants.INTERPOLATION_QUALITY + 1):
        interpolation = step / (constants.INTERPOLATION_QUALITY)
        uv_p_2d.append(p2_2d * interpolation + p1_2d * (1 - interpolation))

    ip_3d = mapUVPointTo3d(layer, uv_p_2d)

    return ip_3d
