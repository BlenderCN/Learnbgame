import bpy

from mathutils import Matrix, Vector

from . import refresh
from .. import addon, modifier
from ... import topbar


def change(ot, context, event, to='CUT', init=False):
    preference = addon.preference()
    bc = context.window_manager.bc

    if ot.datablock['targets'] or init:
        value = to if init or to != ot.mode else ot.last['mode']

        offset = preference.shape.offset

        if value == 'MAKE':
            offset = 0
        elif value == 'JOIN':
            offset = -offset

        matrix = ot.start['matrix'] @ Matrix.Translation(Vector((0, 0, offset)))
        bc.shape.matrix_world.translation = matrix.translation
        bc.plane.matrix_world.translation = matrix.translation
        bc.lattice.matrix_world.translation = matrix.translation

        def store_last(value, to):
            if value != to:
                ot.last['mode'] = value
            else:
                ot.last['mode'] = 'CUT' if value != 'CUT' else value

        store_last(value, to)

        for obj in ot.datablock['targets']:
            for mod in obj.modifiers:
                if mod == modifier.shape_bool(ot, obj) or mod.type == 'BOOLEAN' and not mod.object:
                    obj.modifiers.remove(mod)

        if not init and ot.original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            for pair in zip(ot.datablock['targets'], ot.datablock['overrides']):
                obj = pair[0]
                override = pair[1]

                name = obj.data.name
                obj.data.name = 'tmp'
                obj.data = override
                obj.data.name = name

            bpy.ops.object.mode_set(mode='EDIT')

        for obj in ot.datablock['slices']:
            bpy.data.objects.remove(obj)

        ot.datablock['slices'] = list()

        ot.mode = value
        topbar.change_prop(context, 'mode', value)

        if not init:

            refresh.shape(ot, context, event)

            ot.report({'INFO'}, '{}{}{}'.format(
                value.title()[:-1 if value in {'SLICE', 'MAKE'} else len(value)] if value != 'KNIFE' else 'Using Knife',
                't' if value in {'CUT', 'INSET'} else '',
                'ing' if value != 'KNIFE' else ''))
