import bmesh


def init_bm(mesh):
    bm = bmesh.from_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()
    return bm


def compare_loops(luv1, luv2):
    return luv1.uv[0] == luv2.uv[0] and luv1.uv[1] == luv2.uv[1]


def get_island(bm, f):
    island = {f.index}
    faces_a = [f]
    faces_b = []
    uvl = bm.loops.layers.uv.verify()
    select = False

    while faces_a:
        for f in faces_a:
            for l in f.loops:
                select = select or l[uvl].select
                for ll in l.vert.link_loops:
                    if ll == l:
                        continue
                    if not compare_loops(l[uvl], ll[uvl]):
                        continue
                    f_next = ll.face
                    if f_next.index not in island:
                        island.add(f_next.index)
                        faces_b.append(f_next)

        faces_a, faces_b = faces_b, faces_a
        faces_b.clear()

    return island, select


def get_islands(bm, selected_only=False):
    faces = set()
    islands = []
    for f in bm.faces:
        if f.index in faces:
            continue
        island, select = get_island(bm, f)
        faces |= island
        if not selected_only or select:
            islands.append(island)

    return islands

