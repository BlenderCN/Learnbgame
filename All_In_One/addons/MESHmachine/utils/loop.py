import mathutils
from . support import get_angle_between_edges, get_center_between_verts, get_distance_between_points, average_normals


def topo_loop(vert, loop_candidates, debug=False):
    loop = loop_candidates[0]

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                print("topo loop:", loop.index)
                loop.select = True
        else:
            print("topo loop:", loop.index)
            loop.select = True
    return loop


def biggest_angle_loop(vert, edge, loop_candidates, debug=False):
    angles = []
    for e in loop_candidates:
        a = int(get_angle_between_edges(edge, e, radians=False))
        angles.append((a, e))

    # sorting from biggest to smallest
    angles = sorted(angles, key=lambda a: a[0], reverse=True)

    a1 = angles[0][0]
    a2 = angles[1][0]

    # if a1 == a2:
    if abs(a1 - a2) < 10:
        if debug:
            # print("angles are the same")
            print("angles (almost) the same")
        return

    angle, loop = angles[0]

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                print("biggest angle loop:", loop.index)
                loop.select = True
        else:
            print("biggest angle loop:", loop.index)
            loop.select = True
    return loop, angle


def magic_loop(bm, vert, edge, connected, strict, debug=False):
    # get "the face" to draw the magic loop on
    face = [f for f in vert.link_faces if not f.select and f not in edge.link_faces][0]

    # the 2 faces bordering the sweep edge
    f1 = edge.link_faces[0]
    f2 = edge.link_faces[1]

    # TODO: maybe you shouldnt get the face center medians and face normals, but instead the medians and normals of a triangle created form the face
    # should possibly deals better with non planar faces

    # face median centers
    m1co = f1.calc_center_median()  # NOTE: there's also calc_center_median_weighted()
    m2co = f2.calc_center_median()

    # move them both to the same distance from the edge, this ensures the resultuing loop is perfectly aligned with the edge
    if strict:
        # first get a center point on the edge
        medgeco = get_center_between_verts(vert, edge.other_vert(vert))

        # get the minium distance distances
        d1 = get_distance_between_points(medgeco, m1co)
        d2 = get_distance_between_points(medgeco, m2co)

        if d1 < d2:
            m2dir = m2co - medgeco
            m2co = medgeco + m2dir.normalized() * d1

        if d2 < d1:
            m1dir = m1co - medgeco
            m1co = medgeco + m1dir.normalized() * d2

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                # if self.strict:
                    # medge = bm.verts.new()
                # medge.co = medgeco

                m1 = bm.verts.new()
                m1.co = m1co

                m2 = bm.verts.new()
                m2.co = m2co
        else:
            # if self.strict:
                # medge = bm.verts.new()
                # medge.co = medgeco

            m1 = bm.verts.new()
            m1.co = m1co

            m2 = bm.verts.new()
            m2.co = m2co

    # points where face normals intersect "the face"
    i1co = mathutils.geometry.intersect_line_plane(m1co, m1co + f1.normal, vert.co, face.normal)
    i2co = mathutils.geometry.intersect_line_plane(m2co, m2co + f2.normal, vert.co, face.normal)

    if not all([i1co, i2co]):
        print("aborting magic loop, \"the face\" could not be interesected")
        return

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                i1 = bm.verts.new()
                i1.co = i1co

                i2 = bm.verts.new()
                i2.co = i2co

                bm.edges.new((m1, i1))
                bm.edges.new((m2, i2))
        else:
            i1 = bm.verts.new()
            i1.co = i1co

            i2 = bm.verts.new()
            i2.co = i2co

            bm.edges.new((m1, i1))
            bm.edges.new((m2, i2))

    # projecting the intersection points across the centeredge endpoint vert, "the vert"
    crossv1co = vert.co + (vert.co - i1co)
    crossv2co = vert.co + (vert.co - i2co)

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                crossv1 = bm.verts.new()
                crossv1.co = crossv1co

                crossv2 = bm.verts.new()
                crossv2.co = crossv2co

                bm.edges.new((crossv1, i1))
                bm.edges.new((crossv2, i2))

                bm.edges.new((crossv1, crossv2))
        else:
            crossv1 = bm.verts.new()
            crossv1.co = crossv1co

            crossv2 = bm.verts.new()
            crossv2.co = crossv2co

            bm.edges.new((crossv1, i1))
            bm.edges.new((crossv2, i2))

            bm.edges.new((crossv1, crossv2))

    # point orthogonal to the crossedge in the direction of "the vert"( = the closest point on that vector to "the vert")
    crossvco, distance = mathutils.geometry.intersect_point_line(vert.co, crossv1co, crossv2co)

    # check the direction of the vert-crossv vector, against the other_vert-vert direction
    # if its not the same, the vert-crossv vector needs to be flipped, or rather the crossv vert needs to be on the other side
    vert_crossv = crossvco - vert.co
    othervert_vert = vert.co - edge.other_vert(vert).co

    dot = vert_crossv.dot(othervert_vert)

    if dot < 0:
        newdir = vert.co - crossvco
        crossvco = vert.co + newdir
        if debug:
            if type(debug) is list:
                if vert.index in debug:
                    print("flipping the magic loop edge")
            else:
                print("flipping the magic loop edge")

    crossv = bm.verts.new()
    crossv.co = crossvco

    loop = bm.edges.new((vert, crossv))
    bm.edges.index_update()

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                bm.edges.index_update()
                print("magic loop:", loop.index)
                loop.select = True
        else:
            bm.edges.index_update()
            print("magic loop:", loop.index)
            loop.select = True
    return loop


def projected_loop(bm, vert, edge, debug=False):
    # get "the face" to draw the magic loop on
    face = [f for f in vert.link_faces if not f.select and f not in edge.link_faces][0]
    # avg_face_normal = average_normals([f.normal.normalized() for f in vert.link_faces if not f.select and f not in edge.link_faces])

    v1 = vert
    v2 = edge.other_vert(v1)

    # we are now offsetting the v1.co's a small amount
    # this is a safe guard for loops that go 90 degreees (which should  not actually be a valid chamfer)
    # normals = [f.normal.normalized() for f in edge.link_faces]
    normals = [f.normal.normalized() for f in edge.link_faces if f.select]

    avg_edge_normal = average_normals(normals) * 0.1

    # the direction of the offset is important, see 054_fuse_fail2_xeon.blend
    # --o       |
    #   | vs _ _o

    # we average the edge and face normals and get the dot product from it with the v1_v2 vector
    avg_edge_face_normals = average_normals([avg_edge_normal, face.normal])
    v1_v2_dir = v2.co - v1.co

    dot = v1_v2_dir.dot(avg_edge_face_normals)

    if dot < 0:
        v1co_offset = v1.co - avg_edge_normal
        if debug:
            print("Offsetting in a negative direction")
    else:
        v1co_offset = v1.co + avg_edge_normal
        if debug:
            print("Offsetting in a positive direction")

    # return

    # extend in the direction of "the edge" (v2 to v1)
    edge_dir = v1.co - v2.co
    # ext_edgeco = v1.co + edge_dir
    ext_edgeco = v1co_offset + edge_dir

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                ext_edge = bm.verts.new()
                ext_edge.co = ext_edgeco
        else:
            ext_edge = bm.verts.new()
            ext_edge.co = ext_edgeco

    # return

    # add the face normal to get a perpendicular vector
    perpco = ext_edgeco + face.normal
    # perpco = ext_edgeco + avg_face_normal

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                perp = bm.verts.new()
                perp.co = perpco
        else:
            perp = bm.verts.new()
            perp.co = perpco


    # intersect with the face to get the point, which is gonna be the end point of the loop
    ico = mathutils.geometry.intersect_line_plane(ext_edgeco, perpco, v1.co, face.normal)
    # ico = mathutils.geometry.intersect_line_plane(ext_edgeco, perpco, v1.co, avg_face_normal)

    i = bm.verts.new()
    i.co = ico

    loop = bm.edges.new((v1, i))
    bm.edges.index_update()

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                bm.edges.index_update()
                print("projected loop:", loop.index)
                loop.select = True

                bm.edges.new((perp, ext_edge))
        else:
            bm.edges.index_update()
            print("projected loop:", loop.index)
            loop.select = True

            bm.edges.new((i, ext_edge))
    return loop


def ngon_loop(ngon, edge, vert, debug=False):
    for e in ngon.edges:
        if e != edge and vert in e.verts:
            if debug:
                print("ngon loop")
            return e


def angle_loop(bm, vert, connected, debug=False):
    vert1 = connected[0].other_vert(vert)
    vert2 = connected[1].other_vert(vert)

    v = bm.verts.new()
    v.co = get_center_between_verts(vert1, vert2)

    loop = bm.edges.new((vert, v))

    if debug:
        print("angle loop")
    return loop
