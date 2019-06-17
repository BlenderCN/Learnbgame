import bpy
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree as BVH
from mathutils.geometry import intersect_line_plane
from math import radians
import sys
from . object import flatten


# RAYCASTING BVH

def cast_bvh_ray_from_object(source, ray_direction, backtrack=None, limit=None, exclude_decals=True, debug=False):
    mxw = source.matrix_world
    origin, _, _ = mxw.decompose()
    direction = mxw @ Vector(ray_direction) - origin

    # when the object is perfectly on the face of another object, you may miss the face with the ray, so shift the origin in the opposite direction
    if backtrack:
        origin = origin - direction * backtrack

    # get candidate objects, that could be hit
    if exclude_decals:
        visible = [obj for obj in bpy.context.visible_objects if obj.type == "MESH" and obj != source and not obj.DM.isdecal]
    else:
        visible = [obj for obj in bpy.context.visible_objects if obj.type == "MESH" and obj != source]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    for obj in visible:
        mx = obj.matrix_world
        mxi = mx.inverted()

        origin_local = mxi @ origin
        direction_local = mxi.to_3x3() @ direction

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bvh = BVH.FromBMesh(bm)

        location, normal, index, distance = bvh.ray_cast(origin_local, direction_local)

        if debug:
            print("candidate:", obj.name, location, normal, index, distance)


        # check direction of face if something was hit
        if normal:
            dot = normal.dot(direction_local)

            # it's facing the wrong way, so cast another ray in the opposite direction
            if dot > 0:
                rlocation, rnormal, rindex, rdistance = bvh.ray_cast(origin_local, direction_local * -1)

                if debug:
                    print(" reverse candidate:", obj.name, rlocation, rnormal, rindex, rdistance)

                # check if the reverse cast hits a face with the correct direction and see it its distance is shorter than th other one
                if rnormal and rnormal.dot(direction_local) < 0 and rdistance < distance:
                    location = rlocation
                    normal = rnormal
                    index = rindex
                    distance = rdistance

                    if debug:
                        print("  reverse ray cast found a closer and properly aligned face.")

                else:
                    distance = None

                    if debug:
                        print(" a backface was hit, treating it as if nothing was hit.")

        bm.free()

        if distance:
            if distance < hitdistance:
                # Matrix.to_3x3() removes the transform and shear channels from the matrix,
                # ####: so that the scale and rotation is the only thing we are multiplying, which is used to bring direction vectors into another space
                hitobj, hitlocation, hitnormal, hitindex, hitdistance = obj, mx @ location, mx.to_3x3() @ normal, index, distance


    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)

    if hitobj:
        if limit:
            if hitdistance < limit:
                return hitobj, hitlocation, hitnormal, hitindex, hitdistance
            else:
                if debug:
                    print("hit is beyond the limit")
                return None, None, None, None, None

        else:
            return hitobj, hitlocation, hitnormal, hitindex, hitdistance

    return None, None, None, None, None


def get_bvh_ray_distance_from_verts(target, source, ray_direction, backtrack=None, limit=None, debug=False):
    smxw = source.matrix_world
    origin, _, _ = smxw.decompose()
    direction = smxw @ Vector(ray_direction) - origin

    tmxw = target.matrix_world
    tmxi = tmxw.inverted()
    direction_local = tmxi.to_3x3() @ direction

    bm = bmesh.new()
    bm.from_mesh(target.data)
    bvh = BVH.FromBMesh(bm)

    front_distances = []
    back_distances = []

    for v in source.data.vertices:
        # vertex location in world space
        co_world = smxw @ v.co

        # vertex location in target's local space
        co_local = tmxi @ co_world


        # cast into -z direction of the decal
        location, normal, index, distance = bvh.ray_cast(co_local, direction_local)

        reverse = False

        # somethin was hit
        if normal:
            dot = normal.dot(direction_local)

            # it's facing against the projection direction, perfect! remember the distance
            if dot < 0:
                # distances.append(distance)
                front_distances.append(distance)

                if debug:
                    print("frontside", index, distance)

            # it's a backside, cast again in the opposite direction
            else:
                reverse = True

        # nothing was hit, cast again in the opposite direction
        else:
            reverse = True


        # cast again in the opposite direction, the decal may be under the surface
        if reverse:
            location, normal, index, distance = bvh.ray_cast(co_local, direction_local * -1)

            if normal:
                dot = normal.dot(direction_local)

                # check face alignment again
                if dot < 0:
                    # distances.append(distance)
                    back_distances.append(distance)

                    if debug:
                        print("backside", index, distance)

        if debug and index:
            target.data.polygons[index].select = True

    bm.free()

    front = max(front_distances) if front_distances else 0
    back = max(back_distances) if back_distances else 0


    return front, back


def cast_bvh_ray_from_mouse(mousepos, candidates=None, depsgraph=None, exclude_decals=True, debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    # get candidate objects, that could be hit
    if not candidates:
        candidates = bpy.context.visible_objects

    if exclude_decals:
        objects = [(obj, None) for obj in candidates if obj.type == "MESH" and not obj.DM.isdecal]
    else:
        objects = [(obj, None) for obj in candidates if obj.type == "MESH"]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    for obj, src in objects:
        mx = obj.matrix_world
        mxi = mx.inverted()

        ray_origin = mxi @ origin_3d
        ray_direction = mxi.to_3x3() @ vector_3d

        bm = bmesh.new()

        # evaluated or original mesh
        mesh = obj.evaluated_get(depsgraph).to_mesh() if depsgraph else obj.data
        bm.from_mesh(mesh)

        bvh = BVH.FromBMesh(bm)

        location, normal, index, distance = bvh.ray_cast(ray_origin, ray_direction)

        # recalculate distance in worldspace
        if distance:
            distance = (mx @ location - origin_3d).length

        bm.free()

        if debug:
            print("candidate:", obj.name, location, normal, index, distance)

        if distance and distance < hitdistance:
            hitobj, hitlocation, hitnormal, hitindex, hitdistance = obj, mx @ location, mx.to_3x3() @ normal, index, distance


    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)
        print()

    if hitobj:
        return hitobj, hitlocation, hitnormal, hitindex, hitdistance

    return None, None, None, None, None


# RAYCASTING OBJ

def cast_obj_ray_from_object(source, ray_direction, backtrack=None, limit=None, exclude_decals=True, debug=False):
    mxw = source.matrix_world
    origin, _, _ = mxw.decompose()
    direction = mxw @ Vector(ray_direction) - origin

    # when the object is perfectly on the face of another object, you may miss the face with the ray, so shift the origin in the opposite direction
    if backtrack:
        origin = origin - direction * backtrack

    # get candidate objects, that could be hit
    if exclude_decals:
        visible = [obj for obj in bpy.context.visible_objects if obj.type == "MESH" and obj != source and not obj.DM.isdecal]
    else:
        visible = [obj for obj in bpy.context.visible_objects if obj.type == "MESH" and obj != source]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    for obj in visible:
        mx = obj.matrix_world
        mxi = mx.inverted()

        origin_local = mxi @ origin
        direction_local = mxi.to_3x3() @ direction

        success, location, normal, index = obj.ray_cast(origin=origin_local, direction=direction_local)
        distance = (mx @ location - origin).length if success else sys.maxsize

        if debug:
            print("candidate:", success, obj.name, location, normal, index, distance)


        # check direction of face if something was hit
        if success:
            dot = normal.dot(direction_local)

            # it's facing the wrong way, so cast another ray in the opposite direction
            if dot > 0:
                rsuccess, rlocation, rnormal, rindex = obj.ray_cast(origin=origin_local, direction=direction_local * -1)
                rdistance = (mx @ rlocation - origin).length if rsuccess else sys.maxsize

                if debug:
                    print(" reverse candidate:", rsuccess, obj.name, rlocation, rnormal, rindex, rdistance)

                # check if the reverse cast hits a face with the correct direction and see it its distance is shorter than th other one
                if rsuccess and rnormal.dot(direction_local) < 0 and rdistance < distance:
                    location = rlocation
                    normal = rnormal
                    index = rindex
                    distance = rdistance

                    if debug:
                        print("  reverse ray cast found a closer and properly aligned face.")

                else:
                    distance = None

                    if debug:
                        print(" a backface was hit, treating it as if nothing was hit.")

        if success:
            if distance < hitdistance:
                # Matrix.to_3x3() removes the transform and shear channels from the matrix,
                # ####: so that the scale and rotation is the only thing we are multiplying, which is used to bring direction vectors into another space
                hitobj, hitlocation, hitnormal, hitindex, hitdistance = obj, mx @ location, mx.to_3x3() @ normal, index, distance


    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)
        print()

    if hitobj:
        if limit:
            if hitdistance < limit:
                return hitobj, hitlocation, hitnormal, hitindex, hitdistance
            else:
                if debug:
                    print("hit is beyond the limit")
                return None, None, None, None, None

        else:
            return hitobj, hitlocation, hitnormal, hitindex, hitdistance

    return None, None, None, None, None


def cast_obj_ray_from_mouse(mousepos, candidates=None, exclude_decals=True, debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    # get candidate objects, that could be hit
    if not candidates:
        candidates = bpy.context.visible_objects

    if exclude_decals:
        objects = [(obj, None) for obj in candidates if obj.type == "MESH" and not obj.DM.isdecal]
    else:
        objects = [(obj, None) for obj in candidates if obj.type == "MESH"]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    for obj, src in objects:
        mx = obj.matrix_world
        mxi = mx.inverted()

        ray_origin = mxi @ origin_3d
        ray_direction = mxi.to_3x3() @ vector_3d

        # success, location, normal, index = obj.ray_cast(origin=ray_origin, direction=ray_direction, depsgraph=depsgraph)
        success, location, normal, index = obj.ray_cast(origin=ray_origin, direction=ray_direction)
        distance = (mx @ location - origin_3d).length

        if debug:
            print("candidate:", success, obj.name, location, normal, index, distance)

        if success and distance < hitdistance:
            hitobj, hitlocation, hitnormal, hitindex, hitdistance = obj, mx @ location, mx.to_3x3() @ normal, index, distance

    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)
        print()

    if hitobj:
        return hitobj, hitlocation, hitnormal, hitindex, hitdistance

    return None, None, None, None, None


# FIND NEAREST

def find_nearest(targets, origin, debug=False):
    nearestobj = None
    nearestlocation = None
    nearestnormal = None
    nearestindex = None
    nearestdistance = sys.maxsize

    for target in targets:
        bm = bmesh.new()
        bm.from_mesh(target.data)
        bvh = BVH.FromBMesh(bm)

        mx = target.matrix_world

        origin_local = mx.inverted() @ origin

        location, normal, index, distance = bvh.find_nearest(origin_local)

        if debug:
            print("candidate:", target, location, normal, index, distance)

        if distance is not None and distance < nearestdistance:
            nearestobj, nearestlocation, nearestnormal, nearestindex, nearestdistance = target, location, normal, index, distance

    if debug:
        print("best hit:", nearestobj, nearestlocation, nearestnormal, nearestindex, nearestdistance)


    return nearestobj, mx @ nearestlocation, mx.to_3x3() @ nearestnormal, nearestindex, nearestdistance


def shrinkwrap(bm, bmt, debug=False):
    bvh = BVH.FromBMesh(bmt)

    for v in bm.verts:
        location, normal, index, distance = bvh.find_nearest(v.co)

        if debug:
            print(location, normal, index, distance)

        if location:
            v.co = location

    bmt.free()


def find_nearest_normals(bm, targetmesh, debug=False):
    bmt = bmesh.new()
    bmt.from_mesh(targetmesh)
    bvh = BVH.FromBMesh(bmt)

    normals = {}

    for v in bm.verts:
        location, normal, index, distance = bvh.find_nearest(v.co)

        if debug:
            print(location, normal, index, distance)

            # if index:
                # target.data.polygons[index].select = True

        normals[v] = normal

    return normals, bmt


# ORIGINS

def get_origin_from_object(obj, direction=(0, 0, -1), debug=False):
    mxw = obj.matrix_world
    origin, _, _ = mxw.decompose()

    direction = mxw @ Vector(direction) - origin

    if debug:
        print("world origin:", origin, "world direction:", direction)

    return origin, direction


def get_origin_from_object_boundingbox(obj):
    minx = miny = minz = 0
    maxx = maxy = maxz = 0

    for v in obj.data.vertices:
        minx = v.co.x if v.co.x < minx else minx
        miny = v.co.y if v.co.y < miny else miny
        minz = v.co.z if v.co.z < minz else minz

        maxx = v.co.x if v.co.x > maxx else maxx
        maxy = v.co.y if v.co.y > maxy else maxy
        maxz = v.co.z if v.co.z > maxz else maxz

    centerx = (minx + maxx) / 2
    centery = (miny + maxy) / 2
    centerz = (minz + maxz) / 2

    origin = obj.matrix_world @ Vector((centerx, centery, centerz))

    return origin


def get_origin_from_face(obj, index=0, debug=False):
    mxw = obj.matrix_world

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    bm.faces.ensure_lookup_table()

    face = bm.faces[index]
    origin = face.calc_center_median()
    direction = face.normal

    bm.clear()

    if debug:
        print("local origin:", origin, "local direction:", direction)
        print("world origin:", mxw @ origin, "world direction:", mxw.to_3x3() @ direction)

    return mxw @ origin, mxw.to_3x3() @ direction


# MISC

def get_grid_intersection(mousepos):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    xdot = round(Vector((1, 0, 0)).dot(vector_3d), 2)
    ydot = round(Vector((0, 1, 0)).dot(vector_3d), 2)
    zdot = round(Vector((0, 0, 1)).dot(vector_3d), 2)

    # prefer alignment on z
    if abs(zdot * 2) >= max([abs(xdot), abs(ydot)]):
        angle = 0 if zdot <= 0 else 180
        return intersect_line_plane(origin_3d, origin_3d + vector_3d, Vector((0, 0, 0)), Vector((0, 0, 1))), Matrix.Rotation(radians(angle), 4, "X")

    elif abs(ydot) > abs(xdot):
        angle = 90 if ydot >= 0 else -90
        return intersect_line_plane(origin_3d, origin_3d + vector_3d, Vector((0, 0, 0)), Vector((0, 1, 0))), Matrix.Rotation(radians(angle), 4, "X")

    else:
        angle = 90 if xdot <= 0 else -90
        return intersect_line_plane(origin_3d, origin_3d + vector_3d, Vector((0, 0, 0)), Vector((1, 0, 0))), Matrix.Rotation(radians(angle), 4, "Y")
