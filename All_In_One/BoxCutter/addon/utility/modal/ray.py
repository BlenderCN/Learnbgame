import bpy

from math import radians
from mathutils import Vector, Matrix

from . import refresh
from .. import addon, lattice, object, modifier, ray
from ... import topbar


def custom(ot, context, event, axis=None):
    preference = addon.preference()
    bc = context.window_manager.bc

    verts = [Vector(( 100000.0,  100000.0, 0.0)), Vector((-100000.0,  100000.0, 0.0)),
             Vector((-100000.0, -100000.0, 0.0)), Vector(( 100000.0, -100000.0, 0.0))]

    edges = [(0, 1), (1, 2),
             (2, 3), (3, 0)]

    faces = [(0, 1, 2, 3)]

    data = bpy.data.meshes.new(name='Box')
    data.bc.removeable = True

    if not bc.snap.hit:
        data.from_pydata(verts, edges, faces)
        data.validate()

    original_active = context.active_object

    box = bpy.data.objects.new(name='Box', object_data=data if not bc.snap.hit else bc.snap.mesh)
    bpy.context.scene.collection.objects.link(box)
    context.view_layer.objects.active = box

    if not axis:
        axis = preference.cursor_axis

    if not bc.snap.hit:
        current = {
            'X': 'Y',
            'Y': 'X',
            'Z': 'Z'}

        rotation = Matrix.Rotation(radians(-90 if axis in {'X', 'Y'} else 90), 4, current[axis])

        cursor = context.scene.cursor.rotation_euler.to_matrix().to_4x4()
        cursor.translation = context.scene.cursor.location

        matrix = cursor @ rotation if preference.surface == 'CURSOR' else rotation

        box.data.transform(matrix)
        box.data.validate()
        context.scene.update()

    if bc.snap.hit:
        hit, ot.ray['location'], ot.ray['normal'], index = ray.cast.objects(*ot.mouse['location'], mesh=bc.snap.mesh)
    else:
        hit, ot.ray['location'], ot.ray['normal'], index = ray.cast.objects(*ot.mouse['location'], obj=box)

    if not hit:
        index = [axis == a for a in 'XYZ'].index(True)

        if index > 1:
            index = 0
        else:
            index += 1

        axis = 'XYZ'[index]

        bpy.data.objects.remove(box)

        del box

        custom(ot, context, event, axis=axis)
        return

    bc.lattice.matrix_world = matrix if not bc.snap.hit else Matrix()
    bc.lattice.matrix_world.translation = Vector(ot.ray['location'][:] if not bc.snap.hit else bc.snap.location)
    bc.shape.matrix_world = bc.lattice.matrix_world
    bc.plane.matrix_world = bc.lattice.matrix_world

    ot.start['matrix'] = bc.plane.matrix_world.copy()

    bc.location = ot.ray['location'] if not bc.snap.hit else bc.snap.location

    context.view_layer.objects.active = original_active

    bpy.data.objects.remove(box)

    del box

    refresh.shape(ot, context, event)


def screen(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc

    verts = [Vector((-1000.0, -1000.0, 0.0)), Vector(( 1000.0, -1000.0, 0.0)),
             Vector((-1000.0,  1000.0, 0.0)), Vector(( 1000.0,  1000.0, 0.0))]

    edges = [(0, 2), (0, 1),
             (1, 3), (2, 3)]

    faces = [(0, 1, 3, 2)]

    data = bpy.data.meshes.new(name='Box')
    data.bc.removeable = True

    if not bc.snap.hit:
        data.from_pydata(verts, edges, faces)
        data.validate()

    box = bpy.data.objects.new(name='Box', object_data=data if not bc.snap.hit else bc.snap.mesh)
    bpy.context.scene.collection.objects.link(box)

    del data

    box.data.bc.removeable = True if not bc.snap.hit else False

    if not bc.snap.hit:
        mod = box.modifiers.new(name='Solidify', type='SOLIDIFY')
        mod.thickness = max(dimension for dimension in ot.datablock['dimensions']) * 1.75
        mod.offset = 0

        modifier.apply(obj=box, mod=mod)

        del mod

        box.data.transform(context.region_data.view_rotation.to_euler().to_matrix().to_4x4())

        matrix = Matrix()
        matrix.translation = bc.original_active.matrix_world @ object.center(bc.original_active)

        box.data.transform(matrix)

    hit, ot.ray['location'], ot.ray['normal'], index = ray.cast.objects(*ot.mouse['location'], mesh=box.data)

    bpy.data.objects.remove(box)

    del box

    bc.lattice.matrix_world = context.region_data.view_rotation.to_euler().to_matrix().to_4x4()
    bc.lattice.matrix_world.translation = Vector(ot.ray['location'][:] if not bc.snap.hit else bc.snap.location)
    bc.shape.matrix_world = bc.lattice.matrix_world
    bc.plane.matrix_world = bc.lattice.matrix_world

    ot.start['matrix'] = bc.plane.matrix_world.copy()

    bc.location = ot.ray['location'] if not bc.snap.hit else bc.snap.location
    refresh.shape(ot, context, event)


# TODO: consider parent matrix
def surface(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc

    obj = context.active_object if not bc.snap.hit else bc.snap.object

    # TODO: needs to pick obj ray trace target for matrix
    if ot.active_only: # XXX: add different prop controller for this?
        if len(ot.datablock['targets']) == 2:
            for o in ot.datablock['targets']:
                if o != context.active_object:
                    obj = o

    ray_normal = ot.ray['normal'] if not bc.snap.hit else Vector(bc.snap.normal[:])
    normal = obj.matrix_world.inverted().to_3x3() @ ray_normal
    track_quat = normal.to_track_quat('Z', 'Y')
    track_mat = track_quat.to_matrix().to_4x4()
    track_mat.translation = bc.plane.data.polygons[0].center

    # XXX: doesnt work for rotated objects properly
    ray_location = ot.ray['location'] if not bc.snap.hit else bc.snap.location
    bc.lattice.matrix_world = obj.matrix_world @ track_mat
    bc.lattice.matrix_world.translation = Vector(ray_location[:])
    bc.shape.matrix_world = bc.lattice.matrix_world
    bc.plane.matrix_world = bc.lattice.matrix_world

    del obj

    ot.start['matrix'] = bc.plane.matrix_world.copy()

    bc.location = ray_location
    refresh.shape(ot, context, event)
