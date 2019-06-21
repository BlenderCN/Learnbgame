import math
import mathutils
from . graph import build_mesh_graph
from . loop import projected_loop, topo_loop, biggest_angle_loop
from . debug import debug_sweeps, vert_debug_print
from . support import get_distance_between_points, check_ngon, get_center_between_points, average_normals
from . ui import popup_message
from . import MACHIN3 as m3


def get_2_rails(bm, mg, verts, faces, reverse=False, debug=False):
    length_mode = False

    # ngons and tris
    ngons = [f for f in faces if len(f.verts) > 4]
    tris = [f for f in faces if len(f.verts) < 4]

    if ngons:
        # print("Selection includes ngons, aborting")
        popup_message("Selection includes ngons, aborting", title="Illegal Selection")
        return
    elif tris:
        # print("Selection includes tris, aborting")
        popup_message("Selection includes tris, aborting", title="Illegal Selection")
        return

    if len(faces) == 0:
        # print("Selection does not include faces, aborting")
        popup_message("Selection does not include faces, aborting", title="Illegal Selection")
        return
    elif len(faces) == 1:
        if debug:
            print("Selection is a single quad, determining direction via edge length")
        length_mode = True
    else:
        if debug:
            print("Determining direction via vert hops")


    corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

    # if no corners are found, its a cyclic selection!
    if len(corners) == 0:
        cyclic = True

        # take one of the faces and deselect it
        f = faces[0]
        f.select_set(False)

        if debug:
            print("Selection is cyclic")
            print("cyclic deselect of face:", f.index)

        # build a new mesh graph and run the corners algo again
        mg = build_mesh_graph(bm)
        corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

        # if there's still no corners, you are dealing with a cyclic fuse/bevel selection
        if not corners:
            # print("Selection is not a chamfer, aborting")
            popup_message("Selection is not a chamfer, aborting", title="Illegal Selection")
            return
    else:
        cyclic = False

    if debug:
        print("corner verts:", [c.index for c in corners])

    # get the short sides, the sides where its one hop to the next corner
    # c1 - o - o - c3
    # |    |   |   |  X sweeps
    # c2 - o - o - c4
    #    2  rails

    # pick one corner
    c1 = corners[0]
    corners.remove(c1)

    c2_candidates = [c for c in corners if c.index in [idx for idx, vselect, eselect in mg[c1.index] if eselect]]

    # if nothing can be found for c2, its because c1 and c2 arent seperated by one hop, it's not a chamfer selection
    if not c2_candidates:
        # print("Selection is not a chamfer, aborting")
        popup_message("Selection is not a chamfer, aborting", title="Illegal Selection")
        return
    elif length_mode:
        # get two opposing edges and compare the average lengths
        c2 = c2_candidates[0]
        c3 = c2_candidates[1]

        corners.remove(c2)
        corners.remove(c3)

        c4 = corners[-1]

        edgeA1 = bm.edges.get([c1, c3])
        edgeA2 = bm.edges.get([c2, c4])

        edgeB1 = bm.edges.get([c1, c2])
        edgeB2 = bm.edges.get([c3, c4])

        averageA = (edgeA1.calc_length() + edgeA2.calc_length()) / 2
        averageB = (edgeB1.calc_length() + edgeB2.calc_length()) / 2

        if averageA >= averageB:
            rail1 = [c1, c3]
            rail2 = [c2, c4]
        else:
            rail1 = [c1, c2]
            rail2 = [c3, c4]

        if reverse:
            rail1, rail2 = [rail1[0], rail2[0]], [rail1[1], rail2[1]]
    else:
        c2 = c2_candidates[0]
        corners.remove(c2)

        # walk the polygons, this will establish the sequence of sweeps

        rail1 = [c1]
        rail2 = [c2]

        if debug:
            print("rail1 start:", rail1[-1].index)
            print("rail2 start:", rail2[-1].index)

        not_yet_walked = [f for f in faces]
        while not_yet_walked:
            v1 = rail1[-1]
            v2 = rail2[-1]
            sweep = bm.edges.get([v1, v2])
            if debug:
                print("sweep:", sweep.index)

            current_face = [f for f in sweep.link_faces if f.select and f in not_yet_walked]

            if current_face:
                cf = current_face[0]
                if debug:
                    print("current face:", cf.index)
                not_yet_walked.remove(cf)

                next_verts = [v for v in cf.verts if v not in rail1 + rail2]
                if debug:
                    print("next verts:", [v.index for v in next_verts])

                # TODO: i dont think you need to iterate over all verts here???
                # rail1_next_vert = [bm.verts[idx] for idx, _, _ in mg[v1.index] if bm.verts[idx] in next_verts][0]
                rail1_next_vert = [e.other_vert(v1) for e in v1.link_edges if e.other_vert(v1) in next_verts][0]
                if debug:
                    print("next vert 1:", rail1_next_vert.index)

                # rail2_next_vert = [bm.verts[idx] for idx, _, _ in mg[v2.index] if bm.verts[idx] in next_verts][0]
                rail2_next_vert = [e.other_vert(v2) for e in v2.link_edges if e.other_vert(v2) in next_verts][0]
                if debug:
                    print("next vert 2:", rail2_next_vert.index)
                    print()

                rail1.append(rail1_next_vert)
                rail2.append(rail2_next_vert)
            else:
                break

        # reselect the face that was unselected when cyclicity was detected
        # NOTE: we do not need to append the first rails to the end, that would result duplicate magic loop creation or other unwanted results if debug mode is on(which changes some edge selection states)
        if cyclic:
            f.select_set(True)

    #TODO: check if any rail edges are non-manifold

    if debug:
        rail1ids = [str(v.index) for v in rail1]
        rail2ids = [str(v.index) for v in rail2]
        print(" » ".join(rail1ids))
        print(" » ".join(rail2ids))

    return (rail1, rail2), cyclic


def init_sweeps(bm, active, rails, verts=True, edges=True, loop_candidates=True, freestyle=True, loops=True, loop_types=True, handles=True, avg_face_normals=True, debug=False):
    # initialize the list of sweep dictionaries
    sweeps = []
    for idx, vertpair in enumerate(zip(rails[0], rails[1])):
        sweep = {}
        if verts:
            sweep["verts"] = vertpair
        if edges:
            sweep["edges"] = [bm.edges.get(vertpair)]
        if loop_candidates:
            # exclude 0 length edges

            # debug output if you run into an zero length edge
            candidates = []
            for v in sweep["verts"]:
                side = []
                for e in v.link_edges:
                    if not e.select:
                        if e.calc_length() != 0:
                            side.append(e)
                        elif debug:
                            print("Zero length edge detected, ignoring edge %d. Results may be unexpected!" % (e.index))

                # prefer or excluding freestyle edges if any are present!
                # NOTE: it looks like you can't access freestyle layers using bmes
                # https://developer.blender.org/T47275A
                if freestyle:
                    fsloopcount = sum([active.data.edges[e.index].use_freestyle_mark for e in side])

                    # print("freestyle loop count:", fsloopcount)
                    # print("side count:", len(side))

                    if fsloopcount > 0:
                        if fsloopcount == 1 and len(side) != 1:
                            side = [e for e in side if active.data.edges[e.index].use_freestyle_mark]
                            if debug:
                                print("Using freestyle edge %d as the only loop candidate." % (side[0].index))
                        else:
                            exclude = [e for e in side if active.data.edges[e.index].use_freestyle_mark]
                            if debug:
                                for e in exclude:
                                    print("Excluding freestyle edge %d from loop edge candidates" % (e.index))
                            side = [e for e in side if e not in exclude]

                candidates.append(side)
            sweep["loop_candidates"] = candidates
        if loops:
            sweep["loops"] = []
        if loop_types:
            sweep["loop_types"] = []
        if handles:
            sweep["handles"] = []
        if avg_face_normals:
            inos = []
            for v in sweep["verts"]:
                inos.append(average_normals([f.normal.normalized() for f in v.link_faces if not f.select and f not in sweep["edges"][0].link_faces]))
            sweep["avg_face_normals"] = inos

        sweeps.append(sweep)
        if debug:
            debug_sweeps([sweeps[-1]], index=idx, verts=verts, edges=edges, loop_candidates=loop_candidates, loops=loops, loop_types=loop_types, handles=handles, avg_face_normals=avg_face_normals)

    return sweeps


def create_loop_intersection_handles(bm, sweeps, tension, debug=False):
    # tension = 1
    for idx, sweep in enumerate(sweeps):
        # get all the elements we'll need
        edge = sweep["edges"][0]
        edgelen = edge.calc_length()

        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        loop1 = sweep["loops"][0]
        loop1_end = loop1.other_vert(v1)
        loop1_dir = v1.co - loop1_end.co

        loop2 = sweep["loops"][1]
        loop2_end = loop2.other_vert(v2)
        loop2_dir = v2.co - loop2_end.co

        if debug:
            print()
            print("sweep:", idx)
            print(" » edge:", edge.index, "length:", edgelen)
            print(" » vert 1:", v1.index)
            print("   » loop", loop1.index)
            print("     » loop end", loop1_end.index)
            print("     » direction", loop1_dir)
            print()
            print(" » vert 2:", v2.index)
            print("   » loop", loop2.index)
            print("     » loop end", loop2_end.index)
            print("     » direction", loop2_dir)
            print()


        loop_angle = math.degrees(loop1_dir.angle(loop2_dir))
        if debug:
            print("loop angle:", loop_angle)

        # tuple, the first item is the handle location for the first edge, the second for the other
        h = mathutils.geometry.intersect_line_line(v1.co, loop1_end.co, v2.co, loop2_end.co)

        # if h is None:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
        # if h is None or -2 <= loop_angle <= 2 or 178 <= loop_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
        if h is None or 178 <= loop_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
            if debug:
                print(" » handles could not be determined via line-line instersection")
                print(" » falling back to closest point to handle vector")

            h1_full = mathutils.geometry.intersect_point_line(v2.co, v1.co, loop1_end.co)[0]
            h2_full = mathutils.geometry.intersect_point_line(v1.co, v2.co, loop2_end.co)[0]

            # taking the half distance
            # h1 = v1.co + ((h1_full - v1.co) / 2)
            # h2 = v2.co + ((h2_full - v2.co) / 2)
            h1 = v1.co + (h1_full - v1.co)
            h2 = v2.co + (h2_full - v2.co)

            h = (h1, h2)
        elif -2 <= loop_angle <= 2:  # if loops on both sides are parallel, this should not happen in a valid chamfer as its 90 degrees on both sides |._.|
            if debug:
                print(" » loops on both sides are parallel and go in the same direction")
                print(" » falling back to handle creation from loop edge")
            h1 = v1.co + (loop1_end.co - v1.co).normalized()
            h2 = v2.co + (loop2_end.co - v2.co).normalized()

            h = (h1, h2)

        # in an edge case like this:  _._./  the handle of the right loop edge will be in the same location as the end vert
        # this will result in an exception when trying to determine the angle between the handles (dirangle), so push that handle out by half the distance of the end points
        if v1.co == h[0] or v2.co == h[1]:
            # h1 = (v1.co + loop1_dir.normalized() * edgelen / 2)
            # h2 = (v2.co + loop2_dir.normalized() * edgelen / 2)

            # h = (h1, h2)
            if debug:
                # print(" » handle position lies on end point, created aligned center handles instead")
                print(" » handle position lies on end point")
                print(" » falling back to handle creation from loop edge")

            h1 = v1.co + (loop1_end.co - v1.co).normalized()
            h2 = v2.co + (loop2_end.co - v2.co).normalized()

            h = (h1, h2)

        # take the handles and add in the tension
        handle1co = v1.co + ((h[0] - v1.co) * tension)
        handle2co = v2.co + ((h[1] - v2.co) * tension)

        # check if the handle is going into the right direction, which is the direction of the loop edges, towards the sweep edge
        handle1_dir = handle1co - v1.co
        handle2_dir = handle2co - v2.co

        dot1 = loop1_dir.dot(handle1_dir)
        dot2 = loop2_dir.dot(handle2_dir)


        # if necessary, create a new handle with the same length, but the propper direction
        if dot1 < 0:
            handle1co = v1.co + loop1_dir.normalized() * handle1_dir.length
            handle1_dir = handle1co - v1.co

            if debug:
                print(" » flipped handle 1 direction")

        if dot2 < 0:
            handle2co = v2.co + loop2_dir.normalized() * handle2_dir.length
            handle2_dir = handle2co - v2.co
            if debug:
                print(" » flipped handle 2 direction")

        # """

        # check handle length and correct if necessary
        # the length ratio should never be above 1 for a tension of 1, in ideal cases it sits around 0.7 if the surface angle is 90 degrees
        # it looks like the ideal ratio is tension / handle_dir_angle (radians)
        # a good max ratio seems to be ideal ratio + tension

        handle1_v1_dist = get_distance_between_points(v1.co, handle1co)
        handle2_v2_dist = get_distance_between_points(v2.co, handle2co)

        handle1_edge_ratio = handle1_v1_dist / edgelen
        handle2_edge_ratio = handle2_v2_dist / edgelen

        handle_dir_angle = handle1_dir.angle(handle2_dir) + 0.0001  # adding in a tiny amount to prevetn edge case where angle is 0

        ideal_ratio = tension / handle_dir_angle
        max_ratio = tension + ideal_ratio

        if handle1_edge_ratio > max_ratio or handle2_edge_ratio > max_ratio:
            if debug:
                print(" » surface angle:", math.degrees(handle_dir_angle), handle_dir_angle)
                print(" » ideal ratio:", ideal_ratio, "max ratio:", max_ratio)


            if handle1_edge_ratio > max_ratio:
                # handle1co = v1.co + loop1_dir.normalized() * edgelen * ideal_ratio * overshootmod
                if debug:
                    print(" » handle overshoot! handle 1 to edge length ratio:", handle1_edge_ratio)
                    print(" » falling back to closest point to handle vector")

                h1_full = mathutils.geometry.intersect_point_line(v2.co, v1.co, loop1_end.co)[0]

                # taking half the distance + adding in the tension
                # handle1co = v1.co + ((h1_full - v1.co) / 2) * tension
                handle1co = v1.co + (h1_full - v1.co) * tension

            if handle2_edge_ratio > max_ratio:
                # handle2co = v2.co + loop2_dir.normalized() * edgelen * ideal_ratio * overshootmod
                if debug:
                    print(" » handle overshoot! handle 2 to edge length  ratio:", handle2_edge_ratio)
                    print(" » falling back to closest point to handle vector")

                h2_full = mathutils.geometry.intersect_point_line(v1.co, v2.co, loop2_end.co)[0]

                # taking half the distance + adding in the tension
                # handle2co = v2.co + ((h2_full - v2.co) / 2) * tension
                handle2co = v2.co + (h2_full - v2.co) * tension

        sweep["handles"] = [handle1co, handle2co]
        # """

        if debug:
            handle1 = bm.verts.new()
            handle1.co = handle1co

            handle2 = bm.verts.new()
            handle2.co = handle2co

            bm.edges.new((v1, handle1))
            bm.edges.new((v2, handle2))
        # """


def create_face_intersection_handles(bm, sweeps, tension, average=False, debug=False):
    # tension = 1
    for idx, sweep in enumerate(sweeps):
        # get all the elements we'll need
        edge = sweep["edges"][0]
        edgelen = edge.calc_length()

        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        loop1 = sweep["loops"][0]
        loop1_end = loop1.other_vert(v1)
        loop1_dir = v1.co - loop1_end.co

        loop2 = sweep["loops"][1]
        loop2_end = loop2.other_vert(v2)
        loop2_dir = v2.co - loop2_end.co

        ino1 = sweep["avg_face_normals"][0]
        ino2 = sweep["avg_face_normals"][1]

        if debug:
            print()
            print("sweep:", idx)
            print(" » edge:", edge.index, "length:", edgelen)
            print(" » vert 1:", v1.index)
            print("   » loop", loop1.index)
            print("     » loop end", loop1_end.index)
            print("     » direction", loop1_dir)
            print("   » intersection_normal", ino1)
            print()
            print(" » vert 2:", v2.index)
            print("   » loop", loop2.index)
            print("     » loop end", loop2_end.index)
            print("     » direction", loop2_dir)
            print("   » intersection_normal", ino2)
            print()


        ico1 = mathutils.geometry.intersect_line_plane(v1.co, loop1_end.co, v2.co, ino2)
        ico2 = mathutils.geometry.intersect_line_plane(v2.co, loop2_end.co, v1.co, ino1)

        # fall back to the old method:
        if not all([ico1, ico2]):
            if debug:
                print("WARNING: falling back to the old handle creation method")
            create_loop_intersection_handles(bm, [sweeps[idx]], tension, debug=debug)
        else:
            # take the handles and add in the tension
            handle1co = v1.co + ((ico1 - v1.co) * tension)
            handle2co = v2.co + ((ico2 - v2.co) * tension)

            # check if the handle is going into the right direction, which is the direction of the loop edges, towards the sweep edge
            handle1_dir = handle1co - v1.co
            handle2_dir = handle2co - v2.co

            dot1 = loop1_dir.dot(handle1_dir)
            dot2 = loop2_dir.dot(handle2_dir)

            # if necessary, create a new handle with the same length, but the propper direction
            if dot1 < 0:
                handle1co = v1.co + loop1_dir.normalized() * handle1_dir.length
                handle1_dir = handle1co - v1.co

                if debug:
                    print(" » flipped handle 1 direction")

            if dot2 < 0:
                handle2co = v2.co + loop2_dir.normalized() * handle2_dir.length
                handle2_dir = handle2co - v2.co
                if debug:
                    print(" » flipped handle 2 direction")


            if average:
                handle1co = v1.co + handle1_dir.normalized() * (handle1_dir.length + handle2_dir.length) / 2
                handle2co = v2.co + handle2_dir.normalized() * (handle2_dir.length + handle1_dir.length) / 2


            sweep["handles"] = [handle1co, handle2co]


            if debug:
                handle1 = bm.verts.new()
                handle1.co = handle1co

                handle2 = bm.verts.new()
                handle2.co = handle2co

                bm.edges.new((v1, handle1))
                bm.edges.new((v2, handle2))


def create_splines(bm, sweeps, segments, debug=False):
    spline_sweeps = []
    for idx, sweep in enumerate(sweeps):
        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        handle1co = sweep["handles"][0]
        handle2co = sweep["handles"][1]

        # create bezier, but throw away the first and lost coordinates, we have these verts aleady and dont need to create new verts for them
        bezier_verts = mathutils.geometry.interpolate_bezier(v1.co, handle1co, handle2co, v2.co, segments + 2)[1:-1]

        spline_verts = []
        spline_verts.append(v1)

        for vco in bezier_verts:
            v = bm.verts.new()
            v.co = vco
            spline_verts.append(v)

        spline_verts.append(v2)

        if debug:
            bm.verts.index_update()
            print("sweep:", idx)
            print(" » spline verts:", [v.index for v in spline_verts])
            print()
            for vert in spline_verts:
                vert.select = True

        spline_sweeps.append(spline_verts)

    return spline_sweeps


def get_loops(bm, faces, sweeps, force_projected=False, debug=False):
    if debug:
        print()
    # debug = True
    # debug = [113, 109]

    for sweep in sweeps:
        for idx, v in enumerate(sweep["verts"]):
            vert_debug_print(debug, v, "\n" + str(v.index), end=" » ")

            ccount = len(sweep["loop_candidates"][idx])
            vert_debug_print(debug, v, "\nloop count: " + str(ccount))

            # if ccount == 0:
            # if ccount == 0 or (override and idx == 0):
            if ccount == 0 or force_projected:
                # sweep["loops"].append(magic_loop(bm, v, sweep["edges"][0], sweep["loop_candidates"][idx], self.strict, debug=debug))
                # sweep["loop_types"].append("MAGIC")
                loop = projected_loop(bm, v, sweep["edges"][0], debug=debug)
                sweep["loops"].append(loop)
                sweep["loop_types"].append("PROJECTED")
            elif ccount == 1:
                loop_candidate = sweep["loop_candidates"][idx][0]
                edge = sweep["edges"][0]
                link_edges = [e for e in v.link_edges]

                # vert_debug_print(debug, v, "loop_candidate: " + str(loop_candidate.index))
                # vert_debug_print(debug, v, "edge: " + str(edge.index))
                # vert_debug_print(debug, v, "link_edges: " + str([e.index for e in link_edges]))

                if not edge.is_manifold:
                        vert_debug_print(debug, v, "topo loop next to an open boundary")
                elif check_ngon(edge):
                    if check_ngon(loop_candidate):
                        vert_debug_print(debug, v, "topo loop next to an ngon")
                elif check_ngon(loop_candidate) and len(link_edges) == 3:
                # elif len(link_edges) == 3:
                    if 89 < math.degrees(edge.calc_face_angle()) < 91:
                        vert_debug_print(debug, v, "topo loop next to face angled at 90 degrees")
                    else:
                        # vert_debug_print(debug, v, "magic loop redirect")
                        # loop = magic_loop(bm, v, sweep["edges"][0], sweep["loop_candidates"][idx], True, debug=debug)
                        # if loop:
                            # sweep["loops"].append(loop)
                            # sweep["loop_types"].append("MAGIC")
                            # continue
                        vert_debug_print(debug, v, "projected loop redirect")
                        loop = projected_loop(bm, v, sweep["edges"][0], debug=debug)
                        if loop:
                            sweep["loops"].append(loop)
                            sweep["loop_types"].append("PROJECTED")
                            continue
                        else:
                            vert_debug_print(debug, v, "topo loop redirect after projected loop failed")
                else:
                    vert_debug_print(debug, v, "normal topo loop")
                sweep["loops"].append(topo_loop(v, sweep["loop_candidates"][idx], debug=debug))
                sweep["loop_types"].append("TOPO")
            else:
                ret = biggest_angle_loop(v, sweep["edges"][0], sweep["loop_candidates"][idx], debug=debug)
                if ret:
                    loop, angle = ret
                    vert_debug_print(debug, v, "angle: " + str(angle))
                    if 89 <= angle <= 91:  # NOTE: this may need to be dialed in
                    # if 60 <= angle <= 120:
                        vert_debug_print(debug, v, "topo loop redirect after biggest angle returned a 90 degrees angle")
                        loop2 = topo_loop(v, sweep["loop_candidates"][idx], debug=debug)
                        if loop2 == loop:
                            vert_debug_print(debug, v, "projected loop redirect after topo loop returned the same loop as the biggest angle loop")
                            if debug:
                                loop.select = False
                            loop = projected_loop(bm, v, sweep["edges"][0], debug=debug)
                            sweep["loops"].append(loop)
                            sweep["loop_types"].append("PROJECTED")
                        else:
                            sweep["loops"].append(loop2)
                            sweep["loop_types"].append("TOPO")
                    else:
                        sweep["loops"].append(loop)
                        sweep["loop_types"].append("BIGGEST_ANGLE")
                else:
                    # vert_debug_print(debug, v, "magic loop after biggest angle loop found no efinitive result")
                    # sweep["loops"].append(magic_loop(bm, v, sweep["edges"][0], sweep["loop_candidates"][idx], self.strict, debug=debug))
                    # sweep["loop_types"].append("MAGIC")
                    vert_debug_print(debug, v, "projected loop after biggest angle loop found no definitive result")
                    loop = projected_loop(bm, v, sweep["edges"][0], debug=debug)
                    sweep["loops"].append(loop)
                    sweep["loop_types"].append("PROJECTED")


def get_selection_islands(bm, debug=False):
    selected = [f for f in bm.faces if f.select]

    if debug:
        print("selected:", [f.index for f in selected])

    face_islands = []

    while selected:
        island = [selected[0]]
        foundmore = [selected[0]]

        if debug:
            print("island:", [f.index for f in island])
            print("foundmore:", [f.index for f in foundmore])

        while foundmore:
            for e in foundmore[0].edges:
                # get unseen selected border faces
                bf = [f for f in e.link_faces if f.select and f not in island]
                if bf:
                    island.append(bf[0])
                    foundmore.append(bf[0])

            if debug:
                print("popping", foundmore[0].index)

            foundmore.pop(0)

        face_islands.append(island)

        for f in island:
            selected.remove(f)

    if debug:
        print()
        for idx, island in enumerate(face_islands):
            print("island:", idx)
            print(" » ", ", ".join([str(f.index) for f in island]))


    islands = []

    for fi in face_islands:
        vi = []
        ei = []

        for f in fi:
            vi.extend(f.verts)
            ei.extend(f.edges)

            # f.select = False

        islands.append((vi, ei, fi))

    return islands


def get_side(verts, edges, startvert, startloop, endvert=None, flushedges=[], reverse=False, offset=None, debug=False):
    vert = startvert
    loop = startloop

    # initiate those to lists with the start vert and loop
    edges_travelled = [loop.edge]

    startedge = []
    # for a non cylic selection(where an endvert is passed in), grab one potential side edge of the start vert
    # for cyclic selecrions you get this one at the end automatically
    if endvert:
        if startloop.link_loop_prev.edge not in edges:
            startedge.append(startloop.link_loop_prev.edge)

    d = {"vert": vert, "seledge": loop.edge, "edges": startedge, "faces": [loop.face]}
    side = [d]

    while True:
        # non cyclic end
        if vert == endvert:
            # the end vert in non-cyclic selections won't have a seledge, so just add the previous one
            d["seledge"] = edges_travelled[-1]
            break

        # get the next loop
        loop = loop.link_loop_next

        vert = loop.vert
        edge = loop.edge
        face = loop.face

        # abort if an edge is non-manifold
        if not edge.is_manifold:
            return

        # print("vert:", vert.index)
        # print("edge:", edge.index)

        # cyclic end
        if edge in edges_travelled:
            break

        if vert in verts:
            # if you've added this vert before, fetch its dict
            if vert in [s["vert"] for s in side]:
                append = False
                d = [s for s in side if s["vert"] == vert][0]

            # if this vert is not yet in the list of dicts create a new dict
            else:
                append = True
                d = {}
                d["vert"] = vert
                d["edges"] = []
                d["faces"] = []

            if edge in edges:
                edges_travelled.append(edge)
                d["seledge"] = edge
            else:
                d["edges"].append(edge)

            d["faces"].append(face)

            if append:
                side.append(d)

            # if you are on a flushed edge, the next loop is not just link_loop_next
            if edge in flushedges:
                # print("flushed edge radial looping")
                loop = loop.link_loop_radial_next

        # if the current vert is not part of the selection, the next loop is not just link_loop_next..
        else:
            # print("side edge radial looping")
            loop = loop.link_loop_prev.link_loop_radial_next


    # since the loops go in opposite directions, we are now reversing the second side, so the order in both side lists is the same
    if reverse:
        side.reverse()

    # for cyclic selections and offset is needed as well
    if offset:
        side = side[-offset:] + side[:-offset]

    if debug:
        print()
        for d in side:
            print("vert:", d["vert"].index)
            print(" » seledge", d["seledge"].index)
            print(" » edges:", [e.index for e in d["edges"]])
            print(" » faces:", [f.index for f in d["faces"]])

    return side


def get_sides(bm, verts, edges, debug=False):
    if any([not e.is_manifold for e in edges]):
        errmsg = "Non-manifold edges are part of the selection. Failed to determine sides of the selection."
        errtitle = "Non-Manifold Geometry"
        return None, None, None, (errmsg, errtitle)

    # flush the selection, to get any potential "flushedges" see chamfer_fail2a.blend for why
    bm.select_flush(True)
    flushedges = [e for e in bm.edges if e.select and e not in edges]

    for e in flushedges:
        e.select = False

    bm.select_flush(False)

    # find out if the edge selection is cyclic
    # if not get the start and end verts
    ends = []
    for v in verts:
        if sum([e.select for e in v.link_edges]) == 1:
            ends.append(v)

    endslen = len(ends)

    cyclic = False


    # create the side lists of dictionaries, note how cyclic ans non-cyclic are treated differently
    if endslen == 0:
        if debug:
            print("Cyclic edge loop selection")

        cyclic = True

        loops = [l for l in verts[0].link_loops if l.edge in edges]

        sideA = get_side(verts, edges, verts[0], loops[0], flushedges=flushedges, debug=debug)
        sideB = get_side(verts, edges, verts[0], loops[1], flushedges=flushedges, reverse=True, offset=1, debug=debug)

        if sideA and sideB:
            return sideA, sideB, cyclic, None
        else:
            errmsg = "There's a non-manifold edge closeby, failed to determine sides of the selection."
            errtitle = "Non-Manifold Geometry"

            return None, None, None, (errmsg, errtitle)

    elif endslen == 2:
        if debug:
            print("Non-Cyclic edge loop selection")

        loops = [l for v in ends for l in v.link_loops if l.edge in edges]

        # create the side lists of dictionaries
        sideA = get_side(verts, edges, ends[0], loops[0], endvert=ends[1], flushedges=flushedges, debug=debug)
        sideB = get_side(verts, edges, ends[1], loops[1], endvert=ends[0], flushedges=flushedges, reverse=True, debug=debug)

        if sideA and sideB:
            return sideA, sideB, cyclic, None
        else:
            errmsg = "There's a non-manifold edge closeby, failed to determine sides of the selection."
            errtitle = "Non-Manifold Geometry"

            return None, None, None, (errmsg, errtitle)

    else:
        if debug:
            print("Invalid selection.")

        errmsg = "Only single-island cyclic or non-cyclic edge loop selections are supproted."
        errtitle = "Illegal Selection"

        return None, None, None, (errmsg, errtitle)
