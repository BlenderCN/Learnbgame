from mathutils import Vector

from . import array, axis, behavior, bevel, display, draw, extrude, mode, move, offset, operation, origin, ray, refresh, solidify

from .. import lattice, mesh, modifier
from .. view3d import location2d_intersect3d, location2d_to_location3d, location3d_to_location2d


def shape(ot, context, event):
    wm = context.window_manager
    bc = wm.bc

    mouse = ot.mouse['location']

    if bc.running:
        matrix = bc.plane.matrix_world
        inverse = matrix.inverted()

        normal = matrix.to_3x3() @ Vector((0, 0, 1))

        ot.mouse['intersect'] = inverse @ location2d_intersect3d(mouse.x, mouse.y, ot.ray['location'], normal)
        ot.view3d['origin'] = matrix.inverted() @ matrix.translation

        in_extrude = ot.operation == 'EXTRUDE'
        coord = lattice.center(ot, matrix, side='back' if in_extrude else 'front')

        thin = bc.lattice.dimensions[2] < 0.0001

        location = inverse @ location2d_to_location3d(mouse.x, mouse.y, coord)
        start_offset = ot.start['offset'] if ot.operation == 'EXTRUDE' else ot.start['offset'] + ot.start['extrude']
        ot.view3d['location'] = Vector((ot.mouse['intersect'].x, ot.mouse['intersect'].y, location.z - start_offset + ot.start['extrude']))

        if ot.operation != 'NONE':
            globals()[ot.operation.lower()].shape(ot, context, event)

        if context.active_object:
            if modifier.shape_bool(ot, context.active_object):
                display.shape.boolean(ot)

        if ot.operation not in {'NONE', 'BEVEL'} and not bc.shape.bc.copy:
            for mod in bc.shape.modifiers:
                if mod.type == 'BEVEL':
                    mod.width = ot.last['modifier']['width'] if ot.last['modifier']['width'] > 0.0004 else 0.0004

                    if mod.width > bevel.clamp(ot):
                        mod.width = bevel.clamp(ot) - 0.0025

        if ot.operation != 'DRAW' and ot.live:
            if ot.mode in {'CUT', 'SLICE', 'INSET', 'JOIN'}:
                if hasattr(wm, 'Hard_Ops_material_options'):
                    bc.shape.hops.status = 'BOOLSHAPE'

                if bc.shape.display_type != 'WIRE':
                    bc.shape.display_type = 'WIRE'
                    bc.shape.hide_set(False)

                if not modifier.shape_bool(ot, context.active_object):
                    modifier.create(ot)

                if ot.original_mode == 'EDIT_MESH':

                    for target in ot.datablock['targets']:
                        for mod in target.modifiers:
                            if mod != modifier.shape_bool(ot, target):
                                mod.show_viewport = False

                                if ot.mode == 'INSET' and mod.type == 'BOOLEAN' and mod.object in ot.datablock['slices'] and not thin:
                                    mod.show_viewport = True

                    modifier.update(ot, context)

            elif ot.mode == 'MAKE':
                if hasattr(wm, 'Hard_Ops_material_options'):
                    bc.shape.hops.status = 'UNDEFINED'

                if bc.shape.display_type != 'SOLID':
                    bc.shape.display_type = 'SOLID'
                    bc.shape.hide_set(True)

                if ot.datablock['targets']:
                    if modifier.shape_bool(ot, context.active_object):
                        modifier.clean(ot)

            elif ot.mode == 'KNIFE':
                if hasattr(wm, 'Hard_Ops_material_options'):
                    bc.shape.hops.status = 'UNDEFINED'

                if bc.shape.display_type != 'WIRE':
                    bc.shape.display_type = 'WIRE'
                    bc.shape.hide_set(False)

                if modifier.shape_bool(ot, context.active_object):
                    modifier.clean(ot)

                mesh.knife(ot, context, event)
