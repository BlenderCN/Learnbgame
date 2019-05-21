import bpy

from mathutils import Vector

from . import addon


front = (4, 5, 6, 7)
back = (0, 1, 2, 3)
left = (0, 2, 4, 6)
right = (1, 3, 5, 7)
top = (2, 3, 6, 7)
bottom = (0, 1, 4, 5)


def create(ot, context, event):
    dat = bpy.data.lattices.new(name='Lattice')
    dat.bc.removeable = True
    ot.datablock['lattice'] = bpy.data.objects.new(name='Lattice', object_data=dat)
    bpy.data.collections['Cutters'].objects.link(ot.datablock['lattice'])

    ot.datablock['lattice'].hide_viewport = True

    dat.interpolation_type_u = 'KEY_LINEAR'
    dat.interpolation_type_v = 'KEY_LINEAR'
    dat.interpolation_type_w = 'KEY_LINEAR'

    mod = ot.datablock['shape'].modifiers.new(name='Lattice', type='LATTICE')
    mod.object = ot.datablock['lattice']

    addon.log(value='Created lattice modifier on shape', indent=2)

    if ot.shape == 'CIRCLE' and ot.mode !='MAKE':
        mod = ot.datablock['shape_d'].modifiers.new(name='Lattice', type='LATTICE')
        mod.object = ot.datablock['lattice']

        addon.log(value='Created lattice modifier on shape display', indent=2)

    addon.log(value='Created lattice modifier on simple', indent=2)

    ot.datablock['lattice'].data.transform(ot.datablock['lattice'].matrix_world.copy().Translation(Vector((0.0, 0.0, -0.5))))

    if ot.origin == 'CORNER':
        ot.datablock['lattice'].data.transform(ot.datablock['lattice'].matrix_world.copy().Translation(Vector((0.5, 0.5, 0.0))))

    addon.log(value='Moved lattice to origin', indent=2)

    for point in ot.datablock['lattice'].data.points:
        point.co_deform.z = 0.0002

    for point in front:
        ot.datablock['lattice'].data.points[point].co_deform.z -= 0.0004

    addon.log(value='Flattened lattice', indent=2)


def center(ot, matrix, side=''):
    sides = {
        'front': front,
        'back': back,
        'left': left,
        'right': right,
        'top': top,
        'bottom': bottom}

    if not side:
        return matrix @ (0.125 * sum((Vector(ot.datablock['lattice'].data.points[point].co_deform[:]) for point in (0, 1, 2, 3, 4, 5, 6, 7)), Vector()))
    else:

        return matrix @ (0.25 * sum((Vector(ot.datablock['lattice'].data.points[point].co_deform[:]) for point in sides[side]), Vector()))
