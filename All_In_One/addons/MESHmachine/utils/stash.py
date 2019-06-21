import bpy
import re
from . support import flatten_matrix


def create_stash(active, source):
    # create stash objet
    stashindex = len(active.MM.stashes)
    stashname = "stash_%d" % (stashindex)

    stashobj = source.copy()
    stashobj.data = source.data.copy()
    stashobj.MM.isstashobj = True
    stashobj.use_fake_user = True
    stashobj.name = "%s_%s" % (source.name, stashname)

    # clean out any potential stash references in the stash itself
    while stashobj.MM.stashes:
        stashobj.MM.stashes.remove(0)

    # add the new stash to the active object's stash collection
    s = active.MM.stashes.add()
    s.name = stashname
    s.index = stashindex
    s.obj = stashobj

    # and update the active_stash_idx value
    active.MM.active_stash_idx = stashindex

    # we want to keep the existing location and rotation and scale of the source obj, but we need the origin to match the active origin
    # we need this because the data_transfer mod expects it this way if use_object_transform is False(it works in local space)

    # get obj and active matrices
    stashmx = stashobj.matrix_world.copy()
    targetmx = active.matrix_world.copy()
    targetmx_inv = targetmx.inverted()

    # store the matrices on the stashobj
    stashobj.MM.stashmx = flatten_matrix(stashmx)
    stashobj.MM.stashtargetmx = flatten_matrix(targetmx)

    # set obj origin to active
    stashobj.matrix_world = active.matrix_world

    # move the verts back into their original location
    mesh = s.obj.data
    for vert in mesh.vertices:
        vert.co = targetmx_inv * stashmx * vert.co


    print(" + %s" % (stashname))

    return s


def retrieve_stash(active, stashobj):
    retrieved = stashobj.copy()
    retrieved.data = stashobj.data.copy()

    retrieved.MM.isstashobj = False
    retrieved.use_fake_user = False
    bpy.context.scene.objects.link(retrieved)

    stashmx = retrieved.MM.stashmx
    targetmx = retrieved.MM.stashtargetmx
    activemx = active.matrix_world if active else targetmx  # orphan retrieval

    # bring the object's origin back to its original location and orient the object properly again (relative to the active)
    if stashmx != targetmx:
        # this was stashed from one object to the active one with differing matrices
        retrieved.matrix_world = activemx * targetmx.inverted() * stashmx

        for vert in retrieved.data.vertices:
            vert.co = stashmx.inverted() * targetmx * vert.co

    else:
        retrieved.matrix_world = activemx

    # undo the stash naming on on the retrieved, for example: "Cube.001_stash_0.001"
    nameRegex = re.compile(r"(.*)_stash_.*")
    mo = nameRegex.match(retrieved.name)
    basename = mo.group(1)

    retrieved.name = basename

    return retrieved


def transfer_stashes(source, target, restash=False):
    print("Transfering stashes from '%s' to '%s'" % (source.name, target.name))

    activestashlen = len(target.MM.stashes)

    for stash in source.MM.stashes:
        # retrieving and restashing
        if restash:
            r = retrieve_stash(source, stash.obj)
            s = create_stash(target, r)
            bpy.data.objects.remove(r, do_unlink=True)

            print(" » retrieved and re-stashed %s's %s to %s's %s" % (source.name, stash.name, target.name, s.name))

        # transfering
        else:
            s = target.MM.stashes.add()
            s.index = stash.index + activestashlen
            s.name = "stash_%d" % (s.index)
            s.obj = stash.obj

            s.flipped = stash.flipped

            print(" » transfered %s's %s to %s's %s" % (source.name, stash.name, target.name, s.name))

    target.MM.active_stash_idx = len(target.MM.stashes) - 1
