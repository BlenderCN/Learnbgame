import bpy
import bmesh

from mathutils import Matrix, Vector

from .. import addon, lattice, modifier

current_index = 0
sum_index = 0


def clear_sum():
    global sum_index
    sum_index = 0


def cycle(ot, context, event, index=1, custom=None):
    global current_index
    global sum_index

    preference = addon.preference()
    bc = context.window_manager.bc

    bc.lattice.hide_set(False)

    original_active = context.active_object
    context.view_layer.objects.active = bc.shape
    bc.shape.select_set(True)

    matrix = bc.shape.matrix_world.copy()
    dimension = Vector(bc.shape.dimensions)

    if not custom and not bc.shape.bc.applied and not bc.shape.bc.applied_cycle:
        bc.shape.bc.applied_cycle = True
        keep_modifiers = [type for type in ['ARRAY', 'BEVEL', 'SOLIDIFY', 'SCREW', 'MIRROR'] if getattr(preference.behavior, F'keep_{type.lower()}')]
        modifier.apply(obj=bc.shape, exclude=[mod for mod in bc.shape.modifiers if mod.type in keep_modifiers])

        for obj in ot.datablock['targets']:
            modifier.shape_bool(ot, obj).object = None

        for obj in ot.datablock['slices']:
            modifier.shape_bool(ot, obj).object = None

    objects = []
    for obj in bc.collection.objects:
        holdout = obj.bc.applied_cycle and not (sum_index > len(bc.collection.objects) - 1) or obj.bc.copy

        if obj.type == 'MESH' and obj != bc.shape and not holdout:
            objects.append(obj)

    obj = None
    if not custom:
        next_index = current_index + index

        if next_index > len(objects) - 1:
            next_index = 0

        elif next_index < -1:
            next_index = len(objects) - 1

        current_index = next_index
        sum_index += 1

        if objects:
            obj = objects[next_index if next_index < len(objects) - 1 else 0]
        else:
            return

    del objects

    if bc.shape.bc.copy:
        bpy.data.objects.remove(bc.shape)

    obj = obj if obj else custom

    if custom:
        bpy.data.objects.remove(bc.shape)
        bc.shape = None

    bc.shape = obj.copy()
    bc.collection.objects.link(bc.shape)
    context.view_layer.objects.active = bc.shape

    bc.shape.bc.copy = True
    bc.shape.data = obj.data.copy()

    bc.shape.data.use_auto_smooth = True

    del obj

    modifier.apply(bc.shape, exclude=[mod for mod in bc.shape.modifiers if mod.type == 'BEVEL'])

    scale = bc.shape.matrix_world.to_scale()
    bc.shape.data.transform(Matrix.Scale(scale.x, 4, Vector((1, 0, 0))))
    bc.shape.data.transform(Matrix.Scale(scale.y, 4, Vector((0, 1, 0))))
    bc.shape.data.transform(Matrix.Scale(scale.z, 4, Vector((0, 0, 1))))
    bc.shape.scale = Vector((1, 1, 1))
    bc.shape.location = Vector()
    bc.shape.rotation_euler = Vector()

    center = 0.125 * sum((Vector(point) for point in bc.shape.bound_box), Vector())
    bc.shape.data.transform(Matrix.Translation(-center))

    scale_x = 1 / bc.shape.dimensions[0]
    scale_y = 1 / bc.shape.dimensions[1]
    scale_z = 1 / bc.shape.dimensions[2]

    if bc.shape.bc.shape and len(ot.datablock['targets']):
        scale_x = -scale_x

    if not bc.shape.bc.shape and ot.shape_type == 'CUSTOM':
        scale_y = -scale_y

    bc.shape.data.transform(Matrix.Scale(scale_x, 4, Vector((1, 0, 0))))
    bc.shape.data.transform(Matrix.Scale(scale_y, 4, Vector((0, 1, 0))))
    bc.shape.data.transform(Matrix.Scale(-scale_z, 4, Vector((0, 0, 1))))

    bm = bmesh.new()
    bm.from_mesh(bc.shape.data)

    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    for f in bm.faces:
        f.smooth = True

    bm.to_mesh(bc.shape.data)
    bm.free()

    for obj in ot.datablock['targets']:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and not mod.object:
                mod.object = bc.shape

    for obj in ot.datablock['slices']:
        for mod in obj.modifiers:
            if mod.type == 'BOOLEAN' and not mod.object:
                mod.object = bc.shape

    bc.lattice.matrix_world = Matrix()

    points = [Vector(point.co_deform) for point in bc.lattice.data.points]
    bc.lattice.data.points[0].co_deform = Vector((-0.5, -0.5, -0.5))
    bc.lattice.data.points[1].co_deform = Vector(( 0.5, -0.5, -0.5))
    bc.lattice.data.points[2].co_deform = Vector((-0.5,  0.5, -0.5))
    bc.lattice.data.points[3].co_deform = Vector(( 0.5,  0.5, -0.5))
    bc.lattice.data.points[4].co_deform = Vector((-0.5, -0.5,  0.5))
    bc.lattice.data.points[5].co_deform = Vector(( 0.5, -0.5,  0.5))
    bc.lattice.data.points[6].co_deform = Vector((-0.5,  0.5,  0.5))
    bc.lattice.data.points[7].co_deform = Vector(( 0.5,  0.5,  0.5))

    mod = bc.shape.modifiers.new(name='Lattice', type='LATTICE')
    mod.object = bc.lattice

    modifier.sort(ot, bc.shape, force=True)

    bc.lattice.data.transform(Matrix.Translation(Vector((0, 0, -0.5))))

    if ot.origin == 'CORNER':
        bc.lattice.data.transform(Matrix.Translation(Vector((0.5, 0.5, 0))))

    for pair in zip(points, bc.lattice.data.points):
        pair[1].co_deform = pair[0]

    bc.shape.display_type = 'WIRE'

    bc.lattice.matrix_world = matrix
    bc.shape.matrix_world = matrix

    bc.shape.hide_set(True)
    bc.lattice.hide_set(True)

    context.view_layer.objects.active = original_active
