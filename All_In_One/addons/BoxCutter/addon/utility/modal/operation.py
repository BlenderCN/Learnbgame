from mathutils import Vector

from . import axis, display, refresh, bevel
from .. import lattice, mesh, modifier
from .. view3d import location2d_intersect3d, location2d_to_location3d, location3d_to_location2d
from ... import topbar


def change(ot, context, event, to='NONE', modified=True, init=False, clear_mods=[]):
    bc = context.window_manager.bc
    rebevel = False
    ot.modified = modified

    if not init:
        ot.last['operation'] = ot.operation

    for mod in bc.shape.modifiers:
        if mod.type in clear_mods:
            setattr(bc.shape.bc, mod.type.lower(), False)
            bc.shape.modifiers.remove(mod)

    if ot.operation == 'DRAW' and ot.shape_type == 'NGON':
        if not ot.add_point:
            mesh.remove_point(ot, context, event)

    elif ot.operation in {'EXTRUDE', 'OFFSET'}:
        ot.start['matrix'] = bc.shape.matrix_world.copy()
        ot.start['extrude'] = bc.lattice.data.points[lattice.back[0]].co_deform.z

    elif ot.operation == 'ARRAY':
        if ot.axis == 'NONE':
            axis.change(ot, context, to='X')

        axis_index = [ot.axis == axis for axis in 'XYZ'].index(True)

        for mod in bc.shape.modifiers:
            if mod.type == 'ARRAY':
                ot.last['modifier']['offset'] = mod.constant_offset_displace[axis_index]
                ot.last['modifier']['count'] = mod.count
                break

        if modified:
            if to == 'ARRAY': to = 'NONE'

    elif ot.operation == 'SOLIDIFY':
        obj = bc.shape if ot.mode != 'INSET' else ot.datablock['slices'][-1]
        for mod in obj.modifiers:
            if mod.type == 'SOLIDIFY':
                if ot.mode != 'INSET':
                    ot.last['modifier']['thickness'] = mod.thickness
                else:
                    ot.last['thickness'] = mod.thickness
                break

        if modified:
            if to == 'SOLIDIFY': to = 'NONE'

        del obj

    elif ot.operation == 'BEVEL':
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                ot.last['modifier']['width'] = mod.width
                ot.last['modifier']['segments'] = mod.segments
                ot.last['modifier']['limit_method'] = mod.limit_method
                ot.last['modifier']['use_only_vertices'] = mod.use_only_vertices
                ot.last['modifier']['use_clamp_overlap'] = mod.use_clamp_overlap
                break

        ot.last['mouse'] = ot.mouse['location']

        if modified:
            if to == 'BEVEL':
                to = 'NONE'

    bevel_mod = True in [mod.type == 'BEVEL' for mod in bc.shape.modifiers]
    if bevel_mod and ot.shape_type == 'NGON' and to == 'EXTRUDE':
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                bc.shape.modifiers.remove(mod)

        rebevel = True

    if ot.modified and ot.alt_lock:
        ot.alt_lock = False

    value = to

    ot.operation = value
    topbar.change_prop(context, 'operation', value)

    if value in {'EXTRUDE', 'OFFSET'}:
        mouse = ot.mouse['location']

        matrix = bc.plane.matrix_world
        inverse = matrix.inverted()

        in_extrude = ot.operation == 'EXTRUDE'
        coord = lattice.center(ot, matrix, side='back' if in_extrude else 'front')

        location = inverse @ location2d_to_location3d(mouse.x, mouse.y, coord)

        ot.start['offset'] = location.z if not ot.align_to_view else 0


    elif value == 'ROTATE':
        ot.angle = 0
        ot.last['track'] = ot.mouse['location'] - location3d_to_location2d(bc.lattice.matrix_world.translation)
        ot.last['mouse'] = ot.mouse['location']
        ot.axis = 'Z' if ot.axis == 'NONE' else ot.axis

    elif value == 'ARRAY':
        bc.shape.bc.array = True
        if ot.axis == 'NONE':
            axis.change(ot, context, to='Y')

        axis_index = [ot.axis == axis for axis in 'XYZ'].index(True)

        for mod in bc.shape.modifiers:
            if mod.type == 'ARRAY':
                ot.last['modifier']['offset'] = mod.constant_offset_displace[axis_index]
                ot.last['modifier']['count'] = mod.count
                break

    elif value == 'SOLIDIFY':
        bc.shape.bc.solidify = True
        obj = bc.shape if ot.mode != 'INSET' else ot.datablock['slices'][-1]
        for mod in obj.modifiers:
            if mod.type == 'SOLIDIFY':
                if ot.mode != 'INSET':
                    ot.last['modifier']['thickness'] = mod.thickness
                else:
                    ot.last['thickness'] = mod.thickness
                break

        del obj

        ot.last['mouse'] = ot.mouse['location']

    elif value == 'BEVEL':
        bc.shape.bc.bevel = True
        for mod in bc.shape.modifiers:
            if mod.type == 'BEVEL':
                bc.shape.modifiers.remove(mod)

        ot.last['mouse'] = ot.mouse['location']

    if not init:
        if value == 'NONE':
            ot.report({'INFO'}, 'Shape Locked')

        else:
            ot.report({'INFO'}, '{}{}{}'.format(
                'Added ' if value == 'ARRAY' else '',
                value.title()[:-1 if value in {'MOVE', 'ROTATE', 'SCALE', 'EXTRUDE'} else len(value)],
                'ing' if value != 'ARRAY' else ''))

        refresh.shape(ot, context, event)

    elif value != 'DRAW':
        refresh.shape(ot, context, event)

    if rebevel:
        bevel.shape(ot, context, event)
