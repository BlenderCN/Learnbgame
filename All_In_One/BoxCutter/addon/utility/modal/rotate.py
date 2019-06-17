from math import radians
from mathutils import Matrix


def shape(ot, context, event, inside=False):
    bc = context.window_manager.bc

    if inside:
        bc.shape.matrix_world @= Matrix.Rotation(radians(90), 4, 'Z')

        return
