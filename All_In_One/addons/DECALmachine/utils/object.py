import bpy
from mathutils import Matrix
from . modifier import add_boolean, get_subd, get_shrinkwrap


def parent(obj, parentobj):
    if not parentobj.parent and parentobj.matrix_parent_inverse != Matrix():
        print("Resetting %s's parent inverse matrix, as no parent is defined." % (parentobj.name))
        parentobj.matrix_parent_inverse = Matrix()

    p = parentobj
    while p.parent:
        p = p.parent

    obj.parent = parentobj
    obj.matrix_world = p.matrix_parent_inverse @ obj.matrix_world


def unparent(obj):
    if obj.parent:
        p = obj.parent
        while p.parent:
            p = p.parent

        obj.parent = None
        obj.matrix_world = p.matrix_parent_inverse.inverted() @ obj.matrix_world


def intersect(obj, target):
    return add_boolean(obj, target, method='INTERSECT')


def unshrinkwrap(obj):
    subd = get_subd(obj)
    shrinkwrap = get_shrinkwrap(obj)

    if subd:
        obj.modifiers.remove(subd)

    if shrinkwrap:
        obj.modifiers.remove(shrinkwrap)


def flatten(obj, depsgraph=None):
    if not depsgraph:
        depsgraph = bpy.context.evaluated_depsgraph_get()

    oldmesh = obj.data

    obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()

    # remove the old mesh
    bpy.data.meshes.remove(oldmesh, do_unlink=True)


def update_local_view(space_data, states):
    """
    states: list of (obj, bool) tuples, True being in local view, False being out
    """
    if space_data.local_view:
        for obj, local in states:
            obj.local_view_set(space_data, local)


def lock(obj):
    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_rotation_w = True
    obj.lock_scale = (True, True, True)
