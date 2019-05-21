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


def unselect(mesh):
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
