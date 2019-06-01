import bpy
import mathutils
import bmesh
from . support import add_vgroup
from . import MACHIN3 as m3


loopmapping = {"NEAREST FACE": "POLYINTERP_NEAREST",
               "PROJECTED": "POLYINTERP_LNORPROJ",
               "NEAREST NORMAL": "NEAREST_NORMAL",
               "NEAREST POLY NORMAL": "NEAREST_POLYNOR"}


def add_normal_transfer_mod(obj, nrmsrc, name, vgroup, mapping=None, debug=False):
    # add data transfer mod
    data_transfer = obj.modifiers.new(name, "DATA_TRANSFER")
    data_transfer.object = nrmsrc
    data_transfer.use_loop_data = True

    if mapping:
        data_transfer.loop_mapping = loopmapping[mapping]
    else:
        data_transfer.loop_mapping = loopmapping["NEAREST FACE"]

    data_transfer.vertex_group = vgroup.name

    data_transfer.data_types_loops = {'CUSTOM_NORMAL'}
    data_transfer.show_expanded = False
    data_transfer.show_in_editmode = True

    # if you turn this off, you don't need to parent the nrmsrc!
    data_transfer.use_object_transform = False

    # make sure autosmooth is on
    obj.data.use_auto_smooth = True

    if debug:
        print(" » Added modifier '%s' to object '%s'." % (name, obj.name))

    return data_transfer


def normal_transfer_from_stash(active, mapping=None):
    m3.set_mode("OBJECT")

    vert_ids = [v.index for v in active.data.vertices if v.select]

    vgroup = add_vgroup(active, vert_ids, "normal_transfer")

    active.show_wire = False

    stashobj = active.MM.stashes[active.MM.active_stash_idx].obj
    data_transfer = add_normal_transfer_mod(active, stashobj, vgroup.name, vgroup, mapping)
    return vgroup, data_transfer


def normal_transfer_from_obj(active, nrmsrc, vertids=False, vgroup=False, remove_vgroup=False):
    m3.set_mode("OBJECT")

    if vertids:
        vgroup = add_vgroup(active, vertids, "normal_transfer")

    if vgroup:
        data_transfer = add_normal_transfer_mod(active, nrmsrc, vgroup.name, vgroup)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=data_transfer.name)

        if remove_vgroup:
            active.vertex_groups.remove(vgroup)

    m3.set_mode("EDIT")


def normal_clear(active, limit=False):
    debug = True
    debug = False

    if debug:
        m3.clear()
        m3.debug_idx()

    m3.set_mode("OBJECT")

    # get existing loop normals
    mesh = active.data
    mesh.calc_normals_split()

    loop_normals = []
    for loop in mesh.loops:
        loop_normals.append(loop.normal)

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    verts = [v for v in bm.verts if v.select]
    faces = [f for f in bm.faces if f.select]

    for v in verts:
        for l in v.link_loops:
            if not limit or l.face in faces:
                loop_normals[l.index] = mathutils.Vector()

    # set the new normals
    mesh.normals_split_custom_set(loop_normals)
    mesh.use_auto_smooth = True

    m3.set_mode("EDIT")

    return True


def normal_clear_across_sharps(active):
    # get existing loop normals
    mesh = active.data
    mesh.calc_normals_split()

    loop_normals = []
    for loop in mesh.loops:
        loop_normals.append(loop.normal)

    # create bmesh
    bm = bmesh.new()
    bm.from_mesh(active.data)
    bm.normal_update()
    bm.verts.ensure_lookup_table()

    verts = [v for v in bm.verts if v.select]
    edges = [e for e in bm.edges if e.select]
    faces = [f for f in bm.faces if f.select]

    faces_across = []
    for e in edges:
        for f in e.link_faces:
            # boundary edge
            if f not in faces:
                if not e.smooth:  # sharp boundary edge
                    faces_across.append(f)  # unselected face across sharp boundary
                break

    if faces_across:
        for v in verts:
            for l in v.link_loops:
                if l.face in faces_across:
                    loop_normals[l.index] = mathutils.Vector()

        # set the new normals
        mesh.normals_split_custom_set(loop_normals)
        mesh.use_auto_smooth = True
