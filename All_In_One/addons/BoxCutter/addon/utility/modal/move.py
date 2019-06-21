# from . import mouse # from __init__
# from . __init__ import mouse
from mathutils import Vector


def shape(ot, context, event):
    bc = context.window_manager.bc
    vector = bc.lattice.matrix_world.to_3x3() @ Vector((ot.mouse['location'].x, ot.mouse['location'].y, 0))
    bc.lattice.matrix_world.translation += vector
    bc.shape.matrix_world.translation += vector
