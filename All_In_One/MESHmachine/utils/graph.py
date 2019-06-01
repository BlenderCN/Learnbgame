def build_mesh_graph(bm, debug=False):
    # create meshgraph {vertex_idx: [(connected_vertex_idx, connected_vertex.select, connected_edge.select), ...]}
    mesh_graph = {}
    for v in bm.verts:
        mesh_graph[v.index] = []

    for edge in bm.edges:
        mesh_graph[edge.verts[0].index].append((edge.verts[1].index, edge.verts[1].select, edge.select))
        mesh_graph[edge.verts[1].index].append((edge.verts[0].index, edge.verts[0].select, edge.select))

    if debug:
        for idx in mesh_graph:
            print(idx, mesh_graph[idx])

    return mesh_graph


def build_edge_graph(verts, edges, debug=False):
    mg = {}
    for v in verts:
        mg[v.index] = {"fixed": v.tag,
                       "connected": [],
                       "children": []}

    for e in edges:
        v1 = e.verts[0]
        v2 = e.verts[1]

        mg[v1.index]["connected"].append((v2.index, v2.tag, e.calc_length()))
        mg[v2.index]["connected"].append((v1.index, v1.tag, e.calc_length()))

    if debug:
        for idx in mg:
            print(idx, mg[idx])

    return mg
