import bpy
import math
import mathutils
from . import MACHIN3 as m3


def get_center_between_verts(vert1, vert2, center=0.5):
    # return vert1.co + (vert2.co - vert1.co) * center
    return get_center_between_points(vert1.co, vert2.co, center=center)


def get_center_between_points(point1, point2, center=0.5):
    return point1 + (point2 - point1) * center


def get_angle_between_edges(edge1, edge2, radians=True):
    # check if edges share a vert, in which case we can properly set up the vectors and get a reliable angle
    # otherwise and angle could be either 2 or 178 depending on vert ids/order
    centervert = None
    for vert in edge1.verts:
        if vert in edge2.verts:
            centervert = vert

    if centervert:
        vector1 = centervert.co - edge1.other_vert(centervert).co
        vector2 = centervert.co - edge2.other_vert(centervert).co
    else:
        vector1 = edge1.verts[0].co - edge1.verts[1].co
        vector2 = edge2.verts[0].co - edge2.verts[1].co

    if radians:
        return vector1.angle(vector2)
    else:
        return math.degrees(vector1.angle(vector2))


def get_distance_between_points(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)


def get_distance_between_verts(vert1, vert2, getvectorlength=True):
    if getvectorlength:
        vector = vert1.co - vert2.co
        return vector.length
    else:
        return get_distance_between_points(vert1.co, vert2.co)


def get_edge_normal(edge):
    return average_normals([f.normal for f in edge.link_faces])


def check_angle(edges):
    angle = get_angle_between_edges(edges[0], edges[1], radians=False)
    return angle


def check_ngon(edge):
    for f in edge.link_faces:
        if len(f.verts) > 4:
            return f
    return False


def average_normals(normalslist):
    avg = mathutils.Vector()

    for n in normalslist:
        avg += n

    return avg.normalized()


def loop_index_update(bm, debug=False):
    # some of the loop indices can become "dirty" (-1), not sure why
    # unfortunately you can't using index_update() or ensure_lookup_table() for bm.loops

    # but surprisingly, you can manually set them like this:
    lidx = 0
    for f in bm.faces:
        if debug:
            print(f)
        for l in f.loops:
            l.index = lidx
            lidx += 1
            if debug:
                print(" »", l)


def flatten_matrix(mx):
    dimension = len(mx)
    return [mx[j][i] for i in range(dimension) for j in range(dimension)]


def add_vgroup(obj, vert_ids=[], name="", debug=False):
    vgroup = obj.vertex_groups.new(name=name)

    if debug:
        print(" » Created new vertex group: %s" % (name))

    if vert_ids:
        vgroup.add(vert_ids, 1, "ADD")
    else:
        obj.vertex_groups.active_index = vgroup.index
        bpy.ops.object.vertex_group_assign()

    return vgroup


def parent(objs, target, debug=False):
    for obj in objs:
            # find the top most parent in the hierarchy and use its matrix
            t = target
            while t.parent:
                t = t.parent

            targetmx = t.matrix_parent_inverse

            obj.parent = target
            obj.matrix_world = targetmx * obj.matrix_world

            if debug:
                print(" » parented %s to %s" % (obj.name, target.name))


def unparent(objs, debug=False):
    for obj in objs:
        if obj.parent:
            parentmx = obj.parent.matrix_parent_inverse.copy()
            # parentmx = obj.matrix_parent_inverse.copy()

            obj.parent = None
            obj.matrix_world = parentmx * obj.matrix_world

            if debug:
                print(" » unparented %s" % obj.name)
        else:
            if debug:
                print(" » %s is not parented" % obj.name)
