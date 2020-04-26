from .. import modifier


def shape(ot, context, event, to=None):
    bc = context.window_manager.bc

    mirror = None

    for mod in bc.shape.modifiers:
        if mod.type == 'MIRROR':
            mirror = mod

            break

    if not to:
        if True not in tuple(bool(axis) for axis in bc.mirror_axis):
            to = 'X'

    if to:
        index = 'XYZ'.index(to)

    if not mirror:
        mod = bc.shape.modifiers.new(name='Mirror', type='MIRROR')

        if bc.original_active:
            mod.mirror_object = bc.original_active

        mod.use_axis = tuple(bool(axis) for axis in bc.mirror_axis)
        mod.use_bisect_axis = (True, True, True)

        if to:
            mod.use_axis[index] = not mod.use_axis[index]

        if bc.original_active:
            location = bc.shape.location @ bc.original_active.matrix_world
        else:
            location = bc.shape.location

        for index in range(len(mod.use_bisect_flip_axis)):
            flip = location[index] < 0
            mod.use_bisect_flip_axis[index] = flip if mod.use_axis[index] else False

        modifier.sort(ot, bc.shape)

    else:
        mod = mirror

        if to:
            mod.use_axis[index] = not mod.use_axis[index]

        if bc.original_active:
            location = bc.shape.location @ bc.original_active.matrix_world
        else:
            location = bc.shape.location

        for index in range(len(mod.use_bisect_flip_axis)):
            flip = location[index] < 0
            mod.use_bisect_flip_axis[index] = flip if mod.use_axis[index] else False


    bc.mirror_axis = mod.use_axis[:]

    del mod
