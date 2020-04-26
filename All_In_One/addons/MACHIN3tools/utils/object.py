import bpy


def flatten(obj):
    bpy.context.scene.update()

    oldmesh = obj.data

    obj.data = obj.to_mesh(bpy.context.depsgraph, apply_modifiers=True)
    obj.modifiers.clear()

    bpy.data.meshes.remove(oldmesh, do_unlink=True)


def add_vgroup(obj, name="", ids=[], weight=1):
    vgroup = obj.vertex_groups.new(name=name)

    if ids:
        vgroup.add(ids, weight, "ADD")

    return vgroup


def add_facemap(obj, name="", ids=[]):
    fmap = obj.face_maps.new(name=name)

    if ids:
        fmap.add(ids)

    return fmap
