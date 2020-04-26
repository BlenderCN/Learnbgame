import sys


def build_mesh_graph(verts, edges, topo=True):
    mg = {}
    for v in verts:
        mg[v] = []

    for e in edges:
        distance = 1 if topo else e.calc_length()

        mg[e.verts[0]].append((e.verts[1], distance))
        mg[e.verts[1]].append((e.verts[0], distance))

    return mg


def get_shortest_path(bm, vstart, vend, topo=False, select=False):
    """
    author: "G Bantle, Bagration, MACHIN3",
    source: "https://blenderartists.org/forum/showthread.php?58564-Path-Select-script(Update-20060307-Ported-to-C-now-in-CVS",
    video: https://www.youtube.com/watch?v=_lHSawdgXpI
    """

    def dijkstra(mg, vstart, vend, topo=True):
        # initiate dict to collect distances from stat vert to every other vert
        d = dict.fromkeys(mg.keys(), sys.maxsize)

        # predecessor dict to track the path walked
        predecessor = dict.fromkeys(mg.keys())

        # the distance of the start vert to itself is 0
        d[vstart] = 0

        # keep track of what verts are seen and add the the accumulated distances to those verts
        unknownverts = [(0, vstart)]

        # with topo you can exit as soon as you hit the vend, without topo you can't, because the shorter distance my involve more vert hops
        # while (topo and vstart != vend) or (not topo and unknownverts):
        while unknownverts:
            # sorting actually doesn't seem to  be required, but it was in the original source
            # I question why the list needs to be sorted by index at all. also, doing it via the lambda function is very slow for some reason
            # unknownverts.sort(key=lambda x: x[1].index)

            # get the next vert that is closest to vstart
            dist, vcurrent = unknownverts[0]

            # use the mesh graph to retrieve the other verts connected
            others = mg[vcurrent]

            # choose the next vert with the shortest accumulated distance
            for vother, distance in others:
                if d[vother] > d[vcurrent] + distance:
                    d[vother] = d[vcurrent] + distance

                    unknownverts.append((d[vother], vother))
                    predecessor[vother] = vcurrent

            # we've finished exploring this vert, pop it
            unknownverts.pop(0)

            # you can break out early when determening the topological distances
            if topo and vcurrent == vend:
                break

        # backtrace from the end vertex using the predecessor dict
        path = []
        endvert = vend

        while endvert is not None:
            path.append(endvert)
            endvert = predecessor[endvert]

        return reversed(path)

    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    verts = [v for v in bm.verts]
    edges = [e for e in bm.edges]

    mg = build_mesh_graph(verts, edges, topo)

    # vert list, shortest dist from vstart to vend
    path = dijkstra(mg, vstart, vend, topo)

    # remove duplicates, keeps order, see https://stackoverflow.com/a/480227
    path = f7(path)

    # optionally select the path
    if select:
        for v in path:
            v.select = True

    return path
