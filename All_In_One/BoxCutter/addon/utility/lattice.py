import bpy

from mathutils import Vector, Matrix

from . import addon


back = (4, 5, 6, 7)
front = (0, 1, 2, 3)
left = (0, 2, 4, 6)
right = (1, 3, 5, 7)
top = (2, 3, 6, 7)
bottom = (0, 1, 4, 5)


def create(ot, context, event, zero=True):
    bc = context.window_manager.bc

    dat = bpy.data.lattices.new(name='Lattice')
    dat.bc.removeable = True
    bc.lattice = bpy.data.objects.new(name='Lattice', object_data=dat)
    bc.lattice = bc.lattice

    bc.collection.objects.link(bc.lattice)

    dat.interpolation_type_u = 'KEY_LINEAR'
    dat.interpolation_type_v = 'KEY_LINEAR'
    dat.interpolation_type_w = 'KEY_LINEAR'

    del dat

    if ot.shape_type != 'NGON':
        mod = bc.shape.modifiers.new(name='Lattice', type='LATTICE')
        mod.object = bc.lattice

    bc.lattice.hide_set(True)
    bc.shape.hide_set(True)

    bc.lattice.data.transform(bc.lattice.matrix_world.copy().Translation(Vector((0.0, 0.0, -0.5))))

    if ot.origin == 'CORNER':
        bc.lattice.data.transform(bc.lattice.matrix_world.copy().Translation(Vector((0.5, 0.5, 0.0))))

    if zero:
        for point in (0, 1, 2, 3, 4, 5, 6, 7):
            bc.lattice.data.points[point].co_deform.x = 0
            bc.lattice.data.points[point].co_deform.y = 0

        for point in front:
            bc.lattice.data.points[point].co_deform.z = 0

        for point in back:
            bc.lattice.data.points[point].co_deform.z = -0.0002


def center(ot, matrix, side=''):
    bc = bpy.context.window_manager.bc
    sides = {
        'front': front,
        'back': back,
        'left': left,
        'right': right,
        'top': top,
        'bottom': bottom}

    if not side:
        return matrix @ (0.125 * sum((Vector(bc.lattice.data.points[point].co_deform[:]) for point in (0, 1, 2, 3, 4, 5, 6, 7)), Vector()))
    else:
        return matrix @ (0.25 * sum((Vector(bc.lattice.data.points[point].co_deform[:]) for point in sides[side]), Vector()))


def draw(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment
    snap_lock = snap and preference.behavior.increment_lock
    points = bc.lattice.data.points

    location_x = ot.view3d['location'].x
    location_y = ot.view3d['location'].y

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.behavior.increment_amount, 8)
        split = str(increment_amount).split('.')[1]

        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_x = round(round(location_x * 10 / increment_amount) * increment_amount, increment_length)
            location_x *= 0.1
            limit = increment_amount * 0.1

            if ot.view3d['location'].x < 0:
                limit = -limit

            if location_x == 0:
                location_x += limit

            location_y = round(round(location_y * 10 / increment_amount) * increment_amount, increment_length)
            location_y *= 0.1

            if location_y == 0:
                location_y += limit

        else:
            location_x = round(round(location_x / increment_amount) * increment_amount, increment_length)
            limit = preference.behavior.increment_amount

            if ot.view3d['location'].x < 0:
                limit = -limit

            if location_x == 0:
                location_x += limit

            location_y = round(round(location_y / increment_amount) * increment_amount, increment_length)

            if location_y == 0:
                location_y += limit


    index1 = 0 if ot.view3d['location'].x < ot.view3d['origin'].x else 1
    sides = ('left', 'right')
    side = globals()[sides[index1]]
    clear = globals()[sides[not index1]]

    use_alt = event.alt and preference.keymap.alt_draw # and not event.ctrl
    use_shift = event.shift and preference.keymap.shift_draw # and not event.ctrl

    if use_alt and not use_shift:

        for point in side:
            points[point].co_deform.x = location_x
        for point in clear:
            points[point].co_deform.x = -location_x

    elif use_shift and not use_alt:

        for point in side:
            points[point].co_deform.x = location_x
        for point in clear:
            points[point].co_deform.x = 0

    elif use_shift and use_alt:

        for point in side:
            points[point].co_deform.x = location_x
        for point in clear:
            points[point].co_deform.x = -location_x

    elif not use_alt or not use_shift:

        for point in side:
            points[point].co_deform.x = location_x

        if ot.origin == 'CORNER':
            for point in clear:
                points[point].co_deform.x = 0

        elif ot.origin == 'CENTER':
            for point in clear:
                points[point].co_deform.x = -location_x

    index2 = 0 if ot.view3d['location'].y > ot.view3d['origin'].y else 1
    sides = ('bottom', 'top')
    side = globals()[sides[index2]]
    clear = globals()[sides[not index2]]

    if use_alt and not use_shift:

        for point in side:
            points[point].co_deform.y = location_y
        for point in clear:
            points[point].co_deform.y = -location_y

    elif use_shift and not use_alt:

        for point in side:
            points[point].co_deform.y = location_x if index1 != index2 else -location_x
        for point in clear:
            points[point].co_deform.y = 0

    elif use_shift and use_alt:

        for point in side:
            points[point].co_deform.y = location_x if index1 != index2 else -location_x
        for point in clear:
            points[point].co_deform.y = -location_x if index1 != index2 else location_x

    elif not use_alt or not use_shift:
        if ot.origin == 'CENTER':
            for point in side:
                points[point].co_deform.y = location_x if index1 != index2 else -location_x

        else:
            for point in side:
                points[point].co_deform.y = location_y

        if ot.origin == 'CENTER':
            for point in clear:
                points[point].co_deform.y = -location_x if index1 != index2 else location_x

        else:
            for point in clear:
                points[point].co_deform.y = 0


def offset(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment
    snap_lock = snap and preference.behavior.increment_lock
    shape = bc.shape
    lat = bc.lattice
    points = lat.data.points

    location_z = ot.view3d['location'].z

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.behavior.increment_amount, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
            location_z *= 0.1

        else:
            location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

    if location_z > ot.start['extrude']:
        matrix = ot.start['matrix'] @ Matrix.Translation(Vector((0, 0, location_z)))
        shape.matrix_world.translation = matrix.translation
        lat.matrix_world.translation = matrix.translation

        for point in back:
            points[point].co_deform.z = -location_z + ot.start['extrude']

    else:
        matrix = ot.start['matrix'] @ Matrix.Translation(Vector((0, 0, ot.start['extrude'])))
        shape.matrix_world.translation = matrix.translation
        lat.matrix_world.translation = matrix.translation

        for point in back:
            points[point].co_deform.z = 0.0


def extrude(ot, context, event):
    preference = addon.preference()
    bc = context.window_manager.bc
    snap = preference.behavior.snap and preference.behavior.snap_increment
    snap_lock = snap and preference.behavior.increment_lock
    points = bc.lattice.data.points

    location_z = ot.view3d['location'].z

    if snap and event.ctrl or snap_lock:
        increment_amount = round(preference.behavior.increment_amount, 8)
        split = str(increment_amount).split('.')[1]
        increment_length = len(split) if int(split) != 0 else 0

        if event.shift:
            location_z = round(round(location_z * 10 / increment_amount) * increment_amount, increment_length)
            location_z *= 0.1

        else:
            location_z = round(round(location_z / increment_amount) * increment_amount, increment_length)

    for point in back:
        points[point].co_deform.z = location_z if location_z < 0 else -0.0001
