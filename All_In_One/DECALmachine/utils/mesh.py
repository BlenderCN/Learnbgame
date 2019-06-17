import bmesh


def hide(mesh):
    for el in set(mesh.polygons) | set(mesh.edges) | set(mesh.vertices):
        el.hide = True


def unhide(mesh):
    for el in set(mesh.polygons) | set(mesh.edges) | set(mesh.vertices):
        el.hide = False


def select(mesh):
    for el in set(mesh.polygons) | set(mesh.edges) | set(mesh.vertices):
        el.select = True


def deselect(mesh):
    for el in set(mesh.polygons) | set(mesh.edges) | set(mesh.vertices):
        el.select = False


def blast(mesh, prop, type):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()

    if prop == "hidden":
        faces = [f for f in bm.faces if f.hide]

    elif prop == "visible":
        faces = [f for f in bm.faces if not f.hide]

    elif prop == "selected":
        faces = [f for f in bm.faces if f.select]

    bmesh.ops.delete(bm, geom=faces, context=type)

    bm.to_mesh(mesh)
    bm.clear()


def loop_index_update(bm, debug=False):
    """
    some of the loop indices can become "dirty" (-1), not sure why
    unfortunately you can't using index_update() or ensure_lookup_table() for bm.loops

    but surprisingly, you can manually set them like this:
    """

    lidx = 0

    for f in bm.faces:
        if debug:
            print(f)
        for l in f.loops:
            l.index = lidx
            lidx += 1
            if debug:
                print(" »", l)


def smooth(mesh, smooth=True):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bm.verts.ensure_lookup_table()

    for f in bm.faces:
        f.smooth = smooth

    bm.to_mesh(mesh)
    bm.clear()
